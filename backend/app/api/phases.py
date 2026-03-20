"""Phase timeline API with filesystem-based status detection."""

import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.schemas.phase import PhaseTimelineResponse, PhaseStatusResponse, ContextFilesResponse
from app.models.project import Project
from app.config import get_settings
from app.config_phases import PROJECT_TYPE_PHASES, get_cli_command


router = APIRouter(prefix="/api/projects/{project_id}/phases", tags=["phases"])


def _get_phases_for_project_type(project_type: str) -> list[dict]:
    """Get phase definitions for a project type from v1.0 extracted data."""
    phases = PROJECT_TYPE_PHASES.get(project_type, [])
    return [
        {"number": p["number"], "name": p["name"], "goal": p["description"]}
        for p in phases
    ]


def _derive_phase_status(project_dir: Path, phase_number: int) -> dict:
    """
    Derive phase status from filesystem artifacts.
    Checks for: CONTEXT.md, PLAN.md, SUMMARY.md (content), VERIFICATION.md, REVIEW.md
    """
    phase_pattern = f"{phase_number:02d}-*"
    planning_dir = project_dir / ".planning" / "phases"

    phase_dirs = list(planning_dir.glob(phase_pattern)) if planning_dir.exists() else []
    if not phase_dirs:
        return {
            "status": "not_started",
            "sub_status": None,
            "has_context": False,
            "has_plans": False,
            "has_content": False,
            "has_verification": False,
            "has_review": False,
        }

    phase_dir = phase_dirs[0]
    has_context = any(phase_dir.glob(f"{phase_number:02d}-CONTEXT.md"))
    has_plans = any(phase_dir.glob(f"{phase_number:02d}-*-PLAN.md"))
    has_content = any(phase_dir.glob(f"{phase_number:02d}-*-SUMMARY.md"))
    has_verification = any(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
    has_review = any(phase_dir.glob(f"{phase_number:02d}-REVIEW.md"))

    if has_review:
        status, sub_status = "reviewed", "Beoordeeld"
    elif has_verification:
        status, sub_status = "verified", "Geverifieerd"
    elif has_content:
        status, sub_status = "written", "Geschreven"
    elif has_plans:
        status, sub_status = "planned", "Gepland"
    elif has_context:
        status, sub_status = "discussed", "Besproken"
    else:
        status, sub_status = "not_started", None

    return {
        "status": status,
        "sub_status": sub_status,
        "has_context": has_context,
        "has_plans": has_plans,
        "has_content": has_content,
        "has_verification": has_verification,
        "has_review": has_review,
    }


def _extract_decisions(content: str) -> list[str]:
    """Extract bullet decisions from <decisions> XML section of CONTEXT.md."""
    match = re.search(r'<decisions>(.*?)</decisions>', content, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    decisions = re.findall(r'^[-*]\s+(.+)', block, re.MULTILINE)
    return [d.strip() for d in decisions if d.strip()]


def _extract_verification_summary(content: str) -> dict:
    """Extract score and gap count from VERIFICATION.md."""
    score_match = re.search(r'(\d+)/(\d+)\s+levels?\s+passed', content, re.IGNORECASE)
    gap_matches = re.findall(r'\|\s*(CRITICAL|MAJOR|MINOR)\s*\|', content, re.IGNORECASE)
    score = f"{score_match.group(1)}/{score_match.group(2)}" if score_match else None
    severity = {
        "critical": sum(1 for g in gap_matches if g.upper() == "CRITICAL"),
        "major": sum(1 for g in gap_matches if g.upper() == "MAJOR"),
        "minor": sum(1 for g in gap_matches if g.upper() == "MINOR"),
    }
    return {
        "score": score,
        "gap_count": len(gap_matches),
        "severity": severity,
    }


def _get_project_dir(project_id: int) -> Path:
    """Get the project directory path from PROJECT_ROOT setting."""
    settings = get_settings()
    return Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)


@router.get("/", response_model=PhaseTimelineResponse)
async def get_phase_timeline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseTimelineResponse:
    """Get all phases with filesystem-derived status for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    phases_data = _get_phases_for_project_type(project.type.value)
    project_dir = _get_project_dir(project_id)

    phases = []
    for phase_data in phases_data:
        phase_number = phase_data["number"]
        status_info = _derive_phase_status(project_dir, phase_number)
        cli_command = get_cli_command(status_info["status"], phase_number)

        phases.append(PhaseStatusResponse(
            number=phase_number,
            name=phase_data["name"],
            goal=phase_data["goal"],
            cli_command=cli_command,
            **status_info,
        ))

    return PhaseTimelineResponse(project_id=project_id, phases=phases)


@router.get("/{phase_number}/context-files", response_model=ContextFilesResponse)
async def get_phase_context_files(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
) -> ContextFilesResponse:
    """Read CONTEXT.md and VERIFICATION.md from project filesystem."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    planning_dir = project_dir / ".planning" / "phases"
    phase_dirs = list(planning_dir.glob(f"{phase_number:02d}-*")) if planning_dir.exists() else []

    decisions: list[str] = []
    verification_score: Optional[str] = None
    verification_gaps: Optional[int] = None
    verification_severity: Optional[dict] = None
    has_context = False
    has_verification = False

    if phase_dirs:
        phase_dir = phase_dirs[0]

        # Read CONTEXT.md
        context_files = list(phase_dir.glob(f"{phase_number:02d}-CONTEXT.md"))
        if context_files:
            try:
                content = context_files[0].read_text(encoding="utf-8")
                decisions = _extract_decisions(content)
                has_context = True
            except (OSError, UnicodeDecodeError):
                pass

        # Read VERIFICATION.md
        verification_files = list(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
        if verification_files:
            try:
                content = verification_files[0].read_text(encoding="utf-8")
                summary = _extract_verification_summary(content)
                verification_score = summary["score"]
                verification_gaps = summary["gap_count"]
                verification_severity = summary["severity"]
                has_verification = True
            except (OSError, UnicodeDecodeError):
                pass

    return ContextFilesResponse(
        decisions=decisions,
        verification_score=verification_score,
        verification_gaps=verification_gaps,
        verification_severity=verification_severity,
        has_context=has_context,
        has_verification=has_verification,
    )


@router.get("/{phase_number}", response_model=PhaseStatusResponse)
async def get_phase_status(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseStatusResponse:
    """Get detailed status for a single phase."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    phases_data = _get_phases_for_project_type(project.type.value)
    phase_data = next(
        (p for p in phases_data if p["number"] == phase_number), None
    )
    if not phase_data:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found for project type {project.type.value}")

    project_dir = _get_project_dir(project_id)
    status_info = _derive_phase_status(project_dir, phase_number)
    cli_command = get_cli_command(status_info["status"], phase_number)

    return PhaseStatusResponse(
        number=phase_number,
        name=phase_data["name"],
        goal=phase_data["goal"],
        cli_command=cli_command,
        **status_info,
    )
