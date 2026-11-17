import duckdb
con = duckdb.connect("data/warehouse.duckdb", read_only=True)
print(con.execute("select count(*), min(invoice_date), max(invoice_date) from raw.order_lines").fetchall())
print(con.execute("select count(*) from raw.fx_rates").fetchall(), con.execute("select count(*) from raw.holidays").fetchall())
print(con.execute("select count(*) filter (where customer_id is null), count(*) filter (where quantity < 0), count(*) filter (where invoice_no like 'C%') from raw.order_lines").fetchall())