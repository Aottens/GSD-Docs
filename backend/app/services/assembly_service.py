"""FDS document assembly service.

Collects phase SUMMARY.md files, orders sections per fds-structure.json,
resolves cross-references, and writes assembled markdown to output/.
"""

import copy
import json
import re
import yaml
from pathlib import Path
from typing import Callable, Optional

from app.schemas.export import AssemblyReadinessSchema


def _parse_project_type(project_dir: Path) -> str:
    """Read PROJECT.md and extract the project type field from YAML frontmatter.

    Returns 'A' as default if the field is missing or the file doesn't exist.
    """
    project_md = project_dir / ".planning" / "PROJECT.md"
    if not project_md.exists():
        return "A"
    try:
        content = project_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return "A"
        end_pos = content.find("\n---", 3)
        if end_pos == -1:
            return "A"
        yaml_content = content[3:end_pos].strip()
        frontmatter = yaml.safe_load(yaml_content)
        if isinstance(frontmatter, dict):
            return str(frontmatter.get("type", "A"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        pass
    return "A"


def _load_fds_structure(v1_docs_path: Path) -> dict:
    """Load and return fds-structure.json from the v1 docs templates directory."""
    fds_path = v1_docs_path / "templates" / "fds-structure.json"
    with open(fds_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_section_tree(
    fds_structure: dict,
    project_type: str,
    language: str,
) -> list[tuple[str, str, int]]:
    """Build an ordered flat list of (section_id, title, depth) tuples.

    Uses depth-first traversal of fds-structure.json sections.
    For Type C/D: inserts baseline section 1.4 and shifts abbreviations to 1.5.
    Selects title by language ('en' or 'nl' key).
    """
    sections = copy.deepcopy(fds_structure.get("sections", []))

    # Type C/D: insert baseline section
    if project_type in ("C", "D"):
        type_conditional = fds_structure.get("type_conditional", {})
        baseline_section = type_conditional.get("baseline_section")
        if baseline_section:
            section_1 = next((s for s in sections if s["id"] == "1"), None)
            if section_1 is not None:
                children = section_1.get("children", [])
                if len(children) >= 4:
                    children[3]["id"] = "1.5"
                new_baseline = {
                    "id": "1.4",
                    "title": baseline_section["title"],
                    "depth": 2,
                    "required": True,
                    "source_type": "baseline",
                    "children": [],
                }
                children.insert(3, new_baseline)
                section_1["children"] = children

    result: list[tuple[str, str, int]] = []

    def _traverse(nodes: list[dict]) -> None:
        for node in nodes:
            title_map = node.get("title", {})
            title = title_map.get(language) or title_map.get("nl") or title_map.get("en", "")
            result.append((node["id"], title, node.get("depth", 1)))
            _traverse(node.get("children", []))

    _traverse(sections)
    return result


def _collect_summary_files(project_dir: Path) -> list[Path]:
    """Return sorted list of SUMMARY.md files found in .planning/phases/."""
    planning_dir = project_dir / ".planning" / "phases"
    if not planning_dir.exists():
        return []
    summaries = []
    for phase_dir in sorted(planning_dir.iterdir()):
        if not phase_dir.is_dir():
            continue
        for summary_file in sorted(phase_dir.glob("*-SUMMARY.md")):
            summaries.append(summary_file)
    return summaries


def _resolve_cross_references(text: str) -> str:
    """Replace {ref:X.Y} with 'Section X.Y' and {fig:N} with 'Figure N'."""
    text = re.sub(r'\{ref:([0-9.]+)\}', lambda m: f"Section {m.group(1)}", text)
    text = re.sub(r'\{fig:(\d+)\}', lambda m: f"Figure {m.group(1)}", text)
    return text


def _iec_heading(title: str, depth: int, number: str) -> str:
    """Return an IEC-style numbered heading string."""
    prefix = "#" * depth
    return f"{prefix} {number} {title}"


async def check_assembly_readiness(
    project_dir: Path,
    mode: str,
) -> AssemblyReadinessSchema:
    """Check whether the project is ready for FDS assembly.

    Draft mode: at least one SUMMARY.md must exist anywhere in phases.
    Final mode: every phase dir with a SUMMARY.md must also have a REVIEW.md.
    """
    summary_files = _collect_summary_files(project_dir)
    has_content = len(summary_files) > 0

    if not has_content:
        return AssemblyReadinessSchema(
            ready=False,
            mode=mode,
            unreviewed_phases=[],
            has_content=False,
        )

    if mode == "draft":
        return AssemblyReadinessSchema(
            ready=True,
            mode=mode,
            unreviewed_phases=[],
            has_content=True,
        )

    # Final mode: check every phase dir with SUMMARY.md also has REVIEW.md
    planning_dir = project_dir / ".planning" / "phases"
    unreviewed_phases: list[str] = []

    if planning_dir.exists():
        for phase_dir in sorted(planning_dir.iterdir()):
            if not phase_dir.is_dir():
                continue
            summaries = list(phase_dir.glob("*-SUMMARY.md"))
            if not summaries:
                continue
            reviews = list(phase_dir.glob("*-REVIEW.md"))
            if not reviews:
                unreviewed_phases.append(phase_dir.name)

    ready = len(unreviewed_phases) == 0
    return AssemblyReadinessSchema(
        ready=ready,
        mode=mode,
        unreviewed_phases=unreviewed_phases,
        has_content=True,
    )


async def assemble_fds(
    project_dir: Path,
    language: str,
    mode: str,
    v1_docs_path: Path,
    on_step: Callable[[str, int], None],
) -> Path:
    """Assemble FDS markdown from phase SUMMARY.md files.

    Steps:
    1. Load fds-structure.json, parse project type, build section order.
    2. Walk phase directories, collect SUMMARY.md content ordered by section tree.
    3. Write assembled markdown to project_dir/output/FDS-assembled-{language}.md.

    Returns the Path to the assembled markdown file.
    """
    # Step 1: Cross-reference resolution setup + section tree
    on_step("Cross-referenties oplossen", 0)

    fds_structure = _load_fds_structure(v1_docs_path)
    project_type = _parse_project_type(project_dir)
    section_tree = _build_section_tree(fds_structure, project_type, language)

    # Build a mapping: section_id -> (title, depth) for assembled output
    section_map: dict[str, tuple[str, int]] = {
        sid: (title, depth) for sid, title, depth in section_tree
    }
    section_order: list[str] = [sid for sid, _title, _depth in section_tree]

    # Step 2: Collect and merge SUMMARY.md files
    on_step("Secties samenvoegen", 1)

    summary_files = _collect_summary_files(project_dir)

    # Accumulate content per section_id
    section_content: dict[str, list[str]] = {sid: [] for sid in section_order}
    unordered_content: list[str] = []  # content not matching any known section

    for summary_file in summary_files:
        try:
            raw = summary_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Strip YAML frontmatter
        content = raw
        if content.startswith("---"):
            end_pos = content.find("\n---", 3)
            if end_pos != -1:
                content = content[end_pos + 4:].strip()

        # Try to assign content blocks to known sections
        # Split by top-level headings
        blocks = re.split(r'(?m)^(#{1,6}\s+)', content)
        # Re-join heading markers with their content
        chunks: list[str] = []
        i = 0
        while i < len(blocks):
            if i + 1 < len(blocks) and re.match(r'^#{1,6}\s+$', blocks[i]):
                chunks.append(blocks[i] + blocks[i + 1] if i + 1 < len(blocks) else blocks[i])
                i += 2
            else:
                if blocks[i].strip():
                    chunks.append(blocks[i])
                i += 1

        # Match chunks to section IDs
        matched_any = False
        for chunk in chunks:
            # Look for section ID references in the chunk header
            assigned = False
            for sid in section_order:
                pattern = rf'(?:^|\n)#{1,6}\s+.*\b{re.escape(sid)}\b'
                if re.search(pattern, chunk):
                    section_content[sid].append(chunk.strip())
                    assigned = True
                    matched_any = True
                    break
            if not assigned and chunk.strip():
                unordered_content.append(chunk.strip())

        # If no section matched, include entire summary content as unordered
        if not matched_any and content.strip():
            unordered_content.append(content.strip())

    # Assemble markdown in section tree order
    assembled_parts: list[str] = []

    for sid in section_order:
        title, depth = section_map[sid]
        heading = _iec_heading(title, depth, sid)
        assembled_parts.append(heading)

        chunks = section_content.get(sid, [])
        if chunks:
            for chunk in chunks:
                # Remove the duplicate heading from the chunk (already added above)
                chunk_without_heading = re.sub(
                    rf'^#{1,6}\s+.*{re.escape(sid)}.*\n?', '', chunk
                ).strip()
                if chunk_without_heading:
                    assembled_parts.append(chunk_without_heading)
        else:
            # Insert placeholder stub
            placeholder = fds_structure.get("placeholder_stub", "[TO BE COMPLETED]")
            assembled_parts.append(f"*{placeholder}*")

        assembled_parts.append("")  # blank line between sections

    # Append any unordered content at the end
    if unordered_content:
        assembled_parts.append("\n---\n\n## Additional Content\n")
        assembled_parts.extend(unordered_content)

    assembled_text = "\n\n".join(part for part in assembled_parts if part != "")

    # Apply cross-reference resolution
    assembled_text = _resolve_cross_references(assembled_text)

    # Draft mode: prepend CONCEPT header
    if mode == "draft":
        assembled_text = "> **CONCEPT — Niet definitief**\n\n" + assembled_text

    # Write to output/
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"FDS-assembled-{language}.md"
    output_path.write_text(assembled_text, encoding="utf-8")

    return output_path
