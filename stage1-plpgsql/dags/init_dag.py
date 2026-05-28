from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    dag_id="chinook_init_all",
    start_date=datetime(2026, 5, 1),
    schedule_interval=None,
    catchup=False,
    template_searchpath=["/opt/airflow/sql"],
) as dag:

    # 1. setup stage
    setup_stage = PostgresOperator(
        task_id="init_chinook",
        postgres_conn_id="postgres_chinook",
        sql="stage/setup_stage.sql",
    )


    setup_stage