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

    database = table_config["database"]

    spark.sql(
        f"""
        CREATE DATABASE IF NOT EXISTS {database}
        """
    )


    if dt is None:
        now = datetime.now(timezone.utc)
        dt = now.strftime("%Y-%m-%d")


    # читаем Bronze один раз

    source_table = table_config["source_table"]

    path = get_latest_partition_path(
        source_table,
        dt=dt
    )

    df = spark.read.parquet(path)


    # Bronze -> Silver

    columns = table_config["columns"]

    select_columns = []

    for target, source in columns.items():
        select_columns.append(
            col(source).alias(target)
        )


    df = (
        df
        .select(*select_columns)
        .dropDuplicates(
            [table_config["business_key"]]
        )
    )


    # строим Hub

    load_hub_artist(
        df,
        table_config
    )


    # строим Satellite

    load_sat_artist(
        df,
        table_config
    )


    spark.stop()

    return True



def load_hub_artist(df, table_config):

    database = table_config["database"]

    business_key = table_config["business_key"]

    hub_config = table_config["hub"]


    df_hub = (
        df
        .select(
            col(business_key)
        )
        .withColumn(
            hub_config["key_column"],
            sha2(
                col(business_key).cast("string"),
                256
            )
        )
        .withColumn(
            hub_config["load_dt_column"],
            current_timestamp()
        )
        .withColumn(
            hub_config["source_column"],
            lit("chinook")
        )
    )


    (
        df_hub.write
        .format("iceberg")
        .mode("append")
        .saveAsTable(
            f"{database}.{hub_config['target_table']}"
        )
    )



def load_sat_artist(df, table_config):

    database = table_config["database"]

    sat_config = table_config["sat"]

    business_key = table_config["business_key"]


    df_sat = (
        df
        .withColumn(
            "artist_hk",
            sha2(
                col(business_key).cast("string"),
                256
            )
        )
        .withColumn(
            sat_config["load_dt_column"],
            current_timestamp()
        )
        .withColumn(
            sat_config["source_column"],
            lit("chinook")
        )
    )


    (
        df_sat.write
        .format("iceberg")
        .mode("append")
        .saveAsTable(
            f"{database}.{sat_config['target_table']}"
        )
    )