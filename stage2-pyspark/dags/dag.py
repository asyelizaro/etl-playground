from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path so we can import ingestion module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from ingestion.ingestion import main as ingestion_main

default_args = {
    'owner': 'asyelizaro',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

with DAG(
    dag_id="stage2_ingestion_pipeline",
    start_date=datetime(2026, 6, 1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args,
    tags=["stage2", "etl", "ingestion", "chinook", "minio"],
    description="Ingestion pipeline: extract Chinook tables to .parquet and upload to MinIO",
) as dag:
    
    ingestion_task = PythonOperator(
        task_id="chinook_ingestion",
        python_callable=ingestion_main,
        retries=2,
        retry_delay=timedelta(minutes=5),
    )
