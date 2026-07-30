FROM apache/airflow:2.10.0

USER root

RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

# Скачать Iceberg и Hadoop AWS при сборке образа
RUN python -c "from pyspark.sql import SparkSession; \
    spark = (SparkSession.builder \
    .master('local[1]') \
    .appName('spark-dependencies-warmup') \
    .config('spark.jars.packages', \
    'org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.hadoop:hadoop-aws:3.3.4') \
    .getOrCreate()); \
    spark.stop()"

ENV SPARK_VERSION=3.5.1
ENV ICEBERG_SPARK_RUNTIME=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1