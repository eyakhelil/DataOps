import argparse
import os
import sys
from datetime import UTC, date, datetime, timedelta

import duckdb
import pandas as pd
import requests

DB = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")
START, END = date(2009, 12, 1), date(2011, 12, 9)


def upsert(con, table, df):
    con.register("df", df)
    con.execute(f"INSERT OR REPLACE INTO raw.{table} SELECT * FROM df")
    con.unregister("df")


def load_lines(d1: date, d2: date) -> pd.DataFrame:
    df = pd.read_csv("data/online_retail_ii.csv",
                     dtype={"invoice_no": str, "stock_code": str, "customer_id": str},
                     parse_dates=["invoice_date"])
    # numéro de ligne calculé AVANT le filtre => line_id stable d'une exécution à l'autre
    df["line_id"] = df["invoice_no"] + "-" + df.groupby("invoice_no").cumcount().astype(str)
    day = df["invoice_date"].dt.date
    return df[(day >= d1) & (day <= d2)]


def window(con, args) -> tuple[date, date]:
    if args.day:  # recharger un jour précis (test d'idempotence)
        d = date.fromisoformat(args.day)
        return d, d
    rows = con.execute("select last_day from ops.ingest_cursor where source='orders'").fetchall()
    d1 = rows[0][0] + timedelta(days=1) if rows else START
    return d1, min(d1 + timedelta(days=args.backfill - 1), END)


def fetch_fx(start: date, end: date) -> pd.DataFrame:
    url = f"https://api.frankfurter.dev/v1/{start - timedelta(days=7)}..{end}"
    r = requests.get(url, params={"base": "GBP", "symbols": "EUR,USD"}, timeout=30)
    r.raise_for_status()
    rows = [{"rate_date": d, "base": "GBP", "quote": q, "rate": v}
            for d, rates in r.json()["rates"].items() for q, v in rates.items()]
    df = pd.DataFrame(rows)
    df["rate_date"] = pd.to_datetime(df["rate_date"]).dt.date
    return df


def fetch_holidays(year: int, country: str = "GB") -> pd.DataFrame:
    r = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}", timeout=30)
    r.raise_for_status()
    df = pd.DataFrame([{"holiday_date": h["date"], "country_code": h["countryCode"],
                        "name": h["name"]} for h in r.json()])
    df["holiday_date"] = pd.to_datetime(df["holiday_date"]).dt.date
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backfill", type=int, default=1)  # nombre de jours à charger
    p.add_argument("--day")                            # jour précis (AAAA-MM-JJ)
    args = p.parse_args()

    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    con = duckdb.connect(DB)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS ops")
    con.execute("""CREATE TABLE IF NOT EXISTS raw.order_lines(
        line_id VARCHAR PRIMARY KEY, invoice_no VARCHAR, stock_code VARCHAR,
        description VARCHAR, quantity INTEGER, unit_price DOUBLE,
        invoice_date TIMESTAMP, customer_id VARCHAR, country VARCHAR,
        ingested_at TIMESTAMPTZ)""")
    con.execute("""CREATE TABLE IF NOT EXISTS raw.fx_rates(
        rate_date DATE, base VARCHAR, quote VARCHAR, rate DOUBLE,
        ingested_at TIMESTAMPTZ, PRIMARY KEY(rate_date, base, quote))""")
    con.execute("""CREATE TABLE IF NOT EXISTS raw.holidays(
        holiday_date DATE, country_code VARCHAR, name VARCHAR,
        ingested_at TIMESTAMPTZ, PRIMARY KEY(holiday_date, country_code))""")
    con.execute("""CREATE TABLE IF NOT EXISTS ops.ingest_cursor(
        source VARCHAR PRIMARY KEY, last_day DATE)""")

    now = datetime.now(UTC)
    d1, d2 = window(con, args)
    if d1 > END:
        print("Historique terminé")
        return

    cols = ["line_id", "invoice_no", "stock_code", "description", "quantity",
            "unit_price", "invoice_date", "customer_id", "country"]
    lines = load_lines(d1, d2)[cols].copy()
    lines["ingested_at"] = now
    upsert(con, "order_lines", lines)

    fx = fetch_fx(d1, d2)
    fx["ingested_at"] = now
    upsert(con, "fx_rates", fx)

    for year in range(d1.year, d2.year + 1):
        hol = fetch_holidays(year)
        hol["ingested_at"] = now
        upsert(con, "holidays", hol)

    if not args.day:  # le curseur n'avance qu'après un chargement réussi
        con.execute("INSERT OR REPLACE INTO ops.ingest_cursor VALUES ('orders', ?)", [d2])

    n = con.execute("select count(*) from raw.order_lines").fetchall()[0][0]
    print(f"OK: {len(lines)} lignes chargées ({d1} -> {d2}), total {n}")


if __name__ == "__main__":
    sys.exit(main())