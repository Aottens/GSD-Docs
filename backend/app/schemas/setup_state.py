"""Pydantic schemas for setup-state and doc-type endpoints."""

from typing import Optional
from pydantic import BaseModel


class DocTypeConfigEntry(BaseModel):
    """A single document type configuration entry."""
    id: str
    label: str
    required: bool


class DocTypeEntry(BaseModel):
    """A document type entry with coverage status for a specific project."""
    id: str
    label: str
    required: bool
    status: str           # "present" | "missing" | "skipped"
    file_count: int
    file_paths: list[str]


class SetupStateResponse(BaseModel):
    """Full setup state for a project, used by CLI handoff."""
    project_id: int
    project_name: str
    project_type: str
    language: str
    project_dir: str
    doc_types: list[DocTypeEntry]
    has_scaffolding: bool
    next_cli_command: Optional[str]
