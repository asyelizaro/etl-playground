FROM apache/airflow:2.10.0

USER root

RUN apt-get update && \
    apt-get install -y default-jdk curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/spark-jars && \
curl -fsSL https://repo.maven.apache.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.6.1/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
    -o /opt/spark-jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar && \
curl -fsSL https://repo.maven.apache.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -o /opt/spark-jars/hadoop-aws-3.3.4.jar && \
curl -fsSL https://repo.maven.apache.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar \
    -o /opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar && \
curl -fsSL https://repo.maven.apache.org/maven2/org/wildfly/openssl/wildfly-openssl/1.0.7.Final/wildfly-openssl-1.0.7.Final.jar \
    -o /opt/spark-jars/wildfly-openssl-1.0.7.Final.jar

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

ENV SPARK_VERSION=3.5.1
ENV ICEBERG_SPARK_RUNTIME=org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1