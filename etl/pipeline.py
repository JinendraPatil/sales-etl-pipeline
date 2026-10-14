"""Command-line entry point: extract -> transform -> load -> report."""
import argparse
import logging

from etl.extract import read_csv
from etl.load import connect, load_orders, write_rejects
from etl.report import print_report
from etl.transform import transform

log = logging.getLogger("etl")


def run(input_path: str, db_path: str, rejects_path: str) -> None:
    raw_rows = list(read_csv(input_path))
    log.info("Extracted %d rows from %s", len(raw_rows), input_path)

    valid, rejected = transform(raw_rows)
    log.info("Transformed: %d valid, %d rejected", len(valid), len(rejected))

    conn = connect(db_path)
    loaded = load_orders(conn, valid)
    log.info("Loaded %d rows into %s", loaded, db_path)

    write_rejects(rejects_path, rejected)
    if rejected:
        log.warning("Rejected rows written to %s", rejects_path)

    print_report(conn)
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales ETL pipeline")
    parser.add_argument("--input", default="data/raw/orders.csv")
    parser.add_argument("--db", default="data/warehouse.db")
    parser.add_argument("--rejects", default="data/rejected_rows.csv")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(args.input, args.db, args.rejects)


if __name__ == "__main__":
    main()
