"""Unit tests for DOC_TYPE_CONFIG and SetupStateResponse schema."""

from datetime import datetime

from app.config_phases import DOC_TYPE_CONFIG
from app.schemas.setup_state import SetupStateResponse, DocTypeEntry, DocTypeConfigEntry


def test_doc_type_config_all_types():
    """DOC_TYPE_CONFIG has all four project types with valid structure."""
    assert set(DOC_TYPE_CONFIG.keys()) == {"A", "B", "C", "D"}
    for project_type, entries in DOC_TYPE_CONFIG.items():
        assert isinstance(entries, list), f"Type {project_type} entries must be a list"
        assert len(entries) > 0, f"Type {project_type} must have at least one entry"
        for entry in entries:
            assert "id" in entry, f"Entry missing 'id' key in type {project_type}"
            assert "label" in entry, f"Entry missing 'label' key in type {project_type}"
            assert "required" in entry, f"Entry missing 'required' key in type {project_type}"
            assert isinstance(entry["id"], str)
            assert isinstance(entry["label"], str)
            assert isinstance(entry["required"], bool)


def test_doc_type_config_type_a_has_standards():
    """Type A must include 'standards' doc type for standards scope documents."""
    type_a_ids = [e["id"] for e in DOC_TYPE_CONFIG["A"]]
    assert "standards" in type_a_ids, "Type A must have 'standards' doc type"


def test_doc_type_config_type_c_has_baseline():
    """Type C must include 'baseline' doc type for existing FDS reference."""
    type_c_ids = [e["id"] for e in DOC_TYPE_CONFIG["C"]]
    assert "baseline" in type_c_ids, "Type C must have 'baseline' doc type"


def test_doc_type_config_type_d_has_change_order():
    """Type D must include 'change_order' doc type for TWN/change order."""
    type_d_ids = [e["id"] for e in DOC_TYPE_CONFIG["D"]]
    assert "change_order" in type_d_ids, "Type D must have 'change_order' doc type"


def test_doc_type_config_entry_schema():
    """DocTypeConfigEntry Pydantic model correctly validates DOC_TYPE_CONFIG entries."""
    for project_type, entries in DOC_TYPE_CONFIG.items():
        for entry in entries:
            parsed = DocTypeConfigEntry(**entry)
            assert parsed.id == entry["id"]
            assert parsed.label == entry["label"]
            assert parsed.required == entry["required"]


def test_doc_type_entry_schema():
    """DocTypeEntry schema correctly tracks coverage status."""
    entry = DocTypeEntry(
        id="pid",
        label="P&ID tekeningen",
        required=True,
        status="present",
        file_count=2,
        file_paths=["/srv/projects/1/uploads/file1.pdf", "/srv/projects/1/uploads/file2.pdf"],
    )
    assert entry.id == "pid"
    assert entry.status == "present"
    assert entry.file_count == 2
    assert len(entry.file_paths) == 2


def test_setup_state_response_schema():
    """SetupStateResponse serializes correctly with all required fields."""
    doc_types = [
        DocTypeEntry(
            id="pid",
            label="P&ID tekeningen",
            required=True,
            status="present",
            file_count=1,
            file_paths=["/srv/projects/1/file.pdf"],
        ),
        DocTypeEntry(
            id="machine_spec",
            label="Machinespecificatie / PLC-spec",
            required=True,
            status="missing",
            file_count=0,
            file_paths=[],
        ),
        DocTypeEntry(
            id="risk_assess",
            label="Risicobeoordeling / RA",
            required=False,
            status="skipped",
            file_count=0,
            file_paths=[],
        ),
    ]

    response = SetupStateResponse(
        project_id=42,
        project_name="Test Project NL",
        project_type="A",
        language="nl",
        project_dir="/srv/projects/42",
        doc_types=doc_types,
        has_scaffolding=True,
        next_cli_command="/doc:discuss-phase 1",
    )

    assert response.project_id == 42
    assert response.project_name == "Test Project NL"
    assert response.project_type == "A"
    assert response.language == "nl"
    assert response.project_dir == "/srv/projects/42"
    assert len(response.doc_types) == 3
    assert response.has_scaffolding is True
    assert response.next_cli_command == "/doc:discuss-phase 1"

    # Verify serialization
    data = response.model_dump()
    assert data["project_id"] == 42
    assert data["doc_types"][0]["status"] == "present"
    assert data["doc_types"][1]["status"] == "missing"
    assert data["doc_types"][2]["status"] == "skipped"


def test_setup_state_response_no_scaffolding():
    """SetupStateResponse with no scaffolding returns /doc:new-fds as next command."""
    response = SetupStateResponse(
        project_id=1,
        project_name="New Project",
        project_type="B",
        language="en",
        project_dir="/srv/projects/1",
        doc_types=[],
        has_scaffolding=False,
        next_cli_command="/doc:new-fds",
    )
    assert response.has_scaffolding is False
    assert response.next_cli_command == "/doc:new-fds"


def test_setup_state_response_all_complete():
    """SetupStateResponse with all phases done returns None as next command."""
    response = SetupStateResponse(
        project_id=5,
        project_name="Complete Project",
        project_type="D",
        language="nl",
        project_dir="/srv/projects/5",
        doc_types=[],
        has_scaffolding=True,
        next_cli_command=None,
    )
    assert response.next_cli_command is None
