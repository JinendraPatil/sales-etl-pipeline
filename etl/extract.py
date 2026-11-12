import csv


def extract(path):
    """Read the CSV file and return a list of rows (each row is a dictionary)."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))