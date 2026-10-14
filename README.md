# Sales ETL Pipeline

A small, readable **ETL (Extract → Transform → Load)** pipeline in pure Python.
It takes a messy sales-orders CSV, cleans and validates it, loads it into a
SQLite "warehouse", and prints SQL analytics reports.

Built as a data-engineering practice project. It uses only the Python standard
library (plus `pytest` for tests), so it runs anywhere with no setup.

## What it does

```
data/raw/orders.csv ──► extract ──► transform ──► load ──► report
                                      │             │
                                      │             └─► data/warehouse.db (SQLite)
                                      └─► data/rejected_rows.csv (bad rows + reason)
```

| Stage       | File                | Responsibility |
|-------------|---------------------|----------------|
| Extract     | `etl/extract.py`    | Stream rows from CSV with `csv.DictReader` |
| Transform   | `etl/transform.py`  | Parse dates (2 formats), strip `$`/`,` from prices, normalise text, validate, de-duplicate |
| Load        | `etl/load.py`       | **Idempotent upsert** into SQLite; write rejected rows to CSV |
| Report      | `etl/report.py`     | SQL aggregations: revenue by category, top products, daily revenue |
| Entry point | `etl/pipeline.py`   | CLI that wires the stages together with logging |

## Data-quality rules

Rows are **rejected** (and saved with a `reject_reason`) when:

- `order_id`, `customer_id` or `product` is missing
- the date is not `YYYY-MM-DD` or `DD/MM/YYYY`
- `quantity` is not a positive integer
- `unit_price` is not a number or is negative
- the `order_id` was already seen (first occurrence wins)

## Quick start

```bash
git clone <your-repo-url>
cd sales-etl-pipeline

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m etl.pipeline           # run the pipeline on the sample data
python -m pytest                 # run the tests
```

Custom paths:

```bash
python -m etl.pipeline --input data/raw/orders.csv --db data/warehouse.db --rejects data/rejected_rows.csv
```

### Sample output

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

## Design decisions

- **Idempotent loads:** `INSERT ... ON CONFLICT DO UPDATE` means re-running the
  pipeline never creates duplicate rows, which is essential for real pipelines
  that get retried.
- **Rejects are kept, not dropped:** bad rows go to `rejected_rows.csv` with a
  reason so data issues can be investigated.
- **Small pure functions:** each parser (`parse_date`, `parse_price`, ...) is
  independently testable.
- **ISO dates in the warehouse:** keeps date sorting and grouping simple in SQL.

## Project structure

```
sales-etl-pipeline/
├── data/raw/orders.csv      # sample messy input
├── etl/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── report.py
│   └── pipeline.py
├── tests/
│   ├── test_transform.py
│   └── test_load.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Ideas for extension

- Add a `--min-amount` CLI filter or a new validation rule
- Add a `monthly_revenue` or `revenue_by_country` report
- Support a second input format (JSON / Parquet)
- Add a data-quality summary (rejects grouped by reason)
- Schedule it with cron or Airflow

## License

MIT
