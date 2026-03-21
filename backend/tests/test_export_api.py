"""Integration tests for export API endpoints."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.export import AssemblyReadinessSchema


@pytest.fixture
def mock_project():
    """Create a mock Project object."""
    project = MagicMock()
    project.id = 1
    project.language = MagicMock()
    project.language.value = "nl"
    project.type = MagicMock()
    project.type.value = "A"
    return project


@pytest.fixture
def mock_db(mock_project):
    """Mock database session that returns a project."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = mock_project
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.fixture
def mock_project_dir(tmp_path):
    """Create a minimal project directory structure."""
    project_dir = tmp_path / "1"
    (project_dir / ".planning" / "phases").mkdir(parents=True)
    return project_dir


# ---------------------------------------------------------------------------
# GET /readiness tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_readiness_endpoint_returns_schema(mock_project, mock_db, mock_project_dir):
    """GET /readiness returns AssemblyReadinessSchema-shaped JSON."""
    with (
        patch("app.api.export.get_db", return_value=mock_db),
        patch("app.api.export._get_project_dir", return_value=mock_project_dir),
        patch(
            "app.api.export.check_assembly_readiness",
            new=AsyncMock(
                return_value=AssemblyReadinessSchema(
                    ready=False,
                    mode="draft",
                    unreviewed_phases=[],
                    has_content=False,
                )
            ),
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/readiness?mode=draft")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "mode" in data
    assert "unreviewed_phases" in data
    assert "has_content" in data
    assert isinstance(data["ready"], bool)
    assert isinstance(data["unreviewed_phases"], list)


# ---------------------------------------------------------------------------
# GET /pandoc-status tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pandoc_status_endpoint_returns_schema():
    """GET /pandoc-status returns PandocStatusSchema-shaped JSON."""
    with patch("app.api.export.detect_pandoc", return_value=(True, "3.1.0")):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/pandoc-status")

    assert response.status_code == 200
    data = response.json()
    assert "installed" in data
    assert "version" in data
    assert isinstance(data["installed"], bool)


@pytest.mark.asyncio
async def test_pandoc_status_endpoint_not_installed():
    """GET /pandoc-status returns installed=False when Pandoc not found."""
    with patch("app.api.export.detect_pandoc", return_value=(False, None)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/pandoc-status")

    assert response.status_code == 200
    data = response.json()
    assert data["installed"] is False
    assert data["version"] is None


# ---------------------------------------------------------------------------
# GET /versions tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_versions_endpoint_returns_schema(mock_project, mock_db, mock_project_dir):
    """GET /versions returns ExportVersionListResponse-shaped JSON."""
    with (
        patch("app.api.export.get_db", return_value=mock_db),
        patch("app.api.export._get_project_dir", return_value=mock_project_dir),
        patch("app.api.export.list_export_versions", return_value=[]),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/versions")

    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert "versions" in data
    assert isinstance(data["versions"], list)


# ---------------------------------------------------------------------------
# GET /download/{filename} path traversal tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_path_traversal_dotdot(mock_project, mock_db, mock_project_dir):
    """GET /download/../../../etc/passwd is blocked (400/422/404 — never 200)."""
    with (
        patch("app.api.export.get_db", return_value=mock_db),
        patch("app.api.export._get_project_dir", return_value=mock_project_dir),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/download/..%2F..%2Fetc%2Fpasswd")

    # Framework normalizes URL-encoded traversal; result is never 200
    assert response.status_code != 200


@pytest.mark.asyncio
async def test_download_path_traversal_literal_dotdot(mock_project, mock_db, mock_project_dir):
    """GET /download/..evil.docx returns 400 (filename starts with ..)."""
    with (
        patch("app.api.export.get_db", return_value=mock_db),
        patch("app.api.export._get_project_dir", return_value=mock_project_dir),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/projects/1/export/download/..evil.docx")

    # Filename starting with '..' triggers path traversal guard
    assert response.status_code in (400, 404)


@pytest.mark.asyncio
async def test_download_nonexistent_file_returns_404(mock_project, mock_db, mock_project_dir):
    """GET /download/{valid_filename} returns 404 when file doesn't exist."""
    with (
        patch("app.api.export.get_db", return_value=mock_db),
        patch("app.api.export._get_project_dir", return_value=mock_project_dir),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/projects/1/export/download/FDS-v1.0_draft_nl.docx"
            )

    assert response.status_code == 404
