"""Discussion API with SSE streaming for chat interface."""

import json
from typing import Optional
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


@router.post("/{conversation_id}/complete")
async def complete_discussion(
    project_id: int,
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a discussion, generating CONTEXT.md.

    Args:
        project_id: Project ID
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Summary data for CONTEXT.md generation
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

    # Create discussion engine and complete
    settings = get_settings()
    llm = get_llm_provider()
    engine = DiscussionEngine(db, llm, settings)

    summary_data = await engine.complete_discussion(conversation_id)

    return {
        "success": True,
        "message": "Discussion completed",
        "summary_data": summary_data,
    }
