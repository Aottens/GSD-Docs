"""Pydantic schemas for export API responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExportVersionSchema(BaseModel):
    """Schema for a single versioned export artifact."""

    filename: str
    doc_type: str  # FDS or SDS
    mode: str  # draft or final
    language: str  # nl or en
    version: str
    created_at: datetime
    size_bytes: int
    download_url: str


class ExportVersionListResponse(BaseModel):
    """Response schema for listing export versions."""

    project_id: int
    versions: list[ExportVersionSchema]


class AssemblyReadinessSchema(BaseModel):
    """Schema for assembly readiness check response."""

    ready: bool
    mode: str
    unreviewed_phases: list[str]
    has_content: bool


class PandocStatusSchema(BaseModel):
    """Schema for Pandoc installation status."""

    installed: bool
    version: Optional[str] = None


class ExportProgressEvent(BaseModel):
    """Schema for SSE progress event data."""

    event: str  # step_start | step_done | complete | error | cancelled
    step: int
    name: str
    total_steps: int
    message: Optional[str] = None
