from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    dag_id="stage1-plpgsql",
    start_date=datetime(2026, 5, 1),
    schedule_interval=None,
    catchup=False,
    template_searchpath=["/opt/airflow/sql"],
    tags=["stage1", "etl", "chinook", "plpgsql", "star-model"],
) as dag:

    # 1. Setup stage - подготовка таблицы stage
    setup_stage = PostgresOperator(
        task_id="setup_stage",
        postgres_conn_id="postgres_star_model",
        sql="stage/setup_stage.sql",
    )
