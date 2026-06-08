# etl-playground

Практический ETL/ELT проект для изучения различных подходов к построению хранилищ данных.

Источник данных — база Chinook (e-commerce).

## Подходы

- **stage0** — источник данных (PostgreSQL, Chinook)

- **stage1** — классический DWH-подход на PL/pgSQL + Airflow  
  Star Schema (DDS) и аналитические витрины (DM)

- **stage2 (planned)** — ELT-пайплайн на PySpark  
  Data Vault 2.0 с хранением в S3 (MinIO) и построением витрин в ClickHouse на тех же исходных данных

## Запуск stage1

```bash
bash stage1-plpgsql/start-stage1.sh
```

## Структура s3 для stage2
chinook-lake/
  raw/
    chinook/
      customers.parquet
      invoices.parquet
  staging/
  dv/
  mart/

## Запуск stage2
```bash
pip install -r requirements.txt
```