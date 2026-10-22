from pyspark.sql import functions as F, Window

from gold_utils import get_spark_session, spark_to_clickhouse

def build_customer_sales():
    spark = get_spark_session("gold-customer-sales")
    try:
        customer_hub = spark.table("silver.customer_hub")
        customer_invoice_link = spark.table("silver.customer_invoice_link")
        invoice_track_link = spark.table("silver.invoice_track_link")

        customer_sat = (
            spark.table("silver.customer_sat")
            .withColumn(
                "_rn",
                F.row_number().over(
                    Window.partitionBy("customer_hk")
                    .orderBy(F.col("load_dt").desc())
                ),
            )
            .filter(F.col("_rn") == 1)
            .drop("_rn")
        )

        invoice_sat = (
            spark.table("silver.invoice_sat")
            .withColumn(
                "_rn",
                F.row_number().over(
                    Window.partitionBy("invoice_hk")
                    .orderBy(F.col("load_dt").desc())
                ),
            )
            .filter(F.col("_rn") == 1)
            .drop("_rn")
        )

        invoice_line_sat = (
            spark.table("silver.invoice_line_sat")
            .withColumn(
                "_rn",
                F.row_number().over(
                    Window.partitionBy("invoice_track_hk")
                    .orderBy(F.col("load_dt").desc())
                ),
            )
            .filter(F.col("_rn") == 1)
            .drop("_rn")
        )
        
        customer_hub_df = customer_hub.select(
            F.col("customer_hk"),
            F.col("customer_id")
        )

        customer_sat_df = customer_sat.select(
            F.col("customer_hk"),
            F.concat_ws(" ", F.col("first_name"), F.col("last_name")).alias("full_name"),
            F.col("country")
        )

        customer_invoice_link_df = customer_invoice_link.select(
            F.col("customer_hk"),
            F.col("invoice_hk")
        )

        invoice_sat_df = invoice_sat.select(
            F.col("invoice_hk"),
            F.col("invoice_date")
        )

        invoice_track_link_df = invoice_track_link.select(
            F.col("invoice_hk"),
            F.col("invoice_track_hk")
        )
        
        invoice_line_sat_df = invoice_line_sat.select(
            F.col("invoice_track_hk"),
            F.col("unit_price").cast("decimal(12,2)").alias("unit_price"),
            F.col("quantity").cast("long").alias("quantity")
        )

        df_customer_sales = (
            customer_hub_df
            .join(customer_sat_df, on="customer_hk", how="inner")
            .join(customer_invoice_link_df, on="customer_hk", how="inner")
            .join(invoice_sat_df, on="invoice_hk", how="inner")
            .join(invoice_track_link_df, on="invoice_hk", how="inner")
            .join(invoice_line_sat_df, on="invoice_track_hk", how="inner")
        )

        window_by_customer = Window.partitionBy("customer_id")

        df_customer_sales = (
            df_customer_sales
            .withColumn("first_purchase", F.min("invoice_date").over(window_by_customer))
            .withColumn("last_purchase", F.max("invoice_date").over(window_by_customer))
        )

        customer_sales = (
            df_customer_sales
            .groupBy(
                "customer_id",
                "full_name",
                "country",
                "first_purchase",
                "last_purchase",
            )
            .agg(
                F.sum(F.col("unit_price") * F.col("quantity"))
                .cast("decimal(12,2)")
                .alias("revenue"),
                F.sum("quantity").cast("long").alias("quantity"),
            )
        )


        spark_to_clickhouse(customer_sales, "dm_customer_sales")

        return customer_sales
    finally:
        spark.stop()
