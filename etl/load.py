import json
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS orders (
    order_id     TEXT PRIMARY KEY,
    order_date   DATE NOT NULL,
    customer_id  TEXT NOT NULL,
    product      TEXT NOT NULL,
    category     TEXT NOT NULL,
    quantity     INT NOT NULL,
    unit_price   NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS rejected_orders (
    id         SERIAL PRIMARY KEY,
    source_row INT,
    reason     TEXT,
    raw_data   TEXT
);
"""


def get_connection():
    load_dotenv()
    url = os.getenv("DB_URL")
    if not url:
        raise RuntimeError("DB_URL is not set. Create a .env file (see .env.example).")
    return psycopg2.connect(url)


def load(conn, valid, rejected):
    """Replace the contents of both tables. Everything happens in one transaction."""
    with conn:                                   # commit if OK, rollback if error
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES)
            cur.execute("TRUNCATE orders, rejected_orders RESTART IDENTITY")

            if valid:
                execute_values(
                    cur,
                    """INSERT INTO orders (order_id, order_date, customer_id, product,
                                           category, quantity, unit_price, total_amount)
                       VALUES %s""",
                    [(r["order_id"], r["order_date"], r["customer_id"], r["product"],
                      r["category"], r["quantity"], r["unit_price"], r["total_amount"])
                     for r in valid],
                )

            if rejected:
                execute_values(
                    cur,
                    "INSERT INTO rejected_orders (source_row, reason, raw_data) VALUES %s",
                    [(r["row_number"], r["reason"], json.dumps(r["raw_data"]))
                     for r in rejected],
                )


def count_rows(conn, table):
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]