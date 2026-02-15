"""Project model and related enums."""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Index
from sqlalchemy.sql import func

from app.models.base import Base


class ProjectType(str, enum.Enum):
    """Project type enumeration (A, B, C, D)."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Language(str, enum.Enum):
    """Language enumeration (Dutch, English)."""
    nl = "nl"
    en = "en"


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    active = "active"
    completed = "completed"
    archived = "archived"


class Project(Base):
    """
    Project model representing a FDS/SDS project.

    Tracks project metadata, progress, and lifecycle information.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)
    type = Column(SQLEnum(ProjectType), nullable=False)
    language = Column(SQLEnum(Language), nullable=False)
    status = Column(
        SQLEnum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.active,
        index=True
    )
    current_phase = Column(String(100), nullable=False, default="setup")
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    last_accessed_at = Column(DateTime, nullable=True)

    # Additional indexes for common queries
    __table_args__ = (
        Index('ix_projects_status_updated', 'status', 'updated_at'),
        Index('ix_projects_last_accessed', 'last_accessed_at'),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', type={self.type.value})>"
