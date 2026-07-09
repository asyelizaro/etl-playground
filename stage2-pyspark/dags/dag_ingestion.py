from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "scripts", "01_ingestion"))

from ingestion import (
    get_chinook_engine,
    get_minio_client,
    extract_table_to_parquet,
    upload_to_minio,
    TABLES
)

logger = logging.getLogger(__name__)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}


def run_ingestion():
    logger.info("Starting ingestion pipeline")

    engine = get_chinook_engine()
    s3_client = get_minio_client()

    stats = {}

    for table in TABLES:
        try:
            buffer, df = extract_table_to_parquet(engine, table)
            upload_to_minio(s3_client, buffer, table)

            stats[table] = {
                "rows": len(df),
                "status": "success"
            }

            logger.info(f"{table}: OK ({len(df)} rows)")

        except Exception as e:
            logger.error(f"{table}: FAILED - {e}")
            stats[table] = {
                "status": "error",
                "error": str(e)
            }

    logger.info("Pipeline finished")
    logger.info(stats)


with DAG(
    dag_id='dag_ingestion',
    default_args=default_args,
    description='Ingestion from Postgres Chinook to MinIO',
    schedule_interval=None,  # ручной запуск
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['chinook', 'ingestion', 'minio']
) as dag:

    ingestion_task = PythonOperator(
        task_id='run_chinook_ingestion',
        python_callable=run_ingestion
    )

    ingestion_task