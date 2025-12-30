import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO
import io

from src.core.config import settings


class StorageService:
    """MinIO/S3 storage service for document files"""

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}" if not settings.MINIO_USE_SSL else f"https://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1",  # MinIO doesn't care about region
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            # Bucket doesn't exist, create it
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, file_content: bytes, file_path: str, content_type: str = "application/pdf") -> str:
        """Upload file to storage and return the path"""
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=file_path,
                Body=file_content,
                ContentType=content_type,
            )
            return file_path
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def get_file(self, file_path: str) -> bytes:
        """Download file from storage"""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=file_path)
            return response["Body"].read()
        except ClientError as e:
            raise Exception(f"Failed to get file: {str(e)}")

    def delete_file(self, file_path: str):
        """Delete file from storage"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
        except ClientError as e:
            raise Exception(f"Failed to delete file: {str(e)}")

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False


storage_service = StorageService()


