import os
from datetime import datetime, timezone

from pyspark.sql import SparkSession


def get_spark_session():
    iceberg_runtime = os.getenv(
        "ICEBERG_SPARK_RUNTIME",
        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1",
    )
    hadoop_aws = os.getenv("HADOOP_AWS_RUNTIME", "org.apache.hadoop:hadoop-aws:3.3.4")
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    minio_access_key = os.environ["MINIO_ACCESS_KEY"]
    minio_secret_key = os.environ["MINIO_SECRET_KEY"]

    return (
        SparkSession.builder
        .master("local[*]")
        .appName("artist-legacy")
        .config(
            "spark.jars",
            os.getenv(
                "SPARK_EXTRA_JARS",
                "/opt/spark-jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar,"
                "/opt/spark-jars/hadoop-aws-3.3.4.jar,"
                "/opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar,"
                "/opt/spark-jars/wildfly-openssl-1.0.7.Final.jar",
            ),
        )
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.spark_catalog.type", "hadoop")
        .config("spark.sql.catalog.spark_catalog.warehouse", os.getenv("ICEBERG_WAREHOUSE", "s3a://chinook-lake"))
        .config("spark.sql.defaultCatalog", "spark_catalog")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        .enableHiveSupport()
        .getOrCreate()
    )


def get_latest_partition_path(table_name: str, dt: str | None = None) -> str:
    bucket = os.getenv("MINIO_BUCKET", "chinook-lake")
    if dt is None:
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"s3a://{bucket}/bronze/{table_name}/dt={dt}/{table_name}.parquet"
