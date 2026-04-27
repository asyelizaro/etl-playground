-- содание схемы и таблдиц деталдьного слоя
CREATE SCHEMA IF NOT EXISTS dds;

DROP TABLE IF EXISTS dds.fact_sales CASCADE;

DROP TABLE IF EXISTS dds.dim_album CASCADE;

DROP TABLE IF EXISTS dds.dim_artist CASCADE;

DROP TABLE IF EXISTS dds.dim_track CASCADE;

DROP TABLE IF EXISTS dds.dim_customer CASCADE;

DROP TABLE IF EXISTS dds.dim_genre CASCADE;

DROP TABLE IF EXISTS dds.dim_employee CASCADE;

DROP TABLE IF EXISTS dds.dim_date CASCADE;

-- таблица фактов
CREATE TABLE IF NOT EXISTS dds.fact_sales (
    sale_id BIGINT PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    track_id BIGINT NOT NULL,
    artist_id INTEGER NOT NULL,
    album_id INTEGER NOT NULL,
    invoice_date DATE NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- таблицы измерений
CREATE TABLE IF NOT EXISTS dds.dim_album (
    album_id INTEGER PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    artist_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_artist (
    artist_id INTEGER PRIMARY KEY,
    "name" VARCHAR(120) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_genre (
    genre_id INTEGER PRIMARY KEY,
    "name" VARCHAR(120) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_track (
    track_id BIGINT PRIMARY KEY,
    "name" VARCHAR(400) NOT NULL,
    album_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    media_type_id INTEGER NOT NULL,
    composer VARCHAR(440),
    milliseconds INTEGER NOT NULL,
    "bytes" INTEGER,
    unit_price NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_customer (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(40) NOT NULL,
    company VARCHAR(160),
    address VARCHAR(140),
    city VARCHAR(80),
    state VARCHAR(80),
    country VARCHAR(80),
    postal_code VARCHAR(20),
    phone VARCHAR(48),
    fax VARCHAR(48),
    email VARCHAR(120) NOT NULL,
    support_rep_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_employee (
    employee_id INTEGER PRIMARY KEY,
    last_name VARCHAR(40) NOT NULL,
    first_name VARCHAR(80) NOT NULL,
    title VARCHAR(60),
    reports_to INTEGER,
    birth_date TIMESTAMP,
    hire_date TIMESTAMP,
    address VARCHAR(140),
    city VARCHAR(80),
    state VARCHAR(80),
    country VARCHAR(80),
    postal_code VARCHAR(20),
    phone VARCHAR(48),
    fax VARCHAR(48),
    email VARCHAR(120),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_date (
    date_key INTEGER PRIMARY KEY,
    "date" DATE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);