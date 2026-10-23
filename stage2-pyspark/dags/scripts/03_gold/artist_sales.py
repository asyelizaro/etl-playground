from pyspark.sql import Window, functions as F

from gold_utils import get_spark_session, spark_to_clickhouse


def _latest_satellite(spark, table_name: str, key_column: str):
    return (
        spark.table(table_name)
        .withColumn(
            "_rn",
            F.row_number().over(
                Window.partitionBy(key_column).orderBy(F.col("load_dt").desc())
            ),
        )
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def build_sales_by_artist():
    spark = get_spark_session("gold-artist-sales")
    try:
        invoice_sat = _latest_satellite(spark, "silver.invoice_sat", "invoice_hk")
        invoice_track_link = spark.table("silver.invoice_track_link")
        album_track_link = spark.table("silver.album_track_link")
        artist_album_link = spark.table("silver.artist_album_link")
        artist_sat = _latest_satellite(spark, "silver.artist_sat", "artist_hk")
        genre_track_link = spark.table("silver.genre_track_link")
        genre_sat = _latest_satellite(spark, "silver.genre_sat", "genre_hk")

        invoice_sat_df = invoice_sat.select(
            F.col("invoice_hk"),
            F.col("invoice_date"),
        )

        invoice_line = _latest_satellite(
            spark,
            "silver.invoice_line_sat",
            "invoice_track_hk",
        )
        invoice_line_df = invoice_line.select(
            F.col("invoice_track_hk"),
            F.col("unit_price")
            .cast("decimal(12,2)")
            .alias("unit_price"),
            F.col("quantity")
            .cast("long")
            .alias("quantity"),
        )

        sales_base = (
            invoice_track_link.select(
                F.col("invoice_hk"),
                F.col("track_hk"),
                F.col("invoice_track_hk"),
            )
            .join(invoice_sat_df, on="invoice_hk", how="left",)
            .join(invoice_line_df, on="invoice_track_hk", how="left",)
            .join(album_track_link.select(F.col("album_hk"), F.col("track_hk")), on="track_hk", how="left",)
            .join(artist_album_link.select(F.col("artist_hk"), F.col("album_hk")), on="album_hk", how="left",)
            .join(artist_sat.select(F.col("artist_hk"), F.col("name").alias("artist_name")), on="artist_hk", how="left",)
            .join(genre_track_link.select(F.col("genre_hk"), F.col("track_hk")), on="track_hk", how="left",)
            .join(genre_sat.select(F.col("genre_hk"), F.col("name").alias("genre_name")), on="genre_hk", how="left",)
            .filter(F.col("artist_hk").isNotNull())
            .withColumn(
                "quantity",
                F.coalesce(F.col("quantity"), F.lit(1)).cast("long"),
            )
            .withColumn(
                "revenue",
                F.col("unit_price").cast("decimal(12,2)")
                * F.col("quantity").cast("decimal(12,2)"),
            )
            .withColumn(
                "invoice_date",
                F.col("invoice_date").cast("date"),
            )
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
                F.avg("avg_price_track")
                .cast("decimal(12,2)")
                .alias("avg_price_track"),
                F.sum("revenue")
                .cast("decimal(12,2)")
                .alias("revenue"),
                F.sum("quantity").cast("long").alias("quantity"),
            )
        )

        spark_to_clickhouse(artist_sales, "dm_sales_by_artist")
    finally:
        spark.stop()
