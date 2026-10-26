# etl-playground

Практический проект для сравнения подходов к обработке данных на примере базы Chinook.

## Этапы

- **stage0-source** — исходная база Chinook в PostgreSQL.
- **stage1-plpgsql** — загрузка в DWH на PostgreSQL. PL/pgSQL формирует слой DDS в модели Star Schema и витрины DM. Оркестрация — Airflow.
- **stage2-pyspark** — загрузка данных из PostgreSQL в MinIO и преобразования на PySpark. Слои: Bronze в Parquet, Silver в Data Vault 2.0 на Iceberg, Gold-витрины в ClickHouse. Оркестрация — Airflow.

## Структура

```text
stage0-source/
  Chinook_PostgreSql.sql   # схема и данные источника
  docker-compose.yaml

stage1-plpgsql/
  dags/                    # DAG-и Airflow
  sql/
    stage/                 # подготовка слоя stage
    dds/                   # таблицы и функции DDS
    dm/                    # таблицы и функции витрин
  start-stage1.sh
  stop-stage1.sh

stage2-pyspark/
  dags/                    # DAG-и Airflow
  dags/scripts/
    01_ingestion/          # выгрузка из PostgreSQL в MinIO
    02_silver/             # загрузка Silver
    03_gold/               # построение витрин
  clickhouse/              # DDL Gold-таблиц
  analitics/               # аналитический ноутбук
  start-stage2.sh
  stop-stage2.sh
```

## Запуск stage1

Создайте файлы окружения и задайте уникальные значения паролей и ключа Fernet:

```bash
cp stage0-source/.env.example stage0-source/.env
cp stage1-plpgsql/.env.example stage1-plpgsql/.env
```

`POSTGRES_CHINOOK_USER` и `POSTGRES_CHINOOK_PASSWORD` в обоих файлах должны совпадать. Запустите сервисы из каталога `stage1-plpgsql`:

```bash
cd stage1-plpgsql
bash start-stage1.sh
```

После запуска откройте Airflow: http://localhost:8080/home. DAG `stage1-plpgsql` запускает обработку слоёв stage, DDS и DM.

Для остановки выполните из того же каталога:

```bash
bash stop-stage1.sh
```

## Запуск stage2

Создайте файлы окружения и задайте уникальные значения паролей и ключа Fernet:

```bash
cp stage0-source/.env.example stage0-source/.env
cp stage2-pyspark/.env.example stage2-pyspark/.env
```

`POSTGRES_CHINOOK_USER` и `POSTGRES_CHINOOK_PASSWORD` в обоих файлах должны совпадать. Запустите сервисы из каталога `stage2-pyspark`:

```bash
cd stage2-pyspark
bash start-stage2.sh
```

В Airflow вручную запустите DAG `ingestion_dag`. Он выгружает таблицы Chinook в MinIO и запускает `silver_load`; после загрузки Silver запускается `gold_load`.

- Airflow: http://localhost:8080/home
- MinIO Console: http://localhost:9001

Для остановки выполните из каталога `stage2-pyspark`:

```bash
bash stop-stage2.sh
```

Файлы Bronze хранятся в бакете `chinook-lake` по таблицам и датам:

```text
chinook-lake/
  bronze/
    artist/
      dt=YYYY-MM-DD/
        artist.parquet
    ...
```
