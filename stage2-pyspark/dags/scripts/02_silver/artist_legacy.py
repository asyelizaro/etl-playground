import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit, sha2

from utils import get_latest_partition_path, get_spark_session


def read_artist_from_minio(spark: SparkSession, dt: str | None = None, table_name: str | None = None):
    source_table = table_name or "artist"
    path = get_latest_partition_path(source_table, dt=dt)
    return spark.read.parquet(path)


def transform_artist_to_hub(df, table_config: dict | None = None):
    columns = table_config.get("columns", {}) if table_config else {"artist_id": "ArtistId", "name": "Name"}
    select_expr = [col(source_name).alias(target_name) for target_name, source_name in columns.items()]

    business_key = (table_config or {}).get("business_key", "artist_id")
    hub_config = (table_config or {}).get("hub", {}) if table_config else {}
    key_column = hub_config.get("key_column", "artist_hk")
    load_dt_column = hub_config.get("load_dt_column", "load_dt")
    source_column = hub_config.get("source_column", "source")

    return (
        df.select(*select_expr)
        .dropDuplicates([business_key])
        .withColumn(key_column, sha2(col(business_key).cast("string"), 256))
        .withColumn(load_dt_column, current_timestamp())
        .withColumn(source_column, lit("chinook"))
    )


def write_artist_to_iceberg(df, table_config: dict | None = None):
    database = (table_config or {}).get("database", "silver")
    target_table = (table_config or {}).get("target_table", "artist_hub")
    df.write.format("iceberg").mode("append").saveAsTable(f"{database}.{target_table}")


def load_artist(dt: str | None = None, table_config: dict | None = None):
    spark = get_spark_session()
    database = (table_config or {}).get("database", "silver")
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

    source_table = (table_config or {}).get("source_table", "artist")
    df = read_artist_from_minio(spark, dt=dt, table_name=source_table)
    df = transform_artist_to_hub(df, table_config=table_config)
    write_artist_to_iceberg(df, table_config=table_config)

    spark.stop()
    return df


if __name__ == "__main__":
    load_artist()
