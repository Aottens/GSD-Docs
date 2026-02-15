"""Filesystem storage operations for uploaded files."""

import os
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import UploadFile

from app.config import Settings
from app.models.file import FileScope


async def ensure_upload_dir(settings: Settings) -> None:
    """
    Ensure the upload directory exists.

    Called during application startup.

    Args:
        settings: Application settings
    """
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)


async def save_file(
    file: UploadFile,
    scope: FileScope,
    project_id: Optional[int],
    folder_path: str,
    file_uuid: str,
    ext: str,
    settings: Settings
) -> str:
    """
    Save uploaded file to filesystem.

    Files are organized as: {scope}/{project_id or 'shared'}/{folder_path}/{uuid}{ext}

    Args:
        file: Uploaded file
        scope: File scope (shared or project)
        project_id: Project ID (None for shared)
        folder_path: Folder path within project/shared
        file_uuid: Unique file identifier
        ext: File extension (with leading dot)
        settings: Application settings

    Returns:
        Relative storage path (relative to UPLOAD_DIR)
    """
    # Generate storage path
    scope_dir = scope.value
    project_dir = str(project_id) if project_id else 'shared'
    storage_path = Path(scope_dir) / project_dir / folder_path / f"{file_uuid}{ext}"

    # Create full path
    full_path = Path(settings.UPLOAD_DIR) / storage_path

    # Create parent directories
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file content
    content = await file.read()
    async with aiofiles.open(full_path, 'wb') as f:
        await f.write(content)

    # Reset file position
    await file.seek(0)

    return str(storage_path)


async def delete_file(storage_path: str, settings: Settings) -> bool:
    """
    Delete file from filesystem (hard delete).

    Note: Soft delete just sets is_deleted flag without calling this.

    Args:
        storage_path: Relative storage path
        settings: Application settings

    Returns:
        True if file was deleted, False if file didn't exist
    """
    full_path = Path(settings.UPLOAD_DIR) / storage_path

    if full_path.exists():
        full_path.unlink()
        return True

    return False


async def replace_file(
    old_storage_path: str,
    file: UploadFile,
    scope: FileScope,
    project_id: Optional[int],
    folder_path: str,
    file_uuid: str,
    ext: str,
    settings: Settings
) -> str:
    """
    Replace existing file with new content.

    Saves new file and deletes old one.

    Args:
        old_storage_path: Old file's storage path
        file: New uploaded file
        scope: File scope
        project_id: Project ID (None for shared)
        folder_path: Folder path
        file_uuid: Unique file identifier
        ext: File extension
        settings: Application settings

    Returns:
        New storage path
    """
    # Save new file
    new_storage_path = await save_file(
        file, scope, project_id, folder_path, file_uuid, ext, settings
    )

    # Delete old file
    await delete_file(old_storage_path, settings)

    return new_storage_path


def get_absolute_path(storage_path: str, settings: Settings) -> Path:
    """
    Get absolute filesystem path from relative storage path.

    Args:
        storage_path: Relative storage path
        settings: Application settings

    Returns:
        Absolute path to file
    """
    return Path(settings.UPLOAD_DIR) / storage_path
