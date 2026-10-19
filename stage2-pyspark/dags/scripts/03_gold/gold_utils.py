import os

from pyspark.sql import SparkSession


def get_spark_session(app_name: str):
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
        .appName(app_name)
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


def spark_to_clickhouse(df, table_name: str):
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
