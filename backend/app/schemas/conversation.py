"""Conversation and Message Pydantic schemas."""

import enum
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class StreamEventType(str, enum.Enum):
    """SSE event types for streaming responses."""
    MESSAGE_DELTA = "message_delta"
    MESSAGE_COMPLETE = "message_complete"
    QUESTION_CARD = "question_card"
    SUMMARY_CARD = "summary_card"
    ERROR = "error"
    DONE = "done"


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    project_id: int = Field(..., description="Project ID")
    phase_number: int = Field(..., ge=1, le=99, description="Phase number")


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    project_id: int
    phase_number: int
    status: str
    title: Optional[str] = None
    summary_data: Optional[dict[str, Any]] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = Field(default=0, description="Number of messages in conversation")

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    conversations: list[ConversationResponse]
    total: int


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    role: str = Field(..., max_length=20, description="Message role: system, user, assistant, summary")
    content: str = Field(..., min_length=1, description="Message content")
    message_type: str = Field(default="text", max_length=30, description="Message type")
    metadata_json: Optional[dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    conversation_id: int
    role: str
    content: str
    message_type: str
    metadata_json: Optional[dict[str, Any]] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class SendMessageRequest(BaseModel):
    """Schema for sending a message in a conversation."""
    content: str = Field(..., min_length=1, description="Message content")
    attachments: Optional[list[str]] = Field(
        default=None,
        description="Optional list of file paths/IDs to attach"
    )


class StreamEvent(BaseModel):
    """Schema for SSE stream events."""
    event: StreamEventType = Field(..., description="Event type")
    data: dict[str, Any] = Field(default_factory=dict, description="Event data")
