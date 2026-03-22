"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base, async_session_maker
from app.api import health, projects, files, folders, phases, documents, export, sds
from app.services.file_storage import ensure_upload_dir
from app.services.file_service import FolderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Creates database tables on startup and cleans up on shutdown.
    """
    settings = get_settings()

    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure upload directory exists
    await ensure_upload_dir(settings)

    # Create default shared library folders
    async with async_session_maker() as db:
        try:
            folder_service = FolderService(db)
            await folder_service.create_default_shared_folders()
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    yield

    # Shutdown: dispose engine
    await engine.dispose()


# Create FastAPI application
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware - must be added FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(projects.doc_types_router)
app.include_router(files.router)
app.include_router(folders.router)
app.include_router(phases.router)
app.include_router(documents.router)
app.include_router(export.router)
app.include_router(sds.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
