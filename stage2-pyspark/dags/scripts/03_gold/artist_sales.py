from pyspark.sql import functions as F

from gold_utils import get_spark_session, spark_to_clickhouse


def build_sales_by_artist():
    spark = get_spark_session("gold-artist-sales")
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

        spark_to_clickhouse(artist_sales, "dm_sales_by_artist")

        return artist_sales
    finally:
        spark.stop()
