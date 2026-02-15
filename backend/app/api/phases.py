"""Phase timeline API for status tracking."""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.schemas.phase import PhaseTimelineResponse, PhaseStatusResponse
from app.models.conversation import Conversation, ConversationStatus


router = APIRouter(prefix="/api/projects/{project_id}/phases", tags=["phases"])


@router.get("/", response_model=PhaseTimelineResponse)
async def get_phase_timeline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseTimelineResponse:
    """
    Get all phases with status for a project.

    Phase status is DERIVED from filesystem artifacts (per CONTEXT.md decision):
    - Check for {phase_dir}/{NN}-CONTEXT.md -> "discussed"
    - Check for {phase_dir}/{NN}-*-PLAN.md -> "planned"
    - Check for {phase_dir}/{NN}-*-SUMMARY.md (content plans) -> "written"
    - Check for {phase_dir}/{NN}-VERIFICATION.md -> "verified"
    - Check for {phase_dir}/{NN}-REVIEW.md -> "reviewed"

    Available actions derived from status:
    - not_started: ["discuss"]
    - discussed: ["plan", "discuss"] (discuss = update)
    - planned: ["write"]
    - written: ["verify"]
    - verified: ["review"]
    - reviewed: [] (phase complete)

    Also queries conversations table for active conversation_id per phase.

    NOTE: Parses ROADMAP.md at project root to get phase names/goals.
    For v2.0, the ROADMAP.md structure follows project type templates from v1.0.

    Args:
        project_id: Project ID
        db: Database session

    Returns:
        Phase timeline with all phases and their statuses
    """
    # TODO: Get project directory from database
    project_dir = Path(f"projects/{project_id}")
    roadmap_path = project_dir / ".planning" / "ROADMAP.md"

    # Parse ROADMAP.md for phases
    phases_data = _parse_roadmap(roadmap_path) if roadmap_path.exists() else []

    # Query active conversations
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.status == ConversationStatus.active.value)
    )
    conversations = {conv.phase_number: conv.id for conv in result.scalars().all()}

    # Build phase statuses
    phases = []
    for phase_data in phases_data:
        phase_number = phase_data["number"]
        phase_name = phase_data["name"]
        phase_goal = phase_data["goal"]

        # Derive status from filesystem
        status_info = _derive_phase_status(project_dir, phase_number)

        phase_status = PhaseStatusResponse(
            number=phase_number,
            name=phase_name,
            goal=phase_goal,
            status=status_info["status"],
            sub_status=status_info["sub_status"],
            available_actions=status_info["available_actions"],
            has_context=status_info["has_context"],
            has_plans=status_info["has_plans"],
            has_content=status_info["has_content"],
            has_verification=status_info["has_verification"],
            has_review=status_info["has_review"],
            conversation_id=conversations.get(phase_number),
        )
        phases.append(phase_status)

    return PhaseTimelineResponse(
        project_id=project_id,
        phases=phases
    )


@router.get("/{phase_number}", response_model=PhaseStatusResponse)
async def get_phase_status(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseStatusResponse:
    """
    Get detailed status for a single phase.

    Args:
        project_id: Project ID
        phase_number: Phase number
        db: Database session

    Returns:
        Phase status details
    """
    # TODO: Get project directory from database
    project_dir = Path(f"projects/{project_id}")
    roadmap_path = project_dir / ".planning" / "ROADMAP.md"

    # Parse ROADMAP.md for phase info
    phases_data = _parse_roadmap(roadmap_path) if roadmap_path.exists() else []
    phase_data = next(
        (p for p in phases_data if p["number"] == phase_number),
        None
    )

    if not phase_data:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found in ROADMAP.md")

    # Query active conversation
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.phase_number == phase_number)
        .where(Conversation.status == ConversationStatus.active.value)
    )
    conversation = result.scalar_one_or_none()

    # Derive status from filesystem
    status_info = _derive_phase_status(project_dir, phase_number)

    return PhaseStatusResponse(
        number=phase_number,
        name=phase_data["name"],
        goal=phase_data["goal"],
        status=status_info["status"],
        sub_status=status_info["sub_status"],
        available_actions=status_info["available_actions"],
        has_context=status_info["has_context"],
        has_plans=status_info["has_plans"],
        has_content=status_info["has_content"],
        has_verification=status_info["has_verification"],
        has_review=status_info["has_review"],
        conversation_id=conversation.id if conversation else None,
    )


def _parse_roadmap(roadmap_path: Path) -> list[dict]:
    """
    Parse ROADMAP.md to extract phase information.

    Args:
        roadmap_path: Path to ROADMAP.md

    Returns:
        List of phase dictionaries with number, name, and goal
    """
    # TODO: Implement robust ROADMAP.md parsing
    # For now, return placeholder
    return [
        {"number": 1, "name": "foundation", "goal": "Foundation phase"},
        {"number": 2, "name": "architecture", "goal": "System architecture"},
    ]


def _derive_phase_status(project_dir: Path, phase_number: int) -> dict:
    """
    Derive phase status from filesystem artifacts.

    Checks for existence of:
    - CONTEXT.md
    - PLAN.md files
    - SUMMARY.md files (content plans)
    - VERIFICATION.md
    - REVIEW.md

    Args:
        project_dir: Project directory path
        phase_number: Phase number

    Returns:
        Dictionary with status fields
    """
    phase_pattern = f"{phase_number:02d}-*"
    planning_dir = project_dir / ".planning" / "phases"

    # Find phase directory
    phase_dirs = list(planning_dir.glob(phase_pattern))
    if not phase_dirs:
        return {
            "status": "not_started",
            "sub_status": None,
            "available_actions": ["discuss"],
            "has_context": False,
            "has_plans": False,
            "has_content": False,
            "has_verification": False,
            "has_review": False,
        }

    phase_dir = phase_dirs[0]

    # Check for artifacts
    has_context = any(phase_dir.glob(f"{phase_number:02d}-CONTEXT.md"))
    has_plans = any(phase_dir.glob(f"{phase_number:02d}-*-PLAN.md"))
    has_content = any(phase_dir.glob(f"{phase_number:02d}-*-SUMMARY.md"))
    has_verification = any(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
    has_review = any(phase_dir.glob(f"{phase_number:02d}-REVIEW.md"))

    # Derive status
    if has_review:
        status = "reviewed"
        sub_status = "Beoordeeld"
        actions = []
    elif has_verification:
        status = "verified"
        sub_status = "Geverifieerd"
        actions = ["review"]
    elif has_content:
        status = "written"
        sub_status = "Geschreven"
        actions = ["verify"]
    elif has_plans:
        status = "planned"
        sub_status = "Gepland"
        actions = ["write"]
    elif has_context:
        status = "discussed"
        sub_status = "Besproken"
        actions = ["plan", "discuss"]
    else:
        status = "not_started"
        sub_status = None
        actions = ["discuss"]

    return {
        "status": status,
        "sub_status": sub_status,
        "available_actions": actions,
        "has_context": has_context,
        "has_plans": has_plans,
        "has_content": has_content,
        "has_verification": has_verification,
        "has_review": has_review,
    }
