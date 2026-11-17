import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import requests
from prefect import flow, task

ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = ROOT / "dbt_project"
DB = os.getenv("DUCKDB_PATH", str(ROOT / "data" / "warehouse.duckdb"))
WEBHOOK = os.getenv("ALERT_WEBHOOK_URL")
DBT = [str(Path(sys.executable).parent / "dbt.exe")]
DBT_ARGS = ["--profiles-dir", "."]


def alert(msg: str):
    print(f"ALERTE: {msg}")
    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": f"ðŸš¨ {msg}"}, timeout=10)


def log_run(status: str, duration: float, detail: str = ""):
    con = duckdb.connect(DB)
    con.execute("CREATE SCHEMA IF NOT EXISTS ops")
    con.execute("""CREATE TABLE IF NOT EXISTS ops.pipeline_runs(
        run_at TIMESTAMPTZ, status VARCHAR, duration_s DOUBLE, detail VARCHAR)""")
    con.execute("INSERT INTO ops.pipeline_runs VALUES (?, ?, ?, ?)",
                [datetime.now(UTC), status, round(duration, 2), detail[:500]])
    con.close()


@task(retries=3, retry_delay_seconds=30, timeout_seconds=300)
def ingest():
    subprocess.run([sys.executable, "ingestion/ingest.py"], check=True, cwd=ROOT,
                   env={**os.environ, "DUCKDB_PATH": DB})


@task
def freshness():
    subprocess.run(DBT + ["source", "freshness"] + DBT_ARGS, check=True, cwd=DBT_DIR)


@task
def build():
    # dbt build = modÃ¨les + tests, dans l'ordre du DAG
    subprocess.run(DBT + ["build"] + DBT_ARGS, check=True, cwd=DBT_DIR)


@flow(name="daily-pipeline")
def pipeline():
    start = time.time()
    try:
        ingest()
        freshness()
        build()
    except Exception as e:
        log_run("FAILED", time.time() - start, str(e))
        alert(f"Pipeline Ã©chouÃ© : {e}")
        raise
    log_run("SUCCESS", time.time() - start)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        pipeline.serve(name="daily", cron="0 6 * * *")  # tous les jours Ã  06h00
    else:
        pipeline()
