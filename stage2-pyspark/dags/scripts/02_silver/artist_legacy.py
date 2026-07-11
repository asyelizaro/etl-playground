from datetime import datetime, timezone
from pyspark.sql.functions import col, current_timestamp, lit, sha2
from utils import get_latest_partition_path, get_spark_session

now = datetime.now(timezone.utc)
date = now.strftime('%Y-%m-%d')

spark = get_spark_session()

spark.sql(
    """
    CREATE DATABASE IF NOT EXISTS silver
    """
)

# читаем Bronze
path = get_latest_partition_path("artist",dt=date)

df = spark.read.parquet(path)

# смотрим что пришло
df.printSchema()

# Bronze -> Silver
df = (
    df
    .select(
        col("artist_id").alias("artist_id"),
        col("Name").alias("name")
    )
    .dropDuplicates(["artist_id"])
)

# добавляем поля Data Vault
df = (
    df
    .withColumn(
        "artist_hk",
        sha2(
            col("artist_id").cast("string"),
            256
        )
    )
    .withColumn(
        "load_dt",
        current_timestamp()
    )
    .withColumn(
        "source",
        lit("chinook")
    )
)

(
    df.write
    .format("iceberg")
    .mode("append")
    .saveAsTable(
        "silver.artist_hub"
    )
)


spark.stop()