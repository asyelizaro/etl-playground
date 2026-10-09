import os

from pyspark.sql import SparkSession, functions as F


def get_spark_session():
    extra_jars = os.getenv("SPARK_EXTRA_JARS", "")
    default_jars = [
        "/opt/spark-jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar",
        "/opt/spark-jars/hadoop-aws-3.3.4.jar",
        "/opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar",
        "/opt/spark-jars/wildfly-openssl-1.0.7.Final.jar",
        "/opt/spark-jars/clickhouse-jdbc-0.6.1-shaded.jar",
    ]
    merged_jars = ",".join(j for j in default_jars if j)
    if extra_jars:
        merged_jars = f"{merged_jars},{extra_jars}"

    return (
        SparkSession.builder
        .master("local[*]")
        .appName("gold-artist-sales")
        .config("spark.jars", merged_jars)
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


def _spark_to_clickhouse(df, table_name: str):
    jdbc_url = (
        f"jdbc:clickhouse://{os.getenv('CLICKHOUSE_HOST', 'clickhouse')}:{os.getenv('CLICKHOUSE_PORT', '8123')}/"
        f"{os.getenv('CLICKHOUSE_DB', 'chinook_gold')}"
    )

    (
        df.write.format("jdbc")
        .mode("overwrite")
        .option("url", jdbc_url)
        .option("dbtable", table_name)
        .option("driver", "com.clickhouse.jdbc.ClickHouseDriver")
        .option("user", os.getenv("CLICKHOUSE_USER", "chinook"))
        .option("password", os.getenv("CLICKHOUSE_PASSWORD", "chinook123"))
        .option("batchsize", "10000")
        .save()
    )


def build_sales_by_artist():
    spark = get_spark_session()
    try:
        invoice_sat = spark.table("silver.invoice_sat")
        invoice_track_link = spark.table("silver.invoice_track_link")
        album_track_link = spark.table("silver.album_track_link")
        artist_album_link = spark.table("silver.artist_album_link")
        artist_sat = spark.table("silver.artist_sat")
        genre_track_link = spark.table("silver.genre_track_link")
        genre_sat = spark.table("silver.genre_sat")

        invoice_sat_df = invoice_sat.select(
            F.col("invoice_hk"),
            F.col("invoice_date"),
            F.col("total").cast("decimal(12,2)").alias("total"),
        )

        invoice_line = spark.table("silver.invoice_line_sat")
        invoice_line_df = invoice_line.select(
            F.col("invoice_track_hk"),
            F.col("unit_price").cast("decimal(12,2)").alias("unit_price"),
            F.col("quantity").cast("long").alias("quantity"),
        )

        sales_base = (
            invoice_track_link
            .select(
                F.col("invoice_hk"),
                F.col("track_hk"),
                F.col("invoice_track_hk"),
            )
            .join(
                invoice_sat_df,
                on="invoice_hk",
                how="left",
            )
            .join(
                invoice_line_df,
                on="invoice_track_hk",
                how="left",
            )
            .join(
                album_track_link.select(F.col("album_hk"), F.col("track_hk")),
                on="track_hk",
                how="left",
            )
            .join(
                artist_album_link.select(F.col("artist_hk"), F.col("album_hk")),
                on="album_hk",
                how="left",
            )
            .join(
                artist_sat.select(
                    F.col("artist_hk"),
                    F.col("name").alias("artist_name"),
                ),
                on="artist_hk",
                how="left",
            )
            .join(
                genre_track_link.select(F.col("genre_hk"), F.col("track_hk")),
                on="track_hk",
                how="left",
            )
            .join(
                genre_sat.select(
                    F.col("genre_hk"),
                    F.col("name").alias("genre_name"),
                ),
                on="genre_hk",
                how="left",
            )
            .filter(F.col("artist_hk").isNotNull())
            .withColumn(
                "revenue",
                F.coalesce(F.col("unit_price"), F.col("total")).cast("decimal(12,2)")
                * F.coalesce(F.col("quantity"), F.lit(1)).cast("decimal(12,2)"),
            )
            .withColumn("quantity", F.coalesce(F.col("quantity"), F.lit(1)).cast("long"))
            .withColumn("invoice_date", F.col("invoice_date").cast("date"))
            .select(
                F.col("invoice_date"),
                F.col("artist_name"),
                F.col("genre_name"),
                F.col("revenue"),
                F.col("quantity"),
                F.col("unit_price").alias("avg_price_track"),
            )
        )

        artist_sales = (
            sales_base
            .groupBy("invoice_date", "artist_name", "genre_name")
            .agg(
                F.avg("avg_price_track").cast("decimal(12,2)").alias("avg_price_track"),
                F.sum("revenue").cast("decimal(12,2)").alias("revenue"),
                F.sum("quantity").cast("long").alias("quantity"),
            )
        )

        _spark_to_clickhouse(artist_sales, "dm_sales_by_artist")

        return artist_sales
    finally:
        spark.stop()
