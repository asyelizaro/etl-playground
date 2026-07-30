from datetime import datetime, timezone

from pyspark.sql.functions import col, concat_ws, current_timestamp, lit, sha2

from utils import get_latest_partition_path, get_spark_session


def load_artist_album_link(dt=None, table_config=None):
    spark = get_spark_session()

    try:
        database = table_config["database"]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")
        
        link = table_config["link"]

        if dt is None:
            dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        source_table = table_config["source_table"]
        source_path = get_latest_partition_path(source_table, dt=dt)

        bronze_df = spark.read.parquet(source_path)

        link_df = (
            bronze_df
            .select(
                col(table_config["columns"]["artist_id"]).alias("artist_id"),
                col(table_config["columns"]["album_id"]).alias("album_id"),
            )
            .filter(
                col("artist_id").isNotNull()
                & col("album_id").isNotNull()
            )
            .dropDuplicates()
            .withColumn(
                link["left_key_column"],
                sha2(col("artist_id").cast("string"), 256),
            )
            .withColumn(
                link["right_key_column"],
                sha2(col("album_id").cast("string"), 256),
            )
            .withColumn(
                link["key_column"],
                sha2(
                    concat_ws(
                        "||",
                        col(link["left_key_column"]),
                        col(link["right_key_column"]),
                    ),
                    256,
                ),
            )
            .withColumn(link["load_dt_column"], current_timestamp())
            .withColumn(link["source_column"], lit("chinook"))
            .select(
                link["key_column"],
                link["left_key_column"],
                link["right_key_column"],
                link["load_dt_column"],
                link["source_column"],
            )
        )

        (
            link_df.write
            .format("iceberg")
            .mode("append")
            .saveAsTable(f"{database}.{link['target_table']}")
        )

        return True

    finally:
        spark.stop()