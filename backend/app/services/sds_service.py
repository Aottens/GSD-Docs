"""SDS scaffolding service — typicals matching with confidence scoring.

Implements Step 4 of gsd-docs-industrial/workflows/generate-sds.md.

Scoring weights per SSOT:
  - I/O match:              40%  (compare module I/O vs typical interfaces)
  - use_cases Jaccard:      30%  (keyword overlap)
  - State count similarity: 20%  (abs difference penalty)
  - Category match:         10%  (category keyword in module keywords)
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Catalog loading
# ---------------------------------------------------------------------------

def load_catalog(project_dir: Path) -> Optional[list[dict]]:
    """Load CATALOG.json from project_dir/references/typicals/CATALOG.json.

    Returns list of typical dicts if found and parseable, None otherwise
    (triggers skeleton mode).
    """
    catalog_path = project_dir / "references" / "typicals" / "CATALOG.json"
    if not catalog_path.exists():
        return None
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        typicals = data.get("typicals")
        if isinstance(typicals, list) and len(typicals) > 0:
            return typicals
        return None
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Equipment module extraction
# ---------------------------------------------------------------------------

def _count_io_from_typical(typical: dict) -> dict[str, int]:
    """Count DI/DO/AI/AO from a typical's interfaces.inputs and outputs arrays.

    BOOL dataType → digital (DI for inputs, DO for outputs)
    INT/REAL/WORD dataType → analog (AI for inputs, AO for outputs)
    """
    counts = {"DI": 0, "DO": 0, "AI": 0, "AO": 0}
    interfaces = typical.get("interfaces", {})

    for inp in interfaces.get("inputs", []):
        dtype = inp.get("dataType", "BOOL").upper()
        if dtype in ("BOOL",):
            counts["DI"] += 1
        elif dtype in ("INT", "REAL", "DINT", "UINT", "DWORD", "WORD", "LREAL"):
            counts["AI"] += 1
        # Ignore UDT / complex types in I/O count

    for out in interfaces.get("outputs", []):
        dtype = out.get("dataType", "BOOL").upper()
        if dtype in ("BOOL",):
            counts["DO"] += 1
        elif dtype in ("INT", "REAL", "DINT", "UINT", "DWORD", "WORD", "LREAL"):
            counts["AO"] += 1

    return counts


def extract_equipment_modules(project_dir: Path, v1_docs_path: Path) -> list[dict]:
    """Extract equipment module profiles from project .planning/phases/ directories.

    Scans for phase dirs matching pattern NN-em-* or NN-equipment-*. For each,
    reads SUMMARY.md files to extract I/O counts, keywords, and state counts.

    Returns list of dicts:
      {"name": str, "io": {"DI": int, "DO": int, "AI": int, "AO": int},
       "keywords": set[str], "state_count": int}
    """
    planning_dir = project_dir / ".planning" / "phases"
    if not planning_dir.exists():
        return []

    equipment_module_dirs = []
    try:
        for phase_dir in sorted(planning_dir.iterdir()):
            if not phase_dir.is_dir():
                continue
            dir_name = phase_dir.name.lower()
            if re.search(r"\d+-em-", dir_name) or re.search(r"\d+-equipment-", dir_name):
                equipment_module_dirs.append(phase_dir)
    except OSError:
        return []

    if not equipment_module_dirs:
        return []

    modules = []
    for module_dir in equipment_module_dirs:
        name = module_dir.name
        # Derive human-readable name: strip leading NN- and replace dashes with spaces
        clean_name = re.sub(r"^\d+-(?:em|equipment)-", "", name, flags=re.IGNORECASE)
        clean_name = clean_name.replace("-", " ").replace("_", " ")

        io_counts: dict[str, int] = {"DI": 0, "DO": 0, "AI": 0, "AO": 0}
        keywords: set[str] = set(_tokenize(clean_name))
        state_count = 0

        # Read SUMMARY.md files in the module dir
        for summary_file in module_dir.glob("*-SUMMARY.md"):
            try:
                content = summary_file.read_text(encoding="utf-8")
                # Count I/O type mentions
                for io_type in ("DI", "DO", "AI", "AO"):
                    matches = re.findall(
                        rf'\b(\d+)\s*{io_type}\b|\b{io_type}\s*:\s*(\d+)\b',
                        content, re.IGNORECASE
                    )
                    for m in matches:
                        val_str = m[0] or m[1]
                        if val_str.isdigit():
                            io_counts[io_type] = max(io_counts[io_type], int(val_str))

                # Count stateDiagram states: lines like "  state_name : description"
                # or stateDiagram nodes
                state_matches = re.findall(
                    r'stateDiagram(?:-v2)?.*?```',
                    content,
                    re.DOTALL | re.IGNORECASE
                )
                for block in state_matches:
                    # Count state declarations (lines that are not arrows or [*])
                    state_lines = re.findall(r'^\s+(\w+)(?:\s*:|\s*-->)', block, re.MULTILINE)
                    unique_states = {
                        s for s in state_lines
                        if s not in ("[*]", "-->", "note", "end", "note")
                        and not s.startswith("[")
                    }
                    state_count = max(state_count, len(unique_states))

                # Extract keywords from markdown headings (## Section N: Keywords)
                heading_words = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
                for heading in heading_words:
                    keywords.update(_tokenize(heading))
            except (OSError, UnicodeDecodeError):
                continue

        modules.append({
            "name": clean_name,
            "io": io_counts,
            "keywords": keywords,
            "state_count": state_count,
        })

    return modules


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase alphabetical tokens (3+ chars)."""
    return [
        w.lower()
        for w in re.findall(r"[a-zA-Z]+", text)
        if len(w) >= 3
    ]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_typical(module: dict, typical: dict) -> float:
    """Calculate confidence score for a module-to-typical match (0-100).

    Weights per generate-sds.md Step 4:
      - I/O match:      40%
      - Jaccard:        30%
      - State count:    20%
      - Category:       10%
    """
    # --- I/O match (40%) ---
    module_io = module["io"]
    typical_io = _count_io_from_typical(typical)

    total_module_io = sum(module_io.values())
    total_diff = sum(
        abs(module_io.get(t, 0) - typical_io.get(t, 0))
        for t in ("DI", "DO", "AI", "AO")
    )
    io_score = 40 * (1 - min(total_diff / max(total_module_io, 1), 1))

    # --- use_cases Jaccard similarity (30%) ---
    module_kw = set(module["keywords"])
    typical_uc = set(
        word.lower()
        for uc in typical.get("use_cases", [])
        for word in re.findall(r"[a-zA-Z]+", uc)
        if len(word) >= 3
    )
    union = module_kw | typical_uc
    intersection = module_kw & typical_uc
    jaccard = len(intersection) / len(union) if union else 0.0
    keyword_score = jaccard * 30

    # --- State count (20%) ---
    module_states = module["state_count"]
    typical_states = len(typical.get("states", []))
    state_diff = abs(module_states - typical_states)
    if state_diff == 0:
        state_score = 20
    elif state_diff == 1:
        state_score = 15
    elif state_diff == 2:
        state_score = 10
    else:
        state_score = 5

    # --- Category (10%) ---
    typical_cat = typical.get("category", "").lower()
    module_kw_lower = {kw.lower() for kw in module["keywords"]}
    category_score = 10 if typical_cat in module_kw_lower else 0

    return io_score + keyword_score + state_score + category_score


def classify_confidence(score: float) -> tuple[str, str]:
    """Return (confidence_level, status) for a given score.

    HIGH   (>=70): matched
    MEDIUM (40-69): low_confidence
    LOW    (1-39): new_typical_needed
    UNMATCHED (0): new_typical_needed
    """
    if score >= 70:
        return ("HIGH", "matched")
    elif score >= 40:
        return ("MEDIUM", "low_confidence")
    elif score > 0:
        return ("LOW", "new_typical_needed")
    else:
        return ("UNMATCHED", "new_typical_needed")


# ---------------------------------------------------------------------------
# Score breakdown helpers
# ---------------------------------------------------------------------------

def _compute_score_breakdown(module: dict, typical: dict) -> dict:
    """Compute per-dimension scores for a module-typical pair."""
    module_io = module["io"]
    typical_io = _count_io_from_typical(typical)
    total_module_io = sum(module_io.values())
    total_diff = sum(
        abs(module_io.get(t, 0) - typical_io.get(t, 0))
        for t in ("DI", "DO", "AI", "AO")
    )
    io_score = 40 * (1 - min(total_diff / max(total_module_io, 1), 1))

    module_kw = set(module["keywords"])
    typical_uc = set(
        word.lower()
        for uc in typical.get("use_cases", [])
        for word in re.findall(r"[a-zA-Z]+", uc)
        if len(word) >= 3
    )
    union = module_kw | typical_uc
    intersection = module_kw & typical_uc
    jaccard = len(intersection) / len(union) if union else 0.0
    keyword_score = jaccard * 30

    module_states = module["state_count"]
    typical_states = len(typical.get("states", []))
    state_diff = abs(module_states - typical_states)
    if state_diff == 0:
        state_score = 20
    elif state_diff == 1:
        state_score = 15
    elif state_diff == 2:
        state_score = 10
    else:
        state_score = 5

    typical_cat = typical.get("category", "").lower()
    module_kw_lower = {kw.lower() for kw in module["keywords"]}
    category_score = 10 if typical_cat in module_kw_lower else 0

    return {
        "io_score": round(io_score, 2),
        "keyword_score": round(keyword_score, 2),
        "state_score": float(state_score),
        "category_score": float(category_score),
        "typical_io": typical_io,
        "module_io": module_io,
        "state_diff": state_diff,
        "typical_cat": typical_cat,
    }


def _build_reason(breakdown: dict, confidence_level: str, typical_name: str) -> str:
    """Build human-readable reason string for a match result."""
    summary = (
        f"I/O match {breakdown['io_score']:.1f}/40, "
        f"keywords {breakdown['keyword_score']:.1f}/30, "
        f"states {breakdown['state_score']:.0f}/20, "
        f"category {breakdown['category_score']:.0f}/10"
    )
    if confidence_level == "HIGH":
        return summary
    else:
        # Identify weakest dimension
        _max_scores = {"I/O match": 40, "keyword overlap": 30, "state count": 20, "category": 10}
        scores = {
            "I/O match": breakdown["io_score"],
            "keyword overlap": breakdown["keyword_score"],
            "state count": breakdown["state_score"],
            "category": breakdown["category_score"],
        }
        weakest = min(scores, key=lambda k: scores[k] / _max_scores[k])
        weakest_score = scores[weakest]
        weakest_max = _max_scores[weakest]
        return (
            f"Low confidence against '{typical_name}' — weakest: {weakest} "
            f"({weakest_score:.1f}/{weakest_max}). "
            + summary
        )


# ---------------------------------------------------------------------------
# Main scaffold function
# ---------------------------------------------------------------------------

async def scaffold_sds(project_dir: Path, v1_docs_path: Path) -> dict:
    """Run SDS scaffolding: extract modules, match against catalog, persist results.

    Returns the results dict (matches SdsResultsResponse schema).
    """
    from app.schemas.sds import (
        MatchDetailSchema,
        SdsResultsResponse,
        TypicalMatchSchema,
    )

    modules = extract_equipment_modules(project_dir, v1_docs_path)
    catalog = load_catalog(project_dir)
    catalog_found = catalog is not None
    scaffold_date = datetime.now(tz=timezone.utc)

    matches: list[TypicalMatchSchema] = []

    if not catalog_found:
        # Skeleton mode: all modules are UNMATCHED / NIEUW TYPICAL NODIG
        for mod in modules:
            matches.append(
                TypicalMatchSchema(
                    equipment_module=mod["name"],
                    matched_typical=None,
                    typical_id=None,
                    confidence=0.0,
                    confidence_level="UNMATCHED",
                    status="new_typical_needed",
                    match_detail=None,
                )
            )
    else:
        # Full matching mode
        for mod in modules:
            best_score = -1.0
            best_typical = None

            # Score every typical
            scored = []
            for typical in catalog:
                s = score_typical(mod, typical)
                scored.append((s, typical))
                if s > best_score:
                    best_score = s
                    best_typical = typical

            confidence_level, status = classify_confidence(best_score)
            cli_hint = f"/doc:generate-sds --refine {mod['name'].replace(' ', '_')}"

            if best_typical is not None and best_score > 0:
                breakdown = _compute_score_breakdown(mod, best_typical)

                # Find second-best for "closest_match" on low-confidence results
                scored_sorted = sorted(scored, key=lambda x: x[0], reverse=True)
                closest_match = None
                closest_confidence = None
                if confidence_level in ("LOW", "UNMATCHED") and len(scored_sorted) >= 1:
                    closest_match = scored_sorted[0][1].get("id") or scored_sorted[0][1].get("description", "unknown")
                    closest_confidence = round(scored_sorted[0][0], 2)

                reason = _build_reason(breakdown, confidence_level, best_typical.get("id", "unknown"))

                match_detail = MatchDetailSchema(
                    reason=reason,
                    io_score=breakdown["io_score"],
                    keyword_score=breakdown["keyword_score"],
                    state_score=breakdown["state_score"],
                    category_score=breakdown["category_score"],
                    closest_match=closest_match,
                    closest_confidence=closest_confidence,
                    cli_hint=cli_hint,
                )
                matches.append(
                    TypicalMatchSchema(
                        equipment_module=mod["name"],
                        matched_typical=best_typical.get("description"),
                        typical_id=best_typical.get("id"),
                        confidence=round(best_score, 2),
                        confidence_level=confidence_level,
                        status=status,
                        match_detail=match_detail,
                    )
                )
            else:
                # No catalog entries or all scored 0
                matches.append(
                    TypicalMatchSchema(
                        equipment_module=mod["name"],
                        matched_typical=None,
                        typical_id=None,
                        confidence=0.0,
                        confidence_level="UNMATCHED",
                        status="new_typical_needed",
                        match_detail=MatchDetailSchema(
                            reason="No catalog typical scored above 0 for this module.",
                            io_score=0.0,
                            keyword_score=0.0,
                            state_score=0.0,
                            category_score=0.0,
                            closest_match=None,
                            closest_confidence=None,
                            cli_hint=cli_hint,
                        ),
                    )
                )

    # Compute summary counts
    matched_count = sum(1 for m in matches if m.confidence_level == "HIGH")
    low_confidence_count = sum(1 for m in matches if m.confidence_level == "MEDIUM")
    unmatched_count = sum(1 for m in matches if m.confidence_level in ("LOW", "UNMATCHED"))

    result = SdsResultsResponse(
        project_id=0,  # will be overwritten by caller
        scaffold_date=scaffold_date,
        total_modules=len(matches),
        matched_count=matched_count,
        low_confidence_count=low_confidence_count,
        unmatched_count=unmatched_count,
        matches=matches,
        catalog_found=catalog_found,
    )

    # Persist to project_dir/output/sds-results.json
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    sds_results_path = output_dir / "sds-results.json"
    with open(sds_results_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(mode="json"), f, indent=2, default=str)

    return result.model_dump(mode="json")
