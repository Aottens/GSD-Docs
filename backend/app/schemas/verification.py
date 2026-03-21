"""Pydantic schemas for verification detail response."""

from typing import Optional
from pydantic import BaseModel, Field


class TruthResult(BaseModel):
    """Per-truth verification result with level details and gap information."""
    description: str = Field(..., description="Truth description from summary table")
    status: str = Field(..., description="PASS or GAP")
    levels: dict = Field(
        default_factory=dict,
        description="Per-level results: exists/substantive/complete/consistent/standards each 'pass'/'gap'/'-'/'n/a'"
    )
    failed_level: Optional[str] = Field(None, description="e.g. 'Level 3 - Complete' if GAP")
    gap_description: Optional[str] = Field(None, description="Descriptive text from Detailed Findings")
    evidence_files: list[str] = Field(default_factory=list, description="File paths from Evidence block")
    standards_violations: list[dict] = Field(
        default_factory=list,
        description="Each: {reference: str, text: str}"
    )


class VerificationDetailResponse(BaseModel):
    """Full verification detail for a phase, parsed from VERIFICATION.md."""
    has_verification: bool = Field(default=False)
    status: Optional[str] = Field(None, description="PASS or GAPS_FOUND or GAPS_FOUND (ESCALATED)")
    current_cycle: int = Field(default=1)
    max_cycles: int = Field(default=2)
    is_blocked: bool = Field(default=False, description="True when ESCALATED")
    truths: list[TruthResult] = Field(default_factory=list)
    total_truths: int = Field(default=0)
    passed_count: int = Field(default=0)
    gap_count: int = Field(default=0)
