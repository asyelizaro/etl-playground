from pyspark.sql import functions as F, Window

from gold_utils import get_spark_session, spark_to_clickhouse

def latest_satellite_rows(df, key_column):
    latest = Window.partitionBy(key_column).orderBy(F.col("load_dt").desc())
    return (
        df.withColumn("_row_number", F.row_number().over(latest))
        .filter(F.col("_row_number") == 1)
        .drop("_row_number")
    )

def first_satellite_rows(df, key_column):
    first = Window.partitionBy(key_column).orderBy(F.col("load_dt").asc())
    return (
        df.withColumn("_row_number", F.row_number().over(first))
        .filter(F.col("_row_number") == 1)
        .drop("_row_number")
    )

def build_customer_sales():
    spark = get_spark_session("gold-customer-sales")
    try:
        customer_hub = spark.table("silver.customer_hub")
        customer_sat = latest_satellite_rows(
            spark.table("silver.customer_sat"),
            "customer_hk",
        )
        invoice_sat = latest_satellite_rows(
            spark.table("silver.invoice_sat"),
            "invoice_hk",
        )
        invoice_line_sat = latest_satellite_rows(
            spark.table("silver.invoice_line_sat"),
            "invoice_track_hk",
        )

        invoice_line_df = invoice_line_sat.select(
            F.col("invoice_track_hk"),
            F.col("unit_price").cast("decimal(12,2)").alias("unit_price"),
            F.col("quantity").cast("long").alias("quantity"),
        )




        customer_sales = ()



        spark_to_clickhouse(customer_sales, "dm_customer_sales")

        return customer_sales
    finally:
        spark.stop()
