import pandas as pd

sheets = pd.read_excel("data/online_retail_II.xlsx", sheet_name=None,
                       dtype={"Invoice": str, "StockCode": str})
df = pd.concat(sheets.values(), ignore_index=True)
df = df.rename(columns={
    "Invoice": "invoice_no", "StockCode": "stock_code", "Description": "description",
    "Quantity": "quantity", "InvoiceDate": "invoice_date", "Price": "unit_price",
    "Customer ID": "customer_id", "Country": "country"})
df["customer_id"] = df["customer_id"].astype("Int64").astype("string")
df.to_csv("data/online_retail_ii.csv", index=False)
print(len(df), "lignes")