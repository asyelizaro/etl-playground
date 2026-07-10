#!/bin/bash

set -e

echo "Stopping Chinook database..."
cd ../stage0-source
docker-compose down

echo "Stopping stage1-plpgsql"
cd ../stage1-plpgsql
docker-compose down

echo "Done. Servers stopped."