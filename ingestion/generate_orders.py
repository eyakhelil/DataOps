import random
from datetime import date, datetime, timedelta

import pandas as pd


def generate(day: date, n_customers=200) -> pd.DataFrame:
    rnd = random.Random(day.toordinal())
    products = pd.read_csv("data/products.csv")["product_id"].tolist()
    rows = []
    for i in range(rnd.randint(80, 120)):
        ts = datetime.combine(day, datetime.min.time()) + timedelta(seconds=rnd.randint(0, 86399))
        rows.append({
            "order_id": f"{day:%Y%m%d}-{i:04d}",
            "customer_id": f"C{rnd.randint(1, n_customers):04d}",
            "product_id": rnd.choice(products),
            "quantity": rnd.randint(1, 5),
            "amount": round(rnd.uniform(10, 300), 2),
            "currency": rnd.choice(["EUR", "EUR", "USD"]),
            "created_at": ts,
        })
    return pd.DataFrame(rows)