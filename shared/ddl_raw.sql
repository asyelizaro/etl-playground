DROP TABLE IF EXISTS olist_customers_dataset;

CREATE TABLE olist_customers_dataset (
    customer_id varchar(50) NULL,
    customer_unique_id varchar(50) NULL,
    customer_zip_code_prefix int4 NULL,
    customer_city varchar(50) NULL,
    customer_state varchar(50) NULL
);

DROP TABLE IF EXISTS olist_geolocation_dataset;

CREATE TABLE olist_geolocation_dataset (
    geolocation_zip_code_prefix int4 NULL,
    geolocation_lat float4 NULL,
    geolocation_lng float4 NULL,
    geolocation_city varchar(50) NULL,
    geolocation_state varchar(50) NULL
);

DROP TABLE IF EXISTS olist_order_items_dataset;

CREATE TABLE olist_order_items_dataset (
    order_id varchar(50) NULL,
    order_item_id int4 NULL,
    product_id varchar(50) NULL,
    seller_id varchar(50) NULL,
    shipping_limit_date varchar(50) NULL,
    price float4 NULL,
    freight_value float4 NULL
);

DROP TABLE IF EXISTS olist_order_payments_dataset;

CREATE TABLE olist_order_payments_dataset (
    order_id varchar(50) NULL,
    payment_sequential int4 NULL,
    payment_type varchar(50) NULL,
    payment_installments int4 NULL,
    payment_value float4 NULL
);

DROP TABLE IF EXISTS olist_order_reviews_dataset;

CREATE TABLE olist_order_reviews_dataset (
    review_id varchar(50) NULL,
    order_id varchar(50) NULL,
    review_score int4 NULL,
    review_comment_title varchar(50) NULL,
    review_comment_message varchar(256) NULL,
    review_creation_date varchar(50) NULL,
    review_answer_timestamp varchar(50) NULL
);

DROP TABLE IF EXISTS olist_orders_dataset;

CREATE TABLE olist_orders_dataset (
    order_id varchar(50) NULL,
    customer_id varchar(50) NULL,
    order_status varchar(50) NULL,
    order_purchase_timestamp varchar(50) NULL,
    order_approved_at varchar(50) NULL,
    order_delivered_carrier_date varchar(50) NULL,
    order_delivered_customer_date varchar(50) NULL,
    order_estimated_delivery_date varchar(50) NULL
);

DROP TABLE IF EXISTS olist_products_dataset;

CREATE TABLE olist_products_dataset (
    product_id varchar(50) NULL,
    product_category_name varchar(50) NULL,
    product_name_lenght int4 NULL,
    product_description_lenght int4 NULL,
    product_photos_qty int4 NULL,
    product_weight_g int4 NULL,
    product_length_cm int4 NULL,
    product_height_cm int4 NULL,
    product_width_cm int4 NULL
);

DROP TABLE IF EXISTS olist_sellers_dataset;

CREATE TABLE olist_sellers_dataset (
    seller_id varchar(50) NULL,
    seller_zip_code_prefix int4 NULL,
    seller_city varchar(50) NULL,
    seller_state varchar(50) NULL
);

DROP TABLE IF EXISTS product_category_name_translation;

CREATE TABLE product_category_name_translation (
    product_category_name varchar(50) NULL,
    product_category_name_english varchar(50) NULL
);