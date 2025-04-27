import boto3
import os
from functools import lru_cache

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://ceph:8080")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "your-access-key")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "your-secret-key")
S3_BUCKET = os.getenv("S3_BUCKET", "product-reviews-api")

@lru_cache()
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    ) 