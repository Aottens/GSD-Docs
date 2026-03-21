"""Tests for document outline API schemas and helper functions."""

import pytest
from app.schemas.document import (
    PlanInfoSchema,
    OutlineNodeSchema,
    DocumentOutlineResponse,
    SectionContentResponse,
)

# These will fail (RED) until Task 2 implements them in app.api.documents
from app.api.documents import _parse_plan_frontmatter, _build_outline_sections, _extract_objective


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


def test_plan_info_schema_valid():
    """PlanInfoSchema validates with all required fields."""
    p = PlanInfoSchema(
        wave=2,
        depends_on=["01-01"],
        plan_name="Test Plan",
        plan_file="01-02-PLAN.md",
        truths=["truth1", "truth2"],
        description="Test description",
    )
    assert p.wave == 2
    assert p.depends_on == ["01-01"]
    assert p.truths == ["truth1", "truth2"]
    assert p.description == "Test description"


def test_plan_info_schema_defaults():
    """PlanInfoSchema defaults truths to empty list and description to None."""
    p = PlanInfoSchema(wave=1, plan_name="test", plan_file="01-01-PLAN.md")
    assert p.truths == []
    assert p.description is None
    assert p.depends_on == []


def test_outline_node_schema_valid():
    """OutlineNodeSchema validates with all required fields."""
    node = OutlineNodeSchema(
        id="1.1",
        title={"en": "Purpose and Scope", "nl": "Doel en Scope"},
        depth=2,
        source_type="system-overview",
    )
    assert node.id == "1.1"
    assert node.status == "empty"
    assert node.has_content is False
    assert node.has_plan is False
    assert node.children == []
    assert node.plan_info is None
    assert node.preview_snippet is None


def test_document_outline_response_valid():
    """DocumentOutlineResponse validates with project_id, language, sections."""
    node = OutlineNodeSchema(
        id="1",
        title={"en": "Introduction", "nl": "Introductie"},
        depth=1,
        source_type="system-overview",
    )
    response = DocumentOutlineResponse(
        project_id=42,
        project_language="nl",
        sections=[node],
    )
    assert response.project_id == 42
    assert response.project_language == "nl"
    assert len(response.sections) == 1


def test_section_content_response_valid():
    """SectionContentResponse validates with section_id, status, content, plan_info."""
    response = SectionContentResponse(
        section_id="1.1",
        status="planned",
        markdown_content=None,
        plan_info=None,
    )
    assert response.section_id == "1.1"
    assert response.status == "planned"
    assert response.markdown_content is None
    assert response.plan_info is None


# ---------------------------------------------------------------------------
# _parse_plan_frontmatter tests
# ---------------------------------------------------------------------------


def test_plan_frontmatter_parsing():
    """_parse_plan_frontmatter extracts wave and depends_on from valid YAML frontmatter."""
    content = """---
phase: 01
plan: 02
wave: 2
depends_on: ["01-01"]
---

Some content here.
"""
    result = _parse_plan_frontmatter(content)
    assert result.get("wave") == 2
    assert result.get("depends_on") == ["01-01"]


def test_plan_frontmatter_truths_extraction():
    """_parse_plan_frontmatter extracts must_haves.truths list from frontmatter."""
    content = """---
phase: 01
plan: 02
wave: 1
must_haves:
  truths:
    - "First truth statement"
    - "Second truth statement"
---

Some content.
"""
    result = _parse_plan_frontmatter(content)
    truths = result.get("must_haves", {}).get("truths", [])
    assert isinstance(truths, list)
    assert len(truths) == 2
    assert "First truth statement" in truths


def test_plan_frontmatter_objective_extraction():
    """_parse_plan_frontmatter extracts objective text as description."""
    content = """---
phase: 01
plan: 02
wave: 1
---

<objective>
Build the backend API for document outline.

This includes multiple endpoints.
</objective>
"""
    result = _parse_plan_frontmatter(content)
    desc = result.get("description")
    assert desc is not None
    assert "Build the backend API" in desc


def test_plan_frontmatter_no_delimiters():
    """_parse_plan_frontmatter returns {} for content without frontmatter delimiters."""
    content = "# Hello\n\nThis is just markdown content without frontmatter."
    result = _parse_plan_frontmatter(content)
    assert result == {}


def test_plan_frontmatter_malformed_yaml():
    """_parse_plan_frontmatter returns {} for malformed YAML (unclosed frontmatter)."""
    content = "---\nphase: 01\n  bad: [unclosed\n"
    result = _parse_plan_frontmatter(content)
    assert result == {}


# ---------------------------------------------------------------------------
# _build_outline_sections tests
# ---------------------------------------------------------------------------


def test_outline_static_sections(fds_structure, tmp_project_dir):
    """_build_outline_sections returns 7 top-level sections for Type A."""
    sections = _build_outline_sections(fds_structure, "A", tmp_project_dir)
    assert len(sections) == 7
    top_level_ids = [s["id"] for s in sections]
    assert top_level_ids == ["1", "2", "3", "4", "5", "6", "7"]


def test_outline_type_c_baseline_shift(fds_structure, tmp_project_dir):
    """_build_outline_sections inserts baseline section 1.4 for Type C, shifts abbreviations to 1.5."""
    sections = _build_outline_sections(fds_structure, "C", tmp_project_dir)
    # Find section 1 (Introduction)
    section_1 = next(s for s in sections if s["id"] == "1")
    children = section_1["children"]
    # Should have 5 children now: 1.1, 1.2, 1.3, 1.4 (Baseline), 1.5 (Abbreviations)
    assert len(children) == 5
    child_ids = [c["id"] for c in children]
    assert "1.4" in child_ids
    assert "1.5" in child_ids
    # 1.4 should be the baseline section
    child_14 = next(c for c in children if c["id"] == "1.4")
    assert child_14["source_type"] == "baseline"
    # 1.5 should be abbreviations (originally 1.4)
    child_15 = next(c for c in children if c["id"] == "1.5")
    assert child_15["source_type"] == "auto-generated"


def test_outline_section_4_placeholder_no_equipment(fds_structure, tmp_project_dir):
    """_build_outline_sections section 4 has placeholder when no equipment modules found."""
    sections = _build_outline_sections(fds_structure, "A", tmp_project_dir)
    section_4 = next(s for s in sections if s["id"] == "4")
    assert len(section_4["children"]) == 1
    placeholder = section_4["children"][0]
    assert placeholder["id"] == "4.0"
    assert placeholder["source_type"] == "placeholder"
