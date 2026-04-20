-- содание схемы и таблдиц деталдьного слоя
CREATE SCHEMA IF NOT EXISTS dds;

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