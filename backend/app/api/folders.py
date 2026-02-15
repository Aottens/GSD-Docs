"""Folder API endpoints."""

from typing import Optional

from fastapi import (
    APIRouter, Depends, HTTPException, Query, status
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.file import FileScope
from app.schemas.file import FolderResponse, FolderCreate, FolderUpdate
from app.services.file_service import FolderService
from app.api.files import get_admin_user

router = APIRouter(prefix="/api", tags=["folders"])


@router.post(
    "/projects/{project_id}/folders",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_project_folder(
    project_id: int,
    data: FolderCreate,
    parent_id: Optional[int] = Query(None, description="Parent folder ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a folder in a project.

    Args:
        project_id: Project ID
        data: Folder creation data
        parent_id: Optional parent folder ID
        db: Database session

    Returns:
        Created folder
    """
    service = FolderService(db)

    try:
        folder = await service.create_folder(
            project_id=project_id,
            scope=FileScope.PROJECT,
            name=data.name,
            parent_id=parent_id
        )
        return folder
    except Exception as e:
        # Handle unique constraint violation
        if "UNIQUE constraint failed" in str(e) or "uq_folder_path" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Map '{data.name}' bestaat al op deze locatie"
            )
        raise


@router.get("/projects/{project_id}/folders", response_model=list[FolderResponse])
async def list_project_folders(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    List folders in a project.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        List of folders
    """
    service = FolderService(db)
    folders = await service.list_folders(project_id, FileScope.PROJECT)
    return folders


@router.patch("/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: int,
    data: FolderUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a folder (rename).

    Args:
        folder_id: Folder ID
        data: Update data
        db: Database session

    Returns:
        Updated folder
    """
    if not data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mapnaam is verplicht"
        )

    service = FolderService(db)

    try:
        folder = await service.update_folder(folder_id, data.name)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Map niet gevonden"
            )
        return folder
    except Exception as e:
        # Handle unique constraint violation
        if "UNIQUE constraint failed" in str(e) or "uq_folder_path" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Map '{data.name}' bestaat al op deze locatie"
            )
        raise


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a folder (only if empty).

    Args:
        folder_id: Folder ID
        db: Database session

    Raises:
        HTTPException: 404 if not found, 409 if not empty
    """
    service = FolderService(db)
    success = await service.delete_folder(folder_id)

    if not success:
        # Check if folder exists
        folders = await service.list_folders(None, FileScope.PROJECT)
        folder_exists = any(f.id == folder_id for f in folders)

        if folder_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Map kan niet worden verwijderd - bevat nog bestanden of submappen"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Map niet gevonden"
            )


# Shared library folder endpoints

@router.get("/files/shared/folders", response_model=list[FolderResponse])
async def list_shared_folders(
    db: AsyncSession = Depends(get_db),
):
    """
    List shared library folders.

    Args:
        db: Database session

    Returns:
        List of shared folders
    """
    service = FolderService(db)
    folders = await service.list_folders(None, FileScope.SHARED)
    return folders


@router.post(
    "/files/shared/folders",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_shared_folder(
    data: FolderCreate,
    parent_id: Optional[int] = Query(None, description="Parent folder ID"),
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user)
):
    """
    Create a shared library folder (admin-only).

    Args:
        data: Folder creation data
        parent_id: Optional parent folder ID
        db: Database session
        _admin: Admin auth dependency

    Returns:
        Created folder
    """
    service = FolderService(db)

    try:
        folder = await service.create_folder(
            project_id=None,
            scope=FileScope.SHARED,
            name=data.name,
            parent_id=parent_id
        )
        return folder
    except Exception as e:
        # Handle unique constraint violation
        if "UNIQUE constraint failed" in str(e) or "uq_folder_path" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Map '{data.name}' bestaat al op deze locatie"
            )
        raise
