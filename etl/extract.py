"""Extract step: read raw rows from a CSV file."""
import csv
from pathlib import Path
from typing import Iterator


def read_csv(path: str | Path) -> Iterator[dict]:
    """Yield each CSV row as a dict (column name -> raw string)."""
    with open(path, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)
