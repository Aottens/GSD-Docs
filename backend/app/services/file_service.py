"""File and folder business logic services."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File, Folder, FileScope
from app.config import DEFAULT_PROJECT_FOLDERS, DEFAULT_SHARED_FOLDERS


class FileService:
    """Service for managing file operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_file(self, file_data: dict) -> File:
        """
        Create a new file record.

        Args:
            file_data: Dictionary with file fields

        Returns:
            Created file with all fields populated
        """
        file_record = File(**file_data)
        self.db.add(file_record)
        await self.db.flush()
        await self.db.refresh(file_record)
        return file_record

    async def get_file(self, file_id: int) -> Optional[File]:
        """
        Get a file by ID (excludes soft-deleted files).

        Args:
            file_id: File ID

        Returns:
            File if found and not deleted, None otherwise
        """
        result = await self.db.execute(
            select(File).where(
                and_(
                    File.id == file_id,
                    File.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_project_files(
        self,
        project_id: int,
        folder_id: Optional[int] = None,
        file_type: Optional[str] = None
    ) -> tuple[list[File], int]:
        """
        List files for a project with optional filtering.

        Args:
            project_id: Project ID
            folder_id: Filter by folder (None = all folders)
            file_type: Filter by MIME type prefix (e.g., "pdf", "image")

        Returns:
            Tuple of (list of files, total count)
        """
        query = select(File).where(
            and_(
                File.project_id == project_id,
                File.scope == FileScope.PROJECT,
                File.is_deleted == False
            )
        )

        if folder_id is not None:
            query = query.where(File.folder_id == folder_id)

        if file_type:
            # Map file type to MIME prefix
            mime_prefix = self._get_mime_prefix(file_type)
            query = query.where(File.mime_type.like(f"{mime_prefix}%"))

        # Get total count
        count_query = select(func.count()).select_from(File).where(
            and_(
                File.project_id == project_id,
                File.scope == FileScope.PROJECT,
                File.is_deleted == False
            )
        )
        if folder_id is not None:
            count_query = count_query.where(File.folder_id == folder_id)
        if file_type:
            mime_prefix = self._get_mime_prefix(file_type)
            count_query = count_query.where(File.mime_type.like(f"{mime_prefix}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Execute query
        query = query.order_by(File.uploaded_at.desc())
        result = await self.db.execute(query)
        files = result.scalars().all()

        return list(files), total

    async def list_shared_files(
        self,
        folder_id: Optional[int] = None,
        file_type: Optional[str] = None
    ) -> tuple[list[File], int]:
        """
        List shared library files with optional filtering.

        Args:
            folder_id: Filter by folder (None = all folders)
            file_type: Filter by MIME type prefix

        Returns:
            Tuple of (list of files, total count)
        """
        query = select(File).where(
            and_(
                File.scope == FileScope.SHARED,
                File.is_deleted == False
            )
        )

        if folder_id is not None:
            query = query.where(File.folder_id == folder_id)

        if file_type:
            mime_prefix = self._get_mime_prefix(file_type)
            query = query.where(File.mime_type.like(f"{mime_prefix}%"))

        # Get total count
        count_query = select(func.count()).select_from(File).where(
            and_(
                File.scope == FileScope.SHARED,
                File.is_deleted == False
            )
        )
        if folder_id is not None:
            count_query = count_query.where(File.folder_id == folder_id)
        if file_type:
            mime_prefix = self._get_mime_prefix(file_type)
            count_query = count_query.where(File.mime_type.like(f"{mime_prefix}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Execute query
        query = query.order_by(File.uploaded_at.desc())
        result = await self.db.execute(query)
        files = result.scalars().all()

        return list(files), total

    async def update_file(self, file_id: int, data: dict) -> Optional[File]:
        """
        Update file metadata (rename, move).

        Args:
            file_id: File ID
            data: Update data

        Returns:
            Updated file if found, None otherwise
        """
        file_record = await self.get_file(file_id)
        if not file_record:
            return None

        for field, value in data.items():
            setattr(file_record, field, value)

        await self.db.flush()
        await self.db.refresh(file_record)
        return file_record

    async def soft_delete_file(self, file_id: int) -> Optional[File]:
        """
        Soft-delete a file (sets is_deleted flag).

        Args:
            file_id: File ID

        Returns:
            Deleted file if found, None otherwise
        """
        file_record = await self.get_file(file_id)
        if not file_record:
            return None

        file_record.is_deleted = True
        file_record.deleted_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(file_record)
        return file_record

    async def create_override(
        self,
        shared_file_id: int,
        project_id: int,
        new_file_data: dict
    ) -> File:
        """
        Create a project-specific override of a shared file.

        Args:
            shared_file_id: ID of shared file being overridden
            project_id: Project ID for the override
            new_file_data: Data for the new file

        Returns:
            Created override file
        """
        new_file_data['overrides_file_id'] = shared_file_id
        new_file_data['project_id'] = project_id
        new_file_data['scope'] = FileScope.PROJECT

        return await self.create_file(new_file_data)

    async def search_files(
        self,
        project_id: Optional[int],
        query: str,
        file_type: Optional[str] = None
    ) -> list[File]:
        """
        Search files by filename.

        Args:
            project_id: Project ID (None for shared library)
            query: Search query (partial filename match)
            file_type: Filter by MIME type prefix

        Returns:
            List of matching files
        """
        filters = [File.is_deleted == False]

        if project_id is not None:
            filters.append(File.project_id == project_id)
            filters.append(File.scope == FileScope.PROJECT)
        else:
            filters.append(File.scope == FileScope.SHARED)

        # Search in both original and safe filename
        search_filter = or_(
            File.original_filename.ilike(f"%{query}%"),
            File.safe_filename.ilike(f"%{query}%")
        )
        filters.append(search_filter)

        if file_type:
            mime_prefix = self._get_mime_prefix(file_type)
            filters.append(File.mime_type.like(f"{mime_prefix}%"))

        result = await self.db.execute(
            select(File).where(and_(*filters)).order_by(File.uploaded_at.desc())
        )
        return list(result.scalars().all())

    def _get_mime_prefix(self, file_type: str) -> str:
        """Map file type filter to MIME type prefix."""
        type_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats',
            'doc': 'application/msword',
            'image': 'image/',
        }
        return type_map.get(file_type.lower(), file_type)


class FolderService:
    """Service for managing folder operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_folder(
        self,
        project_id: Optional[int],
        scope: FileScope,
        name: str,
        parent_id: Optional[int] = None
    ) -> Folder:
        """
        Create a new folder.

        Args:
            project_id: Project ID (None for shared)
            scope: Folder scope
            name: Folder name
            parent_id: Parent folder ID (None for root)

        Returns:
            Created folder
        """
        folder = Folder(
            name=name,
            project_id=project_id,
            scope=scope,
            parent_id=parent_id
        )
        self.db.add(folder)
        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def list_folders(
        self,
        project_id: Optional[int],
        scope: FileScope
    ) -> list[Folder]:
        """
        List folders for project or shared library.

        Args:
            project_id: Project ID (None for shared)
            scope: Folder scope

        Returns:
            List of folders
        """
        query = select(Folder).where(Folder.scope == scope)

        if project_id is not None:
            query = query.where(Folder.project_id == project_id)
        else:
            query = query.where(Folder.project_id.is_(None))

        query = query.order_by(Folder.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_folder(self, folder_id: int, name: str) -> Optional[Folder]:
        """
        Update folder name.

        Args:
            folder_id: Folder ID
            name: New folder name

        Returns:
            Updated folder if found, None otherwise
        """
        result = await self.db.execute(
            select(Folder).where(Folder.id == folder_id)
        )
        folder = result.scalar_one_or_none()

        if not folder:
            return None

        folder.name = name
        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def delete_folder(self, folder_id: int) -> bool:
        """
        Delete folder (only if empty).

        Args:
            folder_id: Folder ID

        Returns:
            True if deleted, False if not found or not empty
        """
        result = await self.db.execute(
            select(Folder).where(Folder.id == folder_id)
        )
        folder = result.scalar_one_or_none()

        if not folder:
            return False

        # Check for files
        file_count = await self.db.execute(
            select(func.count()).select_from(File).where(File.folder_id == folder_id)
        )
        if file_count.scalar_one() > 0:
            return False

        # Check for subfolders
        subfolder_count = await self.db.execute(
            select(func.count()).select_from(Folder).where(Folder.parent_id == folder_id)
        )
        if subfolder_count.scalar_one() > 0:
            return False

        await self.db.delete(folder)
        await self.db.flush()
        return True

    async def create_default_folders(self, project_id: int, project_type: str) -> list[Folder]:
        """
        Create default folders for a project based on its type.

        Idempotent - skips folders that already exist.

        Args:
            project_id: Project ID
            project_type: Project type (A, B, C, D)

        Returns:
            List of created folders
        """
        folder_names = DEFAULT_PROJECT_FOLDERS.get(project_type, [])
        created_folders = []

        for name in folder_names:
            # Check if folder already exists
            existing = await self.db.execute(
                select(Folder).where(
                    and_(
                        Folder.project_id == project_id,
                        Folder.scope == FileScope.PROJECT,
                        Folder.name == name,
                        Folder.parent_id.is_(None)
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            folder = await self.create_folder(
                project_id=project_id,
                scope=FileScope.PROJECT,
                name=name,
                parent_id=None
            )
            created_folders.append(folder)

        return created_folders

    async def create_default_shared_folders(self) -> list[Folder]:
        """
        Create default shared library folders.

        Idempotent - skips folders that already exist.

        Returns:
            List of created folders
        """
        created_folders = []

        for name in DEFAULT_SHARED_FOLDERS:
            # Check if folder already exists
            existing = await self.db.execute(
                select(Folder).where(
                    and_(
                        Folder.scope == FileScope.SHARED,
                        Folder.name == name,
                        Folder.parent_id.is_(None),
                        Folder.project_id.is_(None)
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue

            folder = await self.create_folder(
                project_id=None,
                scope=FileScope.SHARED,
                name=name,
                parent_id=None
            )
            created_folders.append(folder)

        return created_folders
