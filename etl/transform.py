"""Transform step: clean, validate and de-duplicate raw rows."""
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


class ValidationError(ValueError):
    """Raised when a raw row cannot be turned into a valid Order."""


@dataclass(frozen=True)
class Order:
    order_id: str
    order_date: str      # ISO format: YYYY-MM-DD
    customer_id: str
    product: str
    category: str
    quantity: int
    unit_price: float
    country: str

    @property
    def total_amount(self) -> float:
        return round(self.quantity * self.unit_price, 2)


def parse_date(value: str) -> str:
    """Accept several date formats and return ISO YYYY-MM-DD."""
    value = (value or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValidationError(f"invalid date: {value!r}")


def parse_price(value: str) -> float:
    """Handle values like ' $12.50 ' or '1,200.00'."""
    cleaned = (value or "").strip().replace("$", "").replace(",", "")
    try:
        price = float(cleaned)
    except ValueError:
        raise ValidationError(f"invalid unit_price: {value!r}")
    if price < 0:
        raise ValidationError(f"negative unit_price: {price}")
    return price


def parse_quantity(value: str) -> int:
    try:
        qty = int((value or "").strip())
    except ValueError:
        raise ValidationError(f"invalid quantity: {value!r}")
    if qty <= 0:
        raise ValidationError(f"quantity must be positive: {qty}")
    return qty


def clean_row(raw: dict) -> Order:
    """Convert one raw CSV row into an Order, or raise ValidationError."""
    required = ("order_id", "customer_id", "product")
    for field in required:
        if not (raw.get(field) or "").strip():
            raise ValidationError(f"missing {field}")

    return Order(
        order_id=raw["order_id"].strip(),
        order_date=parse_date(raw.get("order_date", "")),
        customer_id=raw["customer_id"].strip(),
        product=raw["product"].strip().title(),
        category=(raw.get("category") or "Unknown").strip().title(),
        quantity=parse_quantity(raw.get("quantity", "")),
        unit_price=parse_price(raw.get("unit_price", "")),
        country=(raw.get("country") or "Unknown").strip().upper(),
    )


def transform(rows: Iterable[dict]) -> tuple[list[Order], list[tuple[dict, str]]]:
    """Return (valid_orders, rejected) where rejected = [(raw_row, reason)].

    Duplicate order_ids are rejected: the first occurrence wins.
    """
    valid: list[Order] = []
    rejected: list[tuple[dict, str]] = []
    seen: set[str] = set()

    for raw in rows:
        try:
            order = clean_row(raw)
        except ValidationError as err:
            rejected.append((raw, str(err)))
            continue

        if order.order_id in seen:
            rejected.append((raw, "duplicate order_id"))
            continue
        seen.add(order.order_id)
        valid.append(order)

    return valid, rejected
