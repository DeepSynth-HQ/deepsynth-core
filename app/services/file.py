from storage.aws_s3 import S3Storage
from config import settings
from app.models.file import File
from uuid import uuid4
from fastapi import UploadFile


class FileService:
    def __init__(self):
        self.s3_storage = S3Storage()

    def upload_file(self, file: UploadFile, user_id: str = None) -> File:
        file_name = f"{settings.FILE_PREFIX}{uuid4()}.{file.filename.split('.')[-1]}"
        result = self.s3_storage.upload_file(file.file, file_name, file.content_type)
        if result["status"] == "success":
            file = File(
                filename=file_name,
                original_filename=file.filename,
                extension=file.filename.split(".")[-1],
                mime_type=file.content_type,
                file_size=file.size,
                file_path=result["url"],
                file_type="image",
                user_id=user_id,
                storage_provider="s3",
                is_public=True,
            )
        return file
