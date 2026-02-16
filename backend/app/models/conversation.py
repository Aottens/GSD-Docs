"""Conversation and Message models for discussion workflow."""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class ConversationStatus(str, enum.Enum):
    """Conversation status enumeration."""
    active = "active"
    completed = "completed"
    archived = "archived"


class MessageRole(str, enum.Enum):
    """Message role enumeration."""
    system = "system"
    user = "user"
    assistant = "assistant"
    summary = "summary"


class MessageType(str, enum.Enum):
    """Message type enumeration."""
    text = "text"
    question_card = "question_card"
    summary_card = "summary_card"
    topic_selection = "topic_selection"
    decision_edit = "decision_edit"
    completion_card = "completion_card"
    topic_boundary = "topic_boundary"
    decision_captured = "decision_captured"
    check_in = "check_in"


class ConversationPhase(str, enum.Enum):
    """Conversation phase enumeration (matches state machine phases)."""
    topic_selection = "topic_selection"
    discussion = "discussion"
    check_in = "check_in"
    completion = "completion"


class Conversation(Base):
    """
    Conversation model for discussion workflow.

    Tracks discussion sessions for phases, including decisions and context.
    Supports revision chains via parent_id for continuing discussions.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default=ConversationStatus.active.value
    )
    title = Column(String(200), nullable=True)
    summary_data = Column(JSON, nullable=True)
    parent_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.timestamp"
    )
    parent = relationship(
        "Conversation",
        remote_side=[id],
        backref="revisions"
    )

    # Indexes
    __table_args__ = (
        Index("ix_conversations_project_phase", "project_id", "phase_number"),
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, project_id={self.project_id}, phase={self.phase_number})>"


class Message(Base):
    """
    Message model for conversation messages.

    Stores individual messages in a conversation with role, content, and optional metadata.
    Supports different message types including interactive cards and decisions.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(30), nullable=False, default=MessageType.text.value)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("ix_messages_conversation_timestamp", "conversation_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"
