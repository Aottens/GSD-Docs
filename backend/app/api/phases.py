"""Phase timeline API with filesystem-based status detection."""

import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.schemas.phase import PhaseTimelineResponse, PhaseStatusResponse, ContextFilesResponse
from app.schemas.verification import VerificationDetailResponse, TruthResult
from app.models.project import Project
from app.config import get_settings
from app.config_phases import PROJECT_TYPE_PHASES, get_cli_command


router = APIRouter(prefix="/api/projects/{project_id}/phases", tags=["phases"])


def _get_phases_for_project_type(project_type: str) -> list[dict]:
    """Get phase definitions for a project type from v1.0 extracted data."""
    phases = PROJECT_TYPE_PHASES.get(project_type, [])
    return [
        {"number": p["number"], "name": p["name"], "goal": p["description"]}
        for p in phases
    ]


def _derive_phase_status(project_dir: Path, phase_number: int) -> dict:
    """
    Derive phase status from filesystem artifacts.
    Checks for: CONTEXT.md, PLAN.md, SUMMARY.md (content), VERIFICATION.md, REVIEW.md
    """
    phase_pattern = f"{phase_number:02d}-*"
    planning_dir = project_dir / ".planning" / "phases"

    phase_dirs = list(planning_dir.glob(phase_pattern)) if planning_dir.exists() else []
    if not phase_dirs:
        return {
            "status": "not_started",
            "sub_status": None,
            "has_context": False,
            "has_plans": False,
            "has_content": False,
            "has_verification": False,
            "has_review": False,
        }

    phase_dir = phase_dirs[0]
    has_context = any(phase_dir.glob(f"{phase_number:02d}-CONTEXT.md"))
    has_plans = any(phase_dir.glob(f"{phase_number:02d}-*-PLAN.md"))
    has_content = any(phase_dir.glob(f"{phase_number:02d}-*-SUMMARY.md"))
    has_verification = any(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
    has_review = any(phase_dir.glob(f"{phase_number:02d}-REVIEW.md"))

    if has_review:
        status, sub_status = "reviewed", "Beoordeeld"
    elif has_verification:
        status, sub_status = "verified", "Geverifieerd"
    elif has_content:
        status, sub_status = "written", "Geschreven"
    elif has_plans:
        status, sub_status = "planned", "Gepland"
    elif has_context:
        status, sub_status = "discussed", "Besproken"
    else:
        status, sub_status = "not_started", None

    return {
        "status": status,
        "sub_status": sub_status,
        "has_context": has_context,
        "has_plans": has_plans,
        "has_content": has_content,
        "has_verification": has_verification,
        "has_review": has_review,
    }


def _extract_decisions(content: str) -> list[str]:
    """Extract bullet decisions from <decisions> XML section of CONTEXT.md."""
    match = re.search(r'<decisions>(.*?)</decisions>', content, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    decisions = re.findall(r'^[-*]\s+(.+)', block, re.MULTILINE)
    return [d.strip() for d in decisions if d.strip()]


def _extract_verification_summary(content: str) -> dict:
    """Extract score and gap count from VERIFICATION.md."""
    score_match = re.search(r'(\d+)/(\d+)\s+levels?\s+passed', content, re.IGNORECASE)
    gap_matches = re.findall(r'\|\s*(CRITICAL|MAJOR|MINOR)\s*\|', content, re.IGNORECASE)
    score = f"{score_match.group(1)}/{score_match.group(2)}" if score_match else None
    severity = {
        "critical": sum(1 for g in gap_matches if g.upper() == "CRITICAL"),
        "major": sum(1 for g in gap_matches if g.upper() == "MAJOR"),
        "minor": sum(1 for g in gap_matches if g.upper() == "MINOR"),
    }
    return {
        "score": score,
        "gap_count": len(gap_matches),
        "severity": severity,
    }


def _get_project_dir(project_id: int) -> Path:
    """Get the project directory path from PROJECT_ROOT setting."""
    settings = get_settings()
    return Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)


@router.get("", response_model=PhaseTimelineResponse)
async def get_phase_timeline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseTimelineResponse:
    """Get all phases with filesystem-derived status for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    phases_data = _get_phases_for_project_type(project.type.value)
    project_dir = _get_project_dir(project_id)

    phases = []
    for phase_data in phases_data:
        phase_number = phase_data["number"]
        status_info = _derive_phase_status(project_dir, phase_number)
        cli_command = get_cli_command(status_info["status"], phase_number)

        phases.append(PhaseStatusResponse(
            number=phase_number,
            name=phase_data["name"],
            goal=phase_data["goal"],
            cli_command=cli_command,
            **status_info,
        ))

    return PhaseTimelineResponse(project_id=project_id, phases=phases)


@router.get("/{phase_number}/context-files", response_model=ContextFilesResponse)
async def get_phase_context_files(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
) -> ContextFilesResponse:
    """Read CONTEXT.md and VERIFICATION.md from project filesystem."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    planning_dir = project_dir / ".planning" / "phases"
    phase_dirs = list(planning_dir.glob(f"{phase_number:02d}-*")) if planning_dir.exists() else []

    decisions: list[str] = []
    verification_score: Optional[str] = None
    verification_gaps: Optional[int] = None
    verification_severity: Optional[dict] = None
    has_context = False
    has_verification = False

    if phase_dirs:
        phase_dir = phase_dirs[0]

        # Read CONTEXT.md
        context_files = list(phase_dir.glob(f"{phase_number:02d}-CONTEXT.md"))
        if context_files:
            try:
                content = context_files[0].read_text(encoding="utf-8")
                decisions = _extract_decisions(content)
                has_context = True
            except (OSError, UnicodeDecodeError):
                pass

        # Read VERIFICATION.md
        verification_files = list(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
        if verification_files:
            try:
                content = verification_files[0].read_text(encoding="utf-8")
                summary = _extract_verification_summary(content)
                verification_score = summary["score"]
                verification_gaps = summary["gap_count"]
                verification_severity = summary["severity"]
                has_verification = True
            except (OSError, UnicodeDecodeError):
                pass

    return ContextFilesResponse(
        decisions=decisions,
        verification_score=verification_score,
        verification_gaps=verification_gaps,
        verification_severity=verification_severity,
        has_context=has_context,
        has_verification=has_verification,
    )


def _parse_verification_summary_table(content: str) -> list[dict]:
    """Parse the summary table from VERIFICATION.md into per-truth dicts.

    Returns list of dicts:
        {"description": str, "exists": str, "substantive": str,
         "complete": str, "consistent": str, "standards": str, "status": str}

    Checkmark mapping:
        ✓ / ✔ -> "pass"
        ⚠ / ⚠️  -> "gap"
        "-"    -> "-"
        "N/A"  -> "n/a"
    """

    def _map_cell(cell: str) -> str:
        cell = cell.strip()
        if cell in ("✓", "✔", "✅"):
            return "pass"
        if cell in ("⚠", "⚠️"):
            return "gap"
        if cell.upper() in ("N/A", "N\\A"):
            return "n/a"
        if cell == "-":
            return "-"
        # Fallback: lowercase normalise
        if "pass" in cell.lower():
            return "pass"
        if "gap" in cell.lower():
            return "gap"
        return cell.lower() if cell else "-"

    rows: list[dict] = []
    in_table = False
    header_seen = False

    for line in content.splitlines():
        stripped = line.strip()

        # Detect header row
        if not in_table and re.match(r'^\|\s*Truth', stripped, re.IGNORECASE):
            in_table = True
            header_seen = False
            continue

        if in_table:
            # Skip separator row (---|--- pattern)
            if re.match(r'^\|[-|\s]+\|', stripped):
                header_seen = True
                continue

            # Stop at next section heading or blank line after data rows
            if stripped.startswith("#") or (not stripped and rows):
                break

            if not stripped.startswith("|"):
                if rows:
                    break
                continue

            # Parse data row
            cells = [c.strip() for c in stripped.split("|")]
            # cells[0] is empty (before first |), cells[-1] is empty (after last |)
            cells = [c for c in cells if c != ""][:]
            if len(cells) < 7:
                continue

            description = cells[0].strip()
            if not description or description.lower() in ("truth", "---"):
                continue

            row = {
                "description": description,
                "exists": _map_cell(cells[1]) if len(cells) > 1 else "-",
                "substantive": _map_cell(cells[2]) if len(cells) > 2 else "-",
                "complete": _map_cell(cells[3]) if len(cells) > 3 else "-",
                "consistent": _map_cell(cells[4]) if len(cells) > 4 else "-",
                "standards": _map_cell(cells[5]) if len(cells) > 5 else "-",
                "status": cells[6].strip().upper() if len(cells) > 6 else "UNKNOWN",
            }
            rows.append(row)

    return rows


def _parse_verification_detail(content: str) -> VerificationDetailResponse:
    """Parse full VERIFICATION.md content into VerificationDetailResponse."""

    # Extract overall status
    status_match = re.search(
        r'\*\*Status:\*\*\s*(PASS|GAPS_FOUND(?:\s*\(ESCALATED\))?)',
        content,
        re.MULTILINE,
    )
    status = status_match.group(1).strip() if status_match else "UNKNOWN"
    is_blocked = "ESCALATED" in status

    # Extract cycle info
    cycle_match = re.search(r'\*\*Cycle:\*\*\s*(\d+)\s+of\s+(\d+)', content, re.MULTILINE)
    current_cycle = int(cycle_match.group(1)) if cycle_match else 1
    max_cycles = int(cycle_match.group(2)) if cycle_match else 2

    # Parse summary table for quick per-truth status
    summary_rows = _parse_verification_summary_table(content)
    summary_map: dict[str, dict] = {r["description"]: r for r in summary_rows}

    # Split on ### Truth blocks for detailed findings
    truth_blocks = re.split(r'(?=###\s+Truth\s+\d+)', content)

    truths: list[TruthResult] = []

    for block in truth_blocks:
        if not re.match(r'###\s+Truth\s+\d+', block.strip()):
            continue

        # Extract truth title line to get description
        title_match = re.match(r'###\s+Truth\s+\d+:\s*(.+)', block.strip())
        if not title_match:
            continue
        truth_description = title_match.group(1).strip()

        # Extract status from block
        block_status_match = re.search(
            r'\*\*Status:\*\*\s*(PASS|GAP(?:\s*\(Level\s*\d+\s*-\s*[^)]+\))?)',
            block,
        )
        truth_status = "UNKNOWN"
        failed_level: Optional[str] = None
        if block_status_match:
            raw = block_status_match.group(1).strip()
            if raw == "PASS":
                truth_status = "PASS"
            else:
                truth_status = "GAP"
                level_match = re.search(r'Level\s*\d+\s*-\s*([^)]+)', raw)
                if level_match:
                    failed_level = level_match.group(0).strip()

        # Extract gap description (between **Gap description:** and **Evidence:** or ---)
        gap_description: Optional[str] = None
        gap_match = re.search(
            r'\*\*Gap description:\*\*\s*(.*?)(?=\*\*Evidence:\*\*|^---|\Z)',
            block,
            re.DOTALL | re.MULTILINE,
        )
        if gap_match:
            gap_description = gap_match.group(1).strip() or None

        # Extract evidence file paths
        evidence_files: list[str] = []
        evidence_section = re.search(
            r'\*\*Evidence:\*\*\s*(.*?)(?=\*\*|^---|\Z)',
            block,
            re.DOTALL | re.MULTILINE,
        )
        if evidence_section:
            evidence_files = re.findall(r'-\s*File:\s*(.+)', evidence_section.group(1))
            evidence_files = [f.strip() for f in evidence_files]

        # Extract standards violations from gap description
        standards_violations: list[dict] = []
        if gap_description:
            violation_matches = re.findall(
                r'((?:PackML|ISA-88|IEC|EN|NEN)\s*[§#]?[\d.]+(?:-[\d.]+)?)',
                gap_description,
                re.IGNORECASE,
            )
            for ref in violation_matches:
                standards_violations.append({
                    "reference": ref.strip(),
                    "text": gap_description,
                })

        # Build per-level dict from summary table row (if available)
        levels: dict = {}
        if truth_description in summary_map:
            row = summary_map[truth_description]
            levels = {
                "exists": row["exists"],
                "substantive": row["substantive"],
                "complete": row["complete"],
                "consistent": row["consistent"],
                "standards": row["standards"],
            }

        truths.append(TruthResult(
            description=truth_description,
            status=truth_status,
            levels=levels,
            failed_level=failed_level,
            gap_description=gap_description,
            evidence_files=evidence_files,
            standards_violations=standards_violations,
        ))

    passed_count = sum(1 for t in truths if t.status == "PASS")
    gap_count = sum(1 for t in truths if t.status == "GAP")

    return VerificationDetailResponse(
        has_verification=True,
        status=status,
        current_cycle=current_cycle,
        max_cycles=max_cycles,
        is_blocked=is_blocked,
        truths=truths,
        total_truths=len(truths),
        passed_count=passed_count,
        gap_count=gap_count,
    )


@router.get("/{phase_number}/verification-detail", response_model=VerificationDetailResponse)
async def get_phase_verification_detail(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db),
) -> VerificationDetailResponse:
    """Return parsed VERIFICATION.md data for a phase as structured verification detail."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    planning_dir = project_dir / ".planning" / "phases"
    phase_dirs = list(planning_dir.glob(f"{phase_number:02d}-*")) if planning_dir.exists() else []

    if not phase_dirs:
        return VerificationDetailResponse(has_verification=False)

    phase_dir = phase_dirs[0]
    verification_files = list(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
    if not verification_files:
        return VerificationDetailResponse(has_verification=False)

    try:
        content = verification_files[0].read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return VerificationDetailResponse(has_verification=False)

    return _parse_verification_detail(content)


@router.get("/{phase_number}", response_model=PhaseStatusResponse)
async def get_phase_status(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseStatusResponse:
    """Get detailed status for a single phase."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    phases_data = _get_phases_for_project_type(project.type.value)
    phase_data = next(
        (p for p in phases_data if p["number"] == phase_number), None
    )
    if not phase_data:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found for project type {project.type.value}")

    project_dir = _get_project_dir(project_id)
    status_info = _derive_phase_status(project_dir, phase_number)
    cli_command = get_cli_command(status_info["status"], phase_number)

    return PhaseStatusResponse(
        number=phase_number,
        name=phase_data["name"],
        goal=phase_data["goal"],
        cli_command=cli_command,
        **status_info,
    )
