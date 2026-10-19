# Sales Data Cleaner

A Python automation tool that cleans sales data from CSV and Excel files, validates records, detects duplicates, and generates daily sales reports.

This project demonstrates how repetitive spreadsheet-cleaning work can be automated to save time and make sales data easier to review.

## Features

- Reads CSV and Excel input files.
- Prioritizes CSV when both input files exist.
- Cleans unnecessary whitespace.
- Validates required columns, dates, quantities, and unit prices.
- Detects duplicate sales records.
- Separates valid records from rejected records and includes rejection reasons.
- Calculates sales totals.
- Generates a daily sales summary.
- Logs application start, successful completion, and output-related errors.
- Includes automated unit tests.

## Example Results

Using the included sample CSV file, the program reported:

| Metric | Result |
|---|---:|
| Input records checked | 17 |
| Valid records | 12 |
| Rejected records | 5 |
| Total valid sales | 29500.00 |

Results depend on the input file.

## Requirements

- Python 3
- openpyxl 3.1.5 or newer

## Installation

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install the dependency:

```powershell
py -m pip install -r requirements.txt
```

## How to Run

1. Place your input file in the `data/` folder.
2. Ensure the first row contains these required headers:

   `order_id, date, product, quantity, unit_price`

3. Run the program:

```powershell
py main.py
```

If both input files exist, the program uses `data/sales.csv` first. It uses `data/sales.xlsx` when the CSV file is absent.

## Output Files

Generated files are saved in the `output/` folder:

- `cleaned_sales.csv` — validated records with calculated totals.
- `rejected_rows.csv` — rejected records and their reasons.
- `daily_sales_report.csv` — daily sales totals and valid order counts.
- `sales_cleaner.log` — application log messages.

## Run the Tests

Run the automated tests with:

```powershell
py -m unittest discover -s tests -v
```

## Limitations

- Input files must contain the required column headers.
- CSV input is prioritized when both supported input files exist.
- Review rejected records before using the cleaned data for business decisions.

## Technologies

- Python
- CSV processing
- openpyxl
- unittest
- logging

## Project Purpose

This project demonstrates Python-based data cleaning, validation, file handling, error handling, automated testing, and report generation.