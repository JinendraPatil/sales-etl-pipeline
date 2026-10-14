from etl.load import connect, load_orders
from etl.transform import Order


def sample_order(**overrides):
    data = dict(order_id="1", order_date="2024-03-01", customer_id="C1",
                product="Laptop", category="Electronics", quantity=1,
                unit_price=100.0, country="IN")
    data.update(overrides)
    return Order(**data)


def test_load_is_idempotent(tmp_path):
    conn = connect(tmp_path / "test.db")
    load_orders(conn, [sample_order()])
    load_orders(conn, [sample_order()])
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1


def test_load_updates_existing_row(tmp_path):
    conn = connect(tmp_path / "test.db")
    load_orders(conn, [sample_order(quantity=1)])
    load_orders(conn, [sample_order(quantity=5)])
    qty, total = conn.execute("SELECT quantity, total_amount FROM orders").fetchone()
    assert (qty, total) == (5, 500.0)
