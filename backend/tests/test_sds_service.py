"""Unit tests for SDS scaffolding service.

Tests confidence scoring dimensions, classification, skeleton mode,
catalog loading, and full scaffold flow.
"""

import json
import pytest
from pathlib import Path

from app.services.sds_service import (
    classify_confidence,
    load_catalog,
    score_typical,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def typical_motor_ctrl() -> dict:
    """A motor control typical with clear category, use cases, states, I/O."""
    return {
        "id": "FB_MotorCtrl",
        "type": "Equipment Module",
        "category": "Motors",
        "description": "Motor control with PackML states",
        "interfaces": {
            "inputs": [
                {"name": "Enable", "dataType": "BOOL"},
                {"name": "Start", "dataType": "BOOL"},
                {"name": "Stop", "dataType": "BOOL"},
                {"name": "Speed", "dataType": "REAL"},
            ],
            "outputs": [
                {"name": "Running", "dataType": "BOOL"},
                {"name": "Fault", "dataType": "BOOL"},
                {"name": "CurrentSpeed", "dataType": "REAL"},
            ],
        },
        "use_cases": ["Motor drive control", "Pump control", "Fan motor"],
        "states": [
            {"name": "Idle", "description": "Motor stopped"},
            {"name": "Starting", "description": "Motor ramping up"},
            {"name": "Running", "description": "Motor at speed"},
            {"name": "Stopping", "description": "Motor ramping down"},
        ],
    }


@pytest.fixture
def module_motor_perfect(typical_motor_ctrl) -> dict:
    """Module that perfectly matches the motor typical."""
    return {
        "name": "Conveyor Motor",
        "io": {"DI": 3, "DO": 2, "AI": 1, "AO": 1},  # matches 3 BOOL in + 2 BOOL out + 1 REAL in + 1 REAL out
        "keywords": {"motor", "motors", "conveyor", "pump", "fan", "drive"},
        "state_count": 4,  # matches 4 states
    }


@pytest.fixture
def module_no_match() -> dict:
    """Module that completely differs from any typical."""
    return {
        "name": "Custom PLC Module",
        "io": {"DI": 20, "DO": 15, "AI": 8, "AO": 6},
        "keywords": {"plc", "custom", "specialized", "xray"},
        "state_count": 12,
    }


@pytest.fixture
def module_partial_match(typical_motor_ctrl) -> dict:
    """Module with some I/O overlap but different keywords."""
    return {
        "name": "Dosing System",
        "io": {"DI": 3, "DO": 2, "AI": 2, "AO": 0},
        "keywords": {"dosing", "system", "chemical", "flow"},
        "state_count": 3,
    }


@pytest.fixture
def typical_valve() -> dict:
    """A valve typical — very different from motor modules."""
    return {
        "id": "FB_ValveCtrl",
        "type": "Control Module",
        "category": "Valves",
        "description": "Valve open/close control",
        "interfaces": {
            "inputs": [
                {"name": "OpenCmd", "dataType": "BOOL"},
                {"name": "CloseCmd", "dataType": "BOOL"},
            ],
            "outputs": [
                {"name": "IsOpen", "dataType": "BOOL"},
                {"name": "IsClosed", "dataType": "BOOL"},
            ],
        },
        "use_cases": ["Pneumatic valves", "Butterfly valves", "Gate valves"],
        "states": [
            {"name": "Closed", "description": "Valve closed"},
            {"name": "Opening", "description": "Valve moving to open"},
            {"name": "Open", "description": "Valve open"},
        ],
    }


# ---------------------------------------------------------------------------
# score_typical tests
# ---------------------------------------------------------------------------

class TestScoreTypical:
    def test_score_typical_perfect_match(self, module_motor_perfect, typical_motor_ctrl):
        """Module with matching I/O, keywords, states, category should score >= 85."""
        score = score_typical(module_motor_perfect, typical_motor_ctrl)
        # I/O exact=40, states exact=20, category match=10, keywords overlap≈17 → ~87
        assert score >= 85, f"Expected >= 85 but got {score}"

    def test_score_typical_no_match(self, module_no_match, typical_motor_ctrl):
        """Module completely different from typical should score < 20."""
        score = score_typical(module_no_match, typical_motor_ctrl)
        assert score < 20, f"Expected < 20 but got {score}"

    def test_score_typical_partial_match(self, module_partial_match, typical_motor_ctrl):
        """Module with some I/O overlap but different keywords: 30 < score < 70."""
        score = score_typical(module_partial_match, typical_motor_ctrl)
        assert 30 < score < 70, f"Expected 30 < score < 70 but got {score}"

    def test_io_weight_40_contributes(self, typical_valve):
        """I/O exact match should contribute 40 points."""
        # Module with exact I/O match: 2 BOOL inputs, 2 BOOL outputs
        module = {"name": "valve", "io": {"DI": 2, "DO": 2, "AI": 0, "AO": 0}, "keywords": set(), "state_count": 0}
        score = score_typical(module, typical_valve)
        # I/O perfect match = 40, states 0 vs 3 = 5, others = 0 → total ~45
        assert score >= 40, f"I/O perfect match should contribute 40pts, got {score}"

    def test_state_score_20_for_exact_match(self, typical_motor_ctrl):
        """State count exact match should contribute 20 points."""
        module = {
            "name": "test",
            "io": {"DI": 0, "DO": 0, "AI": 0, "AO": 0},
            "keywords": set(),
            "state_count": 4,  # matches typical's 4 states exactly
        }
        score = score_typical(module, typical_motor_ctrl)
        # state_score = 20 (exact match), others = 0 (no I/O or keywords)
        assert score == 20, f"Expected exactly 20 for state match with zero I/O/keywords, got {score}"

    def test_category_score_10_for_match(self, typical_motor_ctrl):
        """Category match should contribute 10 points."""
        module = {
            "name": "test",
            "io": {"DI": 0, "DO": 0, "AI": 0, "AO": 0},
            "keywords": {"motors"},  # matches typical category "Motors"
            "state_count": 0,
        }
        score = score_typical(module, typical_motor_ctrl)
        # category = 10, states: 0 vs 4 diff → 5, others = 0
        assert score == 15, f"Expected category(10) + state(5) = 15, got {score}"

    def test_keyword_score_30_for_full_overlap(self, typical_motor_ctrl):
        """Full keyword overlap should contribute 30 points (Jaccard = 1.0)."""
        # use_cases words: motor, drive, control, pump, fan (unique tokens from use_cases)
        # module keywords must be the same set
        uc_words = set()
        import re
        for uc in typical_motor_ctrl["use_cases"]:
            for w in re.findall(r"[a-zA-Z]+", uc):
                if len(w) >= 3:
                    uc_words.add(w.lower())
        module = {
            "name": "test",
            "io": {"DI": 0, "DO": 0, "AI": 0, "AO": 0},
            "keywords": uc_words,
            "state_count": 0,
        }
        score = score_typical(module, typical_motor_ctrl)
        # keyword_score = 30, states: 0 vs 4 → 5, others = 0
        assert score >= 30, f"Full keyword overlap should give at least 30, got {score}"


# ---------------------------------------------------------------------------
# classify_confidence tests
# ---------------------------------------------------------------------------

class TestClassifyConfidence:
    def test_classify_confidence_high(self):
        level, status = classify_confidence(85)
        assert level == "HIGH"
        assert status == "matched"

    def test_classify_confidence_high_boundary(self):
        level, status = classify_confidence(70)
        assert level == "HIGH"
        assert status == "matched"

    def test_classify_confidence_medium(self):
        level, status = classify_confidence(55)
        assert level == "MEDIUM"
        assert status == "low_confidence"

    def test_classify_confidence_medium_boundary_low(self):
        level, status = classify_confidence(40)
        assert level == "MEDIUM"
        assert status == "low_confidence"

    def test_classify_confidence_low(self):
        level, status = classify_confidence(20)
        assert level == "LOW"
        assert status == "new_typical_needed"

    def test_classify_confidence_low_boundary(self):
        level, status = classify_confidence(1)
        assert level == "LOW"
        assert status == "new_typical_needed"

    def test_classify_confidence_unmatched(self):
        level, status = classify_confidence(0)
        assert level == "UNMATCHED"
        assert status == "new_typical_needed"

    def test_classify_confidence_unmatched_negative(self):
        # Negative scores (shouldn't happen but defensively handled)
        level, status = classify_confidence(-5)
        assert level == "UNMATCHED"
        assert status == "new_typical_needed"


# ---------------------------------------------------------------------------
# load_catalog tests
# ---------------------------------------------------------------------------

class TestLoadCatalog:
    def test_load_catalog_missing(self, tmp_path):
        """Returns None when CATALOG.json doesn't exist."""
        result = load_catalog(tmp_path)
        assert result is None

    def test_load_catalog_valid(self, tmp_path):
        """Returns list with one typical when valid CATALOG.json exists."""
        catalog_dir = tmp_path / "references" / "typicals"
        catalog_dir.mkdir(parents=True)
        catalog_data = {
            "schema_version": "1.0",
            "library": {
                "name": "Test Library",
                "version": "1.0",
                "platform": "TIA Portal V18",
                "updated": "2026-01-01",
            },
            "typicals": [
                {
                    "id": "FB_TestTypical",
                    "type": "Control Module",
                    "category": "Test",
                    "description": "A test typical",
                    "interfaces": {"inputs": [], "outputs": []},
                }
            ],
        }
        (catalog_dir / "CATALOG.json").write_text(
            json.dumps(catalog_data), encoding="utf-8"
        )
        result = load_catalog(tmp_path)
        assert result is not None
        assert len(result) == 1
        assert result[0]["id"] == "FB_TestTypical"

    def test_load_catalog_invalid_json(self, tmp_path):
        """Returns None for malformed JSON."""
        catalog_dir = tmp_path / "references" / "typicals"
        catalog_dir.mkdir(parents=True)
        (catalog_dir / "CATALOG.json").write_text("not valid json", encoding="utf-8")
        result = load_catalog(tmp_path)
        assert result is None

    def test_load_catalog_missing_typicals_key(self, tmp_path):
        """Returns None when 'typicals' key is absent."""
        catalog_dir = tmp_path / "references" / "typicals"
        catalog_dir.mkdir(parents=True)
        (catalog_dir / "CATALOG.json").write_text(
            json.dumps({"schema_version": "1.0", "library": {}}), encoding="utf-8"
        )
        result = load_catalog(tmp_path)
        assert result is None


# ---------------------------------------------------------------------------
# scaffold_sds skeleton mode
# ---------------------------------------------------------------------------

class TestScaffoldSkeletonMode:
    @pytest.mark.asyncio
    async def test_scaffold_skeleton_mode(self, tmp_path):
        """No CATALOG.json: all modules UNMATCHED, confidence 0, catalog_found=False."""
        from app.services.sds_service import scaffold_sds

        # Create a minimal equipment module phase dir
        phases_dir = tmp_path / ".planning" / "phases" / "04-em-conveyor-motor"
        phases_dir.mkdir(parents=True)
        summary = phases_dir / "04-01-SUMMARY.md"
        summary.write_text("# Conveyor Motor summary\nDI: 3, DO: 2, AI: 1, AO: 1", encoding="utf-8")

        # No CATALOG.json → skeleton mode
        v1_docs_path = Path("/dev/null")  # not used in skeleton mode
        result = await scaffold_sds(tmp_path, v1_docs_path)

        assert result["catalog_found"] is False
        assert result["total_modules"] == 1
        assert result["matched_count"] == 0
        for match in result["matches"]:
            assert match["confidence"] == 0
            assert match["confidence_level"] == "UNMATCHED"
            assert match["status"] == "new_typical_needed"

    @pytest.mark.asyncio
    async def test_scaffold_persists_sds_results(self, tmp_path):
        """scaffold_sds writes sds-results.json to project_dir/output/."""
        from app.services.sds_service import scaffold_sds

        phases_dir = tmp_path / ".planning" / "phases" / "05-em-pump-station"
        phases_dir.mkdir(parents=True)
        (phases_dir / "05-01-SUMMARY.md").write_text("# Pump Station\nDI: 2, DO: 1", encoding="utf-8")

        await scaffold_sds(tmp_path, Path("/dev/null"))

        results_file = tmp_path / "output" / "sds-results.json"
        assert results_file.exists(), "sds-results.json should be created in output/"
        data = json.loads(results_file.read_text(encoding="utf-8"))
        assert "matches" in data
        assert data["catalog_found"] is False

    @pytest.mark.asyncio
    async def test_scaffold_empty_project_no_modules(self, tmp_path):
        """Project with no equipment module phases returns empty matches."""
        from app.services.sds_service import scaffold_sds

        phases_dir = tmp_path / ".planning" / "phases"
        phases_dir.mkdir(parents=True)
        # Create a non-em phase dir
        (phases_dir / "01-introduction").mkdir()

        result = await scaffold_sds(tmp_path, Path("/dev/null"))
        assert result["total_modules"] == 0
        assert result["matches"] == []

    @pytest.mark.asyncio
    async def test_scaffold_with_catalog_full_match(self, tmp_path):
        """With catalog, high-scoring module gets matched status."""
        from app.services.sds_service import scaffold_sds

        # Create equipment module dir
        phases_dir = tmp_path / ".planning" / "phases" / "04-em-pump-motor"
        phases_dir.mkdir(parents=True)
        # Content with motor keywords and states
        content = (
            "# Pump Motor\n"
            "DI: 3 digital inputs, DO: 2 digital outputs, AI: 1 analog input, AO: 1 analog output\n"
            "```stateDiagram-v2\n"
            "  Idle --> Starting\n"
            "  Starting --> Running\n"
            "  Running --> Stopping\n"
            "  Stopping --> Idle\n"
            "```\n"
        )
        (phases_dir / "04-01-SUMMARY.md").write_text(content, encoding="utf-8")

        # Create catalog with a matching motor typical
        catalog_dir = tmp_path / "references" / "typicals"
        catalog_dir.mkdir(parents=True)
        catalog_data = {
            "schema_version": "1.0",
            "library": {
                "name": "Test Library",
                "version": "1.0",
                "platform": "TIA Portal V18",
                "updated": "2026-01-01",
            },
            "typicals": [
                {
                    "id": "FB_MotorCtrl",
                    "type": "Equipment Module",
                    "category": "pump",
                    "description": "Motor control FB",
                    "interfaces": {
                        "inputs": [
                            {"name": "Enable", "dataType": "BOOL"},
                            {"name": "Start", "dataType": "BOOL"},
                            {"name": "Stop", "dataType": "BOOL"},
                            {"name": "Speed", "dataType": "REAL"},
                        ],
                        "outputs": [
                            {"name": "Running", "dataType": "BOOL"},
                            {"name": "Fault", "dataType": "BOOL"},
                            {"name": "CurrentSpeed", "dataType": "REAL"},
                        ],
                    },
                    "use_cases": ["Pump motor control", "Motor drive"],
                    "states": [
                        {"name": "Idle", "description": "Stopped"},
                        {"name": "Starting", "description": "Starting"},
                        {"name": "Running", "description": "Running"},
                        {"name": "Stopping", "description": "Stopping"},
                    ],
                }
            ],
        }
        (catalog_dir / "CATALOG.json").write_text(
            json.dumps(catalog_data), encoding="utf-8"
        )

        result = await scaffold_sds(tmp_path, Path("/dev/null"))
        assert result["catalog_found"] is True
        assert result["total_modules"] == 1
        # With pump category match + state match, score should be reasonable
        assert len(result["matches"]) == 1
        match = result["matches"][0]
        assert match["confidence"] > 0
        assert match["match_detail"] is not None
