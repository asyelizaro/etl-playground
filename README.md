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

## Архитектура решения

Проект разделён на два этапа:
## Быстрый старт

### stage0-source
```bash
cd stage0-source
docker-compose up -d
```

### stage1-plpgsql
```bash
cd ../stage1-plpgsql
docker-compose up -d
```
Ждём инициализации (30-60 секунд).
### Поток данных:

1. **STAGE слой** (`setup_stage.sql`):
   - Подключаемся к source БД через `postgres_fdw` (Foreign Data Wrapper)
   - Создаём foreign tables для всех исходных таблиц Chinook
   
2. **DDS слой** (функции `fn_dim_*.sql`, `fn_fact_*.sql`):
   - Читаем из stage таблиц
   - Пишем в таблицы фактов и измерений
   - Вся логика в PL/pgSQL функциях

3. **DM слой** (функции `fn_dm_*.sql`):
   - Читаем из DDS таблиц
   - Агрегируем по клиентам, артистам, сотрудникам
   - Пишем результаты в витрины

4. **Оркестрация** (`stage1_etl.py`):
   - Airflow контролирует порядок выполнения всех функций
   - Гарантирует, что stage выполнится раньше dds, а dds раньше dm
   - Логирует результаты и обрабатывает ошибки

### Порядок выполнения в stage1-plpgsql DAG:

```
setup_stage.sql (создание foreign tables)
    ↓
dds_table.sql (создание таблиц dds)
    ↓
fn_dim_*.sql (создание функций размерности) + fn_fact_*.sql (создание функций фактов)
    ↓
run_fn_dim_* (запуск функций размерности)
    ↓
run_fn_fact_* (запуск функций фактов)
    ↓
dm_table.sql (создание таблиц витрин)
    ↓
fn_dm_*.sql (создание функций витрин)
    ↓
run_fn_dm_* (запуск функций витрин)
```

## Ключевые технологии и концепции

- **PostgreSQL** — основная БД
- **PL/pgSQL** — процедурный язык SQL
- **postgres_fdw** — расширение для доступа к внешним БД (staging)
- **Apache Airflow** — оркестратор
- **Star Schema** — модель хранилища
- **Docker** — контейнеры

### stage1-plpgsql

**Airflow UI:** http://localhost:8080 (admin/admin)
- DAG `chinook_init_all` — инициализация источника
- DAG `stage1-plpgsql` — основной пайплайн

**PostgreSQL (star_model):** localhost:5433 (star/star)
- Схема `stage` — foreign tables
- Схема `dds` — факты и измерения
- Схема `data_mart` — витрины
```
stage1-plpgsql/
├── dags/                   # DAG-ы Airflow
├── sql/                    # SQL скрипты
│   ├── stage/              # setup_stage.sql
│   ├── dds/                # таблицы и функции
│   └── dm/                 # витрины
├── docker-compose.yaml
└── .env
```

## Сценарий запуска

1. Открыть Airflow UI (localhost:8080)
2. Запустить DAG `chinook_init_all` (инициализация source)
3. Запустить DAG `stage1-plpgsql` (основной пайплайн)
4. Смотреть статус и логи в Airflow UI

Витрины появятся в PostgreSQL (localhost:5433) в схеме 'data_mart'.