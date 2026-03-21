"""Export API: SSE streaming assembly + DOCX export, version list, download."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_db
from app.models.project import Project
from app.config import get_settings
from app.schemas.export import (
    AssemblyReadinessSchema,
    ExportVersionListResponse,
    ExportVersionSchema,
    PandocStatusSchema,
)
from app.services.assembly_service import assemble_fds, check_assembly_readiness
from app.services.export_service import (
    detect_pandoc,
    export_to_docx,
    list_export_versions,
    render_diagrams,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["export"])

PIPELINE_STEPS = [
    "Cross-referenties oplossen",
    "Secties samenvoegen",
    "DOCX genereren",
    "Diagrammen renderen",
]
TOTAL_STEPS = len(PIPELINE_STEPS)


def _get_project_dir(project_id: int) -> Path:
    """Get the project directory path from PROJECT_ROOT setting."""
    settings = get_settings()
    return Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)


@router.get("/readiness", response_model=AssemblyReadinessSchema)
async def get_assembly_readiness(
    project_id: int,
    mode: str = Query(default="draft", description="Assembly mode: draft or final"),
    db: AsyncSession = Depends(get_db),
) -> AssemblyReadinessSchema:
    """Check whether the project is ready for FDS assembly in the requested mode."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    return await check_assembly_readiness(project_dir, mode)


@router.get("/pandoc-status", response_model=PandocStatusSchema)
async def get_pandoc_status(project_id: int) -> PandocStatusSchema:
    """Check if Pandoc is installed on the server."""
    found, version = detect_pandoc()
    return PandocStatusSchema(installed=found, version=version)


@router.get("/stream", response_class=EventSourceResponse)
async def stream_export(
    request: Request,
    project_id: int,
    mode: str = Query(default="draft", description="Assembly mode: draft or final"),
    language: str = Query(default="nl", description="Output language: nl or en"),
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    """SSE streaming endpoint for assembly + DOCX export pipeline.

    Streams named step events (step_start, step_done, complete, error, cancelled)
    as each pipeline stage progresses.
    """
    # Pre-flight: check Pandoc
    pandoc_found, _version = detect_pandoc()
    if not pandoc_found:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Pandoc niet gevonden",
                "fix_hint": "brew install pandoc",
            },
        )

    # Pre-flight: check readiness
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)

    if mode == "final":
        readiness = await check_assembly_readiness(project_dir, mode)
        if not readiness.ready:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Niet alle fases zijn beoordeeld",
                    "unreviewed_phases": readiness.unreviewed_phases,
                },
            )

    settings = get_settings()
    v1_docs_path = Path(settings.V1_DOCS_PATH).expanduser().resolve()

    # Capture step events from services for SSE replay
    step_events: list[tuple[str, int]] = []

    def _on_step(name: str, step_idx: int) -> None:
        step_events.append((name, step_idx))

    async def event_generator():
        current_step = 0
        current_step_name = ""
        artifact_filename: Optional[str] = None

        try:
            for step_idx, step_name in enumerate(PIPELINE_STEPS):
                # Check if client disconnected
                if await request.is_disconnected():
                    yield {
                        "event": "cancelled",
                        "data": json.dumps({}),
                    }
                    return

                current_step = step_idx
                current_step_name = step_name

                yield {
                    "event": "step_start",
                    "data": json.dumps({
                        "event": "step_start",
                        "step": step_idx,
                        "name": step_name,
                        "total_steps": TOTAL_STEPS,
                    }),
                }

                # Execute the pipeline step
                if step_idx == 0:
                    # Steps 0 + 1 are both handled by assemble_fds
                    assembled_path = await assemble_fds(
                        project_dir=project_dir,
                        language=language,
                        mode=mode,
                        v1_docs_path=v1_docs_path,
                        on_step=_on_step,
                    )
                    # Yield step_done for step 0 then immediately start/done step 1
                    yield {
                        "event": "step_done",
                        "data": json.dumps({"step": 0}),
                    }

                    if await request.is_disconnected():
                        yield {
                            "event": "cancelled",
                            "data": json.dumps({}),
                        }
                        return

                    yield {
                        "event": "step_start",
                        "data": json.dumps({
                            "event": "step_start",
                            "step": 1,
                            "name": PIPELINE_STEPS[1],
                            "total_steps": TOTAL_STEPS,
                        }),
                    }
                    yield {
                        "event": "step_done",
                        "data": json.dumps({"step": 1}),
                    }
                    # Skip to step 2 in the loop
                    continue

                elif step_idx == 1:
                    # Already handled above alongside step 0
                    continue

                elif step_idx == 2:
                    artifact_filename = await export_to_docx(
                        assembled_md=assembled_path,
                        project_dir=project_dir,
                        mode=mode,
                        language=language,
                        v1_docs_path=v1_docs_path,
                        on_step=_on_step,
                    )

                elif step_idx == 3:
                    await render_diagrams(
                        project_dir=project_dir,
                        on_step=_on_step,
                    )

                yield {
                    "event": "step_done",
                    "data": json.dumps({"step": step_idx}),
                }

            # All steps done — emit complete
            yield {
                "event": "complete",
                "data": json.dumps({
                    "event": "complete",
                    "step": TOTAL_STEPS - 1,
                    "name": "Voltooid",
                    "total_steps": TOTAL_STEPS,
                    "artifact_filename": artifact_filename,
                }),
            }

        except Exception as exc:
            logger.exception("Export pipeline error at step %d (%s)", current_step, current_step_name)
            yield {
                "event": "error",
                "data": json.dumps({
                    "event": "error",
                    "step": current_step,
                    "name": current_step_name,
                    "total_steps": TOTAL_STEPS,
                    "message": str(exc),
                }),
            }

    return EventSourceResponse(event_generator())


@router.get("/versions", response_model=ExportVersionListResponse)
async def list_versions(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> ExportVersionListResponse:
    """List all versioned DOCX export artifacts for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    raw_versions = list_export_versions(project_dir)

    versions = []
    for v in raw_versions:
        versions.append(
            ExportVersionSchema(
                filename=v["filename"],
                doc_type=v["doc_type"],
                mode=v["mode"],
                language=v["language"],
                version=v["version"],
                created_at=datetime.fromtimestamp(v["created_at"], tz=timezone.utc),
                size_bytes=v["size_bytes"],
                download_url=f"/api/projects/{project_id}/export/download/{v['filename']}",
            )
        )

    return ExportVersionListResponse(project_id=project_id, versions=versions)


@router.get("/download/{filename}")
async def download_artifact(
    project_id: int,
    filename: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download a specific DOCX export artifact.

    Path traversal is blocked: filenames containing '..' or '/' are rejected.
    """
    # Path traversal protection
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename: path traversal not allowed",
        )

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    file_path = project_dir / "output" / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Artifact '{filename}' not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
