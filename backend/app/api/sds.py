"""SDS scaffolding API endpoints.

Provides:
  POST /api/projects/{project_id}/sds/scaffold  — trigger SDS matching
  GET  /api/projects/{project_id}/sds/results   — read last results
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.project import Project
from app.schemas.sds import SdsResultsResponse
from app.services.sds_service import scaffold_sds
from app.config import get_settings


router = APIRouter(prefix="/api/projects/{project_id}/sds", tags=["sds"])


def _get_project_dir(project_id: int) -> Path:
    """Get the project directory path from PROJECT_ROOT setting."""
    settings = get_settings()
    return Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)


@router.post("/scaffold", response_model=SdsResultsResponse)
async def trigger_sds_scaffold(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> SdsResultsResponse:
    """Trigger SDS scaffolding for a project.

    Loads equipment modules from project phases, matches against CATALOG.json
    typicals with weighted confidence scoring, and persists results to
    project_dir/output/sds-results.json.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    settings = get_settings()
    project_dir = _get_project_dir(project_id)
    v1_docs_path = Path(settings.V1_DOCS_PATH).expanduser().resolve()

    raw = await scaffold_sds(project_dir, v1_docs_path)

    # Inject the real project_id (scaffold_sds uses 0 as placeholder)
    raw["project_id"] = project_id

    return SdsResultsResponse(**raw)


@router.get("/results", response_model=SdsResultsResponse)
async def get_sds_results(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> SdsResultsResponse:
    """Return last SDS scaffolding results from filesystem.

    Returns empty response if scaffolding has not been run yet.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    sds_results_path = project_dir / "output" / "sds-results.json"

    if not sds_results_path.exists():
        return SdsResultsResponse(
            project_id=project_id,
            scaffold_date=None,
            total_modules=0,
            matched_count=0,
            low_confidence_count=0,
            unmatched_count=0,
            matches=[],
            catalog_found=False,
        )

    try:
        with open(sds_results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["project_id"] = project_id
        return SdsResultsResponse(**data)
    except (OSError, json.JSONDecodeError, Exception) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read SDS results: {e}"
        )
