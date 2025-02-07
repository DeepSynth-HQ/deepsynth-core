from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.client import Base
import uuid


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(
        String(100), nullable=False
    )  # e.g., 'image', 'document', 'video'
    mime_type = Column(
        String(100), nullable=False
    )  # e.g., 'image/jpeg', 'application/pdf'
    extension = Column(String(20))  # e.g., '.jpg', '.pdf'

    # Storage information
    storage_provider = Column(String(50))  # e.g., 'local', 's3', 'google_cloud'
    storage_path = Column(String(500))  # Full storage path

    # Status and visibility
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # User relationship (if needed)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="files", lazy="select")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def __init__(
        self,
        filename,
        original_filename,
        file_path,
        file_size,
        file_type,
        mime_type,
        extension,
        storage_provider="local",
        is_public=False,
        user_id=None,
    ):
        self.filename = filename
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        self.mime_type = mime_type
        self.extension = extension
        self.storage_provider = storage_provider
        self.is_public = is_public
        self.user_id = user_id
        self.storage_path = file_path  # You can modify this based on your storage logic

    def __repr__(self):
        return f"<File {self.filename}>"

    def to_dict(self):
        """Convert the file object to a dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "extension": self.extension,
            "storage_provider": self.storage_provider,
            "is_public": self.is_public,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def file_url(self):
        """Generate a URL for the file based on storage provider"""
        if self.storage_provider == "local":
            return f"/files/{self.filename}"
        elif self.storage_provider == "s3":
            return f"https://s3.amazonaws.com/your-bucket/{self.storage_path}"
        return self.storage_path

    def soft_delete(self):
        """Soft delete the file"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False

    @property
    def is_deleted(self):
        """Check if the file is deleted"""
        return self.deleted_at is not None

    @property
    def human_readable_size(self):
        """Convert file size to human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if self.file_size < 1024:
                return f"{self.file_size:.2f}{unit}"
            self.file_size /= 1024
