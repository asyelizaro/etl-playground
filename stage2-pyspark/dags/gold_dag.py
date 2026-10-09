import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts", "03_gold"))

from artist_sales import build_sales_by_artist


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="gold_load",
    start_date=datetime(2026, 7, 1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
    tags=["stage2", "gold"],
    description="PySpark Gold mart for artist sales in ClickHouse",
) as dag:

    build_artist_sales = PythonOperator(
        task_id="build_sales_by_artist",
        python_callable=build_sales_by_artist,
    )