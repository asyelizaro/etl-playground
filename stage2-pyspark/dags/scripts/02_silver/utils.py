import os
from datetime import datetime, timezone

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, sha2


RECORD_SOURCE = os.getenv("DV_RECORD_SOURCE", "chinook")


def get_spark_session(app_name: str = "chinook-silver"):
    return (
        SparkSession.builder
        .master("local[*]")
        .appName(app_name)
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
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.spark_catalog.type", "hadoop")
        .config(
            "spark.sql.catalog.spark_catalog.warehouse",
            os.getenv("ICEBERG_WAREHOUSE", "s3a://chinook-lake"),
        )
        .config("spark.sql.defaultCatalog", "spark_catalog")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT", "http://minio:9000"))
        .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"])
        .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"])
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .getOrCreate()
    )


def get_latest_partition_path(table_name: str, dt: str | None = None) -> str:
    bucket = os.getenv("MINIO_BUCKET", "chinook-lake")
    if dt is None:
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"s3a://{bucket}/bronze/{table_name}/dt={dt}/{table_name}.parquet"


def resolve_dt(dt: str | None) -> str:
    if dt is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return dt


def full_table_name(database: str, table: str) -> str:
    return f"{database}.{table}"


def business_key_hash(column_name: str):
    return sha2(col(column_name).cast("string"), 256)


def link_hash(left_hk_column: str, right_hk_column: str):
    return sha2(
        concat_ws("||", col(left_hk_column), col(right_hk_column)),
        256,
    )


def hash_diff(attributes: list[str]):
    if not attributes:
        raise ValueError("Satellite attributes must not be empty")

    return sha2(
        concat_ws(
            "||",
            *[col(attribute).cast("string") for attribute in attributes],
        ),
        256,
    )


def append_new_rows(spark, dataframe, table_name: str, key_column: str):
    if spark.catalog.tableExists(table_name):
        existing = spark.table(table_name).select(key_column).distinct()
        dataframe = dataframe.join(existing, on=key_column, how="left_anti")

    if not dataframe.isEmpty():
        dataframe.write.format("iceberg").mode("append").saveAsTable(table_name)


def append_changed_satellite_rows(
    spark,
    dataframe,
    table_name: str,
    hk_column: str,
    hash_diff_column: str,
    load_dt_column: str,
):
    if spark.catalog.tableExists(table_name):
        latest_hashes = spark.sql(
            f"""
            SELECT {hk_column}, {hash_diff_column} AS existing_hash_diff
            FROM (
                SELECT
                    {hk_column},
                    {hash_diff_column},
                    ROW_NUMBER() OVER (
                        PARTITION BY {hk_column}
                        ORDER BY {load_dt_column} DESC
                    ) AS rn
                FROM {table_name}
            )
            WHERE rn = 1
            """
        )
        dataframe = (
            dataframe
            .join(latest_hashes, on=hk_column, how="left")
            .filter(
                col("existing_hash_diff").isNull()
                | (col(hash_diff_column) != col("existing_hash_diff"))
            )
            .drop("existing_hash_diff")
        )

    if not dataframe.isEmpty():
        dataframe.write.format("iceberg").mode("append").saveAsTable(table_name)
