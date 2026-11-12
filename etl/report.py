QUERIES = {
    "Revenue by category": """
        SELECT category, ROUND(SUM(total_amount), 2) AS revenue
        FROM orders GROUP BY category ORDER BY revenue DESC""",
    "Top 5 products by revenue": """
        SELECT product, SUM(quantity) AS units, ROUND(SUM(total_amount), 2) AS revenue
        FROM orders GROUP BY product ORDER BY revenue DESC LIMIT 5""",
    "Monthly revenue": """
        SELECT TO_CHAR(order_date, 'YYYY-MM') AS order_month,
               ROUND(SUM(total_amount), 2) AS revenue
        FROM orders GROUP BY order_month ORDER BY order_month""",
    "Rejected rows by reason": """
        SELECT reason, COUNT(*) AS row_count
        FROM rejected_orders GROUP BY reason ORDER BY row_count DESC""",
}


def print_reports(conn):
    with conn.cursor() as cur:
        for title, sql in QUERIES.items():
            cur.execute(sql)
            print(f"\n=== {title} ===")
            for row in cur.fetchall():
                print("   ".join(str(value) for value in row))