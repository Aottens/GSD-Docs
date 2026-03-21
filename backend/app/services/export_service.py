"""DOCX export service.

Invokes Pandoc asynchronously to produce versioned DOCX artifacts in output/.
Handles version detection, artifact storage, and optional Mermaid diagram rendering.
"""

import asyncio
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def detect_pandoc() -> tuple[bool, Optional[str]]:
    """Check if Pandoc is installed and return (found, version_string).

    Uses shutil.which for availability check, then subprocess for version.
    """
    if not shutil.which("pandoc"):
        return False, None

    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # First line: "pandoc 3.x.y"
            first_line = result.stdout.splitlines()[0]
            parts = first_line.split()
            version = parts[1] if len(parts) >= 2 else first_line
            return True, version
    except (subprocess.TimeoutExpired, OSError, IndexError):
        pass

    return True, None  # found but couldn't parse version


def _determine_next_version(output_dir: Path, mode: str, language: str) -> str:
    """Scan existing DOCX files and determine the next minor version number.

    Pattern: FDS-v{major}.{minor}_{mode}_{language}.docx
    Starts at v1.0. Each subsequent run with the same mode+language increments minor.
    """
    if not output_dir.exists():
        return "1.0"

    pattern = re.compile(
        rf'^FDS-v(\d+)\.(\d+)_{re.escape(mode)}_{re.escape(language)}\.docx$'
    )
    max_minor = -1

    for f in output_dir.iterdir():
        m = pattern.match(f.name)
        if m:
            major = int(m.group(1))
            minor = int(m.group(2))
            if major == 1:  # We always use major 1 for now
                max_minor = max(max_minor, minor)

    if max_minor < 0:
        return "1.0"
    return f"1.{max_minor + 1}"


async def export_to_docx(
    assembled_md: Path,
    project_dir: Path,
    mode: str,
    language: str,
    v1_docs_path: Path,
    on_step: Callable[[str, int], None],
) -> str:
    """Invoke Pandoc asynchronously to convert assembled markdown to DOCX.

    Returns the output filename (not the full path).
    """
    on_step("DOCX genereren", 2)

    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    version = _determine_next_version(output_dir, mode, language)
    output_filename = f"FDS-v{version}_{mode}_{language}.docx"
    output_path = output_dir / output_filename

    # Build Pandoc command
    cmd = [
        "pandoc",
        str(assembled_md),
        "--from", "markdown+yaml_metadata_block+pipe_tables+grid_tables+implicit_figures",
        "--to", "docx",
        "--standalone",
        "--toc",
        "--toc-depth=3",
        "--number-sections",
        f"--resource-path={output_dir}",
        "-o", str(output_path),
    ]

    # Add reference-doc if huisstijl.docx exists
    huisstijl_path = v1_docs_path / "references" / "huisstijl.docx"
    if huisstijl_path.exists():
        cmd.extend(["--reference-doc", str(huisstijl_path)])
    else:
        logger.warning("huisstijl.docx not found at %s — using Pandoc defaults", huisstijl_path)

    # Run Pandoc asynchronously
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"Pandoc failed (exit {proc.returncode}): {error_msg}")

    return output_filename


def list_export_versions(project_dir: Path) -> list[dict]:
    """Scan project_dir/output/ for DOCX artifacts and return parsed metadata.

    Returns list of dicts with: filename, doc_type, mode, language, version,
    created_at (file mtime), size_bytes. Sorted by created_at descending.
    """
    output_dir = project_dir / "output"
    if not output_dir.exists():
        return []

    pattern = re.compile(
        r'^(FDS|SDS)-v(\d+\.\d+)_(draft|final)_(nl|en)\.docx$'
    )

    versions: list[dict] = []
    for f in output_dir.iterdir():
        if not f.is_file() or not f.name.endswith(".docx"):
            continue
        m = pattern.match(f.name)
        if not m:
            continue

        doc_type = m.group(1)
        version = m.group(2)
        mode = m.group(3)
        lang = m.group(4)
        stat = f.stat()

        versions.append({
            "filename": f.name,
            "doc_type": doc_type,
            "mode": mode,
            "language": lang,
            "version": version,
            "created_at": stat.st_mtime,
            "size_bytes": stat.st_size,
        })

    # Sort by created_at descending (most recent first)
    versions.sort(key=lambda v: v["created_at"], reverse=True)
    return versions


async def render_diagrams(
    project_dir: Path,
    on_step: Callable[[str, int], None],
) -> None:
    """Render Mermaid diagrams in the assembled markdown to PNG.

    Gracefully skips if mmdc (mermaid-cli) is not available.
    """
    on_step("Diagrammen renderen", 3)

    if not shutil.which("mmdc"):
        logger.warning("mmdc (mermaid-cli) not found — skipping diagram rendering")
        return

    output_dir = project_dir / "output"
    assembled_files = list(output_dir.glob("FDS-assembled-*.md"))
    if not assembled_files:
        return

    # Process the most recently modified assembled file
    assembled_md = max(assembled_files, key=lambda f: f.stat().st_mtime)
    content = assembled_md.read_text(encoding="utf-8")

    # Find all mermaid code blocks
    mermaid_pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)
    matches = list(mermaid_pattern.finditer(content))

    if not matches:
        return

    new_content = content
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for idx, match in enumerate(matches, start=1):
            diagram_code = match.group(1)
            mmd_file = tmp_path / f"diagram-{idx}.mmd"
            png_file = output_dir / f"diagram-{idx}.png"
            mmd_file.write_text(diagram_code, encoding="utf-8")

            try:
                proc = await asyncio.create_subprocess_exec(
                    "mmdc",
                    "-i", str(mmd_file),
                    "-o", str(png_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(proc.communicate(), timeout=60)
                if proc.returncode == 0 and png_file.exists():
                    img_ref = f"![diagram-{idx}](diagram-{idx}.png)"
                    new_content = new_content.replace(match.group(0), img_ref, 1)
                else:
                    logger.warning("mmdc failed for diagram %d", idx)
            except (asyncio.TimeoutError, OSError) as e:
                logger.warning("mmdc error for diagram %d: %s", idx, e)

    if new_content != content:
        assembled_md.write_text(new_content, encoding="utf-8")
