import pandas as pd
from sqlalchemy import create_engine
import boto3
from botocore.exceptions import ClientError
from io import BytesIO
from datetime import datetime, timezone
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHINOOK_CONFIG = {
    'host': os.getenv('POSTGRES_CHINOOK_HOST', 'postgres-stage0'),
    'port': int(os.getenv('POSTGRES_CHINOOK_PORT', 5432)),
    'database': os.getenv('POSTGRES_CHINOOK_DB', 'chinook'),
    'user': os.getenv('POSTGRES_CHINOOK_USER', 'postgres'),
    'password': os.getenv('POSTGRES_CHINOOK_PASSWORD', 'postgres')
}

MINIO_CONFIG = {
    'endpoint': os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
    'access_key': os.getenv('MINIO_ACCESS_KEY', 'minio'),
    'secret_key': os.getenv('MINIO_SECRET_KEY', 'minio123'),
    'bucket': os.getenv('MINIO_BUCKET', 'chinook-lake'),  # bucket для сырых данных
    'secure': os.getenv('MINIO_SECURE', 'False').lower() == 'true'
}

TABLES = ['artist', 'genre',  'playlist', 'album', 'employee', 'track', 'customer', 'invoice', 'invoice_line', 'playlist_track']


#Подключение к MinIO
def get_minio_client():
    return boto3.client(
        's3',
        endpoint_url=MINIO_CONFIG['endpoint'],
        aws_access_key_id=MINIO_CONFIG['access_key'],
        aws_secret_access_key=MINIO_CONFIG['secret_key'],
        region_name='us-east-1',
        use_ssl=MINIO_CONFIG['secure'],
        verify=False,
        config=boto3.session.Config(
            s3={"addressing_style": "path"}
        )
    )

#Подключение к БД Chinook
def get_chinook_engine():
    db_url = f"postgresql://{CHINOOK_CONFIG['user']}:{CHINOOK_CONFIG['password']}@{CHINOOK_CONFIG['host']}:{CHINOOK_CONFIG['port']}/{CHINOOK_CONFIG['database']}"
    return create_engine(db_url)


#Извлекаем данные и кладем в parquet
def extract_table_to_parquet(engine, table_name):
    logger.info(f'Extracting table: {table_name}')
    
    df = pd.read_sql(f'SELECT * FROM "{table_name}"', engine)

    buffr = BytesIO()
    df.to_parquet(buffr, index=False)
    buffr.seek(0)

    return buffr, df

def upload_to_minio(s3_client, buffer, table_name):
    try:

        logger.info(f"BUCKET USED: {MINIO_CONFIG['bucket']}")

        ensure_bucket(s3_client, MINIO_CONFIG['bucket'])

        now = datetime.now(timezone.utc)
        date = now.strftime('%Y-%m-%d')

        s3_client.upload_fileobj(
            buffer,
            MINIO_CONFIG['bucket'],
            f"{table_name}/dt={date}/{table_name}.parquet",
            ExtraArgs={
                'ContentType': 'application/octet-stream',
                'Metadata': {
                    'source': 'chinook-db',
                    'extracted_at': now.isoformat()
                }
            }
        )
        logger.info(f"Uploaded s3://{MINIO_CONFIG['bucket']}/{table_name}/dt={date}/{table_name}.parquet")
    except Exception as e:
        logger.error(f"Error uploading {table_name}: {e}")
        raise

def ensure_bucket(client, bucket_name):
    try:
        client.head_bucket(Bucket=bucket_name)
        return
    except ClientError as e:
        if e.response["Error"]["Code"] in ["404", "NoSuchBucket", "NotFound"]:
            client.create_bucket(Bucket=bucket_name)
        else:
            raise

def main():
    logger.info("Starting Chinook Ingestion Pipeline")

    client = get_minio_client()
    engine = get_chinook_engine()

    ensure_bucket(client, MINIO_CONFIG["bucket"])
    logger.info(f"Bucket ready: {MINIO_CONFIG['bucket']}")

    stats = {}

    for table in TABLES:
        try:
            buffer, df = extract_table_to_parquet(engine, table)
            upload_to_minio(client, buffer, table)

            stats[table] = {
                'rows': len(df),
                'columns': len(df.columns),
                'status': 'success'
            }

            logger.info(f"{table}: OK ({len(df)} rows)")

        except Exception as e:
            logger.error(f"{table}: FAILED - {e}")
            stats[table] = {'status': 'error', 'error': str(e)}

    logger.info("Pipeline Summary:")
    logger.info(stats)

    success = sum(1 for s in stats.values() if s.get("status") == "success")
    logger.info(f"Success: {success}/{len(TABLES)}")

    logger.info("Done")

if __name__ == "__main__":
    main()