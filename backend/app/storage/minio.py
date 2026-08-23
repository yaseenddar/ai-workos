import io
from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class MinioStorage:
    def __init__(self):
        settings = get_settings()

        self.bucket = settings.minio_bucket

        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        self._ensure_bucket()

    def _ensure_bucket(self):
        exists = self.client.bucket_exists(self.bucket)

        if not exists:
            self.client.make_bucket(self.bucket)

    def upload_file(
        self,
        object_name: str,
        data: bytes,
        content_type: str,
    ):
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def delete_file(self, object_name: str):
        self.client.remove_object(self.bucket, object_name)
        
    def download_file(self, object_name: str) -> bytes:
        response = None

        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )

            return response.read()

        finally:
            if response is not None:
                response.close()
                response.release_conn()