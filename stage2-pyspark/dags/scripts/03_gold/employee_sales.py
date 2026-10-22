from pyspark.sql import functions as F, Window

from gold_utils import get_spark_session, spark_to_clickhouse


def build_sales_by_employee():
    spark = get_spark_session("gold-employee-sales")
    try:
        customer_invoice_link_df = spark.table("silver.customer_invoice_link").select(
            F.col("customer_hk"),
            F.col("invoice_hk")
        )

        invoice_track_link_df = spark.table("silver.invoice_track_link").select(
            F.col("invoice_hk"),
            F.col("invoice_track_hk")
        )

        employee_customer_link_df = spark.table("silver.employee_customer_link").select(
            F.col("employee_hk"),
            F.col("customer_hk"),
            F.col("load_dt"),
        ).withColumn(
            "_rn",
            F.row_number().over(
                Window.partitionBy("customer_hk").orderBy(F.col("load_dt").desc())
            ),
        ).filter(
            F.col("_rn") == 1
        ).drop(
            "_rn",
            "load_dt",
        )

        employee_hub_df = spark.table("silver.employee_hub").select(
            F.col("employee_hk"),
            F.col("employee_id")
        )
        
        employee_sat_df = (
            spark.table("silver.employee_sat")
            .withColumn(
                "_rn",
                F.row_number().over(
                    Window.partitionBy("employee_hk")
                    .orderBy(F.col("load_dt").desc())
                ),
            )
            .filter(F.col("_rn") == 1)
            .drop("_rn")
        ).select(
            F.col("employee_hk"),
            F.concat_ws(" ", F.col("last_name"), F.col("first_name")).alias("full_name")
        )

        invoice_line_sat_df = (
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
        ).select(
            F.col("invoice_track_hk"),
            F.col("unit_price").cast("decimal(12,2)").alias("unit_price"),
            F.col("quantity").cast("long").alias("quantity")
        )

        sales = (
            customer_invoice_link_df
            .join(invoice_track_link_df, on="invoice_hk", how="inner")
            .join(invoice_line_sat_df, on="invoice_track_hk", how="inner")
            .withColumn(
                "revenue",
                (F.col("unit_price") * F.col("quantity")).cast("decimal(12,2)"),
            )
            .select(
                "customer_hk",
                "invoice_hk",
                "invoice_track_hk",
                "unit_price",
                "quantity",
                "revenue",
            )
        )

        clients_by_employee = (
            employee_customer_link_df
            .groupBy("employee_hk")
            .agg(F.countDistinct("customer_hk").alias("clients_count"))
        )

        metric_by_employee = (
            sales
            .join(employee_customer_link_df, on="customer_hk", how="inner")
            .groupBy("employee_hk")
            .agg(
                F.count("*").alias("purchase_count"),
                F.sum("revenue").cast("decimal(12,2)").alias("revenue_amount"),
            )
            .join(clients_by_employee, on="employee_hk", how="left")
            .select(
                "employee_hk",
                "purchase_count",
                "revenue_amount",
                "clients_count",
            )
        )

        sales_by_employee = (
            metric_by_employee
            .join(employee_hub_df, on="employee_hk", how="inner")
            .join(employee_sat_df, on="employee_hk", how="inner")
            .select(
                "employee_id",
                "full_name",
                "clients_count",
                "purchase_count",
                "revenue_amount",
            )
        )

        spark_to_clickhouse(sales_by_employee, "dm_sales_by_employee")

        return sales_by_employee
    finally:
        spark.stop()
