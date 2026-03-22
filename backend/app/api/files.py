"""File API endpoints."""

from typing import Optional
from uuid import uuid4
from pathlib import Path

from fastapi import (
    APIRouter, Depends, HTTPException, Query, UploadFile, File as FastAPIFile,
    status, Header
)
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.config import get_settings, Settings
from app.models.file import FileScope
from app.models.project import Project
from app.schemas.file import (
    FileResponse, FileUploadResponse, FileUpdate, FileListResponse
)
from app.services.file_validator import validate_file_upload
from app.services.file_storage import save_file, replace_file, get_absolute_path
from app.services.file_service import FileService

router = APIRouter(prefix="/api", tags=["files"])


def get_admin_user(
    x_admin_key: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> None:
    """
    Simple admin authentication dependency.

    If ADMIN_API_KEY is set, requires matching X-Admin-Key header.
    If ADMIN_API_KEY is empty (dev mode), allows all requests.

    Args:
        x_admin_key: Admin API key from header
        settings: Application settings

    Raises:
        HTTPException: 403 if auth fails
    """
    if settings.ADMIN_API_KEY:
        if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Onvoldoende rechten - admin toegang vereist"
            )


@router.post(
    "/projects/{project_id}/files",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_project_file(
    project_id: int,
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[int] = Query(None, description="Folder ID"),
    doc_type: Optional[str] = Query(None, max_length=50, description="Document type classification"),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Upload a file to a project.

    Validates file, saves to filesystem, and creates database record.

    Args:
        project_id: Project ID
        file: File to upload
        folder_id: Optional folder ID
        db: Database session
        settings: Application settings

    Returns:
        Upload response with file metadata
    """
    # Verify project exists
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project met id {project_id} niet gevonden"
        )

    # Validate file
    validation = await validate_file_upload(file, settings)

    # Generate UUID for file
    file_uuid = str(uuid4())

    # Determine folder path
    folder_path = str(folder_id) if folder_id else "root"

    # Save file to filesystem
    storage_path = await save_file(
        file=file,
        scope=FileScope.PROJECT,
        project_id=project_id,
        folder_path=folder_path,
        file_uuid=file_uuid,
        ext=validation['extension'],
        settings=settings
    )

    # Create database record
    service = FileService(db)
    file_record = await service.create_file({
        'uuid': file_uuid,
        'original_filename': file.filename,
        'safe_filename': validation['safe_filename'],
        'mime_type': validation['mime_type'],
        'size_bytes': validation['size'],
        'scope': FileScope.PROJECT,
        'project_id': project_id,
        'folder_id': folder_id,
        'storage_path': storage_path,
        'doc_type': doc_type,
    })

    return FileUploadResponse(
        id=file_record.id,
        uuid=file_record.uuid,
        filename=file_record.safe_filename,
        mime_type=file_record.mime_type,
        size_bytes=file_record.size_bytes,
        doc_type=file_record.doc_type,
        uploaded_at=file_record.uploaded_at
    )


@router.get("/projects/{project_id}/files", response_model=FileListResponse)
async def list_project_files(
    project_id: int,
    folder_id: Optional[int] = Query(None, description="Filter by folder"),
    file_type: Optional[str] = Query(None, description="Filter by type (pdf, docx, image)"),
    search: Optional[str] = Query(None, description="Search in filename"),
    db: AsyncSession = Depends(get_db),
):
    """
    List files in a project.

    Args:
        project_id: Project ID
        folder_id: Optional folder filter
        file_type: Optional file type filter
        search: Optional search query
        db: Database session

    Returns:
        List of files and total count
    """
    service = FileService(db)

    if search:
        files = await service.search_files(project_id, search, file_type)
        total = len(files)
    else:
        files, total = await service.list_project_files(project_id, folder_id, file_type)

    # Add download URLs
    file_responses = [
        FileResponse(
            **{k: v for k, v in file.__dict__.items() if k != '_sa_instance_state'},
            download_url=f"/api/files/{file.id}/download"
        )
        for file in files
    ]

    return FileListResponse(files=file_responses, total=total)


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Download a file.

    Args:
        file_id: File ID
        db: Database session
        settings: Application settings

    Returns:
        File content with attachment disposition
    """
    service = FileService(db)
    file_record = await service.get_file(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )

    file_path = get_absolute_path(file_record.storage_path, settings)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand bestaat niet op schijf"
        )

    return FastAPIFileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type=file_record.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{file_record.original_filename}"'}
    )


@router.get("/files/{file_id}/preview")
async def preview_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Preview a file (inline disposition).

    Args:
        file_id: File ID
        db: Database session
        settings: Application settings

    Returns:
        File content with inline disposition
    """
    service = FileService(db)
    file_record = await service.get_file(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )

    file_path = get_absolute_path(file_record.storage_path, settings)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand bestaat niet op schijf"
        )

    return FastAPIFileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type=file_record.mime_type,
        headers={"Content-Disposition": f'inline; filename="{file_record.original_filename}"'}
    )


@router.patch("/files/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: int,
    data: FileUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update file metadata (rename, move).

    Args:
        file_id: File ID
        data: Update data
        db: Database session

    Returns:
        Updated file
    """
    service = FileService(db)

    update_data = data.model_dump(exclude_unset=True)
    file_record = await service.update_file(file_id, update_data)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )

    return FileResponse(
        **{k: v for k, v in file_record.__dict__.items() if k != '_sa_instance_state'},
        download_url=f"/api/files/{file_record.id}/download"
    )


@router.put("/files/{file_id}/replace", response_model=FileResponse)
async def replace_file_content(
    file_id: int,
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Replace file content while keeping metadata record.

    Args:
        file_id: File ID
        file: New file content
        db: Database session
        settings: Application settings

    Returns:
        Updated file record
    """
    service = FileService(db)
    file_record = await service.get_file(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )

    # Validate new file
    validation = await validate_file_upload(file, settings)

    # Determine folder path
    folder_path = str(file_record.folder_id) if file_record.folder_id else "root"

    # Replace file on filesystem
    new_storage_path = await replace_file(
        old_storage_path=file_record.storage_path,
        file=file,
        scope=file_record.scope,
        project_id=file_record.project_id,
        folder_path=folder_path,
        file_uuid=file_record.uuid,
        ext=validation['extension'],
        settings=settings
    )

    # Update database record
    file_record = await service.update_file(file_id, {
        'storage_path': new_storage_path,
        'mime_type': validation['mime_type'],
        'size_bytes': validation['size'],
        'safe_filename': validation['safe_filename'],
    })

    return FileResponse(
        **{k: v for k, v in file_record.__dict__.items() if k != '_sa_instance_state'},
        download_url=f"/api/files/{file_record.id}/download"
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft-delete a file.

    Args:
        file_id: File ID
        db: Database session
    """
    service = FileService(db)
    file_record = await service.soft_delete_file(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )


# Shared library endpoints

@router.post(
    "/files/shared",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_shared_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[int] = Query(None, description="Folder ID"),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    _admin: None = Depends(get_admin_user)
):
    """
    Upload a file to shared library (admin-only).

    Args:
        file: File to upload
        folder_id: Optional folder ID
        db: Database session
        settings: Application settings
        _admin: Admin auth dependency

    Returns:
        Upload response with file metadata
    """
    # Validate file
    validation = await validate_file_upload(file, settings)

    # Generate UUID for file
    file_uuid = str(uuid4())

    # Determine folder path
    folder_path = str(folder_id) if folder_id else "root"

    # Save file to filesystem
    storage_path = await save_file(
        file=file,
        scope=FileScope.SHARED,
        project_id=None,
        folder_path=folder_path,
        file_uuid=file_uuid,
        ext=validation['extension'],
        settings=settings
    )

    # Create database record
    service = FileService(db)
    file_record = await service.create_file({
        'uuid': file_uuid,
        'original_filename': file.filename,
        'safe_filename': validation['safe_filename'],
        'mime_type': validation['mime_type'],
        'size_bytes': validation['size'],
        'scope': FileScope.SHARED,
        'project_id': None,
        'folder_id': folder_id,
        'storage_path': storage_path,
    })

    return FileUploadResponse(
        id=file_record.id,
        uuid=file_record.uuid,
        filename=file_record.safe_filename,
        mime_type=file_record.mime_type,
        size_bytes=file_record.size_bytes,
        uploaded_at=file_record.uploaded_at
    )


@router.get("/files/shared", response_model=FileListResponse)
async def list_shared_files(
    folder_id: Optional[int] = Query(None, description="Filter by folder"),
    file_type: Optional[str] = Query(None, description="Filter by type (pdf, docx, image)"),
    search: Optional[str] = Query(None, description="Search in filename"),
    db: AsyncSession = Depends(get_db),
):
    """
    List shared library files.

    Args:
        folder_id: Optional folder filter
        file_type: Optional file type filter
        search: Optional search query
        db: Database session

    Returns:
        List of files and total count
    """
    service = FileService(db)

    if search:
        files = await service.search_files(None, search, file_type)
        total = len(files)
    else:
        files, total = await service.list_shared_files(folder_id, file_type)

    # Add download URLs
    file_responses = [
        FileResponse(
            **{k: v for k, v in file.__dict__.items() if k != '_sa_instance_state'},
            download_url=f"/api/files/{file.id}/download"
        )
        for file in files
    ]

    return FileListResponse(files=file_responses, total=total)


@router.delete("/files/shared/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shared_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: None = Depends(get_admin_user)
):
    """
    Soft-delete a shared library file (admin-only).

    Args:
        file_id: File ID
        db: Database session
        _admin: Admin auth dependency
    """
    service = FileService(db)
    file_record = await service.soft_delete_file(file_id)

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestand niet gevonden"
        )


@router.post("/files/{file_id}/override", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def create_file_override(
    file_id: int,
    project_id: int = Query(..., description="Project ID for override"),
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Create project-specific override of a shared file.

    Args:
        file_id: Shared file ID being overridden
        project_id: Project ID for the override
        file: New file content
        db: Database session
        settings: Application settings

    Returns:
        Created override file
    """
    service = FileService(db)

    # Verify shared file exists
    shared_file = await service.get_file(file_id)
    if not shared_file or shared_file.scope != FileScope.SHARED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gedeeld bestand niet gevonden"
        )

    # Validate new file
    validation = await validate_file_upload(file, settings)

    # Generate UUID for override file
    file_uuid = str(uuid4())

    # Use same folder structure as shared file
    folder_path = str(shared_file.folder_id) if shared_file.folder_id else "root"

    # Save file to filesystem
    storage_path = await save_file(
        file=file,
        scope=FileScope.PROJECT,
        project_id=project_id,
        folder_path=folder_path,
        file_uuid=file_uuid,
        ext=validation['extension'],
        settings=settings
    )

    # Create override record
    override_file = await service.create_override(
        shared_file_id=file_id,
        project_id=project_id,
        new_file_data={
            'uuid': file_uuid,
            'original_filename': file.filename,
            'safe_filename': validation['safe_filename'],
            'mime_type': validation['mime_type'],
            'size_bytes': validation['size'],
            'folder_id': shared_file.folder_id,
            'storage_path': storage_path,
        }
    )

    return FileUploadResponse(
        id=override_file.id,
        uuid=override_file.uuid,
        filename=override_file.safe_filename,
        mime_type=override_file.mime_type,
        size_bytes=override_file.size_bytes,
        uploaded_at=override_file.uploaded_at
    )
