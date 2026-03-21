"""Unit tests for FDS assembly service."""

import pytest
from pathlib import Path

from app.services.assembly_service import (
    check_assembly_readiness,
    _build_section_tree,
    _resolve_cross_references,
)


# ---------------------------------------------------------------------------
# check_assembly_readiness tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_readiness_draft_with_content(tmp_project_dir):
    """Draft mode: project with at least one SUMMARY.md returns ready=True."""
    phase_dir = tmp_project_dir / ".planning" / "phases" / "01-system-overview"
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "01-01-SUMMARY.md").write_text("# Section 1\n\nContent here.", encoding="utf-8")

    result = await check_assembly_readiness(tmp_project_dir, "draft")

    assert result.ready is True
    assert result.has_content is True
    assert result.mode == "draft"
    assert result.unreviewed_phases == []


@pytest.mark.asyncio
async def test_check_readiness_draft_no_content(tmp_project_dir):
    """Draft mode: project with no SUMMARY.md returns ready=False, has_content=False."""
    result = await check_assembly_readiness(tmp_project_dir, "draft")

    assert result.ready is False
    assert result.has_content is False
    assert result.mode == "draft"


@pytest.mark.asyncio
async def test_check_readiness_final_unreviewed(tmp_project_dir):
    """Final mode: phase with SUMMARY.md but no REVIEW.md makes ready=False."""
    phase_dir = tmp_project_dir / ".planning" / "phases" / "01-system-overview"
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "01-01-SUMMARY.md").write_text("# Section 1\n\nContent.", encoding="utf-8")
    # No REVIEW.md — unreviewed

    result = await check_assembly_readiness(tmp_project_dir, "final")

    assert result.ready is False
    assert result.has_content is True
    assert "01-system-overview" in result.unreviewed_phases


@pytest.mark.asyncio
async def test_check_readiness_final_reviewed(tmp_project_dir):
    """Final mode: phase with both SUMMARY.md and REVIEW.md returns ready=True."""
    phase_dir = tmp_project_dir / ".planning" / "phases" / "01-system-overview"
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "01-01-SUMMARY.md").write_text("# Section 1\n\nContent.", encoding="utf-8")
    (phase_dir / "01-REVIEW.md").write_text("# Review\n\nApproved.", encoding="utf-8")

    result = await check_assembly_readiness(tmp_project_dir, "final")

    assert result.ready is True
    assert result.unreviewed_phases == []


# ---------------------------------------------------------------------------
# _build_section_tree tests
# ---------------------------------------------------------------------------


def test_build_section_tree_language_nl(fds_structure):
    """_build_section_tree with language='nl' returns Dutch titles."""
    tree = _build_section_tree(fds_structure, "A", "nl")

    assert len(tree) > 0
    # Check that the first section has Dutch title
    first_id, first_title, first_depth = tree[0]
    assert first_id == "1"
    assert first_title == "Introductie"
    assert first_depth == 1


def test_build_section_tree_language_en(fds_structure):
    """_build_section_tree with language='en' returns English titles."""
    tree = _build_section_tree(fds_structure, "A", "en")

    assert len(tree) > 0
    first_id, first_title, first_depth = tree[0]
    assert first_id == "1"
    assert first_title == "Introduction"


def test_build_section_tree_type_c_has_baseline(fds_structure):
    """_build_section_tree for Type C includes baseline section 1.4."""
    tree = _build_section_tree(fds_structure, "C", "nl")

    ids = [sid for sid, _t, _d in tree]
    assert "1.4" in ids  # baseline
    assert "1.5" in ids  # abbreviations shifted


def test_build_section_tree_type_a_no_baseline(fds_structure):
    """_build_section_tree for Type A does not include a shifted 1.5."""
    tree = _build_section_tree(fds_structure, "A", "nl")

    ids = [sid for sid, _t, _d in tree]
    assert "1.5" not in ids
    assert "1.4" in ids  # abbreviations remain at 1.4


# ---------------------------------------------------------------------------
# Cross-reference resolution tests
# ---------------------------------------------------------------------------


def test_cross_reference_resolution():
    """_resolve_cross_references replaces {ref:X.Y} and {fig:N} patterns."""
    text = "See {ref:1.2} and {ref:3.1} also check {fig:3} and {fig:12}."
    result = _resolve_cross_references(text)

    assert "Section 1.2" in result
    assert "Section 3.1" in result
    assert "Figure 3" in result
    assert "Figure 12" in result
    assert "{ref:" not in result
    assert "{fig:" not in result


def test_cross_reference_no_matches():
    """_resolve_cross_references leaves text unchanged when no patterns found."""
    text = "This text has no cross-references at all."
    result = _resolve_cross_references(text)
    assert result == text
