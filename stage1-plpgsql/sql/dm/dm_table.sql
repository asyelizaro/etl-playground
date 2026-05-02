-- содание схемы и таблиц data_mart слоя
CREATE SCHEMA IF NOT EXISTS data_mart;

DROP TABLE IF EXISTS data_mart.t_dm_sales_customer;

DROP TABLE IF EXISTS data_mart.t_dm_sales_by_artist;

DROP TABLE IF EXISTS data_mart.t_dm_sales_by_employee;

CREATE TABLE IF NOT EXISTS data_mart.t_dm_sales_customer (
    customer_id int4,
    full_name text,
    country varchar(80),
    first_purchase date,
    last_purchase date,
    revenue numeric(12, 2),
    quanity int8
);

CREATE TABLE IF NOT EXISTS data_mart.t_dm_sales_by_artist (
    invoice_date date,
    artist_name varchar(80),
    genre_name varchar(120),
    avg_price_track numeric(12, 2),
    revenue numeric(12, 2),
    quantity numeric(12, 2)
)

CREATE TABLE IF NOT EXISTS data_mart.t_dm_sales_by_employee (
    employee_id int8,
    full_name varchar(120),
    clients_count int8,
    purchase_count int8,
    revenue_amount numeric(12, 2)
)