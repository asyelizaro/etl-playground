# etl-playground

Практический ETL/ELT проект для изучения различных подходов к построению хранилищ данных.

Источник данных — база Chinook (e-commerce).

## Подходы

- **stage0** — источник данных (PostgreSQL, Chinook)

- **stage1** — DWH с PL/pgSQL + Airflow  
  Star Schema (DDS) и аналитические витрины (DM)

- **stage2 (planned)** — DataLake на S3 (MinIO) с PySpark + Airflow  
  Data Vault 2.0 (Silver layer) и аналитические витрины (DM) на ClickHouse

## Запуск stage1

```bash
bash stage1-plpgsql/start-stage1.sh
```

## Структура s3 для stage2
chinook-lake/
  raw/
    date-upload/
      artist.parquet
      genre.parquet
      playlist.parquet
      ...
  staging/
  dv/

## Запуск stage2
```bash
pip install -r requirements.txt
```