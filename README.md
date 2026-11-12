# Sales ETL Pipeline

A small ETL (Extract, Transform, Load) pipeline written in Python. It reads a messy sales orders CSV file, cleans and validates the data, loads it into a SQLite database, and prints a few SQL reports.

I built this as a practice project for data engineering. It only uses the Python standard library (plus pytest for tests), so there is nothing extra to set up.

## How it works

1. **Extract** (`etl/extract.py`): reads rows from `data/raw/orders.csv`.
2. **Transform** (`etl/transform.py`): cleans the data. It parses dates in two formats, removes `$` and `,` from prices, normalises text, validates each row and removes duplicate orders.
3. **Load** (`etl/load.py`): saves valid rows into SQLite (`data/warehouse.db`). Bad rows are written to `data/rejected_rows.csv` along with the reason.
4. **Report** (`etl/report.py`): runs SQL queries for revenue by category, top products and daily revenue.

`etl/pipeline.py` is the entry point that runs all the steps with logging. Tests are in the `tests` folder.

## Validation rules

A row is rejected if:

- `order_id`, `customer_id` or `product` is missing
- the date is not in `YYYY-MM-DD` or `DD/MM/YYYY` format
- `quantity` is not a positive whole number
- `unit_price` is not a number or is negative
- the `order_id` has already appeared (the first one is kept)

## Setup

```bash
git clone https://github.com/JinendraPatil/sales-etl-pipeline.git
cd sales-etl-pipeline

python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m etl.pipeline
```

You can also pass your own file paths:

```bash
python -m etl.pipeline --input data/raw/orders.csv --db data/warehouse.db --rejects data/rejected_rows.csv
```

## Run tests

```bash
python -m pytest
```

## Sample output

```
INFO Extracted 13 rows from data/raw/orders.csv
INFO Transformed: 8 valid, 5 rejected
INFO Loaded 8 rows into data/warehouse.db

=== Revenue by category ===
Electronics        2120.97
Home                135.00
Stationery           49.00

=== Top 3 products ===
Laptop              2 units    1949.99
Desk Lamp           3 units     135.00
Headphones          2 units     119.98
```

