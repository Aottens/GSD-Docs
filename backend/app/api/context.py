"""Context API for CONTEXT.md generation and retrieval."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.conversation import Conversation


router = APIRouter(prefix="/api/projects/{project_id}/context", tags=["context"])


@router.post("/{phase_number}")
async def generate_context(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate CONTEXT.md from a completed discussion.

    Args:
        project_id: Project ID
        phase_number: Phase number
        db: Database session

    Returns:
        Generated CONTEXT.md content and file path
    """
    # Find the most recent completed conversation for this phase
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .where(Conversation.phase_number == phase_number)
        .order_by(Conversation.updated_at.desc())
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"No conversation found for phase {phase_number}"
        )

    # Generate CONTEXT.md
    from app.services.context_generator import ContextGenerator

    # TODO: Get project type from database
    project_type = "B"  # Placeholder

    generator = ContextGenerator()
    content = generator.generate(conversation, project_type)
    file_path = generator.save(project_id, phase_number, content)

    return {
        "success": True,
        "message": "CONTEXT.md generated",
        "content": content,
        "file_path": file_path,
    }


@router.get("/{phase_number}")
async def get_context(
    project_id: int,
    phase_number: int
):
    """
    Get existing CONTEXT.md content for a phase.

    Args:
        project_id: Project ID
        phase_number: Phase number

    Returns:
        CONTEXT.md content
    """
    # TODO: Get project directory from database
    project_dir = Path(f"projects/{project_id}")
    phase_pattern = f"{phase_number:02d}-*"
    planning_dir = project_dir / ".planning" / "phases"

    # Find phase directory
    phase_dirs = list(planning_dir.glob(phase_pattern))
    if not phase_dirs:
        raise HTTPException(
            status_code=404,
            detail=f"Phase {phase_number} directory not found"
        )

    phase_dir = phase_dirs[0]
    context_path = phase_dir / f"{phase_number:02d}-CONTEXT.md"

    if not context_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"CONTEXT.md not found for phase {phase_number}"
        )

    content = context_path.read_text(encoding="utf-8")

    return {
        "success": True,
        "content": content,
        "file_path": str(context_path),
    }
