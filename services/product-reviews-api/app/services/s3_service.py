import boto3
from botocore.config import Config
from fastapi import UploadFile
import uuid
from typing import Optional
import os
import botocore.exceptions


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self.bucket_name = os.getenv('S3_BUCKET')

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response.get('Error', {}).get('Code', 0))
            if error_code == 404:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                raise

    async def upload_file(self, file: UploadFile) -> Optional[str]:
        try:
            file_extension = file.filename.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"

            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_name
            )

            return file_name
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def list_bucket_files(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            return files
        except Exception as e:
            print(f"Error listing bucket files: {e}")
            return []

    def get_file_stream(self, filename):
        try:
            fileobj = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return fileobj['Body'], fileobj.get('ContentType', 'application/octet-stream')
        except Exception as e:
            print(f"Error getting file stream: {e}")
            return None, None
