"""Discussion API with SSE streaming for chat interface."""

import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sse_starlette.sse import EventSourceResponse

from app.dependencies import get_db
from app.config import get_settings
from app.schemas.conversation import (
    ConversationResponse,
    ConversationListResponse,
    MessageResponse,
    SendMessageRequest,
)
from app.models.conversation import Conversation, Message, ConversationStatus
from app.services.discussion_engine import DiscussionEngine
from app.services.llm_service import get_llm_provider


router = APIRouter(prefix="/api/projects/{project_id}/discussions", tags=["discussions"])


@router.post("/", response_model=ConversationResponse)
async def start_discussion(
    project_id: int,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db)
) -> ConversationResponse:
    """Start a new discussion for a phase.

    Creates conversation and returns initial state with topic selection.
    """
    phase_number = body.get("phase_number")
    if phase_number is None:
        raise HTTPException(status_code=400, detail="phase_number is required")

    settings = get_settings()
    llm = get_llm_provider()
    engine = DiscussionEngine(db, llm, settings)

    conversation = await engine.start_discussion(project_id, phase_number)

    # Count messages
    result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation.id)
    )
    message_count = result.scalar() or 0

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        phase_number=conversation.phase_number,
        status=conversation.status,
        title=conversation.title,
        summary_data=conversation.summary_data,
        parent_id=conversation.parent_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=message_count,
    )


@router.get("/", response_model=ConversationListResponse)
async def list_discussions(
    project_id: int,
    phase_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> ConversationListResponse:
    """
    List all discussions for a project, optionally filtered by phase.

    Args:
        project_id: Project ID
        phase_number: Optional phase number filter
        db: Database session

    Returns:
        List of conversations
    """
    query = select(Conversation).where(Conversation.project_id == project_id)

    if phase_number is not None:
        query = query.where(Conversation.phase_number == phase_number)

    query = query.order_by(Conversation.created_at.desc())

    result = await db.execute(query)
    conversations = result.scalars().all()

    # Build response with message counts
    conversation_responses = []
    for conv in conversations:
        msg_result = await db.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conv.id)
        )
        message_count = msg_result.scalar() or 0

        conversation_responses.append(
            ConversationResponse(
                id=conv.id,
                project_id=conv.project_id,
                phase_number=conv.phase_number,
                status=conv.status,
                title=conv.title,
                summary_data=conv.summary_data,
                parent_id=conv.parent_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count,
            )
        )

    return ConversationListResponse(
        conversations=conversation_responses,
        total=len(conversation_responses)
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_discussion(
    project_id: int,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
) -> ConversationResponse:
    """
    Get a single discussion with summary.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation details
    """
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Count messages
    msg_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation.id)
    )
    message_count = msg_result.scalar() or 0

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        phase_number=conversation.phase_number,
        status=conversation.status,
        title=conversation.title,
        summary_data=conversation.summary_data,
        parent_id=conversation.parent_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=message_count,
    )


@router.get("/{conversation_id}/messages")
async def get_messages(
    project_id: int,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> list[MessageResponse]:
    """
    Get messages for a conversation (paginated).

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        skip: Number of messages to skip
        limit: Maximum number of messages to return
        db: Database session

    Returns:
        List of messages
    """
    # Verify conversation exists and belongs to project
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            message_type=msg.message_type,
            metadata_json=msg.metadata_json,
            timestamp=msg.timestamp,
        )
        for msg in messages
    ]


@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    project_id: int,
    conversation_id: int,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and stream AI response via SSE.

    Uses EventSourceResponse from sse-starlette.
    Events: message_delta, message_complete, question_card, decision_captured,
            topic_boundary, check_in, completion_signal, error, done.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        request: Message content and optional attachments
        db: Database session

    Returns:
        EventSourceResponse with SSE stream
    """
    # Verify conversation exists and belongs to project
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.status != ConversationStatus.active.value:
        raise HTTPException(status_code=400, detail="Conversation is not active")

    # Create discussion engine
    settings = get_settings()
    llm = get_llm_provider()
    engine = DiscussionEngine(db, llm, settings)

    # Stream events
    async def event_generator():
        try:
            async for event in engine.send_message(
                conversation_id, request.content, request.attachments
            ):
                # Format as SSE — frontend expects {"event": ..., "data": {...}} in data field
                yield {
                    "data": json.dumps(event),
                }
        except Exception as e:
            yield {
                "data": json.dumps({"event": "error", "data": {"error": str(e)}}),
            }

    return EventSourceResponse(event_generator())


@router.patch("/{conversation_id}/decisions/{decision_index}")
async def update_decision(
    project_id: int,
    conversation_id: int,
    decision_index: int,
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a decision in the running summary.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        decision_index: Index of decision to update
        body: Request body with new_value
        db: Database session

    Returns:
        Success response
    """
    # Verify conversation exists and belongs to project
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    new_value = body.get("new_value")
    if not new_value:
        raise HTTPException(status_code=400, detail="new_value is required")

    # Create discussion engine and update
    settings = get_settings()
    llm = get_llm_provider()
    engine = DiscussionEngine(db, llm, settings)

    await engine.update_decision(conversation_id, decision_index, new_value)

    return {"success": True, "message": "Decision updated"}


@router.post("/{conversation_id}/preview-context")
async def preview_context(
    project_id: int,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate CONTEXT.md preview from current conversation decisions.

    Returns content without saving to disk or changing conversation status.
    Used by frontend to show engineer what CONTEXT.md will contain before finalizing.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        db: Database session

    Returns:
        {
            "content": str,
            "line_count": int,
            "decisions_count": int,
            "unconfirmed_count": int
        }
    """
    from app.services.context_generator import ContextGenerator
    from app.models.project import Project

    # Verify conversation exists and belongs to project
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load project to get type
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Generate preview
    generator = ContextGenerator()
    content = generator.generate_preview(
        conversation.summary_data or {},
        project.type.value
    )

    # Count decisions
    decisions = conversation.summary_data.get("decisions", [])
    confirmed_count = sum(1 for d in decisions if isinstance(d, dict) and d.get("confirmed", False))
    unconfirmed_count = sum(1 for d in decisions if isinstance(d, dict) and not d.get("confirmed", False))

    return {
        "content": content,
        "line_count": len(content.split("\n")),
        "decisions_count": confirmed_count,
        "unconfirmed_count": unconfirmed_count,
    }


@router.post("/{conversation_id}/finalize")
async def finalize_discussion(
    project_id: int,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Finalize discussion: generate and save CONTEXT.md, mark conversation completed.

    Steps:
    1. Validate all decisions are confirmed (or warn about unconfirmed)
    2. Generate final CONTEXT.md via context_generator
    3. Save CONTEXT.md to project's phase directory
    4. Mark conversation as completed (status = "completed")
    5. Return next step guidance (suggests planning, does NOT auto-advance)

    Per user decision: "suggest next workflow step (planning), do NOT auto-advance"
    Per user decision: "Clear context window between workflow steps" -- conversation marked completed, new session for planning

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        db: Database session

    Returns:
        {
            "success": True,
            "context_file": str,
            "next_step": "planning",
            "message": "Discussion complete. Run /gsd:plan-phase to plan this phase."
        }
    """
    from app.services.context_generator import ContextGenerator
    from app.models.project import Project

    # Verify conversation exists and belongs to project
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.project_id == project_id)
    )
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load project to get type
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check for unconfirmed decisions
    decisions = conversation.summary_data.get("decisions", [])
    unconfirmed_count = sum(1 for d in decisions if isinstance(d, dict) and not d.get("confirmed", False))

    warnings = []
    if unconfirmed_count > 0:
        warnings.append(f"{unconfirmed_count} unconfirmed decision(s) will be marked as 'Pending Review' in CONTEXT.md")

    # Generate CONTEXT.md
    generator = ContextGenerator()
    content = generator.generate(conversation, project.type.value)

    # Save CONTEXT.md to project's phase directory
    phase_number = conversation.phase_number
    context_file = generator.save(project_id, phase_number, content)

    # Mark conversation as completed
    conversation.status = ConversationStatus.completed.value
    conversation.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "success": True,
        "context_file": context_file,
        "next_step": "planning",
        "message": "Discussion complete. Run /gsd:plan-phase to plan this phase.",
        "warnings": warnings if warnings else None,
    }


@router.post("/{conversation_id}/complete")
async def complete_discussion(
    project_id: int,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a discussion, generating CONTEXT.md.

    DEPRECATED: Use /finalize endpoint instead.
    This endpoint is kept for backwards compatibility.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Redirect to finalize endpoint
    """
    return await finalize_discussion(project_id, conversation_id, db)
