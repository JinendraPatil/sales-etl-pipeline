"""Load step: write clean orders into SQLite (idempotent upsert)."""
import csv
import sqlite3
from pathlib import Path
from typing import Iterable

from etl.transform import Order

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id      TEXT PRIMARY KEY,
    order_date    TEXT NOT NULL,
    customer_id   TEXT NOT NULL,
    product       TEXT NOT NULL,
    category      TEXT NOT NULL,
    quantity      INTEGER NOT NULL,
    unit_price    REAL NOT NULL,
    total_amount  REAL NOT NULL,
    country       TEXT NOT NULL
);
"""

UPSERT = """
INSERT INTO orders (order_id, order_date, customer_id, product, category,
                    quantity, unit_price, total_amount, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(order_id) DO UPDATE SET
    order_date   = excluded.order_date,
    customer_id  = excluded.customer_id,
    product      = excluded.product,
    category     = excluded.category,
    quantity     = excluded.quantity,
    unit_price   = excluded.unit_price,
    total_amount = excluded.total_amount,
    country      = excluded.country;
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def load_orders(conn: sqlite3.Connection, orders: Iterable[Order]) -> int:
    """Upsert orders. Running the pipeline twice will not create duplicates."""
    rows = [
        (o.order_id, o.order_date, o.customer_id, o.product, o.category,
         o.quantity, o.unit_price, o.total_amount, o.country)
        for o in orders
    ]
    conn.executemany(UPSERT, rows)
    conn.commit()
    return len(rows)


def write_rejects(path: str | Path, rejected: list[tuple[dict, str]]) -> None:
    """Save rejected rows with the reason, so bad data can be investigated."""
    if not rejected:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rejected[0][0].keys()) + ["reject_reason"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for raw, reason in rejected:
            writer.writerow({**raw, "reject_reason": reason})
