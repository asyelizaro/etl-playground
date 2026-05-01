-- содание схемы и таблиц data_mart слоя
CREATE SCHEMA IF NOT EXISTS data_mart;

CREATE TABLE IF NOT EXISTS data_mart.t_dm_sales_customer (
    customer_id int4,
    full_name text,
    country varchar(80),
    first_purchase date,
    last_purchase date,
    revenue numeric(12, 2),
    quanity int8
);