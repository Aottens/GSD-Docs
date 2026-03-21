"""Document outline and section content Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class PlanInfoSchema(BaseModel):
    """Schema for plan metadata extracted from PLAN.md frontmatter."""

    wave: int = Field(..., description="Execution wave number")
    depends_on: list[str] = Field(default_factory=list, description="Plan IDs this plan depends on")
    plan_name: str = Field(..., description="Plan name from frontmatter")
    plan_file: str = Field(..., description="Plan filename e.g. 01-02-PLAN.md")
    truths: list[str] = Field(default_factory=list, description="Must-have truths from PLAN.md frontmatter must_haves.truths")
    description: Optional[str] = Field(default=None, description="Plan description extracted from PLAN.md <objective> block")


class OutlineNodeSchema(BaseModel):
    """Schema for a single node in the document outline tree."""

    id: str = Field(..., description="Section ID e.g. '1', '1.1', '4.2.3'")
    title: dict[str, str] = Field(..., description="Bilingual title {en: ..., nl: ...}")
    depth: int = Field(..., description="Nesting depth 1-3")
    required: bool = Field(default=True)
    source_type: str = Field(..., description="e.g. system-overview, dynamic, auto-generated")
    status: str = Field(default="empty", description="empty|planned|written|verified")
    has_content: bool = Field(default=False)
    has_plan: bool = Field(default=False)
    plan_info: Optional[PlanInfoSchema] = Field(default=None)
    preview_snippet: Optional[str] = Field(default=None, description="First ~80 chars of content")
    children: list["OutlineNodeSchema"] = Field(default_factory=list)


class DocumentOutlineResponse(BaseModel):
    """Response schema for full document outline."""

    project_id: int
    project_language: str = Field(..., description="'nl' or 'en'")
    sections: list[OutlineNodeSchema]


class SectionContentResponse(BaseModel):
    """Response schema for section content."""

    section_id: str
    status: str = Field(default="empty")
    markdown_content: Optional[str] = Field(default=None)
    plan_info: Optional[PlanInfoSchema] = Field(default=None)
