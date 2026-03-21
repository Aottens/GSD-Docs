"""Document outline and section content API endpoints."""

import copy
import json
import re
import yaml
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.schemas.document import (
    DocumentOutlineResponse,
    OutlineNodeSchema,
    PlanInfoSchema,
    SectionContentResponse,
)
from app.models.project import Project
from app.config import get_settings


router = APIRouter(prefix="/api/projects/{project_id}/documents", tags=["documents"])


def _parse_plan_frontmatter(content: str) -> dict:
    """
    Parse YAML frontmatter from a PLAN.md file.

    Returns dict with parsed frontmatter keys (including must_haves, description).
    Returns {} if no frontmatter delimiters found or YAML is invalid.
    Also extracts the <objective> block as 'description'.
    """
    if not content.startswith("---"):
        return {}

    # Find closing ---
    end_pos = content.find("\n---", 3)
    if end_pos == -1:
        return {}

    yaml_content = content[3:end_pos].strip()
    try:
        frontmatter = yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return {}

    if not isinstance(frontmatter, dict):
        return {}

    # Extract <objective> block from the rest of the content after frontmatter
    remaining = content[end_pos + 4:]
    objective = _extract_objective(remaining)
    if objective:
        frontmatter["description"] = objective

    return frontmatter


def _extract_objective(content: str) -> Optional[str]:
    """
    Extract the first non-empty line from an <objective>...</objective> block.

    Returns None if no <objective> block found.
    """
    match = re.search(r'<objective>(.*?)</objective>', content, re.DOTALL)
    if not match:
        return None
    objective_text = match.group(1).strip()
    # Return the first non-empty line as the plan description
    for line in objective_text.splitlines():
        line = line.strip()
        if line:
            return line
    return None


def _build_outline_sections(fds_structure: dict, project_type: str, project_dir: Path) -> list[dict]:
    """
    Build the ordered list of outline sections from fds-structure.json.

    Applies:
    - Type C/D: inserts baseline section 1.4, shifts abbreviations to 1.5
    - Equipment module discovery: adds 4.x subsections or placeholder 4.0
    - Status detection per node from filesystem artifacts
    """
    # Step 1: Deep-copy sections to avoid mutating original
    sections = copy.deepcopy(fds_structure.get("sections", []))

    # Step 2: Type C/D baseline insertion
    if project_type in ("C", "D"):
        type_conditional = fds_structure.get("type_conditional", {})
        baseline_section = type_conditional.get("baseline_section")
        if baseline_section:
            # Find section 1 (Introduction)
            section_1 = next((s for s in sections if s["id"] == "1"), None)
            if section_1 is not None:
                children = section_1.get("children", [])
                # Shift the existing child at index 3 (Abbreviations 1.4) to 1.5
                if len(children) >= 4:
                    children[3]["id"] = "1.5"
                # Insert new baseline child at index 3
                new_baseline = {
                    "id": "1.4",
                    "title": baseline_section["title"],
                    "depth": 2,
                    "required": True,
                    "source_type": "baseline",
                    "status": "empty",
                    "has_content": False,
                    "has_plan": False,
                    "children": [],
                }
                children.insert(3, new_baseline)
                section_1["children"] = children

    # Step 3: Equipment module discovery for section 4
    section_4 = next((s for s in sections if s["id"] == "4"), None)
    if section_4 is not None:
        equipment_modules = _discover_equipment_modules(fds_structure, project_dir)
        if equipment_modules:
            section_4["children"] = equipment_modules
        else:
            # Add placeholder when no equipment modules found
            section_4["children"] = [
                {
                    "id": "4.0",
                    "title": {
                        "en": "No equipment modules yet",
                        "nl": "Nog geen apparaatmodules",
                    },
                    "depth": 2,
                    "required": False,
                    "source_type": "placeholder",
                    "status": "empty",
                    "has_content": False,
                    "has_plan": False,
                    "children": [],
                }
            ]

    # Step 4: Status detection per section node (recursive)
    planning_dir = project_dir / ".planning" / "phases"
    for section in sections:
        _enrich_node_status(section, planning_dir)

    return sections


def _discover_equipment_modules(fds_structure: dict, project_dir: Path) -> list[dict]:
    """
    Scan .planning/phases for equipment module directories.

    Equipment modules are identified by PLAN.md files in phase dirs that
    indicate equipment module content (naming pattern: phase dirs that are
    equipment-specific in the project's ROADMAP).

    Returns list of section 4.x dicts with subsections, or [] if none found.
    """
    planning_dir = project_dir / ".planning" / "phases"
    if not planning_dir.exists():
        return []

    subsection_templates = (
        fds_structure
        .get("dynamic_sections", {})
        .get("equipment_modules", {})
        .get("subsections", [])
    )

    # Scan for phase dirs that contain equipment module markers
    # Pattern: directories named like "NN-em-*" or containing EQUIPMENT_MODULE marker
    equipment_module_dirs = []
    for phase_dir in sorted(planning_dir.iterdir()):
        if not phase_dir.is_dir():
            continue
        dir_name = phase_dir.name.lower()
        # Equipment module dirs follow naming: NN-em-* or NN-equipment-*
        if re.search(r'\d+-em-', dir_name) or re.search(r'\d+-equipment-', dir_name):
            equipment_module_dirs.append(phase_dir)

    if not equipment_module_dirs:
        return []

    modules = []
    for idx, module_dir in enumerate(equipment_module_dirs, start=1):
        module_id = str(idx)
        module_name = module_dir.name
        # Create section 4.N with subsections 4.N.1 through 4.N.9
        subsections = []
        for sub in subsection_templates:
            suffix = sub["suffix"]
            sub_id = f"4.{module_id}.{suffix}"
            subsections.append({
                "id": sub_id,
                "title": sub["title"],
                "depth": 3,
                "required": sub.get("required", False),
                "source_type": "dynamic",
                "status": "empty",
                "has_content": False,
                "has_plan": False,
                "children": [],
            })
        modules.append({
            "id": f"4.{module_id}",
            "title": {"en": module_name, "nl": module_name},
            "depth": 2,
            "required": True,
            "source_type": "dynamic",
            "status": "empty",
            "has_content": False,
            "has_plan": False,
            "children": subsections,
        })

    return modules


def _enrich_node_status(node: dict, planning_dir: Path) -> None:
    """
    Detect and set status, has_content, has_plan, plan_info, preview_snippet
    for a single outline node by scanning filesystem artifacts.

    Operates recursively on children.
    """
    section_id = node["id"]

    # Ensure base fields are present
    node.setdefault("status", "empty")
    node.setdefault("has_content", False)
    node.setdefault("has_plan", False)
    node.setdefault("plan_info", None)
    node.setdefault("preview_snippet", None)
    node.setdefault("children", [])

    if planning_dir.exists():
        has_plan = False
        has_content = False
        has_verification = False
        plan_info = None
        preview_snippet = None

        # Scan all phase dirs for PLAN.md / SUMMARY.md / VERIFICATION.md mentioning this section
        for phase_dir in planning_dir.iterdir():
            if not phase_dir.is_dir():
                continue

            # Check PLAN.md files for references to this section ID
            for plan_file in phase_dir.glob("*-PLAN.md"):
                try:
                    plan_content = plan_file.read_text(encoding="utf-8")
                    # Check if this plan file references this section ID
                    if _plan_references_section(plan_content, section_id):
                        has_plan = True
                        frontmatter = _parse_plan_frontmatter(plan_content)
                        truths_raw = frontmatter.get("must_haves", {}).get("truths", [])
                        truths = truths_raw if isinstance(truths_raw, list) else []
                        objective_desc = frontmatter.get("description")
                        plan_info = PlanInfoSchema(
                            wave=frontmatter.get("wave", 0),
                            depends_on=frontmatter.get("depends_on", []) or [],
                            plan_name=frontmatter.get("plan_name", plan_file.stem),
                            plan_file=plan_file.name,
                            truths=truths,
                            description=objective_desc,
                        )
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            # Check SUMMARY.md files for section content
            for summary_file in phase_dir.glob("*-SUMMARY.md"):
                try:
                    summary_content = summary_file.read_text(encoding="utf-8")
                    if _plan_references_section(summary_content, section_id):
                        has_content = True
                        # Extract first 80 chars as preview snippet
                        snippet = _extract_preview_snippet(summary_content)
                        if snippet:
                            preview_snippet = snippet
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            # Check VERIFICATION.md
            for verif_file in phase_dir.glob("*-VERIFICATION.md"):
                try:
                    verif_content = verif_file.read_text(encoding="utf-8")
                    if _plan_references_section(verif_content, section_id):
                        has_verification = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

        # Derive status
        if has_verification:
            status = "verified"
        elif has_content:
            status = "written"
        elif has_plan:
            status = "planned"
        else:
            status = "empty"

        node["status"] = status
        node["has_content"] = has_content
        node["has_plan"] = has_plan
        node["plan_info"] = plan_info.model_dump() if plan_info else None
        node["preview_snippet"] = preview_snippet

    # Recurse into children
    for child in node.get("children", []):
        _enrich_node_status(child, planning_dir)


def _plan_references_section(content: str, section_id: str) -> bool:
    """Check if a document references a specific section ID."""
    # Match patterns like "section 1.1", "Section 1.1", "#1.1", "1.1." in context
    patterns = [
        rf'[Ss]ection\s+{re.escape(section_id)}\b',
        rf'#{re.escape(section_id)}\b',
        rf'\b{re.escape(section_id)}\.',
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False


def _extract_preview_snippet(content: str) -> Optional[str]:
    """Extract first ~80 chars of meaningful content, stripping markdown headers."""
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        # Skip empty lines, headers, and frontmatter delimiters
        if not line or line.startswith("#") or line == "---":
            continue
        # Strip leading markdown formatting
        clean = re.sub(r'^[\*_`>]+', '', line).strip()
        if clean:
            return clean[:80]
    return None


def _get_project_dir(project_id: int) -> Path:
    """Get the project directory path from PROJECT_ROOT setting."""
    settings = get_settings()
    return Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)


@router.get("/outline", response_model=DocumentOutlineResponse)
async def get_document_outline(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> DocumentOutlineResponse:
    """Get full FDS section tree with status per node for a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    settings = get_settings()
    fds_path = Path(settings.V1_DOCS_PATH).expanduser().resolve() / "templates" / "fds-structure.json"
    try:
        with open(fds_path, "r", encoding="utf-8") as f:
            fds_structure = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to load fds-structure.json: {e}")

    project_dir = _get_project_dir(project_id)
    sections_data = _build_outline_sections(fds_structure, project.type.value, project_dir)

    # Convert dicts to OutlineNodeSchema objects
    sections = [_dict_to_outline_node(s) for s in sections_data]

    return DocumentOutlineResponse(
        project_id=project_id,
        project_language=project.language.value,
        sections=sections,
    )


def _dict_to_outline_node(data: dict) -> OutlineNodeSchema:
    """Recursively convert a section dict to OutlineNodeSchema."""
    children = [_dict_to_outline_node(c) for c in data.get("children", [])]
    plan_info = None
    if data.get("plan_info"):
        pi = data["plan_info"]
        if isinstance(pi, dict):
            plan_info = PlanInfoSchema(**pi)
        elif isinstance(pi, PlanInfoSchema):
            plan_info = pi
    return OutlineNodeSchema(
        id=data["id"],
        title=data["title"],
        depth=data["depth"],
        required=data.get("required", True),
        source_type=data["source_type"],
        status=data.get("status", "empty"),
        has_content=data.get("has_content", False),
        has_plan=data.get("has_plan", False),
        plan_info=plan_info,
        preview_snippet=data.get("preview_snippet"),
        children=children,
    )


@router.get("/sections/{section_id:path}/content", response_model=SectionContentResponse)
async def get_section_content(
    project_id: int,
    section_id: str,
    db: AsyncSession = Depends(get_db),
) -> SectionContentResponse:
    """Get markdown content and plan info for a specific section."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    project_dir = _get_project_dir(project_id)
    planning_dir = project_dir / ".planning" / "phases"

    markdown_content: Optional[str] = None
    plan_info: Optional[PlanInfoSchema] = None
    has_plan = False
    has_content = False
    has_verification = False

    if planning_dir.exists():
        for phase_dir in planning_dir.iterdir():
            if not phase_dir.is_dir():
                continue

            # Check for PLAN.md referencing this section
            for plan_file in phase_dir.glob("*-PLAN.md"):
                try:
                    plan_content = plan_file.read_text(encoding="utf-8")
                    if _plan_references_section(plan_content, section_id):
                        has_plan = True
                        frontmatter = _parse_plan_frontmatter(plan_content)
                        truths_raw = frontmatter.get("must_haves", {}).get("truths", [])
                        truths = truths_raw if isinstance(truths_raw, list) else []
                        objective_desc = frontmatter.get("description")
                        plan_info = PlanInfoSchema(
                            wave=frontmatter.get("wave", 0),
                            depends_on=frontmatter.get("depends_on", []) or [],
                            plan_name=frontmatter.get("plan_name", plan_file.stem),
                            plan_file=plan_file.name,
                            truths=truths,
                            description=objective_desc,
                        )
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            # Check for SUMMARY.md with content for this section
            for summary_file in phase_dir.glob("*-SUMMARY.md"):
                try:
                    summary_content = summary_file.read_text(encoding="utf-8")
                    if _plan_references_section(summary_content, section_id):
                        has_content = True
                        markdown_content = summary_content
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            # Check for VERIFICATION.md
            for verif_file in phase_dir.glob("*-VERIFICATION.md"):
                try:
                    verif_content = verif_file.read_text(encoding="utf-8")
                    if _plan_references_section(verif_content, section_id):
                        has_verification = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

    # Derive status
    if has_verification:
        status = "verified"
    elif has_content:
        status = "written"
    elif has_plan:
        status = "planned"
    else:
        status = "empty"

    return SectionContentResponse(
        section_id=section_id,
        status=status,
        markdown_content=markdown_content,
        plan_info=plan_info,
    )
