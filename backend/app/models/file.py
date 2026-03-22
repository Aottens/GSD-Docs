"""File and Folder models for reference library management."""

import enum
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Enum as SQLEnum,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.sql import func

from app.models.base import Base


class FileScope(str, enum.Enum):
    """File/folder scope enumeration (shared library or project-specific)."""
    SHARED = "shared"
    PROJECT = "project"


class Folder(Base):
    """
    Folder model for organizing files.

    Can be project-specific or part of shared library.
    Supports hierarchical structure via parent_id.
    """
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    scope = Column(SQLEnum(FileScope), nullable=False)
    parent_id = Column(Integer, ForeignKey('folders.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_folders_project_scope', 'project_id', 'scope'),
        UniqueConstraint('project_id', 'scope', 'parent_id', 'name',
                        name='uq_folder_path'),
    )

    def __repr__(self) -> str:
        return f"<Folder(id={self.id}, name='{self.name}', scope={self.scope.value})>"


class File(Base):
    """
    File model for storing file metadata.

    Files are stored on filesystem, this model tracks metadata.
    Supports soft delete and project-specific overrides of shared files.
    """
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    original_filename = Column(String(255), nullable=False)
    safe_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    scope = Column(SQLEnum(FileScope), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    folder_id = Column(Integer, ForeignKey('folders.id'), nullable=True)
    storage_path = Column(String(1000), nullable=False)
    doc_type = Column(String(50), nullable=True, index=True)
    overrides_file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now())
    uploaded_by = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_files_project_scope_deleted', 'project_id', 'scope', 'is_deleted'),
        Index('ix_files_scope_deleted', 'scope', 'is_deleted'),
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename='{self.safe_filename}', scope={self.scope.value})>"
