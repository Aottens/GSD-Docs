"""Phase timeline API for status tracking."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.schemas.phase import PhaseTimelineResponse, PhaseStatusResponse
from app.models.conversation import Conversation, ConversationStatus
from app.models.project import Project
from app.prompts.discuss_phase import PROJECT_TYPE_PHASES


router = APIRouter(prefix="/api/projects/{project_id}/phases", tags=["phases"])


def _get_phases_for_project_type(project_type: str) -> list[dict]:
    """Get phase definitions for a project type from v1.0 extracted data."""
    phases = PROJECT_TYPE_PHASES.get(project_type, [])
    return [
        {"number": p["number"], "name": p["name"], "goal": p["description"]}
        for p in phases
    ]


@router.get("/", response_model=PhaseTimelineResponse)
async def get_phase_timeline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseTimelineResponse:
    """Get all phases with status for a project.

    Phase list comes from project type (A/B/C/D) definitions.
    Status is derived from conversation records in the database.
    """
    # Get project from database
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Get phases for this project type
    phases_data = _get_phases_for_project_type(project.type.value)

    # Query active conversations
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.status == ConversationStatus.active.value)
    )
    active_conversations = {conv.phase_number: conv.id for conv in result.scalars().all()}

    # Query completed conversations (for discussed status)
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.status == ConversationStatus.completed.value)
    )
    completed_conversations = {conv.phase_number for conv in result.scalars().all()}

    # Build phase statuses with dependency chain enforcement
    phases = []
    for i, phase_data in enumerate(phases_data):
        phase_number = phase_data["number"]

        # Check if previous phase is completed (dependency chain)
        previous_completed = True
        if i > 0:
            prev_number = phases_data[i - 1]["number"]
            previous_completed = prev_number in completed_conversations

        # Derive status from conversation records
        if phase_number in completed_conversations:
            status = "discussed"
            sub_status = "Besproken"
            actions = ["plan", "discuss"]
        elif phase_number in active_conversations:
            status = "discussing"
            sub_status = "In bespreking"
            actions = ["discuss"]
        elif previous_completed:
            status = "not_started"
            sub_status = None
            actions = ["discuss"]
        else:
            # Locked — previous phase not completed
            status = "not_started"
            sub_status = None
            actions = []

        phase_status = PhaseStatusResponse(
            number=phase_number,
            name=phase_data["name"],
            goal=phase_data["goal"],
            status=status,
            sub_status=sub_status,
            available_actions=actions,
            has_context=phase_number in completed_conversations,
            has_plans=False,
            has_content=False,
            has_verification=False,
            has_review=False,
            conversation_id=active_conversations.get(phase_number),
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
    """Get detailed status for a single phase."""
    # Get project from database
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Get phases for this project type
    phases_data = _get_phases_for_project_type(project.type.value)
    phase_data = next(
        (p for p in phases_data if p["number"] == phase_number),
        None
    )

    if not phase_data:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found for project type {project.type.value}")

    # Query conversations for this phase
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.phase_number == phase_number)
    )
    conversations = result.scalars().all()
    active = next((c for c in conversations if c.status == ConversationStatus.active.value), None)
    completed = any(c.status == ConversationStatus.completed.value for c in conversations)

    if completed:
        status = "discussed"
        sub_status = "Besproken"
        actions = ["plan", "discuss"]
    elif active:
        status = "discussing"
        sub_status = "In bespreking"
        actions = ["discuss"]
    else:
        status = "not_started"
        sub_status = None
        actions = ["discuss"]

    return PhaseStatusResponse(
        number=phase_number,
        name=phase_data["name"],
        goal=phase_data["goal"],
        status=status,
        sub_status=sub_status,
        available_actions=actions,
        has_context=completed,
        has_plans=False,
        has_content=False,
        has_verification=False,
        has_review=False,
        conversation_id=active.id if active else None,
    )


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
