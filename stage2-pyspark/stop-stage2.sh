#!/bin/bash

set -e

echo "Stopping Chinook database..."
cd ../stage0-source
docker-compose down

echo "Stopping stage2-pyspark"
cd ../stage2-pyspark
docker-compose down

echo "Done. Servers stopped."