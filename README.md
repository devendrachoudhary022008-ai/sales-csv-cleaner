# Sales CSV Cleaner

A beginner-friendly Python automation project that cleans sales CSV data, detects invalid and duplicate records, and generates useful reports.

## Features

- Reads sales data from a CSV file.
- Removes unnecessary spaces from values.
- Validates dates, quantities, prices, and required fields.
- Detects duplicate sales records.
- Calculates total sales for each valid record.
- Exports rejected records with rejection reasons.
- Generates a daily sales summary.

## Project Structure

```text
sales-csv-cleaner/
├── main.py
├── data/
│   └── sales.csv
├── output/
│   ├── cleaned_sales.csv
│   ├── rejected_rows.csv
│   └── daily_sales_report.csv
└── README.md
```

## Requirements

- Python 3
- No third-party Python packages required.

## How to Run

1. Download or clone this repository.
2. Open the project folder in a terminal.
3. Place your input CSV at `data/sales.csv`.
4. Run:

```bash
python main.py
```

The generated reports will appear in the `output/` directory.

## Output Files

- `cleaned_sales.csv` — validated sales records with calculated totals.
- `rejected_rows.csv` — rejected records and their rejection reasons.
- `daily_sales_report.csv` — date-wise sales totals and valid order counts.

## Learning Goals

This project demonstrates Python functions, CSV processing, file handling, validation, exception handling, and automated report generation.