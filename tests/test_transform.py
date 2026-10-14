import pytest

from etl.transform import ValidationError, clean_row, parse_date, parse_price, transform


def make_row(**overrides):
    row = {
        "order_id": "1", "order_date": "2024-03-01", "customer_id": "C1",
        "product": "laptop", "category": "electronics",
        "quantity": "2", "unit_price": "$10.50", "country": "in",
    }
    row.update(overrides)
    return row


def test_parse_date_handles_both_formats():
    assert parse_date("2024-03-01") == "2024-03-01"
    assert parse_date("01/03/2024") == "2024-03-01"


def test_parse_date_rejects_garbage():
    with pytest.raises(ValidationError):
        parse_date("yesterday")


def test_parse_price_strips_symbols():
    assert parse_price(" $1,200.50 ") == 1200.50


def test_clean_row_normalises_text_and_computes_total():
    order = clean_row(make_row(product="  wireless mouse "))
    assert order.product == "Wireless Mouse"
    assert order.country == "IN"
    assert order.total_amount == 21.0


@pytest.mark.parametrize("field,value", [
    ("customer_id", ""), ("quantity", "0"), ("quantity", "abc"), ("unit_price", "-5"),
])
def test_clean_row_rejects_bad_values(field, value):
    with pytest.raises(ValidationError):
        clean_row(make_row(**{field: value}))


def test_transform_rejects_duplicates_keeping_first():
    rows = [make_row(order_id="1"), make_row(order_id="1", quantity="9")]
    valid, rejected = transform(rows)
    assert len(valid) == 1 and valid[0].quantity == 2
    assert rejected[0][1] == "duplicate order_id"
