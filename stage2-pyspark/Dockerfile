FROM apache/airflow:2.10.0

USER root

RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

ENV SPARK_VERSION=3.5.1
ENV ICEBERG_SPARK_RUNTIME=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1