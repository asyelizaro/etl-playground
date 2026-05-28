from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

with DAG(
    dag_id="stage1-plpgsql",
    start_date=datetime(2026, 5, 1),
    schedule_interval=None,
    catchup=False,
    template_searchpath=["/opt/airflow/sql"],
    tags=["stage1", "etl", "chinook", "plpgsql", "star-model"],
) as dag:
    
    # 1. Setup stage - подготовка таблицы stage
    with TaskGroup("stage_layer", tooltip="Создание foreign таблиц") as stage_layer:
        setup_stage = PostgresOperator(
            task_id="setup_stage",
            postgres_conn_id="postgres_star_model",
            sql="stage/setup_stage.sql",
        )

    # 2. Setup stage - подготовка объектов в dds
    with TaskGroup("dds_layer", tooltip="Создание детального слоя") as dds_layer:
        dds_table = PostgresOperator(
            task_id="dds_table",
            postgres_conn_id="postgres_star_model",
            sql="dds/dds_table.sql",
        )

        dds_fn_tasks = [
            PostgresOperator(task_id="fn_dim_customer", postgres_conn_id="postgres_star_model", sql="dds/fn_dim_customer.sql"),
            PostgresOperator(task_id="fn_dim_date", postgres_conn_id="postgres_star_model", sql="dds/fn_dim_date.sql"),
            PostgresOperator(task_id="fn_dim_employee", postgres_conn_id="postgres_star_model", sql="dds/fn_dim_employee.sql"),
            PostgresOperator(task_id="fn_dim_genre", postgres_conn_id="postgres_star_model", sql="dds/fn_dim_genre.sql"),
            PostgresOperator(task_id="fn_dim_track", postgres_conn_id="postgres_star_model", sql="dds/fn_dim_track.sql"),
            PostgresOperator(task_id="fn_fact_album", postgres_conn_id="postgres_star_model", sql="dds/fn_fact_album.sql"),
            PostgresOperator(task_id="fn_fact_artist", postgres_conn_id="postgres_star_model", sql="dds/fn_fact_artist.sql"),
            PostgresOperator(task_id="fn_fact_sales", postgres_conn_id="postgres_star_model", sql="dds/fn_fact_sales.sql"),
        ]

        run_dim = [
            PostgresOperator(task_id="run_fn_dim_artist", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_artist();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_genre", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_genre();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_album", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_album();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_track", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_track();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_customer", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_customer();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_employee", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_employee();", retries=2, retry_delay=timedelta(seconds=15)),
            PostgresOperator(task_id="run_fn_dim_date", postgres_conn_id="postgres_star_model", sql="SELECT fn_dim_date();", retries=2, retry_delay=timedelta(seconds=15)),
        ]

        run_facts = [
            PostgresOperator(task_id="run_fn_fact_sales", postgres_conn_id="postgres_star_model", sql="SELECT fn_fact_sales();", retries=2, retry_delay=timedelta(seconds=15)),
        ]

        dds_table >> dds_fn_tasks

        for create_task in dds_fn_tasks:
            create_task >> run_dim
            
        for dim_task in run_dim:
            dim_task >> run_facts

    with TaskGroup("dm_layer", tooltip="Создание слоя витрин данных") as dm_layer:
        dm_table = PostgresOperator(
            task_id="dm_table",
            postgres_conn_id="postgres_star_model",
            sql="dm/dm_table.sql",
        )
        dm_fn_tasks = [
            PostgresOperator(task_id="fn_dm_sales_by_artist", postgres_conn_id="postgres_star_model", sql="dm/fn_dm_sales_by_artist.sql"),
            PostgresOperator(task_id="fn_dm_sales_by_employee", postgres_conn_id="postgres_star_model", sql="dm/fn_dm_sales_by_employee.sql"),
            PostgresOperator(task_id="fn_dm_sales_customer", postgres_conn_id="postgres_star_model", sql="dm/fn_dm_sales_customer.sql"),
        ]

        dm_table >> dm_fn_tasks

        for 

    stage_layer >> dds_layer >> dm_layer