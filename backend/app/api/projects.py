"""Project API endpoints."""

import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.config import get_settings, Settings
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.setup_state import SetupStateResponse, DocTypeEntry, DocTypeConfigEntry
from app.services.project_service import ProjectService
from app.config_phases import DOC_TYPE_CONFIG, get_cli_command
from app.models.project import Project
from app.models.file import File
from app.api.phases import _get_project_dir, _derive_phase_status

router = APIRouter(prefix="/api/projects", tags=["projects"])
doc_types_router = APIRouter(prefix="/api/doc-types", tags=["doc-types"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new project.

    Args:
        data: Project creation data
        db: Database session

    Returns:
        Created project
    """
    service = ProjectService(db)
    project = await service.create_project(data)
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in project name"),
    sort_by: str = Query("updated_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort direction (asc/desc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    List projects with filtering, sorting, and pagination.

    Args:
        status: Filter by status (active, completed, archived)
        search: Search in project name
        sort_by: Field to sort by
        sort_order: Sort direction
        skip: Pagination offset
        limit: Pagination limit
        db: Database session

    Returns:
        List of projects and total count
    """
    service = ProjectService(db)
    projects, total = await service.list_projects(
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return ProjectListResponse(projects=projects, total=total)


@router.get("/recent", response_model=list[ProjectResponse])
async def get_recent_projects(
    limit: int = Query(4, ge=1, le=20, description="Number of recent projects"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recently accessed projects.

    Args:
        limit: Maximum number of projects to return
        db: Database session

    Returns:
        List of recently accessed projects
    """
    service = ProjectService(db)
    projects = await service.get_recent_projects(limit=limit)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single project by ID.

    Also updates the last_accessed_at timestamp.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: 404 if project not found
    """
    service = ProjectService(db)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Update last accessed timestamp
    project = await service.update_last_accessed(project_id)

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a project.

    Args:
        project_id: Project ID
        data: Update data (only provided fields are updated)
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: 404 if project not found
    """
    service = ProjectService(db)
    project = await service.update_project(project_id, data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return project


@router.get("/{project_id}/setup-state", response_model=SetupStateResponse)
async def get_setup_state(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Get setup state for a project — used by CLI handoff.

    Returns doc-type coverage, scaffolding status, and next CLI command.

    Args:
        project_id: Project ID
        db: Database session
        settings: Application settings

    Returns:
        SetupStateResponse with complete project setup information
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Get doc type config for project type
    doc_type_config = DOC_TYPE_CONFIG.get(project.type.value, [])

    # Query non-deleted files with doc_type set
    files_result = await db.execute(
        select(File).where(
            and_(
                File.project_id == project_id,
                File.is_deleted == False,
                File.doc_type.isnot(None),
            )
        )
    )
    files = files_result.scalars().all()

    # Group files by doc_type
    files_by_doc_type: dict[str, list[File]] = {}
    for f in files:
        if f.doc_type not in files_by_doc_type:
            files_by_doc_type[f.doc_type] = []
        files_by_doc_type[f.doc_type].append(f)

    # Parse skipped doc types
    skipped_ids: list[str] = []
    if project.skipped_doc_types:
        try:
            skipped_ids = json.loads(project.skipped_doc_types)
        except (json.JSONDecodeError, TypeError):
            skipped_ids = []

    # Build doc type entries
    doc_types: list[DocTypeEntry] = []
    for config_entry in doc_type_config:
        dt_id = config_entry["id"]
        matching_files = files_by_doc_type.get(dt_id, [])

        if matching_files:
            entry_status = "present"
            file_paths = [
                str(Path(settings.UPLOAD_DIR).resolve() / f.storage_path)
                for f in matching_files
            ]
        elif dt_id in skipped_ids:
            entry_status = "skipped"
            file_paths = []
        else:
            entry_status = "missing"
            file_paths = []

        doc_types.append(DocTypeEntry(
            id=dt_id,
            label=config_entry["label"],
            required=config_entry["required"],
            status=entry_status,
            file_count=len(matching_files),
            file_paths=file_paths,
        ))

    # Check for scaffolding (.planning directory)
    project_dir = _get_project_dir(project_id)
    has_scaffolding = (project_dir / ".planning").is_dir()

    # Compute next CLI command
    next_cli_command: Optional[str] = None
    if not has_scaffolding:
        next_cli_command = "/doc:new-fds"
    else:
        from app.config_phases import PROJECT_TYPE_PHASES
        phases_config = PROJECT_TYPE_PHASES.get(project.type.value, [])
        for phase in phases_config:
            phase_num = phase["number"]
            phase_status_info = _derive_phase_status(project_dir, phase_num)
            cmd = get_cli_command(phase_status_info["status"], phase_num)
            if cmd is not None:
                next_cli_command = cmd
                break

    return SetupStateResponse(
        project_id=project.id,
        project_name=project.name,
        project_type=project.type.value,
        language=project.language.value,
        project_dir=str(project_dir),
        doc_types=doc_types,
        has_scaffolding=has_scaffolding,
        next_cli_command=next_cli_command,
    )


@router.patch("/{project_id}/skipped-doc-types", response_model=ProjectResponse)
async def update_skipped_doc_types(
    project_id: int,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Persist skipped doc types for a project ('Niet beschikbaar' toggle).

    Args:
        project_id: Project ID
        payload: JSON body with "skipped" list of doc type IDs
        db: Database session

    Returns:
        Updated project
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    skipped = payload.get("skipped", [])
    if not isinstance(skipped, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'skipped' must be a list of doc type ID strings"
        )

    project.skipped_doc_types = json.dumps(skipped)
    await db.flush()
    await db.refresh(project)
    return project


@doc_types_router.get("/{project_type}", response_model=list[DocTypeConfigEntry])
async def get_doc_types(project_type: str):
    """
    Get document type configuration for a project type.

    Args:
        project_type: Project type (A, B, C, D)

    Returns:
        List of DocTypeConfigEntry for the given project type
    """
    if project_type not in DOC_TYPE_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project type '{project_type}' not found. Valid types: A, B, C, D"
        )
    return [DocTypeConfigEntry(**entry) for entry in DOC_TYPE_CONFIG[project_type]]
