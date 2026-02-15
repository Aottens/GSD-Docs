"""Project Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectType, Language, ProjectStatus


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ProjectType
    language: Language


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[ProjectType] = None
    language: Optional[Language] = None
    status: Optional[ProjectStatus] = None
    current_phase: Optional[str] = Field(None, max_length=100)
    progress: Optional[int] = Field(None, ge=0, le=100)


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    status: ProjectStatus
    current_phase: str
    progress: int
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response."""
    projects: list[ProjectResponse]
    total: int
