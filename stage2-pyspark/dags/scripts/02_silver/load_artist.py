from datetime import datetime, timezone

from pyspark.sql.functions import col, current_timestamp, lit, sha2

from utils import get_latest_partition_path, get_spark_session


def load_artist(dt=None, table_config=None):

    spark = get_spark_session()

    spark.sql(
        """
        CREATE DATABASE IF NOT EXISTS silver
        """
    )

    if dt is None:
        now = datetime.now(timezone.utc)
        dt = now.strftime("%Y-%m-%d")


    # читаем Bronze
    path = get_latest_partition_path("artist", dt=dt)

    df = spark.read.parquet(path)

    df.printSchema()

    # Bronze -> Silver
    df = df \
        .select(
            col("artist_id"),
            col("name")
        ) \
        .dropDuplicates(["artist_id"])


    # Data Vault поля
    df = df.withColumn("artist_hk", sha2(col("artist_id").cast("string"), 256)) \
        .withColumn("load_dt", current_timestamp()) \
        .withColumn("source", lit("chinook"))


    df.write \
    .format("iceberg") \
    .mode("append") \
    .saveAsTable("silver.artist_hub")
    

    spark.stop()

    return True