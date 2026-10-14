"""Report step: analytics queries on the loaded data."""
import sqlite3


def revenue_by_category(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute(
        """SELECT category, ROUND(SUM(total_amount), 2) AS revenue
           FROM orders GROUP BY category ORDER BY revenue DESC"""
    ).fetchall()


def top_products(conn: sqlite3.Connection, n: int = 3) -> list[tuple]:
    return conn.execute(
        """SELECT product, SUM(quantity) AS units, ROUND(SUM(total_amount), 2) AS revenue
           FROM orders GROUP BY product ORDER BY revenue DESC LIMIT ?""",
        (n,),
    ).fetchall()


def daily_revenue(conn: sqlite3.Connection) -> list[tuple]:
    return conn.execute(
        """SELECT order_date, ROUND(SUM(total_amount), 2) AS revenue
           FROM orders GROUP BY order_date ORDER BY order_date"""
    ).fetchall()


def print_report(conn: sqlite3.Connection) -> None:
    print("\n=== Revenue by category ===")
    for category, revenue in revenue_by_category(conn):
        print(f"{category:<15} {revenue:>10.2f}")

    print("\n=== Top 3 products ===")
    for product, units, revenue in top_products(conn, 3):
        print(f"{product:<15} {units:>5} units {revenue:>10.2f}")

    print("\n=== Daily revenue ===")
    for day, revenue in daily_revenue(conn):
        print(f"{day}  {revenue:>10.2f}")
