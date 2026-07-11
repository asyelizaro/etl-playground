from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "scripts",
        "02_silver"
    )
)

from engine import run_table



def run_silver_table(table_name, **context):

    dt = context.get("ds")

    return run_table(
        table_name,
        dt=dt
    )



with DAG(
    dag_id="silver_load",
    start_date=datetime(2026, 7, 1),
    schedule_interval=None,
    catchup=False,

    default_args={
        "owner": "airflow",
        "retries": 0,
        "retry_delay": timedelta(minutes=1),
    },
    tags=[
        "stage2",
        "silver"
    ],
    description="Generic Silver loader",

) as dag:


    load_artist = PythonOperator(
        task_id="load_artist",
        python_callable=run_silver_table,
        op_kwargs={
            "table_name": "artist"
        },
    )

# Задаем зависимости между задачами:
load_artist 