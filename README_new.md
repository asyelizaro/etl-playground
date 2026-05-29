# etl-playground

Практический проект для изучения полного ETL пайплайна от источника до витрин.

Данные: E-commerce база Chinook ([Kaggle](https://www.kaggle.com/datasets/ranasabrii/chinook))

## Архитектура

Проект реализует классическую архитектуру хранилища с несколькими этапами обработки:

```
source → stage → dds → dm (витрины)
```

Каждый этап решает свои задачи и использует разные технологии.

## Этапы проекта

### stage0-source
Исходная база данных Chinook в PostgreSQL.

### stage1-plpgsql
Первый ETL пайплайн на PL/pgSQL.

Архитектура:
- **stage** — доступ к исходным данным через foreign tables
- **dds** — трансформация и денормализация (star schema)
- **dm** — витрины для аналитики

Оркестрация: Apache Airflow

### stage2-pyspark
*Планируется*

## Быстрый старт

### stage0-source
```bash
cd stage0-source
docker-compose up -d
```
Данные: localhost:5432 (postgres/postgres)

### stage1-plpgsql
```bash
cd ../stage1-plpgsql
docker-compose up -d
```
Ждём инициализации (30-60 секунд).

## Где смотреть результаты

### stage1-plpgsql

**Airflow UI:** http://localhost:8080 (admin/admin)
- DAG `chinook_init_all` — инициализация источника
- DAG `stage1-plpgsql` — основной пайплайн

**PostgreSQL (star_model):** localhost:5433 (star/star)
- Схема `stage` — foreign tables
- Схема `dds` — факты и измерения
- Схема `data_mart` — витрины

## Структура проекта

```
etl-playground/
├── stage0-source/          # Исходная БД
├── stage1-plpgsql/         # Первый ETL (PostgreSQL + PL/pgSQL)
│   ├── dags/               # DAG-ы Airflow
│   ├── sql/                # SQL скрипты
│   │   ├── stage/
│   │   ├── dds/
│   │   └── dm/
│   └── docker-compose.yaml
├── stage2-pyspark/         # Второй ETL (PySpark + MinIO)
└── README.md
```

## Сценарий использования

1. Запустить stage0-source
2. Запустить stage1-plpgsql
3. Открыть Airflow UI (localhost:8080)
4. Запустить DAG `chinook_init_all`
5. Запустить DAG `stage1-plpgsql`
6. Смотреть результаты в PostgreSQL или Airflow логах
