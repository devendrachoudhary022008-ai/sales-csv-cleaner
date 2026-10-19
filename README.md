# Sales Data Cleaner

A Python automation tool that cleans sales data from CSV and Excel files, validates records, detects duplicates, and generates sales reports.

## Features

- Reads CSV (data/sales.csv) or Excel (data/sales.xlsx) input.
- Prioritizes CSV when both input files exist.
- Trims unnecessary spaces and validates required fields, dates, quantities, and prices.
- Detects duplicate sales records.
- Calculates sales totals and exports rejected records with reasons.
- Generates a daily sales summary.

## Requirements

- Python 3
- openpyxl 3.1.5 or newer

## Installation

Install the dependency:

```powershell
py -m pip install -r requirements.txt
```

## How to Run

1. Put your input file in the data/ folder.
2. Ensure the first row contains these headers: order_id, date, product, quantity, unit_price.
3. Run:

```powershell
py main.py
```

If both input files exist, CSV is used first. Excel is used when the CSV file is absent.

## Output Files

Reports are saved in output/:

- cleaned_sales.csv - Validated records with calculated totals.
- ejected_rows.csv - Rejected records and their reasons.
- daily_sales_report.csv - Daily sales totals and valid order counts.

## Learning Goals

This project demonstrates Python functions, CSV processing, Excel handling, data validation, duplicate detection, file operations, and automated report generation.
