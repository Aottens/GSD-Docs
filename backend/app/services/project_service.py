"""Project service for business logic."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.file_service import FolderService


class ProjectService:
    """Service for managing project operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project.

        Args:
            data: Project creation data

        Returns:
            Created project with all fields populated
        """
        project = Project(
            name=data.name,
            description=data.description,
            type=data.type,
            language=data.language,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)

        # Create default folders for the project
        folder_service = FolderService(self.db)
        await folder_service.create_default_folders(project.id, data.type.value)

        return project

    async def get_project(self, project_id: int) -> Optional[Project]:
        """
        Get a single project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project if found, None otherwise
        """
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_projects(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Project], int]:
        """
        List projects with filtering, sorting, and pagination.

        Args:
            status: Filter by status (active, completed, archived)
            search: Search in project name (case-insensitive)
            sort_by: Field to sort by (updated_at, name, type, created_at)
            sort_order: Sort direction (asc, desc)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of projects, total count)
        """
        # Base query
        query = select(Project)
        count_query = select(func.count()).select_from(Project)

        # Apply filters
        if status:
            query = query.where(Project.status == status)
            count_query = count_query.where(Project.status == status)

        if search:
            search_filter = Project.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting
        sort_column = getattr(Project, sort_by, Project.updated_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await self.db.execute(query)
        projects = result.scalars().all()

        return list(projects), total

    async def update_project(
        self, project_id: int, data: ProjectUpdate
    ) -> Optional[Project]:
        """
        Update a project with partial data.

        Args:
            project_id: Project ID
            data: Update data (only provided fields are updated)

        Returns:
            Updated project if found, None otherwise
        """
        project = await self.get_project(project_id)
        if not project:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def update_last_accessed(self, project_id: int) -> Optional[Project]:
        """
        Update the last_accessed_at timestamp for a project.

        Args:
            project_id: Project ID

        Returns:
            Updated project if found, None otherwise
        """
        project = await self.get_project(project_id)
        if project:
            project.last_accessed_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(project)
            return project
        return None

    async def get_recent_projects(self, limit: int = 4) -> list[Project]:
        """
        Get recently accessed projects.

        Args:
            limit: Maximum number of projects to return

        Returns:
            List of recently accessed projects
        """
        query = (
            select(Project)
            .where(Project.last_accessed_at.is_not(None))
            .order_by(Project.last_accessed_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
