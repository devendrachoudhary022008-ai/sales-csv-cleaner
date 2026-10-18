
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Project folders
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "sales.csv"
OUTPUT_DIR = BASE_DIR / "output"

# Required input columns
REQUIRED_COLUMNS = [
    "order_id",
    "date",
    "product",
    "quantity",
    "unit_price",
]

CLEAN_COLUMNS = REQUIRED_COLUMNS + ["total"]


def clean_text(value):
    """Remove spaces around text and handle missing values."""
    return (value or "").strip()


def process_sales():
    # Make sure the output folder exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return

    cleaned_rows = []
    rejected_rows = []
    seen_records = set()
    daily_sales = defaultdict(float)

    # Read the input CSV
    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Check that required columns exist
        if not reader.fieldnames:
            print("ERROR: CSV file is empty or has no header.")
            return

        reader.fieldnames = [
            clean_text(name) for name in reader.fieldnames
        ]

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            print("ERROR: Missing columns:", ", ".join(missing_columns))
            print("Required columns:", ", ".join(REQUIRED_COLUMNS))
            return

        for line_number, row in enumerate(reader, start=2):
            # Skip completely blank lines
            if not row or all(
                not clean_text(value)
                for value in row.values()
                if value is not None
            ):
                continue

            # Keep a copy of the original data for the rejected report
            original_row = {
                key: clean_text(value)
                for key, value in row.items()
                if key is not None
            }

            try:
                # Clean text fields
                order_id = clean_text(row.get("order_id"))
                sale_date = clean_text(row.get("date"))
                product = clean_text(row.get("product"))
                quantity_text = clean_text(row.get("quantity"))
                price_text = clean_text(row.get("unit_price"))

                # Check required values
                if not all([
                    order_id,
                    sale_date,
                    product,
                    quantity_text,
                    price_text,
                ]):
                    raise ValueError("Missing required value")

                # Validate date format
                parsed_date = datetime.strptime(
                    sale_date, "%Y-%m-%d"
                ).date()

                # Validate numeric fields
                quantity = int(quantity_text)
                unit_price = float(price_text)

                if quantity <= 0:
                    raise ValueError("Quantity must be greater than 0")

                if unit_price < 0:
                    raise ValueError("Unit price cannot be negative")

                # Detect exact duplicate records after text cleanup
                record_key = (
                    order_id,
                    sale_date,
                    product,
                    quantity,
                    unit_price,
                )

                if record_key in seen_records:
                    raise ValueError("Duplicate sales record")

                seen_records.add(record_key)

                # Calculate the total for this sale
                total = quantity * unit_price

                clean_row = {
                    "order_id": order_id,
                    "date": parsed_date.isoformat(),
                    "product": product,
                    "quantity": quantity,
                    "unit_price": f"{unit_price:.2f}",
                    "total": f"{total:.2f}",
                }

                cleaned_rows.append(clean_row)
                daily_sales[parsed_date.isoformat()] += total

            except (ValueError, TypeError, OverflowError) as error:
                rejected_rows.append({
                    **original_row,
                    "line_number": line_number,
                    "rejection_reason": str(error),
                })

    # Save valid sales
    clean_file = OUTPUT_DIR / "cleaned_sales.csv"

    with clean_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=CLEAN_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Save rejected records and the reason for each rejection
    rejected_file = OUTPUT_DIR / "rejected_rows.csv"

    rejected_columns = (
        REQUIRED_COLUMNS + ["line_number", "rejection_reason"]
    )

    with rejected_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rejected_columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rejected_rows)

    # Save daily sales totals
    report_file = OUTPUT_DIR / "daily_sales_report.csv"

    with report_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["date", "total_sales", "valid_orders"],
        )
        writer.writeheader()

        for day in sorted(daily_sales):
            orders_for_day = [
                row for row in cleaned_rows if row["date"] == day
            ]

            writer.writerow({
                "date": day,
                "total_sales": f"{daily_sales[day]:.2f}",
                "valid_orders": len(orders_for_day),
            })

    # Print a summary
    print("\n=== SALES CSV CLEANER: COMPLETE ===")
    print(f"Input records checked: {len(cleaned_rows) + len(rejected_rows)}")
    print(f"Valid records:         {len(cleaned_rows)}")
    print(f"Rejected records:      {len(rejected_rows)}")
    print(f"Total valid sales:     {sum(daily_sales.values()):.2f}")
    print("\nOutput files saved in:", OUTPUT_DIR)
    print("- cleaned_sales.csv")
    print("- rejected_rows.csv")
    print("- daily_sales_report.csv")


if __name__ == "__main__":
    process_sales()
