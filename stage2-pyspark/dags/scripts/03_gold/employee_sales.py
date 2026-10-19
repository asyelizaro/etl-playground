from pyspark.sql import functions as F

from gold_utils import get_spark_session, spark_to_clickhouse


def build_sales_by_employee():
    spark = get_spark_session("gold-employee-sales")
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

        sales_base = ()



        spark_to_clickhouse(artist_sales, "dm_sales_by_employee")

        return artist_sales
    finally:
        spark.stop()
