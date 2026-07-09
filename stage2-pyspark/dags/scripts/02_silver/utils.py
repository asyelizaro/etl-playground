import os
from datetime import datetime, timezone

from pyspark.sql import SparkSession


def get_spark_session():
    return (
        SparkSession.builder
        .master("local[*]")
        .appName("artist-legacy")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.spark_catalog.type", "hadoop")
        .config("spark.sql.catalog.spark_catalog.warehouse", os.getenv("ICEBERG_WAREHOUSE", "/tmp/iceberg-warehouse"))
        .config("spark.sql.defaultCatalog", "spark_catalog")
        .enableHiveSupport()
        .getOrCreate()
    )


def get_latest_partition_path(table_name: str, dt: str | None = None) -> str:
    bucket = os.getenv("MINIO_BUCKET", "chinook-lake")
    if dt:
        return f"s3a://{bucket}/{table_name}/dt={dt}/{table_name}.parquet"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"s3a://{bucket}/{table_name}/dt={now}/{table_name}.parquet"
