"""Unit tests for DOCX export service."""

import shutil
import pytest
from pathlib import Path

from app.services.export_service import (
    detect_pandoc,
    list_export_versions,
    _determine_next_version,
)


# ---------------------------------------------------------------------------
# detect_pandoc tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not shutil.which("pandoc"),
    reason="Pandoc is not installed on this system",
)
def test_detect_pandoc_installed():
    """detect_pandoc() returns (True, version_string) when Pandoc is installed."""
    found, version = detect_pandoc()

    assert found is True
    assert version is not None
    assert isinstance(version, str)
    # Version string should look like "3.x.y" or similar
    assert len(version) > 0


def test_detect_pandoc_returns_tuple():
    """detect_pandoc() always returns a 2-tuple (bool, str | None)."""
    result = detect_pandoc()

    assert isinstance(result, tuple)
    assert len(result) == 2
    found, version = result
    assert isinstance(found, bool)
    assert version is None or isinstance(version, str)


# ---------------------------------------------------------------------------
# list_export_versions tests
# ---------------------------------------------------------------------------


def test_list_versions_empty(tmp_path):
    """list_export_versions() returns empty list when output dir doesn't exist."""
    project_dir = tmp_path / "project-1"
    project_dir.mkdir()

    result = list_export_versions(project_dir)

    assert result == []


def test_list_versions_empty_output_dir(tmp_path):
    """list_export_versions() returns empty list when output dir exists but is empty."""
    project_dir = tmp_path / "project-1"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True)

    result = list_export_versions(project_dir)

    assert result == []


def test_list_versions_parses_filename(tmp_path):
    """list_export_versions() correctly parses filename pattern into dict fields."""
    project_dir = tmp_path / "project-1"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True)

    # Create a mock DOCX file with valid naming pattern
    docx_file = output_dir / "FDS-v1.0_draft_nl.docx"
    docx_file.write_bytes(b"PK\x03\x04")  # Minimal zip header (DOCX format)

    result = list_export_versions(project_dir)

    assert len(result) == 1
    v = result[0]
    assert v["filename"] == "FDS-v1.0_draft_nl.docx"
    assert v["doc_type"] == "FDS"
    assert v["version"] == "1.0"
    assert v["mode"] == "draft"
    assert v["language"] == "nl"
    assert v["size_bytes"] > 0


def test_list_versions_multiple_sorted_by_date(tmp_path):
    """list_export_versions() returns artifacts sorted by created_at descending."""
    project_dir = tmp_path / "project-1"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True)

    import time

    # Create files with distinct modification times
    f1 = output_dir / "FDS-v1.0_draft_nl.docx"
    f1.write_bytes(b"PK\x03\x04")
    time.sleep(0.01)
    f2 = output_dir / "FDS-v1.1_draft_nl.docx"
    f2.write_bytes(b"PK\x03\x04")

    result = list_export_versions(project_dir)

    assert len(result) == 2
    # Most recent first
    assert result[0]["version"] == "1.1"
    assert result[1]["version"] == "1.0"


def test_list_versions_skips_non_matching_files(tmp_path):
    """list_export_versions() ignores files that don't match the naming pattern."""
    project_dir = tmp_path / "project-1"
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True)

    # Create files that should NOT be parsed
    (output_dir / "random-export.docx").write_bytes(b"PK")
    (output_dir / "FDS-assembled-nl.md").write_text("# Test", encoding="utf-8")
    # Valid file
    (output_dir / "FDS-v1.0_final_en.docx").write_bytes(b"PK\x03\x04")

    result = list_export_versions(project_dir)

    assert len(result) == 1
    assert result[0]["doc_type"] == "FDS"
    assert result[0]["mode"] == "final"
    assert result[0]["language"] == "en"


# ---------------------------------------------------------------------------
# Version incrementing tests
# ---------------------------------------------------------------------------


def test_version_incrementing_starts_at_1_0(tmp_path):
    """_determine_next_version starts at '1.0' when no existing files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    version = _determine_next_version(output_dir, "draft", "nl")

    assert version == "1.0"


def test_version_incrementing_increments_minor(tmp_path):
    """_determine_next_version increments minor when FDS-v1.0_draft_nl.docx exists."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "FDS-v1.0_draft_nl.docx").write_bytes(b"PK")

    version = _determine_next_version(output_dir, "draft", "nl")

    assert version == "1.1"


def test_version_incrementing_different_mode_starts_fresh(tmp_path):
    """_determine_next_version treats draft and final as separate version sequences."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "FDS-v1.0_draft_nl.docx").write_bytes(b"PK")
    (output_dir / "FDS-v1.1_draft_nl.docx").write_bytes(b"PK")

    # Final mode sequence starts fresh
    version = _determine_next_version(output_dir, "final", "nl")
    assert version == "1.0"
