# ETL Playground: Загрузка Olist Raw
Write-Host "Starting Olist Raw load..." -Foreground Cyan

# 1. DDL
docker exec -i postgres_olist_shared psql -U olist -d olist_source < ddl_raw.sql
Write-Host "DDL loaded" -Foreground Green

# 2. COPY + Import all CSV
Get-ChildItem .\data\*.csv | ForEach-Object { 
    $table = $_.BaseName
    Write-Host "Loading $table..." -Foreground Yellow
    docker cp $_.FullName postgres_olist_shared:/tmp/
    docker exec postgres_olist_shared psql -U olist -d olist_source -c "\copy $table FROM '/tmp/$($_.Name)' WITH (FORMAT csv, HEADER)"
    Write-Host "$table OK" -Foreground Green
}

Write-Host "Raw-layer is ready!" -Foreground Cyan