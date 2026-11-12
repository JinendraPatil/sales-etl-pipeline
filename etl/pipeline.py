import argparse
import logging
import sys

from etl.extract import extract
from etl.load import count_rows, get_connection, load
from etl.report import print_reports
from etl.transform import transform

MAX_REJECT_RATE = 0.30   # stop the pipeline if more than 30% of rows are bad


def run(input_path):
    rows = extract(input_path)
    logging.info("Extracted %d rows from %s", len(rows), input_path)

    valid, rejected = transform(rows)
    logging.info("Transformed: %d valid, %d rejected", len(valid), len(rejected))

    # Check 1: no row was lost during transform
    if len(valid) + len(rejected) != len(rows):
        raise RuntimeError("Row count mismatch after transform")

    # Check 2: too many bad rows means something is wrong with the file
    if rows and len(rejected) / len(rows) > MAX_REJECT_RATE:
        raise RuntimeError(
            f"Too many bad rows ({len(rejected)} of {len(rows)}). Nothing was loaded."
        )

    conn = get_connection()
    try:
        load(conn, valid, rejected)

        # Check 3: the database has the same number of rows we sent
        if count_rows(conn, "orders") != len(valid):
            raise RuntimeError("orders table row count does not match")
        if count_rows(conn, "rejected_orders") != len(rejected):
            raise RuntimeError("rejected_orders table row count does not match")
        logging.info("Loaded %d orders and %d rejected rows", len(valid), len(rejected))

        print_reports(conn)
    finally:
        conn.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Sales ETL pipeline")
    parser.add_argument("--input", default="data/raw/orders.csv")
    args = parser.parse_args()

    try:
        run(args.input)
    except Exception as error:
        logging.error("Pipeline failed: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()