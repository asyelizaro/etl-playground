-- 1. установка расширения
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 2. foreign server
DROP SERVER IF EXISTS stage0_source CASCADE;

CREATE SERVER stage0_source FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'host.docker.internal',
    port '5432',
    dbname 'chinook'
);

-- 3. mapping
CREATE USER MAPPING FOR CURRENT_USER SERVER stage0_source OPTIONS (
    user 'postgres',
    password 'postgres'
);

CREATE SCHEMA IF NOT EXISTS stage;

-- 4. загрузка таблиц
CREATE FOREIGN
TABLE stage.customer (
    customer_id integer,
    first_name varchar(40),
    last_name varchar(20),
    company varchar(80),
    address varchar(70),
    city varchar(40),
    state varchar(40),
    country varchar(40),
    postal_code varchar(10),
    phone varchar(24),
    fax varchar(24),
    email varchar(60),
    support_rep_id integer
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'customer'
);

SELECT * FROM stage.customer;