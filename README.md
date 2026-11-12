# Sales ETL Pipeline

A Python ETL pipeline that cleans a messy sales orders CSV file, loads the valid
rows into PostgreSQL, saves the rejected rows with the reason, and prints SQL reports.

## How it works

1. **Extract** (`etl/extract.py`): reads about 5,000 rows from `data/raw/orders.csv`
2. **Transform** (`etl/transform.py`): cleans each row and checks it against the rules below
3. **Load** (`etl/load.py`): saves good rows to the `orders` table and bad rows to
   `rejected_orders` in PostgreSQL
4. **Report** (`etl/report.py`): runs SQL queries for revenue by category, top products,
   monthly revenue and rejected rows by reason

`etl/pipeline.py` runs all the steps and writes log messages.

## Cleaning and validation rules

A row is rejected if:

- `order_id`, `customer_id` or `product` is missing
- the date is not a real date in `YYYY-MM-DD` or `DD/MM/YYYY` format
- `quantity` is not a positive whole number
- `unit_price` is not a number or is negative
- the `order_id` has already appeared (the first one is kept)

Valid rows are also cleaned: spaces are removed, text is capitalised properly,
`$` and `,` are removed from prices, and `total_amount` is calculated.

## Data quality checks

- Valid rows + rejected rows must equal the rows read from the file
- The pipeline stops if more than 30% of rows are rejected
- Row counts in PostgreSQL must match the rows that were loaded

## Setup

```
git clone https://github.com/JinendraPatil/sales-etl-pipeline.git
cd sales-etl-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a PostgreSQL database called `sales_db`, then copy `.env.example` to `.env`
and put your password in it.

## Run

```
python generate_data.py
python -m etl.pipeline
```

`generate_data.py` creates a messy sample file with about 5,000 rows.

## Run tests

```
python -m pytest
```

Tests also run automatically on every push using GitHub Actions.

## Sample output

```
INFO Extracted 5150 rows from data/raw/orders.csv
INFO Transformed: 4394 valid, 756 rejected
INFO Loaded 4394 orders and 756 rejected rows
```

## If something fails

- **Pipeline failed: DB_URL is not set:** create the `.env` file (see `.env.example`)
- **password authentication failed:** the password in `.env` is wrong
- **Too many bad rows:** the input file has a problem, so check the rejected reasons
  and fix the source. Nothing is loaded in this case.
- **FileNotFoundError:** run `python generate_data.py` or pass the file with `--input`
- **Tests fail:** run `python -m pytest` and read which rule broke

## Tech used

Python, PostgreSQL, psycopg2, pytest, Git, GitHub Actions