from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "scripts", "02_silver"),
)

from engine import load_config, run_table


def run_silver_table(table_name, **context):
    return run_table(table_name, dt=context.get("ds"))


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
    tags=["stage2", "silver"],
    description="Config-driven Data Vault Silver loader",
) as dag:
    table_configs = load_config()["tables"]
    tasks = {}

    for table_config in table_configs:
        table_name = table_config["name"]
        tasks[table_name] = PythonOperator(
            task_id=f"load_{table_name}",
            python_callable=run_silver_table,
            op_kwargs={"table_name": table_name},
        )

    for table_config in table_configs:
        downstream_task = tasks[table_config["name"]]
        for upstream_name in table_config.get("depends_on", []):
            tasks[upstream_name] >> downstream_task
