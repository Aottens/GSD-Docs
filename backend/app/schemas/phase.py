"""Phase timeline Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class PhaseStatusResponse(BaseModel):
    """Schema for phase status in timeline."""
    number: int = Field(..., description="Phase number")
    name: str = Field(..., description="Phase name/slug")
    goal: str = Field(..., description="Phase goal/description")
    status: str = Field(..., description="Phase status (not_started, discussing, etc.)")
    sub_status: Optional[str] = Field(None, description="Dutch label: Besproken, Gepland, etc.")
    available_actions: list[str] = Field(
        default_factory=list,
        description="Available actions: discuss, plan, write, verify, review"
    )
    has_context: bool = Field(default=False, description="Phase has CONTEXT.md")
    has_plans: bool = Field(default=False, description="Phase has PLAN.md files")
    has_content: bool = Field(default=False, description="Phase has written content")
    has_verification: bool = Field(default=False, description="Phase has verification results")
    has_review: bool = Field(default=False, description="Phase has review results")
    conversation_id: Optional[int] = Field(None, description="Active conversation ID for this phase")


class PhaseTimelineResponse(BaseModel):
    """Schema for full phase timeline response."""
    project_id: int = Field(..., description="Project ID")
    phases: list[PhaseStatusResponse] = Field(
        default_factory=list,
        description="List of phase statuses"
    )
