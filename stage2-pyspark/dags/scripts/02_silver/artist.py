from datetime import datetime, timezone

from pyspark.sql.functions import (
    col,
    current_timestamp,
    lit,
    sha2
)

from utils import get_latest_partition_path, get_spark_session


def load_artist(dt=None, table_config=None):

    spark = get_spark_session()

    # берем настройки из config.yaml

    source_table = table_config["source_table"]
    database = table_config["database"]
    target_table = table_config["target_table"]
    business_key = table_config["business_key"]
    columns = table_config["columns"]
    hub_config = table_config["hub"]
    key_column = hub_config["key_column"]
    load_dt_column = hub_config["load_dt_column"]
    source_column = hub_config["source_column"]



    # создаём silver дб если не создана

    spark.sql(
        f"""
        CREATE DATABASE IF NOT EXISTS {database}
        """
    )

    if dt is None:
        now = datetime.now(timezone.utc)
        dt = now.strftime("%Y-%m-%d")

    # читаем Bronze

    path = get_latest_partition_path(source_table, dt=dt)

    df = spark.read.parquet(path)

    df.printSchema()


    # Bronze -> Silver

    select_columns = []

    for target, source in columns.items():
        select_columns.append(
            col(source).alias(target)
        )


    df = df \
        .select(*select_columns) \
        .dropDuplicates([business_key])

    # Data Vault поля

    df = (
            df 
            .withColumn(
                key_column,
                sha2(
                    col(business_key).cast("string"),
                    256
                )
            ) 
            .withColumn(
                load_dt_column,
                current_timestamp()
            ) 
            .withColumn(
                source_column,
                lit("chinook")
            )
        )


    # запись Iceberg

    df.write \
        .format("iceberg") \
        .mode("append") \
        .saveAsTable(f"{database}.{target_table}")


    spark.stop()


    return True