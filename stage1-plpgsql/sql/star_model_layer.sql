-- содание схемы и таблдиц деталдьного слоя
CREATE SCHEMA IF NOT EXISTS dds;

DROP TABLE IF EXISTS dds.fact_sales CASCADE;

DROP TABLE IF EXISTS dds.dim_album CASCADE;

-- таблица фактов
CREATE TABLE IF NOT EXISTS dds.fact_sales (
    sale_id PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    customer_idINTEGER NOT NULL,
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
    album_id int4 NOT NULL,
    title varchar(160) NOT NULL,
    artist_id int4 NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dds.dim_artist (
    artist_id int4 NOT NULL,
    "name" varchar(120) NULL,
    created_at TIMESTAMP DEFAULT NOW()
);