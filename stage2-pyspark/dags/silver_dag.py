from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts", "02_silver"))

from engine import run_table


def run_silver_artist(**context):
    dt = context.get("ds") or context.get("logical_date")
    return run_table("artist", dt=str(dt))


with DAG(
    dag_id="silver_artist_test",
    start_date=datetime(2026, 7, 1),
    schedule_interval=None,
    catchup=False,
    default_args={
        "owner": "airflow",
        "retries": 0,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["stage2", "silver", "test"],
    description="Minimal DAG to trigger the silver artist handler",
) as dag:

    silver_task = PythonOperator(
        task_id="run_silver_artist",
        python_callable=run_silver_artist,
    )
