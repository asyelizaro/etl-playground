#!/bin/bash

set -e

echo "Starting Chinook database..."
cd ../stage0-source
docker-compose up -d

echo "Starting ETL environment..."
cd ../stage2-pyspark
docker-compose up -d

echo "Done. Open Airflow: http://localhost:8080/home"