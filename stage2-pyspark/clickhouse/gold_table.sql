CREATE DATABASE IF NOT EXISTS chinook_gold;

CREATE TABLE IF NOT EXISTS chinook_gold.dm_sales_by_employee (
    employee_id Int64,
    full_name String,
    clients_count Int64,
    purchase_count Int64,
    revenue_amount Decimal(12, 2)
) ENGINE = MergeTree
ORDER BY employee_id;

CREATE TABLE IF NOT EXISTS chinook_gold.dm_customer_sales (
    customer_id Int32,
    full_name String,
    country Nullable(String),
    first_purchase Date,
    last_purchase Date,
    revenue Decimal(12, 2),
    quantity Int64
) ENGINE = MergeTree
ORDER BY customer_id;

CREATE TABLE IF NOT EXISTS chinook_gold.dm_sales_by_artist (
    invoice_date Date,
    artist_name String,
    genre_name Nullable(String),
    avg_price_track Nullable(Decimal(12, 2)),
    revenue Nullable(Decimal(12, 2)),
    quantity Int64
) ENGINE = MergeTree
ORDER BY (invoice_date, artist_name, genre_name);