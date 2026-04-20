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

-- Использование схемы stage как основную схему для foreign table
SET search_path TO stage;

-- 4. загрузка таблиц
CREATE FOREIGN
TABLE stage.artist (
    artist_id int4 NOT NULL,
    "name" varchar(120) NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'artist'
);

CREATE FOREIGN
TABLE stage.genre (
    genre_id int4 NOT NULL,
    "name" varchar(120) NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'genre'
);

CREATE FOREIGN
TABLE stage.media_type (
    media_type_id int4 NOT NULL,
    "name" varchar(120) NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'media_type'
);

CREATE FOREIGN
TABLE stage.playlist (
    playlist_id int4 NOT NULL,
    "name" varchar(120) NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'playlist'
);

CREATE FOREIGN
TABLE stage.album (
    album_id int4 NOT NULL,
    title varchar(160) NOT NULL,
    artist_id int4 NOT NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'album'
);

CREATE FOREIGN
TABLE stage.employee (
    employee_id int4 NOT NULL,
    last_name varchar(20) NOT NULL,
    first_name varchar(20) NOT NULL,
    title varchar(30) NULL,
    reports_to int4 NULL,
    birth_date timestamp NULL,
    hire_date timestamp NULL,
    address varchar(70) NULL,
    city varchar(40) NULL,
    state varchar(40) NULL,
    country varchar(40) NULL,
    postal_code varchar(10) NULL,
    phone varchar(24) NULL,
    fax varchar(24) NULL,
    email varchar(60) NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'employee'
);

CREATE FOREIGN
TABLE stage.track (
    track_id int4 NOT NULL,
    "name" varchar(200) NOT NULL,
    album_id int4 NULL,
    media_type_id int4 NOT NULL,
    genre_id int4 NULL,
    composer varchar(220) NULL,
    milliseconds int4 NOT NULL,
    bytes int4 NULL,
    unit_price numeric(10, 2) NOT NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'track'
);

CREATE FOREIGN
TABLE stage.customer (
    customer_id int4 NOT NULL,
    first_name varchar(40) NOT NULL,
    last_name varchar(20) NOT NULL,
    company varchar(80) NULL,
    address varchar(70) NULL,
    city varchar(40) NULL,
    state varchar(40) NULL,
    country varchar(40) NULL,
    postal_code varchar(10) NULL,
    phone varchar(24) NULL,
    fax varchar(24) NULL,
    email varchar(60) NOT NULL,
    support_rep_id int4 NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'customer'
);

CREATE FOREIGN
TABLE stage.invoice (
    invoice_id int4 NOT NULL,
    customer_id int4 NOT NULL,
    invoice_date timestamp NOT NULL,
    billing_address varchar(70) NULL,
    billing_city varchar(40) NULL,
    billing_state varchar(40) NULL,
    billing_country varchar(40) NULL,
    billing_postal_code varchar(10) NULL,
    total numeric(10, 2) NOT NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'invoice'
);

CREATE FOREIGN
TABLE stage.invoice_line (
    invoice_line_id int4 NOT NULL,
    invoice_id int4 NOT NULL,
    track_id int4 NOT NULL,
    unit_price numeric(10, 2) NOT NULL,
    quantity int4 NOT NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'invoice_line'
);

CREATE FOREIGN
TABLE stage.playlist_track (
    playlist_id int4 NOT NULL,
    track_id int4 NOT NULL
) SERVER stage0_source OPTIONS (
    schema_name 'public',
    table_name 'playlist_track'
);