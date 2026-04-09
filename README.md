# etl-playground
**E-commerce data for practicing ETL from source to analytics**
Практический проект для изучения полного ETL пайплайна

[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)


Предварительно необходимо разархивировать `olist_datasets.zip` ->`shared/data/`

```powershell
cd shared && docker-compose up -d
.\load_all.ps1
docker exec -it postgres_olist_shared psql -U olist -d olist_source -c "\dt"
```


### 1. Analytics Pipeline (stage1-plpgsql)
staging_layer → dds_layer → datamart_layer (Star Schema)
```
Запуск бд и инициализация
cd stage1-plpgsql && docker-compose up -d
psql -h localhost -p 5432 -U star -d star_schema_olist -f sql/init.sql
```