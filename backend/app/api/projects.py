"""Project API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])


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


@router.get("/", response_model=ProjectListResponse)
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
