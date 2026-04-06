# etl-playground
**E-commerce data for practicing ETL from source to analytics**
Практический проект для изучения полного ETL пайплайна

[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)


Ручной 
Предварительно необходимо разархивировать `olist_datasets.zip` ->`shared/data/`

```powershell
cd shared
docker compose up -d
.\load_all.ps1
docker exec -it postgres_olist_shared psql -U olist -d olist_source -c "\dt"
```