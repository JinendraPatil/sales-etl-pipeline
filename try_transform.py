from etl.extract import extract
from etl.transform import transform

rows = extract("data/raw/orders.csv")
valid, rejected = transform(rows)
print(len(rows), len(valid), len(rejected))
print(valid[0])
print(rejected[0])