import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
NUM_ROWS = 5000

# product: (category, normal price)
PRODUCTS = {
    "Laptop": ("Electronics", 1299.99),
    "Monitor": ("Electronics", 189.50),
    "Headphones": ("Electronics", 59.99),
    "Keyboard": ("Electronics", 45.00),
    "Wireless Mouse": ("Electronics", 24.99),
    "Phone Charger": ("Electronics", 15.99),
    "Office Chair": ("Home", 149.00),
    "Desk Lamp": ("Home", 45.00),
    "Water Bottle": ("Home", 12.50),
    "Backpack": ("Accessories", 39.99),
    "Notebook": ("Stationery", 4.50),
    "Pen Set": ("Stationery", 8.99),
}

rows = []
for i in range(NUM_ROWS):
    product = random.choice(list(PRODUCTS))
    category, price = PRODUCTS[product]
    order_date = date(2024, 1, 1) + timedelta(days=random.randint(0, 365))

    # two date formats and two price formats
    if random.random() < 0.5:
        date_text = order_date.strftime("%Y-%m-%d")
    else:
        date_text = order_date.strftime("%d/%m/%Y")
    if random.random() < 0.3:
        price_text = f"${price:,.2f}"
    else:
        price_text = f"{price:.2f}"

    row = {
        "order_id": f"ORD-{1000 + i}",
        "order_date": date_text,
        "customer_id": f"C{random.randint(1, 400):03d}",
        "product": product,
        "category": category,
        "quantity": str(random.randint(1, 5)),
        "unit_price": price_text,
    }

    # extra spaces and wrong capitalisation (still valid after cleaning)
    if random.random() < 0.15:
        row["product"] = "  " + product.lower() + " "
        row["category"] = category.upper()

    # about 12% of rows get one real problem
    roll = random.random()
    if roll < 0.02:
        row["order_id"] = ""
    elif roll < 0.04:
        row["customer_id"] = ""
    elif roll < 0.06:
        row["product"] = ""
    elif roll < 0.08:
        row["order_date"] = random.choice(["2024-13-45", "31/02/2024", "yesterday"])
    elif roll < 0.10:
        row["quantity"] = random.choice(["0", "-2", "two", ""])
    elif roll < 0.12:
        row["unit_price"] = random.choice(["abc", "-15.00", ""])

    rows.append(row)

# about 3% duplicate rows
for _ in range(int(NUM_ROWS * 0.03)):
    rows.append(dict(random.choice(rows)))

random.shuffle(rows)

os.makedirs("data/raw", exist_ok=True)
with open("data/raw/orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {len(rows)} rows in data/raw/orders.csv")