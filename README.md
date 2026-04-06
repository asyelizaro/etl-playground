# etl-playground
**E-commerce data for practicing ETL from source to analytics**
Практический проект для изучения полного ETL пайплайна

Используемый датасет: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data



Предварительно необходимо разахивировать olist_datasets.zip в директорию shared\data

1. Запуск DB:
```bash
cd shared && docker compose up -d
```

1.2 PowerShell копирование в контейнер
```
Get-ChildItem .\data\*.csv | ForEach-Object { 
    docker cp $_.FullName postgres_olist_shared:/tmp/
}
```

2. Загрузка DDL:
```bash
docker exec -i postgres_olist_shared psql -U olist -d olist_source < ddl_raw.sql
```

3. Проверяем что таблицы создались:
```bash
docker exec -it postgres_olist_shared psql -U olist -d olist_source -c "\dt"
```

4. Импорт в БД из .csv поочередно:
```sql
\copy olist_customers_dataset FROM '/tmp/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER);


\copy olist_orders_dataset FROM '/tmp/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_order_items_dataset FROM '/tmp/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_order_payments_dataset FROM '/tmp/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_order_reviews_dataset FROM '/tmp/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_products_dataset FROM '/tmp/olist_products_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_sellers_dataset FROM '/tmp/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER);

\copy olist_geolocation_dataset FROM '/tmp/olist_geolocation_dataset.csv' WITH (FORMAT csv, HEADER);

\copy product_category_name_translation FROM '/tmp/product_category_name_translation.csv' WITH (FORMAT csv, HEADER);
```
