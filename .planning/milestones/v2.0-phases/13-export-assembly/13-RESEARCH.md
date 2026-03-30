# Phase 13: Export & Assembly - Research

**Researched:** 2026-03-21
**Domain:** FastAPI SSE streaming, Pandoc DOCX export, SDS typicals matching, pipeline UX
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Trigger model:**
- GUI triggers assembly, export, and SDS scaffolding directly via backend API endpoints — these are deterministic file-processing operations, not AI
- Backend reimplements core logic in Python: cross-reference resolution, Pandoc invocation, typicals matching from CATALOG.json — no shelling out to CLI commands
- Assembly has two modes: Draft (allows partial/unreviewed content, produces watermarked DOCX) and Final (requires all phases reviewed)
- Each assembly/export stored as versioned artifact (e.g., FDS_v1.0_draft.docx) — engineer can download previous versions

**Export workflow UX:**
- New "Export" tab in workspace (alongside Overzicht, Fasering, Documenten, Referenties)
- Pipeline view layout: three-stage visual flow Assembleren -> Exporteren -> Downloaden, left to right
- Each pipeline stage shows status, action button, and result
- Export options: mode (Draft with watermark / Final) and language (Dutch/English from project setting, overridable per export)
- Version history as simple table below pipeline: Version, Type (Draft/Final), Language, Date, Size, Download button — most recent at top
- SDS scaffolding in separate section below FDS pipeline (but within same Export tab)

**SDS scaffolding display:**
- SDS gets its own workspace tab — foundation for future library manager / code scaffolding vision
- Phase 13 scope: display scaffolding results with typicals matching only (no library browser, no inline editing)
- Equipment-to-typical mapping table: Equipment Module | Matched Typical | Confidence Score | Status
- Status indicators: matched (green), low confidence (amber), "NIEUW TYPICAL NODIG" (red)
- Table is sortable and filterable
- Click to expand: shows why matching failed (missing I/O, no use_case match), closest match, CLI hint for /doc:generate-sds to refine
- Read-only catalog browser deferred to future library manager phase

**Progress & status feedback:**
- Step-by-step progress bar with named steps: "Cross-referenties oplossen" -> "Secties samenvoegen" -> "DOCX genereren" -> "Diagrammen renderen"
- Each step ticks as it completes — engineer sees exactly where the process is
- SSE streaming for real-time progress updates (sse-starlette already installed from Phase 10)
- Cancel button available during operations — aborts gracefully, cleans up partial files, pipeline returns to previous state
- Errors shown inline in the pipeline step that failed: expandable detail block with what went wrong and fix hint (e.g., "Pandoc niet gevonden — installeer via brew install pandoc")
- Pipeline stays visible on error, failed step highlighted red

### Claude's Discretion
- Exact pipeline visual design (card-based steps, stepper, or connected flow)
- SSE event schema for progress updates
- Version numbering scheme for stored artifacts
- Exact Pandoc invocation flags and fallback behavior
- How to detect Pandoc installation and version
- Draft watermark implementation approach
- SDS tab navigation item placement and icon
- Loading/error states for long operations

### Deferred Ideas (OUT OF SCOPE)
- SDS Library Manager — Future tab evolution: browse/manage typicals catalog, generate Siemens TIA and Ignition building blocks/faceplates dynamically
- Batch export — ENAV-01 in v2 requirements: export multiple variants in one action
- Read-only catalog browser — Browse available typicals from CATALOG.json alongside matching results
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| OUTP-02 | Engineer can trigger FDS assembly with cross-reference resolution | FDS assembly Python reimplementation; filesystem scan of SUMMARY.md files; phase readiness check; cross-ref pattern documented in complete-fds.md |
| OUTP-03 | Engineer can export FDS/SDS to DOCX with corporate styling | Pandoc Python subprocess call; huisstijl.docx --reference-doc flag; versioned artifact storage at PROJECT_ROOT/{id}/output/ |
| OUTP-04 | Engineer can see export progress during DOCX generation | SSE streaming via sse-starlette 3.2.0; EventSourceResponse; named step events; cancel via asyncio task |
| OUTP-05 | Engineer can trigger SDS scaffolding from completed FDS with typicals matching | Python CATALOG.json reader; typicals matching algorithm (I/O 40%, use_cases 30%, states 20%, category 10%); FDS section 4.x parser |
| OUTP-06 | Engineer can see typicals matching confidence scores and "NIEUW TYPICAL NODIG" indicators | Confidence classification (HIGH/MEDIUM/LOW/UNMATCHED); sortable/filterable table with expand-on-click detail |
| OUTP-07 | Engineer can generate documents in Dutch or English based on project setting | Language param on export endpoint; project.language already in DB; bilingual titles from fds-structure.json |
</phase_requirements>

---

## Summary

Phase 13 adds three new backend services (assembly, export, SDS scaffolding) and three new frontend sections (Export tab, SDS tab, version history). All operations are deterministic Python reimplementations of existing bash/CLI workflows — no AI or LLM calls involved.

The core technical challenge is the SSE streaming pipeline: a long-running background task (Pandoc can take 5-30s, mermaid-cli longer) must stream named step events to the frontend in real-time, support cancellation, and persist results as versioned DOCX artifacts. The good news is `sse-starlette` 3.2.0 is already installed in the venv and the Phase 10 pattern established the SSE + frontend hook foundation to build on.

The SDS scaffolding tab is architecturally simpler: it's a read-only display of matching results from a previous run. The matching algorithm itself (I/O count comparison, use_cases Jaccard similarity, state count, category) is fully documented in `gsd-docs-industrial/workflows/generate-sds.md` Steps 3-4 and needs to be translated to Python.

**Primary recommendation:** Build two new FastAPI routers (`export.py`, `sds.py`), two new frontend feature directories (`features/export/`, `features/sds/`), and extend `ProjectNavigation` + `ProjectWorkspace` with 'export' and 'sds' cases — following the identical structural patterns established in phases 10-12.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sse-starlette | 3.2.0 (installed) | SSE streaming from FastAPI | Already in venv; Phase 10 decision; `EventSourceResponse` wraps async generator |
| Pandoc | 3.9+ (system) | Markdown to DOCX conversion | Project SSOT; `--reference-doc` for huisstijl.docx; `--toc --number-sections` |
| asyncio | stdlib | Background task + cancel | Python built-in; `asyncio.create_task()` + `task.cancel()` for abort |
| subprocess / asyncio.subprocess | stdlib | Pandoc invocation | `asyncio.create_subprocess_exec` for non-blocking Pandoc execution |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query | 5.90.x (installed) | Server state for version history, SDS results | All data fetching in frontend — established project pattern |
| sonner | 2.0.7 (installed) | Toast notifications | Non-blocking "export complete", "download ready" notifications |
| lucide-react | 0.564.x (installed) | Icons for pipeline stages, SDS status | All icons in project use lucide-react |
| shadcn/ui Badge, Table, Button, Progress, Skeleton | installed | Pipeline UI, version table, SDS mapping table | Already in codebase; consistent design system |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio subprocess | python-docx | python-docx doesn't produce Pandoc-quality DOCX with corporate styling; Pandoc is the project SSOT |
| SSE for progress | WebSocket | SSE is unidirectional (server → client), simpler for one-way progress; WebSocket overkill |
| SSE for progress | polling | Polling at 1s interval would work but SSE gives real-time ticks without interval gaps |

**Installation note:** `sse-starlette` is installed in the venv but NOT in `backend/requirements.txt`. Add it explicitly:
```bash
# Add to backend/requirements.txt:
sse-starlette>=3.2.0
```

---

## Architecture Patterns

### Recommended Project Structure

```
backend/app/api/
├── export.py          # Assembly, export, download, version history endpoints + SSE
└── sds.py             # SDS scaffolding trigger + results endpoints

backend/app/services/
├── assembly_service.py    # FDS assembly: phase collection, cross-ref resolution, section ordering
├── export_service.py      # Pandoc invocation, artifact storage, watermark injection
└── sds_service.py         # CATALOG.json loading, matching algorithm, results persistence

frontend/src/features/
├── export/
│   ├── components/
│   │   ├── ExportTab.tsx          # Top-level Export tab (pipeline + version history + SDS section)
│   │   ├── AssemblyPipeline.tsx   # Three-stage pipeline: Assembleren → Exporteren → Downloaden
│   │   ├── PipelineStage.tsx      # Individual stage card: status, action button, result
│   │   ├── ExportProgressBar.tsx  # Step-by-step named progress (SSE-driven)
│   │   ├── ExportOptions.tsx      # Mode selector (Draft/Final) + language override
│   │   └── VersionHistory.tsx     # Table of past exports with download links
│   └── hooks/
│       ├── useAssemblyStream.ts   # SSE consumer for assembly/export progress
│       └── useVersionHistory.ts   # React Query for version history list
└── sds/
    ├── components/
    │   ├── SdsTab.tsx             # Top-level SDS tab
    │   ├── TypicalsMatchTable.tsx # Sortable/filterable mapping table
    │   └── TypicalMatchDetail.tsx # Expand-on-click: why matched/failed + closest match + CLI hint
    └── hooks/
        └── useSdsResults.ts       # React Query for SDS scaffolding results
```

### Pattern 1: SSE Progress Streaming (Backend)

**What:** FastAPI endpoint using `EventSourceResponse` from sse-starlette that yields named step events as an async generator. A background asyncio task runs the actual work.

**When to use:** Any long-running operation (assembly, export, SDS scaffolding) where the engineer needs step-by-step feedback.

```python
# Source: sse-starlette documentation + Phase 10 established pattern
from sse_starlette.sse import EventSourceResponse
import asyncio

@router.post("/{project_id}/export/assemble-stream")
async def stream_assembly(project_id: int, request: Request, ...):
    async def event_generator():
        steps = [
            "Cross-referenties oplossen",
            "Secties samenvoegen",
            "DOCX genereren",
            "Diagrammen renderen",
        ]
        try:
            for i, step in enumerate(steps):
                if await request.is_disconnected():
                    break
                yield {"event": "step_start", "data": json.dumps({"step": i, "name": step})}
                await _run_step(step, project_id)  # actual work
                yield {"event": "step_done", "data": json.dumps({"step": i})}
            yield {"event": "complete", "data": json.dumps({"artifact_path": "..."})}
        except asyncio.CancelledError:
            yield {"event": "cancelled", "data": "{}"}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"step": i, "message": str(e)})}

    return EventSourceResponse(event_generator())
```

### Pattern 2: SSE Consumer Hook (Frontend)

**What:** React hook that opens an EventSource to the SSE endpoint, parses step events, and exposes pipeline state.

```typescript
// Source: MDN EventSource API + project pattern
export function useAssemblyStream(projectId: number) {
  const [stages, setStages] = useState<PipelineStage[]>(initialStages)
  const [isRunning, setIsRunning] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  const start = useCallback((options: ExportOptions) => {
    const url = `/api/projects/${projectId}/export/assemble-stream?mode=${options.mode}&lang=${options.language}`
    const es = new EventSource(url)
    eventSourceRef.current = es

    es.addEventListener('step_start', (e) => {
      const { step, name } = JSON.parse(e.data)
      setStages(prev => prev.map((s, i) => i === step ? { ...s, status: 'running' } : s))
    })
    es.addEventListener('step_done', (e) => {
      const { step } = JSON.parse(e.data)
      setStages(prev => prev.map((s, i) => i === step ? { ...s, status: 'done' } : s))
    })
    es.addEventListener('complete', (e) => {
      const { artifact_path } = JSON.parse(e.data)
      setIsRunning(false)
      es.close()
      // invalidate version history query
    })
    es.addEventListener('error', (e) => {
      const { step, message } = JSON.parse(e.data)
      setStages(prev => prev.map((s, i) =>
        i === step ? { ...s, status: 'error', errorMessage: message } : s
      ))
      es.close()
    })
  }, [projectId])

  const cancel = useCallback(() => {
    eventSourceRef.current?.close()
    setIsRunning(false)
  }, [])

  return { stages, isRunning, start, cancel }
}
```

### Pattern 3: Pandoc Invocation (Python)

**What:** Non-blocking Pandoc subprocess via `asyncio.create_subprocess_exec`, capturing stdout/stderr for error reporting.

```python
# Source: export.md workflow + Python asyncio docs
async def invoke_pandoc(
    input_path: Path,
    output_path: Path,
    reference_doc: Path | None,
    draft: bool,
    language: str,
) -> None:
    cmd = [
        "pandoc", str(input_path),
        "--from", "markdown+yaml_metadata_block+pipe_tables+grid_tables+implicit_figures",
        "--to", "docx",
        "--standalone",
        "--toc", "--toc-depth=3",
        "--number-sections",
        "--resource-path", str(input_path.parent),
        "-o", str(output_path),
    ]
    if reference_doc and reference_doc.exists():
        cmd += ["--reference-doc", str(reference_doc)]
    if not draft:
        cmd += ["--lof", "--lot"]  # Pandoc 3.9+ flags

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {stderr.decode()}")
```

### Pattern 4: Typicals Matching Algorithm (Python)

**What:** Pure Python implementation of the confidence scoring from `generate-sds.md` Step 4.

```python
# Source: gsd-docs-industrial/workflows/generate-sds.md Step 4.1
def score_typical(module: EquipmentModule, typical: Typical) -> float:
    # I/O match (40%)
    io_score = _io_match_score(module.io, typical.interfaces)  # 0-40

    # use_cases Jaccard similarity (30%)
    module_kw = set(module.keywords)
    typical_uc = set(w.lower() for uc in (typical.use_cases or []) for w in uc.split())
    if module_kw | typical_uc:
        jaccard = len(module_kw & typical_uc) / len(module_kw | typical_uc)
    else:
        jaccard = 0.0
    keyword_score = jaccard * 30

    # State count (20%)
    typical_states = len(typical.states or [])
    state_diff = abs(module.state_count - typical_states)
    state_score = 20 if state_diff == 0 else (15 if state_diff == 1 else (10 if state_diff == 2 else 5))

    # Category (10%)
    category_score = 10 if typical.category.lower() in module.keywords else 0

    return io_score + keyword_score + state_score + category_score
```

### Pattern 5: Versioned Artifact Storage

**What:** Export artifacts stored under `PROJECT_ROOT/{project_id}/output/` with scheme `{TYPE}-v{N}.{minor}_{mode}_{lang}.docx`.

```
projects/
└── {project_id}/
    ├── .planning/
    └── output/
        ├── FDS-v1.0_draft_nl.docx
        ├── FDS-v1.0_final_nl.docx
        └── SDS-v0.1_draft_nl.docx
```

Backend scans `output/` on `GET /export/versions` — no DB table needed for artifact metadata (filesystem is source of truth, consistent with Phase 10 filesystem-based status pattern).

### Pattern 6: Navigation Extension

**What:** Extend `ProjectNavigation.tsx` navigationSections array and `ProjectWorkspace.tsx` switch to add 'export' and 'sds' cases.

```typescript
// Source: frontend/src/features/projects/components/ProjectNavigation.tsx pattern
const navigationSections = [
  { id: 'overview', label: 'Overzicht', icon: LayoutDashboard },
  { id: 'fasering', label: 'Fases', icon: Calendar },
  { id: 'documents', label: 'Documenten', icon: FileText },
  { id: 'references', label: 'Referenties', icon: FolderOpen },
  { id: 'export', label: 'Exporteren', icon: Download },   // NEW
  { id: 'sds', label: 'SDS', icon: Layers },               // NEW
  { id: 'settings', label: 'Instellingen', icon: Settings },
]
```

In `ProjectWorkspace.tsx`, add to the switch:
```typescript
{activeSection === 'export' && (
  <ExportTab projectId={project.id} language={project.language} />
)}
{activeSection === 'sds' && (
  <SdsTab projectId={project.id} />
)}
```

### Anti-Patterns to Avoid

- **Do not use `subprocess.run()` for Pandoc**: It blocks the event loop. Use `asyncio.create_subprocess_exec` to keep SSE streaming alive during Pandoc execution.
- **Do not store artifact paths in SQLite**: The filesystem is the source of truth; scanning `output/` is consistent with the Phase 10 filesystem-based status pattern.
- **Do not auto-apply typicals matches**: The workflow spec is explicit: "Matching is NEVER auto-applied." Display only; engineer acts via CLI.
- **Do not check Pandoc availability at startup**: Check lazily when the first export is triggered, return a clear inline error in the failed pipeline step.
- **Do not block on mermaid-cli**: mermaid-cli is optional. If not available, auto-enable --skip-diagrams (matches export.md Step 1 behavior).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DOCX generation with corporate styles | Custom python-docx renderer | Pandoc + `--reference-doc` huisstijl.docx | Pandoc handles TOC, numbered sections, LOF, LOT, consistent heading styles — python-docx cannot match this fidelity |
| SSE from FastAPI | Manual `StreamingResponse` with text/event-stream | `sse-starlette` EventSourceResponse | Handles connection lifecycle, keep-alive pings, client disconnect detection — already in venv |
| Mermaid PNG rendering | Canvas-based server rendering | `mmdc` (mermaid-cli) subprocess | mermaid-cli is the project SSOT for PNG generation; graceful degradation to --skip-diagrams if absent |
| Confidence scoring | Custom ML classifier | Deterministic scoring algorithm from generate-sds.md Step 4.1 | Algorithm is fully specified: I/O 40% + Jaccard 30% + states 20% + category 10% — no training data needed |

**Key insight:** The v1.0 CLI workflows are the SSOT. The task is to translate bash scripts and step descriptions into Python methods, not to design new algorithms.

---

## Common Pitfalls

### Pitfall 1: Blocking the Event Loop with Pandoc
**What goes wrong:** `subprocess.run(["pandoc", ...])` blocks the entire FastAPI server during DOCX generation (5-30s), freezing all other requests and killing SSE keep-alive.
**Why it happens:** Python `subprocess.run()` is synchronous — it does not yield to the event loop.
**How to avoid:** Use `await asyncio.create_subprocess_exec(...)` + `await proc.communicate()`. This suspends the coroutine without blocking other requests.
**Warning signs:** SSE events stop mid-stream; other API calls hang during export.

### Pitfall 2: Pandoc Not Finding Images
**What goes wrong:** Mermaid PNG images referenced as relative paths in the assembled markdown are not embedded in the DOCX.
**Why it happens:** Pandoc resolves image paths relative to its working directory, not the markdown file location.
**How to avoid:** Pass `--resource-path={project_dir}/output` or run Pandoc with `cwd=project_dir/output`. Images must exist at relative paths from that working directory.
**Warning signs:** DOCX exports successfully but shows broken image placeholders.

### Pitfall 3: SSE Connection Drops Without Client Disconnect Detection
**What goes wrong:** If the engineer navigates away mid-export, the backend task keeps running, consuming CPU and leaving partial files.
**Why it happens:** EventSource disconnect is not automatic — must be checked in generator via `await request.is_disconnected()`.
**How to avoid:** Check `request.is_disconnected()` before each `yield`. On True, cancel the running task and clean up partial output files.
**Warning signs:** Zombie Pandoc processes; orphaned partial DOCX files in output/.

### Pitfall 4: sse-starlette Not in requirements.txt
**What goes wrong:** Works in dev (venv has it as transitive from litellm), fails on fresh deploy or CI.
**Why it happens:** sse-starlette 3.2.0 is installed in the venv but was not added to `requirements.txt` as a direct dependency.
**How to avoid:** Add `sse-starlette>=3.2.0` to `backend/requirements.txt` in Wave 0 (backend setup plan).
**Warning signs:** `ImportError: No module named 'sse_starlette'` on fresh `pip install -r requirements.txt`.

### Pitfall 5: Typicals Path Not Configured (CATALOG.json Missing)
**What goes wrong:** SDS scaffolding endpoint fails with a 500 or returns empty results.
**Why it happens:** Projects may not have a typicals library configured. The workflow spec says: proceed in skeleton mode (all modules = NIEUW TYPICAL NODIG) if no CATALOG.json found.
**How to avoid:** SDS endpoint must gracefully handle missing CATALOG.json. In skeleton mode, every equipment module gets status `NIEUW TYPICAL NODIG` with confidence 0. Never block or error — return skeleton results.
**Warning signs:** SDS tab shows error state instead of the NIEUW TYPICAL NODIG table.

### Pitfall 6: Draft Watermark via python-docx After Pandoc
**What goes wrong:** Trying to inject a "DRAFT" watermark into Pandoc-generated DOCX requires python-docx post-processing, which can corrupt styles if done incorrectly.
**Why it happens:** Pandoc does not natively support watermarks; post-processing is the only option.
**How to avoid:** For MVP, implement draft watermark as a DRAFT text header/footer injection into the assembled markdown (as a visible header line) before Pandoc conversion. True background watermark via python-docx is a stretch goal. Keep it simple.
**Warning signs:** Watermark post-processing breaks heading styles, TOC links.

### Pitfall 7: Version History Filename Collisions
**What goes wrong:** Re-running export with the same mode+language overwrites the previous artifact.
**Why it happens:** If file naming doesn't include a sequence number or timestamp, old files are silently overwritten.
**How to avoid:** Use scheme `FDS-v{major}.{minor}_{mode}_{lang}.docx` where minor increments on each run. Scan output/ to determine next minor version. Alternatively use `FDS-v{major}.{minor}_{timestamp}_{mode}_{lang}.docx`.
**Warning signs:** Engineer asks "where did my previous draft go?" — version history table shows only one entry.

---

## Code Examples

### Backend Router Registration

```python
# Source: backend/app/main.py pattern
from app.api import health, projects, files, folders, phases, documents, export, sds

app.include_router(export.router)
app.include_router(sds.router)
```

### Export Router Skeleton

```python
# Source: backend/app/api/phases.py + documents.py patterns
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.models.project import Project

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["export"])

@router.get("/versions")
async def list_export_versions(project_id: int, db: AsyncSession = Depends(get_db)):
    """Scan output/ directory and return list of versioned artifacts."""
    ...

@router.get("/stream", response_class=EventSourceResponse)
async def stream_export(
    project_id: int,
    request: Request,
    mode: str = "draft",       # "draft" | "final"
    language: str = "nl",      # "nl" | "en"
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint streaming assembly + export progress."""
    ...

@router.get("/download/{filename}")
async def download_artifact(project_id: int, filename: str):
    """Serve a versioned DOCX artifact for download."""
    ...
```

### SDS Router Skeleton

```python
# Source: backend/app/api/documents.py pattern
router = APIRouter(prefix="/api/projects/{project_id}/sds", tags=["sds"])

@router.post("/scaffold")
async def trigger_sds_scaffold(project_id: int, db: AsyncSession = Depends(get_db)):
    """Run SDS scaffolding: load catalog, parse FDS modules, match typicals."""
    ...

@router.get("/results")
async def get_sds_results(project_id: int, db: AsyncSession = Depends(get_db)):
    """Return last SDS scaffolding results from filesystem cache."""
    ...
```

### Pandoc Version Detection

```python
# Source: export.md Step 1 — "Check Pandoc installation"
import shutil
import subprocess

def detect_pandoc() -> tuple[bool, str | None]:
    """Return (found: bool, version: str | None)."""
    pandoc_path = shutil.which("pandoc")
    if not pandoc_path:
        return False, None
    try:
        result = subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True, timeout=5
        )
        version_line = result.stdout.splitlines()[0]  # "pandoc 3.9"
        version = version_line.split()[-1]
        return True, version
    except Exception:
        return False, None
```

### FDS Phase Readiness Check (Final Mode)

```python
# Source: complete-fds.md Step 1 — Pre-flight verification
def _check_assembly_readiness(project_dir: Path, mode: str) -> list[str]:
    """
    Returns list of unreviewed phase names.
    For 'final' mode, all phases must have REVIEW.md.
    For 'draft' mode, at least one SUMMARY.md must exist.
    """
    planning_dir = project_dir / ".planning" / "phases"
    unreviewed = []
    for phase_dir in sorted(planning_dir.iterdir()):
        if not phase_dir.is_dir():
            continue
        has_summary = any(phase_dir.glob("*-SUMMARY.md"))
        has_review = any(phase_dir.glob("*-REVIEW.md"))
        if has_summary and not has_review and mode == "final":
            unreviewed.append(phase_dir.name)
    return unreviewed
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CLI bash scripts for assembly/export | Python FastAPI service endpoints | Phase 13 (this phase) | Engineers trigger from GUI, no terminal needed |
| Blocking subprocess calls | asyncio.create_subprocess_exec | This phase | Non-blocking during SSE streaming |
| Pandoc `--lof --lot` as `--metadata lof:true` | `--lof --lot` native flags | Pandoc 3.9+ | Cleaner command line; must version-check |

**Note on sse-starlette version:** Version 3.2.0 is installed. The API for `EventSourceResponse` takes an async generator. The `data` field in yielded dicts must be a string (serialize JSON with `json.dumps()`).

---

## Open Questions

1. **Where does CATALOG.json live per-project?**
   - What we know: The CLI workflow reads from a path in `.planning/PROJECT.md` (`typicals.path` field) or from `references/typicals/CATALOG.json` (imported mode)
   - What's unclear: The v2.0 GUI projects are created via wizard — do they populate a `typicals.path` in PROJECT.md? Looking at `backend/app/config.py`, there's no `TYPICALS_PATH` setting.
   - Recommendation: For Phase 13, look for CATALOG.json at `{project_dir}/references/typicals/CATALOG.json` (imported mode) first, then fall back to skeleton mode. Reading `typicals.path` from PROJECT.md is a future enhancement.

2. **Where is huisstijl.docx on the server?**
   - What we know: CLI workflow expects it at `~/.claude/gsd-docs-industrial/references/huisstijl.docx`; `config.py` has `V1_DOCS_PATH = "./gsd-docs-industrial"`.
   - What's unclear: Is huisstijl.docx present in the repo at `gsd-docs-industrial/references/huisstijl.docx`?
   - Recommendation: Look for it at `settings.V1_DOCS_PATH + "/references/huisstijl.docx"`. If absent, proceed without `--reference-doc` (Pandoc defaults) and show a warning in the pipeline UI.

3. **Assembled FDS markdown location**
   - What we know: CLI workflow puts assembled docs in `output/FDS-*.md` relative to project root. In GUI, project root is `PROJECT_ROOT/{project_id}/`.
   - What's unclear: Do any GUI projects have assembled FDS files yet, or is this Phase 13 that creates the first assembled output?
   - Recommendation: Assembly endpoint creates `{project_dir}/output/` if missing and writes `FDS-{assembled}.md` there before invoking Pandoc. The plan must define this output path clearly.

---

## Validation Architecture

No `nyquist_validation` key found in `.planning/config.json` — treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ with pytest-asyncio 0.23+ |
| Config file | None detected — Wave 0 creates `backend/pytest.ini` if needed |
| Quick run command | `cd backend && python -m pytest tests/ -x -q` |
| Full suite command | `cd backend && python -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| OUTP-02 | FDS assembly: phase readiness check, cross-ref resolution, output file created | unit | `pytest tests/test_assembly_service.py -x` | Wave 0 |
| OUTP-03 | DOCX export: Pandoc invoked, output file exists, versioned filename correct | unit (mock Pandoc) | `pytest tests/test_export_service.py -x` | Wave 0 |
| OUTP-04 | SSE stream: events emitted in correct order, cancel cleans up | integration | `pytest tests/test_export_api.py::test_sse_stream -x` | Wave 0 |
| OUTP-05 | SDS scaffold: CATALOG.json loaded, modules matched, results stored | unit | `pytest tests/test_sds_service.py -x` | Wave 0 |
| OUTP-06 | Confidence scoring: HIGH/MEDIUM/LOW/UNMATCHED classification correct | unit | `pytest tests/test_sds_service.py::test_confidence_scoring -x` | Wave 0 |
| OUTP-07 | Language param passed to export, bilingual titles used in assembly | unit | `pytest tests/test_assembly_service.py::test_language_param -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && python -m pytest tests/ -x -q`
- **Per wave merge:** `cd backend && python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_assembly_service.py` — covers OUTP-02, OUTP-07
- [ ] `backend/tests/test_export_service.py` — covers OUTP-03
- [ ] `backend/tests/test_export_api.py` — covers OUTP-04
- [ ] `backend/tests/test_sds_service.py` — covers OUTP-05, OUTP-06

---

## Canonical References (Downstream Must Read)

These files are the SSOT — executors must read them before implementing any service logic.

| File | What It Defines |
|------|----------------|
| `gsd-docs-industrial/workflows/complete-fds.md` | 15-step assembly pipeline: section ordering, cross-ref resolution, phase readiness check, frontmatter generation |
| `gsd-docs-industrial/workflows/export.md` | 10-step DOCX pipeline: Pandoc invocation flags, Mermaid rendering, graceful degradation, versioned output filename |
| `gsd-docs-industrial/workflows/generate-sds.md` | 12-step SDS scaffolding: CATALOG.json loading, module profile extraction from section 4.x, matching algorithm |
| `gsd-docs-industrial/templates/fds-structure.json` | Canonical section hierarchy, bilingual titles, Type C/D handling, dynamic equipment module sections |
| `gsd-docs-industrial/references/huisstijl-README.md` | Corporate style spec: heading styles, body text, table headers, header/footer layout |
| `gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json` | JSON Schema for CATALOG.json: typical structure, interfaces, use_cases, states fields |

---

## Sources

### Primary (HIGH confidence)
- `gsd-docs-industrial/workflows/export.md` — Pandoc invocation flags, graceful degradation, output filename pattern (read directly)
- `gsd-docs-industrial/workflows/generate-sds.md` Steps 1-4 — SDS scaffolding, CATALOG loading, matching algorithm (read directly)
- `gsd-docs-industrial/workflows/complete-fds.md` Steps 1-2 — Assembly pre-flight, project config loading (read directly)
- `gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json` — Typicals structure, use_cases, interfaces (read directly)
- `backend/app/main.py` — Router registration pattern (read directly)
- `backend/app/api/phases.py` — Filesystem-based status detection pattern (read directly)
- `backend/app/api/documents.py` — Document content API pattern (read directly)
- `frontend/src/features/projects/ProjectWorkspace.tsx` — activeSection switch pattern (read directly)
- `frontend/src/features/projects/components/ProjectNavigation.tsx` — navigationSections array pattern (read directly)
- `frontend/src/lib/api.ts` — API client typed responses, 204 handling (read directly)
- `backend/requirements.txt` — Confirmed sse-starlette NOT listed (read directly)
- venv pip show sse-starlette — Version 3.2.0 confirmed (verified live)

### Secondary (MEDIUM confidence)
- sse-starlette README (verified via pip show; `EventSourceResponse` wraps async generator, `data` must be string)
- Pandoc 3.9+ `--lof`/`--lot` flags (documented in export.md workflow which references version check)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified in venv/package.json; versions confirmed
- Architecture: HIGH — directly derived from CONTEXT.md decisions + existing codebase patterns
- Pitfalls: HIGH — derived from reading actual workflow files and codebase; no speculation
- Matching algorithm: HIGH — fully specified in generate-sds.md Step 4.1 with exact weights

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable library ecosystem; Pandoc version check is the only time-sensitive item)
