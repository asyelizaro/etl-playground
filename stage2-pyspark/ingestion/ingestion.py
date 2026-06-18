import pandas as pd
from sqlalchemy import create_engine
import boto3
from io import BytesIO
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHINOOK_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'chinook',
    'user': 'postgres',
    'password': 'postgres'
}

MINIO_CONFIG = {
    'endpoint': 'localhost:9000',
    'access_key': 'minioadmin',
    'secret_key': 'minioadmin',
    'bucket': 'chinook_raw',  # bucket для сырых данных
    'secure': False
}

TABLES = [
    'artist', 'genre',  'playlist', 'album', 'employee', 'track', 'customer', 'invoice', 'invoice_line', 'playlist_track'
]

def get_minio_client():
    return boto3.client(
        's3',
        endpoint_url=MINIO_CONFIG['endpoint'],
        aws_access_key_id=MINIO_CONFIG['access_key'],
        aws_secret_access_key=MINIO_CONFIG['secret_key'],
        region_name='us-east-1',
        use_ssl=MINIO_CONFIG['secure']
    )


#Создание подключения к Chinook
def get_chinook_engine():
    db_url = f"postgresql://{CHINOOK_CONFIG['user']}:{CHINOOK_CONFIG['password']}@{CHINOOK_CONFIG['host']}:{CHINOOK_CONFIG['port']}/{CHINOOK_CONFIG['database']}"
    return create_engine(db_url)

#Извлекаем данные и кладем в parquet
def extract_table_to_parquet(engine, table_name):
    logger.info(f"Extract table: {table_name}")
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    return buffer, df

#Загрузка parquet в MiniO
def upload_to_minio(s3_client, buffer, table_name):
    try:
        s3_client.upload_fileobj(
            buffer,
            MINIO_CONFIG['bucket'],
            f"{table_name}.parquet",
            ExtraArgs={
                'ContentType': 'application/octet-stream',
                'Metadata': {
                    'source': 'chinook-db',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            }
        )
        logger.info(f"Uploaded {table_name}.parquet to MinIO (bucket: {MINIO_CONFIG['bucket']})")
    except Exception as e:
        logger.error(f"Error uploading {table_name}: {e}")
        raise



def main():
    logger.info("Starting Chinook Ingestion Pipeline")
    
    # Создаваем коннекты
    engine = get_chinook_engine()
    s3_client = get_minio_client()
    
    # Проверяем, что bucket существует, если нет - создаем
    try:
        s3_client.head_bucket(Bucket=MINIO_CONFIG['bucket'])
        logger.info(f"Bucket {MINIO_CONFIG['bucket']} exists")
    except Exception:
        logger.info(f"Creating bucket {MINIO_CONFIG['bucket']}...")
        s3_client.create_bucket(Bucket=MINIO_CONFIG['bucket'])
    
    # Обрабатываем каждую таблицу
    stats = {}
    for table in TABLES:
        try:
            buffer, df = extract_table_to_parquet(engine, table)
            upload_to_minio(s3_client, buffer, table)
            stats[table] = {
                'rows': len(df),
                'columns': len(df.columns),
                'status': 'success'
            }
            logger.info(f"Success! Rows: {len(df)}, Columns: {len(df.columns)}")
        except Exception as e:
            logger.error(f"Error! processing {table}: {e}")
            stats[table] = {'status': 'error', 'error': str(e)}
    
    # Финальная статистика
    logger.info("\nIngestion Summary")
    for table, stat in stats.items():
        logger.info(f"{table}: {stat}")
    
    success_count = sum(1 for s in stats.values() if s['status'] == 'success')
    logger.info(f"\nTotal: {success_count}/{len(TABLES)} tables loaded successfully")
    logger.info("Pipeline Completed")

if __name__ == "__main__":
    main()