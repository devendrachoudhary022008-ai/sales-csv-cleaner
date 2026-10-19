import csv
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import main
from main import clean_text


class TestCleanText(unittest.TestCase):

    def test_none_becomes_empty_string(self):
        self.assertEqual(clean_text(None), "")

    def test_removes_extra_spaces(self):
        self.assertEqual(clean_text("  Keyboard  "), "Keyboard")

    def test_date_becomes_iso_format(self):
        self.assertEqual(clean_text(date(2026, 10, 19)), "2026-10-19")

    def test_datetime_becomes_date_only(self):
        value = datetime(2026, 10, 19, 14, 30)
        self.assertEqual(clean_text(value), "2026-10-19")


class TestSalesValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.output_dir = self.root / "output"
        self.data_dir.mkdir()

        self.csv_file = self.data_dir / "sales.csv"
        self.excel_file = self.data_dir / "sales.xlsx"
        self.headers = [
            "order_id", "date", "product", "quantity", "unit_price"
        ]

        patcher_csv = patch.object(main, "CSV_FILE", self.csv_file)
        patcher_excel = patch.object(main, "EXCEL_FILE", self.excel_file)
        patcher_output = patch.object(main, "OUTPUT_DIR", self.output_dir)

        patcher_csv.start()
        patcher_excel.start()
        patcher_output.start()

        self.addCleanup(patcher_csv.stop)
        self.addCleanup(patcher_excel.stop)
        self.addCleanup(patcher_output.stop)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_sales(self, rows):
        with self.csv_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(rows)

        with patch("builtins.print"):
            main.process_sales()

        with (self.output_dir / "cleaned_sales.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            cleaned = list(csv.DictReader(file))

        with (self.output_dir / "rejected_rows.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            rejected = list(csv.DictReader(file))

        return cleaned, rejected

    def test_valid_sale_calculates_total(self):
        rows = [{
            "order_id": "A001", "date": "2026-10-19",
            "product": "Keyboard", "quantity": "2", "unit_price": "800",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["total"], "1600.00")
        self.assertEqual(len(rejected), 0)

    def test_zero_quantity_is_rejected(self):
        rows = [{
            "order_id": "A002", "date": "2026-10-19",
            "product": "Mouse", "quantity": "0", "unit_price": "400",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 0)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Quantity must be greater than 0",
                      rejected[0]["rejection_reason"])

    def test_invalid_date_is_rejected(self):
        rows = [{
            "order_id": "A003", "date": "19-10-2026",
            "product": "Mouse", "quantity": "1", "unit_price": "400",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 0)
        self.assertEqual(len(rejected), 1)

    def test_duplicate_record_is_rejected(self):
        row = {
            "order_id": "A004", "date": "2026-10-19",
            "product": "Mouse", "quantity": "1", "unit_price": "400",
        }
        cleaned, rejected = self.run_sales([row, row])
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Duplicate sales record",
                      rejected[0]["rejection_reason"])

    def test_missing_required_value_is_rejected(self):
        rows = [{
            "order_id": "A005", "date": "2026-10-19",
            "product": "", "quantity": "1", "unit_price": "400",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 0)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Missing required value",
                      rejected[0]["rejection_reason"])

    def test_negative_unit_price_is_rejected(self):
        rows = [{
            "order_id": "A006", "date": "2026-10-19",
            "product": "Keyboard", "quantity": "1", "unit_price": "-100",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 0)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Unit price cannot be negative",
                      rejected[0]["rejection_reason"])

    def test_non_finite_unit_prices_are_rejected(self):
        for price in ["NaN", "inf", "-inf"]:
            with self.subTest(price=price):
                rows = [{
                    "order_id": "A008",
                    "date": "2026-10-19",
                    "product": "Keyboard",
                    "quantity": "1",
                    "unit_price": price,
                }]

                cleaned, rejected = self.run_sales(rows)

                self.assertEqual(len(cleaned), 0)
                self.assertEqual(len(rejected), 1)
                self.assertIn(
                    "finite number",
                    rejected[0]["rejection_reason"]
                )
    def test_output_write_error_is_handled(self):
        with patch.object(
            main, "process_sales",
            side_effect=OSError("Permission denied")
        ):
            with patch("builtins.print") as mocked_print:
                main.main()

        printed_output = " ".join(
            str(call) for call in mocked_print.call_args_list
        )
        self.assertIn(
            "ERROR: Could not create or write output files",
            printed_output,
        )
        self.assertIn("Permission denied", printed_output)
    

    def test_decimal_quantity_is_rejected(self):
        rows = [{
            "order_id": "A007", "date": "2026-10-19",
            "product": "Mouse", "quantity": "1.5", "unit_price": "400",
        }]
        cleaned, rejected = self.run_sales(rows)
        self.assertEqual(len(cleaned), 0)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Quantity must be a whole number",
                      rejected[0]["rejection_reason"])


    def test_missing_required_columns_are_reported(self):
        with self.csv_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["order_id", "date", "quantity"])

        with patch("builtins.print") as mocked_print:
            main.process_sales()

        printed_output = " ".join(
            str(call) for call in mocked_print.call_args_list
        )
        self.assertIn("Missing columns", printed_output)
        self.assertIn("product", printed_output)
        self.assertIn("unit_price", printed_output)


    def test_empty_csv_is_reported(self):
        with self.csv_file.open("w", encoding="utf-8"):
            pass

        with patch("builtins.print") as mocked_print:
            main.process_sales()

        printed_output = " ".join(
            str(call) for call in mocked_print.call_args_list
        )
        self.assertIn(
            "CSV file is empty or has no header",
            printed_output
        )

