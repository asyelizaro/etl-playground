# etl-playground

Практический ETL/ELT проект для изучения различных подходов к построению хранилищ данных.

Источник данных — база Chinook (e-commerce).

## Подходы

- **stage0** — источник данных (PostgreSQL, Chinook)

- **stage1** — DWH с PL/pgSQL + Airflow  
  Star Schema (DDS) и аналитические витрины (DM)

- **stage2** — Data Lakehouse на S3-совместимом MinIO с PySpark, Apache Iceberg и Airflow  
  Data Vault 2.0 и аналитические витрины (DM) на ClickHouse

## Запуск stage1

Перед первым запуском создайте файлы окружения из шаблонов и задайте уникальные значения для паролей и ключа Fernet:

```bash
cp stage0-source/.env.example stage0-source/.env
cp stage1-plpgsql/.env.example stage1-plpgsql/.env
bash stage1-plpgsql/start-stage1.sh
```

Значения `POSTGRES_CHINOOK_USER` и `POSTGRES_CHINOOK_PASSWORD` в шаблонах stage0 и stage1 должны совпадать.

## Структура s3 для stage2
Данные загружаются в бакет по таблицам и датам в формате, который использует `ingestion.py`:
```
chinook-lake/
  artist/
    dt=YYYY-MM-DD/
      artist.parquet
  genre/
    dt=YYYY-MM-DD/
      genre.parquet
  playlist/
    dt=YYYY-MM-DD/
      playlist.parquet
  ...
  dv/
```
## Запуск stage2
```bash
cp stage0-source/.env.example stage0-source/.env
cp stage2-pyspark/.env.example stage2-pyspark/.env
bash stage2-pyspark/start-stage2.sh
```

Значения `POSTGRES_CHINOOK_USER` и `POSTGRES_CHINOOK_PASSWORD` в шаблонах stage0 и stage2 должны совпадать.
