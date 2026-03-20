"""Phase status model for timeline data derived from filesystem."""

from typing import Optional
from pydantic import BaseModel, Field


class PhaseStatus(str):
    """Phase status values."""
    NOT_STARTED = "not_started"
    DISCUSSED = "discussed"
    PLANNED = "planned"
    WRITTEN = "written"
    VERIFIED = "verified"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class PhaseInfo(BaseModel):
    """
    Phase information model for phase status.

    Represents phase status derived from filesystem artifacts (CONTEXT.md, PLAN.md, etc.).
    This is NOT a database model - it's a Pydantic model for API responses.
    """
    number: int = Field(..., description="Phase number")
    name: str = Field(..., description="Phase name/slug")
    goal: str = Field(..., description="Phase goal/description")
    status: str = Field(..., description="Phase status (not_started, discussed, planned, written, verified, reviewed, completed)")
    sub_status: Optional[str] = Field(None, description="Dutch label: Besproken, Gepland, etc.")
    cli_command: Optional[str] = Field(None, description="Next recommended /doc:* CLI command")
    has_context: bool = Field(default=False, description="Phase has CONTEXT.md")
    has_plans: bool = Field(default=False, description="Phase has PLAN.md files")
    has_content: bool = Field(default=False, description="Phase has written content")
    has_verification: bool = Field(default=False, description="Phase has verification results")
    has_review: bool = Field(default=False, description="Phase has review results")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "number": 1,
                "name": "core-infrastructure",
                "goal": "Set up FastAPI backend and React frontend",
                "status": "completed",
                "sub_status": "Beoordeeld",
                "cli_command": None,
                "has_context": True,
                "has_plans": True,
                "has_content": True,
                "has_verification": True,
                "has_review": True,
            }
        }
