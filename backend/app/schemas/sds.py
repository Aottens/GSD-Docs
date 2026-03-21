"""Pydantic schemas for SDS scaffolding results."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MatchDetailSchema(BaseModel):
    """Detailed breakdown of a typical match score."""

    reason: str
    """Why matched or failed — e.g., 'I/O count mismatch: module has 12, typical has 5'."""

    io_score: float
    """I/O match component score (0-40)."""

    keyword_score: float
    """use_cases Jaccard similarity component score (0-30)."""

    state_score: float
    """State count similarity component score (0-20)."""

    category_score: float
    """Category keyword match component score (0-10)."""

    closest_match: Optional[str] = None
    """If unmatched, name of the closest typical found."""

    closest_confidence: Optional[float] = None
    """Confidence score of the closest typical if unmatched."""

    cli_hint: str
    """CLI command hint for refining — e.g., '/doc:generate-sds --refine {module_name}'."""


class TypicalMatchSchema(BaseModel):
    """Result of matching a single equipment module to a typical."""

    equipment_module: str
    """Module name from FDS section 4.x."""

    matched_typical: Optional[str] = None
    """Matched typical name, or None if no match found."""

    typical_id: Optional[str] = None
    """Matched typical ID (e.g., 'FB_MotorCtrl'), or None."""

    confidence: float
    """Overall confidence score (0-100)."""

    confidence_level: str
    """Classification: 'HIGH' (>=70) | 'MEDIUM' (40-69) | 'LOW' (1-39) | 'UNMATCHED' (0)."""

    status: str
    """Outcome: 'matched' | 'low_confidence' | 'new_typical_needed'."""

    match_detail: Optional[MatchDetailSchema] = None
    """Detailed score breakdown, or None in skeleton mode."""


class SdsResultsResponse(BaseModel):
    """Full SDS scaffolding results for a project."""

    project_id: int
    """Project identifier."""

    scaffold_date: Optional[datetime] = None
    """When the scaffolding was last run. None if never run."""

    total_modules: int
    """Total number of equipment modules processed."""

    matched_count: int
    """Modules with HIGH confidence match (>=70)."""

    low_confidence_count: int
    """Modules with MEDIUM confidence match (40-69)."""

    unmatched_count: int
    """Modules with LOW or UNMATCHED (< 40)."""

    matches: list[TypicalMatchSchema]
    """Per-module matching results."""

    catalog_found: bool
    """Whether CATALOG.json was located for this project."""
