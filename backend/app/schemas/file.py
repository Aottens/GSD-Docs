"""File and Folder Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.file import FileScope


class FileResponse(BaseModel):
    """Schema for file response."""
    id: int
    uuid: str
    original_filename: str
    safe_filename: str
    mime_type: str
    size_bytes: int
    scope: FileScope
    project_id: Optional[int] = None
    folder_id: Optional[int] = None
    overrides_file_id: Optional[int] = None
    uploaded_at: datetime
    uploaded_by: Optional[str] = None
    is_deleted: bool
    download_url: str

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: int
    uuid: str
    filename: str  # safe_filename
    mime_type: str
    size_bytes: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUpdate(BaseModel):
    """Schema for updating file metadata (rename, move)."""
    original_filename: Optional[str] = Field(None, min_length=1, max_length=255)
    folder_id: Optional[int] = None


class FileListResponse(BaseModel):
    """Schema for file list response."""
    files: list[FileResponse]
    total: int


class FolderResponse(BaseModel):
    """Schema for folder response."""
    id: int
    name: str
    project_id: Optional[int] = None
    scope: FileScope
    parent_id: Optional[int] = None
    created_at: datetime
    file_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class FolderCreate(BaseModel):
    """Schema for creating a folder."""
    name: str = Field(..., min_length=1, max_length=255)


class FolderUpdate(BaseModel):
    """Schema for updating a folder."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
