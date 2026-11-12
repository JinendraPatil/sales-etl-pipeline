from datetime import date

import pytest

from etl.transform import (clean_row, parse_date, parse_price,
                           parse_quantity, transform)


def make_row(**changes):
    """A valid row. Pass keyword arguments to change a field."""
    row = {
        "order_id": "ORD-1",
        "order_date": "2024-03-15",
        "customer_id": "C001",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "100.00",
    }
    row.update(changes)
    return row


def test_parse_date_accepts_both_formats():
    assert parse_date("2024-03-15") == date(2024, 3, 15)
    assert parse_date("15/03/2024") == date(2024, 3, 15)


def test_parse_date_rejects_bad_dates():
    with pytest.raises(ValueError):
        parse_date("31/02/2024")
    with pytest.raises(ValueError):
        parse_date("yesterday")


def test_parse_price_removes_dollar_and_comma():
    assert parse_price("$1,299.99") == 1299.99


def test_parse_price_rejects_negative_and_text():
    with pytest.raises(ValueError):
        parse_price("-15.00")
    with pytest.raises(ValueError):
        parse_price("abc")


def test_parse_quantity_must_be_positive_whole_number():
    assert parse_quantity(" 3 ") == 3
    for bad in ["0", "-2", "two", "", "2.5"]:
        with pytest.raises(ValueError):
            parse_quantity(bad)


def test_clean_row_normalises_text_and_calculates_total():
    row = make_row(product="  laptop ", category="ELECTRONICS", order_id=" ord-1 ")
    clean = clean_row(row)
    assert clean["product"] == "Laptop"
    assert clean["category"] == "Electronics"
    assert clean["order_id"] == "ORD-1"
    assert clean["total_amount"] == 200.00


def test_clean_row_rejects_missing_required_field():
    with pytest.raises(ValueError, match="missing customer_id"):
        clean_row(make_row(customer_id=""))


def test_transform_keeps_first_duplicate_and_rejects_the_rest():
    rows = [make_row(), make_row(), make_row(order_id="ORD-2")]
    valid, rejected = transform(rows)
    assert len(valid) == 2
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "duplicate order_id"


def test_transform_never_loses_rows():
    rows = [make_row(), make_row(quantity="0"), make_row(order_id=""), make_row()]
    valid, rejected = transform(rows)
    assert len(valid) + len(rejected) == len(rows)


def test_rejected_row_keeps_row_number_and_original_data():
    rows = [make_row(), make_row(order_id="ORD-2", unit_price="abc")]
    valid, rejected = transform(rows)
    assert rejected[0]["row_number"] == 3          # line 1 is the header
    assert rejected[0]["reason"] == "invalid unit_price"
    assert rejected[0]["raw_data"]["unit_price"] == "abc"