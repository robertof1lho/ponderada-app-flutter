import boto3
from botocore.config import Config
from app.core.config import settings

_client = None


def get_storage_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        try:
            _client.create_bucket(Bucket=settings.minio_bucket)
        except Exception:
            pass  # bucket already exists
        try:
            _client.put_bucket_policy(
                Bucket=settings.minio_bucket,
                Policy=(
                    '{"Version":"2012-10-17","Statement":[{"Effect":"Allow",'
                    '"Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::'
                    + settings.minio_bucket + '/*"}]}'
                ),
            )
        except Exception:
            pass
    return _client
