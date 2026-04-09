--Создаем схемы для каждого слоя
CREATE SCHEMA IF NOT EXISTS staging_layer;

CREATE SCHEMA IF NOT EXISTS dds_layer;

CREATE SCHEMA IF NOT EXISTS datamart_layer;

--Раздаем права на пользователя star
GRANT ALL ON SCHEMA staging_layer TO star;

GRANT ALL ON SCHEMA dds_layer TO star;

GRANT ALL ON SCHEMA datamart_layer TO star;

GRANT ALL ON ALL TABLES IN SCHEMA staging_layer TO star;

GRANT ALL ON ALL TABLES IN SCHEMA dds_layer TO star;

GRANT ALL ON ALL TABLES IN SCHEMA datamart_layer TO star;