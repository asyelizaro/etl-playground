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
        task_id="setup_stage",
        postgres_conn_id="postgres_chinook",
        sql="stage/setup_stage.sql",
    )

    # 2. DDL dds
    create_dds_tables = PostgresOperator(
        task_id="create_dds_tables",
        postgres_conn_id="postgres_chinook",
        sql="dds/dds_table.sql",
    )

    # 3. Функции dim
    load_dim_customer = PostgresOperator(
        task_id="load_dim_customer",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_customer.sql",
    )
    # load_dim_artist, load_dim_genre, и т.д. — аналогично

    # 4. Функция факта
    fn_fact_sales = PostgresOperator(
        task_id="create_fn_fact_sales",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_fact_sales.sql",
    )

    setup_stage >> create_dds_tables
    create_dds_tables >> load_dim_customer
    load_dim_customer >> fn_fact_sales