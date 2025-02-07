from fastapi import UploadFile
from app.services.file import FileService
from sqlalchemy.orm import Session


class FileController:
    def __init__(self, db: Session):
        self.file_service = FileService()
        self.db = db

    def upload_file(self, file: UploadFile, user_id: str):
        file = self.file_service.upload_file(file, user_id)
        self.db.add(file)
        self.db.commit()
        return file
