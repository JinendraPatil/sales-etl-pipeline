import math
from datetime import datetime

REQUIRED_FIELDS = ["order_id", "customer_id", "product"]
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y"]


def clean_text(value):
    """Turn None into an empty string and remove spaces at both ends."""
    return (value or "").strip()


def parse_date(value):
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(clean_text(value), date_format).date()
        except ValueError:
            pass
    raise ValueError("invalid order_date")


def parse_quantity(value):
    try:
        quantity = int(clean_text(value))
    except ValueError:
        raise ValueError("invalid quantity")
    if quantity <= 0:
        raise ValueError("invalid quantity")
    return quantity


def parse_price(value):
    text = clean_text(value).replace("$", "").replace(",", "")
    try:
        price = float(text)
    except ValueError:
        raise ValueError("invalid unit_price")
    if not math.isfinite(price) or price < 0:
        raise ValueError("invalid unit_price")
    return round(price, 2)


def clean_row(row):
    """Clean one row. Raises ValueError with the reason if the row is bad."""
    for field in REQUIRED_FIELDS:
        if not clean_text(row.get(field)):
            raise ValueError(f"missing {field}")

    quantity = parse_quantity(row.get("quantity"))
    unit_price = parse_price(row.get("unit_price"))

    return {
        "order_id": clean_text(row["order_id"]).upper(),
        "order_date": parse_date(row.get("order_date")),
        "customer_id": clean_text(row["customer_id"]).upper(),
        "product": clean_text(row["product"]).title(),
        "category": clean_text(row.get("category")).title() or "Unknown",
        "quantity": quantity,
        "unit_price": unit_price,
        "total_amount": round(quantity * unit_price, 2),
    }


def transform(rows):
    """Split rows into valid rows and rejected rows (with the reason)."""
    valid = []
    rejected = []
    seen_ids = set()

    for row_number, row in enumerate(rows, start=2):   # line 1 is the header
        try:
            clean = clean_row(row)
            if clean["order_id"] in seen_ids:
                raise ValueError("duplicate order_id")
            seen_ids.add(clean["order_id"])
            valid.append(clean)
        except ValueError as error:
            rejected.append({
                "row_number": row_number,
                "reason": str(error),
                "raw_data": row,
            })

    return valid, rejected