"""Pytest fixtures for backend tests."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def fds_structure():
    """Load the canonical FDS structure from gsd-docs-industrial templates."""
    fds_path = (
        Path(__file__).parent.parent.parent
        / "gsd-docs-industrial"
        / "templates"
        / "fds-structure.json"
    )
    with open(fds_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def tmp_project_dir(tmp_path):
    """Create a temporary project directory with .planning/phases/ structure."""
    planning_dir = tmp_path / ".planning" / "phases"
    planning_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path
