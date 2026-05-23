from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    dag_id="stage1_etl_pipeline",
    start_date=datetime(2026, 5, 1),
    schedule_interval=None,
    catchup=False,
    template_searchpath=["/opt/airflow/sql"],
    tags=["stage1", "etl", "chinook"],
) as dag:

    # 1. Setup stage - подготовка таблицы stage
    setup_stage = PostgresOperator(
        task_id="setup_stage",
        postgres_conn_id="postgres_chinook",
        sql="stage/setup_stage.sql",
    )

    # 2. DDS - Создание таблиц
    create_dds_tables = PostgresOperator(
        task_id="create_dds_tables",
        postgres_conn_id="postgres_chinook",
        sql="dds/dds_table.sql",
    )

    # 3. DDS - Инициализация функций
    init_functions = PostgresOperator(
        task_id="init_functions",
        postgres_conn_id="postgres_chinook",
        sql="dds/start_function.sql",
    )

    # 4. DDS - Загрузка измерений (Dimension Tables)
    load_dim_customer = PostgresOperator(
        task_id="load_dim_customer",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_customer.sql",
    )

    load_dim_date = PostgresOperator(
        task_id="load_dim_date",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_date.sql",
    )

    load_dim_employee = PostgresOperator(
        task_id="load_dim_employee",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_employee.sql",
    )

    load_dim_genre = PostgresOperator(
        task_id="load_dim_genre",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_genre.sql",
    )

    load_dim_track = PostgresOperator(
        task_id="load_dim_track",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_dim_track.sql",
    )

    # 5. DDS - Загрузка фактов (Fact Tables)
    load_fact_album = PostgresOperator(
        task_id="load_fact_album",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_fact_album.sql",
    )

    load_fact_artist = PostgresOperator(
        task_id="load_fact_artist",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_fact_artist.sql",
    )

    load_fact_sales = PostgresOperator(
        task_id="load_fact_sales",
        postgres_conn_id="postgres_chinook",
        sql="dds/fn_fact_sales.sql",
    )

    # 6. DM - Создание таблиц Data Marts
    create_dm_tables = PostgresOperator(
        task_id="create_dm_tables",
        postgres_conn_id="postgres_chinook",
        sql="dm/dm_table.sql",
    )

    # 7. DM - Загрузка витрин данных
    dm_sales_by_artist = PostgresOperator(
        task_id="dm_sales_by_artist",
        postgres_conn_id="postgres_chinook",
        sql="dm/fn_dm_sales_by_artist.sql",
    )

    dm_sales_by_employee = PostgresOperator(
        task_id="dm_sales_by_employee",
        postgres_conn_id="postgres_chinook",
        sql="dm/fn_dm_sales_by_employee.sql",
    )

    dm_sales_customer = PostgresOperator(
        task_id="dm_sales_customer",
        postgres_conn_id="postgres_chinook",
        sql="dm/fn_dm_sales_customer.sql",
    )

    # Определение зависимостей
    (
        setup_stage
        >> create_dds_tables
        >> init_functions
        >> [
            load_dim_customer,
            load_dim_date,
            load_dim_employee,
            load_dim_genre,
            load_dim_track,
        ]
    )

    (
        [
            load_dim_customer,
            load_dim_date,
            load_dim_employee,
            load_dim_genre,
            load_dim_track,
        ]
        >> [load_fact_album, load_fact_artist, load_fact_sales]
    )

    (
        [load_fact_album, load_fact_artist, load_fact_sales]
        >> create_dm_tables
        >> [dm_sales_by_artist, dm_sales_by_employee, dm_sales_customer]
    )
