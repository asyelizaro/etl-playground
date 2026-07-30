from datetime import datetime, timezone

from pyspark.sql.functions import col, current_timestamp, lit, sha2

from utils import get_latest_partition_path, get_spark_session


def load_album(dt=None, table_config=None):
    spark = get_spark_session()

    try:
        database = table_config["database"]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

        if dt is None:
            dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. Читаем Bronze
        source_table = table_config["source_table"]
        source_path = get_latest_partition_path(source_table, dt=dt)

        bronze_df = spark.read.parquet(source_path)

        # 2. Выбираем только нужные колонки
        # Формат YAML: target_column: source_column
        columns_mapping = table_config["columns"]

        silver_df = (
            bronze_df
            .select(
                *[
                    col(source_column).alias(target_column)
                    for target_column, source_column in columns_mapping.items()
                ]
            )
            .dropDuplicates([table_config["business_key"]])
        )

        # 3. Пишем Hub и Satellite
        load_hub(silver_df, table_config)
        load_satellite(silver_df, table_config)

        return True

    finally:
        spark.stop()


def load_hub(df, table_config):
    database = table_config["database"]
    business_key = table_config["business_key"]
    hub = table_config["hub"]

    hub_df = (
        df
        .select(col(business_key))
        .withColumn(
            hub["key_column"],
            sha2(col(business_key).cast("string"), 256),
        )
        .withColumn(hub["load_dt_column"], current_timestamp())
        .withColumn(hub["source_column"], lit("chinook"))
    )

    (
        hub_df.write
        .format("iceberg")
        .mode("append")
        .saveAsTable(f"{database}.{hub['target_table']}")
    )


def load_satellite(df, table_config):
    database = table_config["database"]
    business_key = table_config["business_key"]
    hub = table_config["hub"]
    sat = table_config["sat"]

    sat_df = (
        df
        .withColumn(
            hub["key_column"],
            sha2(col(business_key).cast("string"), 256),
        )
        .select(
            col(hub["key_column"]),
            col("title")
        )
        .withColumn(sat["load_dt_column"], current_timestamp())
        .withColumn(sat["source_column"], lit("chinook"))
    )

    (
        sat_df.write
        .format("iceberg")
        .mode("append")
        .saveAsTable(f"{database}.{sat['target_table']}")
    )