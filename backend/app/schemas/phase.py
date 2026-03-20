"""Phase timeline Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class PhaseStatusResponse(BaseModel):
    """Schema for phase status in timeline."""
    number: int = Field(..., description="Phase number")
    name: str = Field(..., description="Phase name/slug")
    goal: str = Field(..., description="Phase goal/description")
    status: str = Field(..., description="Phase status (not_started, discussed, planned, written, verified, reviewed, completed)")
    sub_status: Optional[str] = Field(None, description="Dutch label: Besproken, Gepland, etc.")
    cli_command: Optional[str] = Field(None, description="Next recommended /doc:* CLI command")
    context_decisions: list[str] = Field(default_factory=list, description="Key decisions from CONTEXT.md")
    verification_score: Optional[str] = Field(None, description="Verification score e.g. 4/5")
    verification_gaps: Optional[int] = Field(None, description="Number of verification gaps")
    has_context: bool = Field(default=False, description="Phase has CONTEXT.md")
    has_plans: bool = Field(default=False, description="Phase has PLAN.md files")
    has_content: bool = Field(default=False, description="Phase has written content")
    has_verification: bool = Field(default=False, description="Phase has verification results")
    has_review: bool = Field(default=False, description="Phase has review results")


class PhaseTimelineResponse(BaseModel):
    """Schema for full phase timeline response."""
    project_id: int = Field(..., description="Project ID")
    phases: list[PhaseStatusResponse] = Field(
        default_factory=list,
        description="List of phase statuses"
    )


class ContextFilesResponse(BaseModel):
    """Response for phase context file data."""
    decisions: list[str] = Field(default_factory=list, description="Key decisions from CONTEXT.md")
    verification_score: Optional[str] = Field(None, description="Verification score e.g. 4/5")
    verification_gaps: Optional[int] = Field(None, description="Number of verification gaps")
    verification_severity: Optional[dict] = Field(None, description="Gap severity breakdown")
    has_context: bool = Field(default=False, description="CONTEXT.md found")
    has_verification: bool = Field(default=False, description="VERIFICATION.md found")
