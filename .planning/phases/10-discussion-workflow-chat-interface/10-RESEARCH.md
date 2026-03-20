# Phase 10: Workflow Status & Cleanup - Research

**Researched:** 2026-03-20
**Domain:** FastAPI/React codebase cleanup + filesystem-based phase status + CLI command guidance UI
**Confidence:** HIGH (all findings based on direct codebase inspection)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Cleanup scope:**
- Remove ALL LLM infrastructure: `llm/` directory, `prompts/`, `services/llm_service.py`, and all LLM dependencies (litellm, sse-starlette for streaming, etc.)
- Remove ALL discussion code: `models/conversation.py`, `api/discussions.py`, `api/context.py`, `services/discussion_engine.py`, `services/conversation_state.py`, `services/decision_extractor.py`, `services/context_generator.py`, `services/structured_output_parser.py`
- Remove frontend discussion feature: entire `features/discussions/` directory (ChatPanel, ChatInput, MessageBubble, QuestionCard, CompletionCard, ContextPreview, ConversationHistory, SummaryCard, SummaryPanel, TopicSelectionCard)
- Create Alembic migration to DROP conversation and message tables — clean slate, no orphaned tables
- Remove the "Gesprekken" (Conversations) sidebar tab entirely — sidebar keeps only Fasering (phases) and Bestanden (files)
- Remove the assistant panel (slide-in Sheet from Phase 8) entirely — future phases add their own panels from scratch if needed
- Backend becomes pure file/project management API with zero LLM dependencies

**CLI command display:**
- Static mapping from phase status to recommended `/doc:*` command (e.g., 'not started' → `/doc:discuss-phase N`, 'discussed' → `/doc:plan-phase N`, etc.)
- Show in phase popover only — keeps timeline clean, users click phase node for details + next action
- CLI command displayed as monospace code block with click-to-copy button
- Remove old action buttons from phase popover (e.g., "Start Discussie") — GUI doesn't trigger operations anymore

**Context file display:**
- Backend reads CONTEXT.md and VERIFICATION.md directly from project filesystem (no DB sync, no filesystem watching)
- Display in phase popover (not sidebar, not separate tab)
- CONTEXT.md: show key decisions only (extract `<decisions>` section as bullet list, skip canonical_refs/code_context/deferred)
- VERIFICATION.md: show score + gap count (e.g., "4/5 levels passed, 2 gaps") with severity breakdown — quick health indicator

**Phase status rework:**
- Phase status derived from filesystem: CONTEXT.md exists → 'discussed', PLAN files exist → 'planned', CONTENT.md exists → 'written', VERIFICATION.md exists → 'verified'
- Backend knows v1.0 FDS directory structure (hardcoded layout: phases/, ROADMAP.md, STATE.md, etc.) — if CLI changes, update backend
- Configurable PROJECT_ROOT via .env — projects stored at PROJECT_ROOT/{project_id}/
- Keep existing PROJECT_TYPE_PHASES mapping for phase list per project type (A/B/C/D) — no ROADMAP.md parsing needed

### Claude's Discretion
- Exact implementation of filesystem status detection logic
- How to handle edge cases (e.g., partial files, corrupted CONTEXT.md)
- Phase popover layout and styling for the new content
- Migration ordering and backward compatibility

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| WORK-01 | Engineer can view phase timeline showing ROADMAP phases with completion status | Existing `PhaseTimeline` + `PhaseNode` components kept; `api/phases.py` reworked to use `_derive_phase_status()` already present in the file |
| WORK-02 | Engineer can view phase status and next recommended CLI command from the timeline | `PhasePopover` reworked to show CLI command code block with copy button; static status→command mapping added to backend response |
</phase_requirements>

---

## Summary

Phase 10 is primarily a **cleanup and rework phase**, not a greenfield build. The existing codebase contains working discussion engine code (phases 10/10.1) that must be surgically removed while keeping and reworking the phase timeline components. The work falls into four buckets: (1) backend cleanup — remove 8 files and 2 packages, add PROJECT_ROOT config, add Alembic drop migration, rework `api/phases.py` to use filesystem-based status; (2) backend new capability — new endpoint to read CONTEXT.md/VERIFICATION.md from project directory; (3) frontend cleanup — remove `features/discussions/` (10 components), remove Sheet/assistant panel, remove Gesprekken sidebar tab; (4) frontend rework — update `PhasePopover` to show CLI command + context content instead of action buttons.

The critical insight is that the backend already has the `_derive_phase_status()` function written in `api/phases.py` (lines 176-255) — it was written but never wired up. The live endpoint currently queries the `conversations` table instead. Phase 10 simply swaps that out. The filesystem status logic is already tested-by-design against the actual directory structure.

**Primary recommendation:** Wire `_derive_phase_status()` into the live `GET /phases/` endpoint, add `PROJECT_ROOT` to settings, move `PROJECT_TYPE_PHASES` out of `prompts/discuss_phase.py` into a standalone config module (since that file will be deleted), then clean up all LLM/discussion code front-to-back.

---

## Standard Stack

### Core (existing — no new dependencies)
| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| FastAPI | >=0.115.0 | Backend API | Already installed |
| SQLAlchemy | >=2.0.0 | ORM + async sessions | Already installed |
| Alembic | >=1.13.0 | DB migrations | Already installed; need new migration |
| Pydantic / pydantic-settings | >=2.0.0 | Schemas + config | Already installed |
| React + TanStack Query | (existing) | Frontend data fetching | Already installed |
| shadcn/ui | (existing) | UI components | Already installed |
| Tailwind v4 | (existing) | Styling | Already installed |

### Packages to REMOVE
| Package | Reason |
|---------|--------|
| `litellm>=1.40.0` | LLM integration — no longer needed |
| `sse-starlette>=2.2.0` | SSE streaming for chat — no longer needed |

No new packages required for this phase.

---

## Architecture Patterns

### Backend: What Gets Removed vs What Stays

**Remove completely:**

```
backend/app/
├── llm/                          # REMOVE entire directory
│   ├── __init__.py
│   ├── provider.py
│   └── litellm_provider.py
├── prompts/                      # REMOVE entire directory
│   ├── __init__.py
│   └── discuss_phase.py         # Contains PROJECT_TYPE_PHASES — EXTRACT FIRST
├── api/
│   ├── discussions.py            # REMOVE
│   └── context.py               # REMOVE
├── models/
│   └── conversation.py           # REMOVE
├── services/
│   ├── llm_service.py            # REMOVE
│   ├── discussion_engine.py      # REMOVE
│   ├── conversation_state.py     # REMOVE
│   ├── decision_extractor.py     # REMOVE
│   ├── context_generator.py      # REMOVE
│   └── structured_output_parser.py # REMOVE
└── schemas/
    └── conversation.py           # REMOVE
```

**Keep and rework:**
```
backend/app/
├── api/
│   └── phases.py                 # REWORK: swap DB queries for _derive_phase_status()
├── models/
│   └── phase.py                  # REWORK: remove conversation_id field
├── schemas/
│   └── phase.py                  # REWORK: remove conversation_id, add cli_command + context fields
├── config.py                     # ADD: PROJECT_ROOT setting
└── main.py                       # REMOVE: discussions/context router registrations
```

**New file:**
```
backend/app/
└── config_phases.py              # NEW: PROJECT_TYPE_PHASES mapping (moved from prompts/)
```

### Backend: Reworked Phase Status Flow

The existing `_derive_phase_status()` function (already in `api/phases.py`, lines 176-255) is nearly complete. It needs:

1. `project_dir` path — derived from `PROJECT_ROOT / str(project_id)`
2. The function scans `.planning/phases/` for directories matching `{N:02d}-*`
3. It checks for presence of: `{N:02d}-CONTEXT.md`, `{N:02d}-*-PLAN.md`, `{N:02d}-*-SUMMARY.md`, `{N:02d}-VERIFICATION.md`, `{N:02d}-REVIEW.md`

**Status → CLI command mapping (static, backend-side):**

```python
STATUS_CLI_COMMANDS = {
    "not_started": "/doc:discuss-phase {N}",
    "discussed":   "/doc:plan-phase {N}",
    "planned":     "/doc:write-phase {N}",
    "written":     "/doc:verify-phase {N}",
    "verified":    "/doc:review-phase {N}",   # future
    "reviewed":    None,                       # complete
    "completed":   None,
}
```

This mapping is injected into `PhaseStatusResponse` as a new `cli_command: Optional[str]` field.

### Backend: New Context File Endpoint

New endpoint on the phases router:

```
GET /api/projects/{project_id}/phases/{phase_number}/context-files
```

Returns:
```python
{
    "decisions": ["decision text 1", "decision text 2"],  # from <decisions> section
    "verification_score": "4/5",  # from VERIFICATION.md if present
    "verification_gaps": 2,       # gap count
    "verification_severity": {"critical": 0, "major": 1, "minor": 1},
    "has_context": bool,
    "has_verification": bool,
}
```

The backend reads files directly with `pathlib.Path.read_text()`. No DB, no caching, no filesystem watching.

**CONTEXT.md parsing:** extract `<decisions>` XML block, strip `###` headers, collect bullet lines.

**VERIFICATION.md parsing:** scan for score pattern (e.g., `4/5 levels passed`) and gap severity counts using simple regex — no full markdown parser needed.

### Alembic Migration

New migration drops `messages` first (FK dependency), then `conversations`:

```python
# Migration: drop_conversation_tables
def upgrade():
    op.drop_table('messages')
    op.drop_table('conversations')

def downgrade():
    # Reconstruct from fb17f556ba07 upgrade() — optional
    pass
```

**Important:** `alembic.ini` uses `script_location = %(here)s/alembic` — migrations live in `backend/alembic/versions/`, NOT `backend/app/alembic/versions/` (that directory is empty). The live migrations are in `backend/alembic/versions/`.

**Also important:** `alembic/env.py` imports `from app.models.base import Base` and `from app.models import project`. After removing `conversation.py`, the env.py import of models is unaffected — project model stays. BUT if `conversation.py` was imported anywhere in `app/models/__init__.py`, that import must be removed before running migrations.

### Frontend: What Gets Removed vs What Stays

**Remove completely:**
```
frontend/src/
├── features/discussions/          # REMOVE entire directory
│   └── components/
│       ├── ChatInput.tsx
│       ├── ChatPanel.tsx
│       ├── CompletionCard.tsx
│       ├── ContextPreview.tsx
│       ├── ConversationHistory.tsx
│       ├── MessageBubble.tsx
│       ├── MessageList.tsx
│       ├── QuestionCard.tsx
│       ├── SummaryCard.tsx
│       ├── SummaryPanel.tsx
│       └── TopicSelectionCard.tsx
```

**Rework `ProjectWorkspace.tsx`:**
- Remove: `Sheet`, `SheetContent`, `SheetTrigger` imports and usage
- Remove: `Bot` icon import
- Remove: `chatOpen`, `discussionPhase`, `discussionConversationId` state
- Remove: `handleViewConversation`, `handleStartRevision` handlers
- Remove: `ChatPanel`, `ConversationHistory` imports
- Remove: `conversations` branch in the content render
- Keep: `PhaseTimeline` + `FaseringTab` + `handlePhaseAction` (simplified)
- Simplify `handlePhaseAction` — no longer opens chat, just shows toast for non-timeline actions

**Rework `ProjectNavigation.tsx`:**
- Remove `conversations` entry from `navigationSections` array
- Remove `MessageSquare` icon import
- Update `isEnabled` check to remove `conversations` from enabled list

**Rework `PhasePopover.tsx`:**
- Remove action buttons (`available_actions` loop)
- Remove "Bekijk bespreking" link (no more `conversation_id`)
- Add CLI command display (monospace code block + copy button)
- Add decisions list from context (collapsible if long)
- Add verification score badge if present

**Update `types/phase.ts`:**
- Remove `conversation_id: number | null`
- Add `cli_command: string | null`
- Add `context_decisions: string[]`
- Add `verification_score: string | null`
- Add `verification_gaps: number | null`

### Frontend: Click-to-Copy Pattern

shadcn/ui does not include a built-in copy button — use the `navigator.clipboard` API directly:

```typescript
// Source: browser Clipboard API (standard)
const handleCopy = async (text: string) => {
  await navigator.clipboard.writeText(text)
  // Optionally: toast.success('Gekopieerd!')
}
```

The `useToast` / Sonner toast is already in the project — use `toast.success('Gekopieerd!')`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CONTEXT.md parsing | Custom markdown parser | Simple regex/string split on `<decisions>` XML block | Structure is known and consistent; overkill to use a parser |
| VERIFICATION.md parsing | Full parser | Regex for score pattern + gap count lines | File format is consistent; a parser adds zero value |
| Clipboard copy | Custom solution | `navigator.clipboard.writeText()` | Already a web standard, no library needed |
| Phase directory lookup | Glob with complex patterns | `pathlib.Path.glob(f"{N:02d}-*")` | Simple, already used in `_derive_phase_status()` |

---

## Common Pitfalls

### Pitfall 1: PROJECT_TYPE_PHASES Lives in the File Being Deleted
**What goes wrong:** `PROJECT_TYPE_PHASES` dict is defined in `backend/app/prompts/discuss_phase.py` (line 422). The `api/phases.py` currently imports it from there. If `prompts/` is deleted before moving this mapping, `api/phases.py` breaks.
**How to avoid:** Create `backend/app/config_phases.py` first with just the `PROJECT_TYPE_PHASES` dict. Update `api/phases.py` import. Then delete `prompts/`.
**Warning sign:** `ImportError: cannot import name 'PROJECT_TYPE_PHASES' from 'app.prompts.discuss_phase'`

### Pitfall 2: Alembic Migration in Wrong Directory
**What goes wrong:** There are TWO alembic directories: `backend/alembic/` (real, has versions) and `backend/app/alembic/` (empty artifact). Running `alembic revision` from `backend/app/` creates files in the wrong place.
**How to avoid:** Always run Alembic commands from `backend/` directory (where `alembic.ini` lives): `alembic -c alembic.ini revision --autogenerate -m "drop_conversation_tables"`
**Warning sign:** New migration file appears in `backend/app/alembic/versions/` instead of `backend/alembic/versions/`

### Pitfall 3: alembic/env.py Still Imports Deleted Models
**What goes wrong:** After deleting `conversation.py`, if any import path tries to load it (directly or via `__init__.py`), Alembic will fail to run.
**How to avoid:** Check `backend/app/models/__init__.py` for conversation imports and remove them. Check `alembic/env.py` — currently only imports `project` model (safe). But if autogenerate is used, it will detect table absence and generate `DROP TABLE` automatically.
**Warning sign:** `ModuleNotFoundError: No module named 'app.models.conversation'` during migration

### Pitfall 4: main.py Still Registers Removed Routers
**What goes wrong:** `main.py` line 9 imports `discussions` and `context` from `app.api`. After deleting those files, startup crashes.
**How to avoid:** Remove the imports and `app.include_router()` calls for `discussions` and `context` in `main.py` before or simultaneously with deleting the files.
**Warning sign:** `ImportError` on app startup

### Pitfall 5: PhasePopover `onAction` Callback Becomes a Dead Letter
**What goes wrong:** `PhasePopover` currently calls `onAction(action, phaseNumber)` for buttons. After removing action buttons, the `onAction` prop may become unused but still in the interface — confusing future developers.
**How to avoid:** After removing action buttons from `PhasePopover`, also remove the `onAction` prop entirely. Propagate that change up to `PhaseTimeline` and `PhaseNode`. `handlePhaseAction` in `ProjectWorkspace` can either be removed or simplified to a stub that handles future use.

### Pitfall 6: PROJECT_ROOT Path Construction
**What goes wrong:** Projects may be stored as absolute paths or relative paths. Using `Path(PROJECT_ROOT) / str(project_id)` breaks if PROJECT_ROOT is not set or uses a trailing slash.
**How to avoid:** Use `Path(settings.PROJECT_ROOT).expanduser().resolve() / str(project_id)` for robust path handling. Provide a sensible default (e.g., `./projects` relative to backend root) in Settings.

### Pitfall 7: `usePhaseTimeline` Refetch Interval After Cleanup
**What goes wrong:** The hook currently refetches every 10 seconds (`refetchInterval: 10000`). After cleanup, the backend does filesystem reads on every request — fine for small projects, but worth documenting.
**How to avoid:** Keep the interval as-is for this phase (filesystem reads are cheap). Note in code that refetch polls the filesystem directly.

---

## Code Examples

### Reworked `GET /phases/` Endpoint Pattern
```python
# Source: existing _derive_phase_status() in backend/app/api/phases.py
# Wire this function into the live endpoint:

@router.get("/", response_model=PhaseTimelineResponse)
async def get_phase_timeline(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> PhaseTimelineResponse:
    settings = get_settings()
    project_root = Path(settings.PROJECT_ROOT).expanduser().resolve()

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    phases_data = _get_phases_for_project_type(project.type.value)
    project_dir = project_root / str(project_id)

    phases = []
    for phase_data in phases_data:
        status_info = _derive_phase_status(project_dir, phase_data["number"])
        cli_command = _get_cli_command(status_info["status"], phase_data["number"])
        phases.append(PhaseStatusResponse(
            number=phase_data["number"],
            name=phase_data["name"],
            goal=phase_data["goal"],
            cli_command=cli_command,
            **status_info,
        ))

    return PhaseTimelineResponse(project_id=project_id, phases=phases)
```

### CLI Command Mapping
```python
# Source: CONTEXT.md locked decision
STATUS_CLI_COMMANDS = {
    "not_started": "/doc:discuss-phase {n}",
    "discussed":   "/doc:plan-phase {n}",
    "planned":     "/doc:write-phase {n}",
    "written":     "/doc:verify-phase {n}",
    "verified":    "/doc:review-phase {n}",
    "reviewed":    None,
    "completed":   None,
}

def _get_cli_command(status: str, phase_number: int) -> Optional[str]:
    template = STATUS_CLI_COMMANDS.get(status)
    if template is None:
        return None
    return template.format(n=phase_number)
```

### CONTEXT.md Decisions Extraction
```python
# Source: CONTEXT.md file format — extract <decisions> block
import re

def extract_decisions(content: str) -> list[str]:
    """Extract bullet decisions from <decisions> XML section."""
    match = re.search(r'<decisions>(.*?)</decisions>', content, re.DOTALL)
    if not match:
        return []
    block = match.group(1)
    # Extract lines starting with - or * (markdown bullets)
    decisions = re.findall(r'^[-*]\s+(.+)', block, re.MULTILINE)
    return [d.strip() for d in decisions if d.strip()]
```

### VERIFICATION.md Score Extraction
```python
# Source: analysis of VERIFICATION.md format patterns
import re

def extract_verification_summary(content: str) -> dict:
    """Extract score and gap count from VERIFICATION.md."""
    score_match = re.search(r'(\d+)/(\d+)\s+levels?\s+passed', content, re.IGNORECASE)
    gap_matches = re.findall(r'\|\s*(CRITICAL|MAJOR|MINOR)\s*\|', content, re.IGNORECASE)

    score = f"{score_match.group(1)}/{score_match.group(2)}" if score_match else None
    severity = {
        "critical": gap_matches.count("CRITICAL"),
        "major": gap_matches.count("MAJOR"),
        "minor": gap_matches.count("MINOR"),
    }
    return {
        "score": score,
        "gap_count": len(gap_matches),
        "severity": severity,
    }
```

### PhasePopover CLI Command Block (React)
```typescript
// Source: project conventions — shadcn/ui + Tailwind v4 + Sonner
import { toast } from 'sonner'
import { Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'

function CliCommandBlock({ command }: { command: string }) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(command)
    toast.success('Gekopieerd!')
  }

  return (
    <div className="flex items-center gap-2 bg-muted rounded px-3 py-2">
      <code className="text-xs font-mono flex-1 text-foreground">{command}</code>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={handleCopy}
        title="Kopieer naar klembord"
      >
        <Copy className="h-3 w-3" />
      </Button>
    </div>
  )
}
```

---

## File Inventory: Everything That Touches Discussion Code

### Backend — Files to DELETE:
- `backend/app/llm/__init__.py`
- `backend/app/llm/provider.py`
- `backend/app/llm/litellm_provider.py`
- `backend/app/prompts/__init__.py`
- `backend/app/prompts/discuss_phase.py`
- `backend/app/api/discussions.py`
- `backend/app/api/context.py`
- `backend/app/models/conversation.py`
- `backend/app/services/llm_service.py`
- `backend/app/services/discussion_engine.py`
- `backend/app/services/conversation_state.py`
- `backend/app/services/decision_extractor.py`
- `backend/app/services/context_generator.py`
- `backend/app/services/structured_output_parser.py`
- `backend/app/schemas/conversation.py`

### Backend — Files to MODIFY:
- `backend/app/main.py` — remove `discussions` and `context` router imports + `include_router()` calls
- `backend/app/api/phases.py` — rework to use `_derive_phase_status()`, remove conversation imports, add PROJECT_ROOT path, add cli_command field
- `backend/app/models/phase.py` — remove `conversation_id` field
- `backend/app/schemas/phase.py` — remove `conversation_id`, add `cli_command`, `context_decisions`, `verification_score`, `verification_gaps`
- `backend/app/config.py` — add `PROJECT_ROOT: str` setting
- `backend/requirements.txt` — remove `litellm` and `sse-starlette` lines

### Backend — New Files:
- `backend/app/config_phases.py` — `PROJECT_TYPE_PHASES` dict (extracted from `prompts/discuss_phase.py`)
- `backend/alembic/versions/{hash}_drop_conversation_tables.py` — DROP messages, DROP conversations

### Frontend — Files/Directories to DELETE:
- `frontend/src/features/discussions/` — entire directory

### Frontend — Files to MODIFY:
- `frontend/src/features/projects/ProjectWorkspace.tsx` — remove Sheet/assistant panel, remove discussion state, remove ConversationHistory section
- `frontend/src/features/projects/components/ProjectNavigation.tsx` — remove 'conversations' nav item
- `frontend/src/features/timeline/types/phase.ts` — update `PhaseStatus` type
- `frontend/src/features/timeline/components/PhasePopover.tsx` — rework content: CLI command block + decisions list + verification score
- `frontend/src/features/timeline/components/FaseringTab.tsx` — remove action buttons, remove conversation_id link, add CLI command block

---

## State of the Art

| Old Approach | New Approach | Reason |
|--------------|--------------|--------|
| Phase status from `conversations` DB table | Phase status from filesystem artifacts | Cockpit pivot — CLI owns the work, GUI reads results |
| Action buttons in popover (Start Discussie, etc.) | CLI command code block with copy | GUI is observer, not actor |
| `conversation_id` in PhaseStatus | Removed entirely | No more conversation concept |
| `PROJECT_TYPE_PHASES` in `prompts/discuss_phase.py` | Standalone `config_phases.py` | Prompts module is being deleted |

---

## Open Questions

1. **PROJECT_ROOT path format**
   - What we know: `.env` currently has `LLM_PROVIDER=ollama` and `LLM_MODEL=ollama/qwen2.5:14b` — no PROJECT_ROOT set
   - What's unclear: Where are projects currently stored? `api/context.py` used hardcoded `Path(f"projects/{project_id}")` — this is the current convention
   - Recommendation: Default to `./projects` in Settings (matching current convention). Engineer sets absolute path in `.env` for production deployment.

2. **Existing projects in the live database**
   - What we know: There is a live `gsd_docs.db` in `backend/`. It may have project rows but likely no conversation rows (discussion code was built but never shipped to end users)
   - What's unclear: Do any existing projects have data in `conversations`/`messages` tables?
   - Recommendation: The drop migration handles this cleanly regardless. CASCADE delete is not needed since we're dropping the whole table.

3. **FaseringTab action buttons**
   - What we know: `FaseringTab.tsx` has action buttons per phase card (Bespreken, Plannen, etc.) mirroring the popover
   - What's unclear: CONTEXT.md says "Remove old action buttons from phase popover" — does this extend to FaseringTab cards too?
   - Recommendation: Yes, remove from both. FaseringTab cards should show the CLI command instead of triggering GUI actions. The cockpit decision applies globally.

---

## Validation Architecture

No test infrastructure detected for this project (no `pytest.ini`, no `vitest.config.*`, no test files outside `node_modules`). This phase is primarily deletion + rework — manual verification is appropriate.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Verification |
|--------|----------|-----------|-------------|
| WORK-01 | Phase timeline shows phases with filesystem-based completion status | Manual smoke | Load a project — timeline displays phases with correct status colors |
| WORK-02 | Phase popover shows next CLI command for phase | Manual smoke | Click phase node — popover shows monospace CLI command with copy button |

### Wave 0 Gaps
- No automated test infrastructure exists — these requirements are verified manually by inspection.
- Recommend smoke-testing: start backend (`uvicorn app.main:app`), open frontend, load a project, verify no 500 errors and timeline renders with filesystem-based statuses.

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection — all findings verified against actual source files
  - `backend/app/api/phases.py` — existing `_derive_phase_status()` function (lines 176-255)
  - `backend/app/models/conversation.py` — table structure to be dropped
  - `backend/alembic/versions/fb17f556ba07_add_conversations_and_messages_tables.py` — migration to reverse
  - `backend/app/prompts/discuss_phase.py` — `PROJECT_TYPE_PHASES` mapping location
  - `backend/app/main.py` — router registration to clean up
  - `frontend/src/features/projects/ProjectWorkspace.tsx` — Sheet + ChatPanel wiring
  - `frontend/src/features/projects/components/ProjectNavigation.tsx` — Gesprekken tab
  - `frontend/src/features/timeline/components/PhasePopover.tsx` — action buttons to replace
  - `backend/requirements.txt` — litellm + sse-starlette to remove

---

## Metadata

**Confidence breakdown:**
- Cleanup scope: HIGH — every file inventoried from direct inspection
- Architecture patterns: HIGH — `_derive_phase_status()` already exists and works correctly
- Pitfalls: HIGH — identified from direct code analysis (import chain, migration directory confusion)
- CLI command mapping: HIGH — locked in CONTEXT.md

**Research date:** 2026-03-20
**Valid until:** 2026-06-01 (stable — no external dependencies changing)
