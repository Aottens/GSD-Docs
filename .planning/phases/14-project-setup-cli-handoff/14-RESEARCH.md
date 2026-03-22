# Phase 14: Project Setup & CLI Handoff - Research

**Researched:** 2026-03-22
**Domain:** Wizard extension, document-type metadata, setup state API, React Query polling, CLI handoff endpoint
**Confidence:** HIGH — all findings derived directly from reading existing codebase source files

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Document-type checklist (Wizard Step 4)**
- Replace generic FileUploadZone with a document-type checklist specific to project type (A/B/C/D)
- Type-specific document type sets — different checklist per project type
- Each doc type row: label, inline upload button, file count, and "Niet beschikbaar" toggle
- "Niet beschikbaar" toggle grays out the row and records the decision; can be undone later
- Multiple files allowed per document type
- Doc-type definitions stored in backend config (like PROJECT_TYPE_PHASES pattern)

**Setup status display**
- Setup status shown in ProjectOverview card — a new "Setup status" section
- Checklist with status icons per doc type: green check (uploaded), yellow warning (marked not available), gray dash (not needed)
- Shows file count per doc type
- CLI command shown as copy-ready code block with copy button (reuses CliCommandBlock pattern from Phase 10)
- Context-aware command: `/doc:new-fds` for initial setup, phase-specific commands after setup

**CLI handoff endpoint**
- Backend exposes `GET /api/projects/{id}/setup-state` endpoint
- Returns: project metadata (name, type, language) + reference file paths grouped by doc type + doc type coverage (present/missing/skipped) + project directory path
- Open endpoint (no auth) — read-only, internal team server

**CLI to GUI feedback loop**
- CLI writes files to disk only — no API callback to GUI
- GUI picks up changes via polling auto-refresh (React Query polling, same pattern as Phase 11 document outline — 15000ms interval, but UI-SPEC says 5000ms for setup state)
- After CLI setup completes, GUI automatically reflects scaffolded phases, sections, and outline

**Re-analysis for late-arriving documents**
- When engineer uploads via Referenties tab, a dropdown prompts for doc-type classification
- Setup status card updates automatically (new doc shows as covered)
- Note appears: "Nieuw document toegevoegd — voer /doc:discuss-phase N uit om opnieuw te analyseren." — guidance only, no action button
- Referenties tab gets "Document dekking" collapsible section above existing file browser
- Upload in file browser auto-prompts for doc-type assignment

### Claude's Discretion
- Exact document types per project type A/B/C/D (informed by v1.0 SPECIFICATION.md)
- Polling interval for auto-refresh (UI-SPEC says 5000ms — use that)
- Setup state endpoint response schema details
- Alembic migration for doc-type metadata on files
- "Document dekking" section layout within Referenties tab

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROJ-01 | Engineer can create a new FDS project through a guided wizard with type classification (A/B/C/D) | Existing 4-step wizard in place; Step 4 replacement with DocTypeChecklist addresses the guided reference collection part of setup |
| PROJ-02 | Engineer can select project language (Dutch/English) during project creation | Already implemented in Step 3; no changes needed for this requirement specifically |
| PROJ-04 | Engineer can browse all projects in a dashboard with status and type indicators | Existing dashboard; setup status feeds into the overview card shown after opening a project |
</phase_requirements>

---

## Summary

Phase 14 builds on a complete, working codebase. Every pattern needed already exists — the work is integration and extension, not invention. The wizard, upload hooks, React Query polling, CliCommandBlock, FileUploadZone, and ProjectOverview are all battle-tested. The primary new work is: (1) a doc-type config structure in the backend, (2) a new File model column for doc_type, (3) the setup-state endpoint, (4) replacing Wizard Step 4's inner content with a doc-type checklist, (5) adding a setup status section to ProjectOverview, and (6) adding a "Document dekking" section to the Referenties tab with doc-type assignment on upload.

The biggest technical decision is **how to store doc_type on File records**. The CONTEXT.md lists two options: a new `doc_type` String column on the File model (simplest), or a separate association table (more normalized). Given the single-engineer scale and the fact that doc_type is a simple nullable label, adding a nullable `doc_type` String column to File with an Alembic migration is the correct approach. The setup-state endpoint can query files grouped by doc_type in one DB call.

The GUI never runs AI and the CLI never calls back to the GUI. The feedback loop is polling only. React Query at 5000ms refetchInterval (per the UI-SPEC) on the setup-state query key will pick up filesystem changes after `/doc:new-fds` completes.

**Primary recommendation:** Implement in four layers — (1) backend config + model + migration, (2) setup-state endpoint, (3) wizard Step 4 replacement, (4) ProjectOverview + Referenties tab extensions.

---

## Standard Stack

### Core (already in project — no new installs)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | existing | New setup-state endpoint | Project-standard backend |
| SQLAlchemy async | existing | File.doc_type column query | Established async ORM pattern |
| Alembic | existing | Add doc_type column migration | Migration tool already in use |
| React Query (@tanstack/react-query) | existing | Polling for setup-state endpoint | Established pattern (Phase 11: `refetchInterval: 15000`) |
| react-hook-form | existing | Wizard form state | Already used in ProjectWizard |
| shadcn/ui components | existing | checkbox, collapsible, select, skeleton | Already installed; confirmed in ui/ directory |
| lucide-react | existing | CheckCircle2, Clock, Circle icons | Established icon library |
| sonner | existing | Toast notifications | Established toast pattern |
| XHR via useFileUpload | existing | File upload with progress | Already used in wizard and Referenties tab |

**No new packages required for this phase.**

### New shadcn components to install (if not already present)

Confirmed present in `/frontend/src/components/ui/`: `checkbox.tsx`, `collapsible.tsx`, `select.tsx`, `skeleton.tsx`, `tooltip.tsx` — all already installed. No `npx shadcn add` required.

---

## Architecture Patterns

### Recommended Project Structure (new files only)

```
backend/
├── app/
│   ├── config_phases.py          # Add DOC_TYPE_CONFIG dict here (same module)
│   ├── models/
│   │   └── file.py               # Add doc_type nullable String column
│   ├── api/
│   │   └── projects.py           # Add GET /api/projects/{id}/setup-state route
│   ├── schemas/
│   │   └── setup_state.py        # New: SetupStateResponse Pydantic schema
│   └── alembic/versions/
│       └── XXXX_add_doc_type_to_files.py  # New migration

frontend/src/features/
├── timeline/components/
│   └── CliCommandBlock.tsx        # Extract from FaseringTab.tsx — shared component
├── wizard/components/
│   └── Step4DocTypeChecklist.tsx  # Replaces Step4ReferenceUpload.tsx
├── projects/
│   ├── components/
│   │   └── SetupStatusSection.tsx # New section added inside ProjectOverview
│   └── hooks/
│       └── useSetupState.ts       # React Query hook for /setup-state endpoint
└── files/components/
    └── DocCoverageSection.tsx     # New collapsible section for Referenties tab
```

### Pattern 1: Doc-type config in config_phases.py

Follow the exact same dict-keyed-by-project-type pattern as `PROJECT_TYPE_PHASES`. Add a `DOC_TYPE_CONFIG` dict in `config_phases.py`. Each entry is a list of doc-type definition objects.

**What:** Central config dict for document types per project type.
**When to use:** Backend setup-state endpoint, wizard Step 4 (fetched via new endpoint or embedded in project response), Referenties tab dropdown.

```python
# Source: config_phases.py (existing module pattern)
DOC_TYPE_CONFIG = {
    "A": [
        {"id": "fds_old",      "label": "Oude FDS / bestaande FDS",       "required": True},
        {"id": "pid",          "label": "P&ID tekeningen",                  "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec",   "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",           "required": False},
        {"id": "standards",    "label": "Standaarden scope documenten",     "required": True},
    ],
    "B": [
        {"id": "fds_old",      "label": "Oude FDS / bestaande FDS",       "required": False},
        {"id": "pid",          "label": "P&ID tekeningen",                  "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec",   "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",           "required": False},
    ],
    "C": [
        {"id": "baseline",     "label": "BASELINE.md / bestaand FDS",       "required": True},
        {"id": "pid",          "label": "P&ID tekeningen (bestaand + delta)","required": True},
        {"id": "machine_spec", "label": "Machinespecificatie / PLC-spec",   "required": True},
        {"id": "risk_assess",  "label": "Risicobeoordeling / RA",           "required": False},
        {"id": "change_order", "label": "Wijzigingsopdracht / TWN",         "required": False},
    ],
    "D": [
        {"id": "pid",          "label": "P&ID tekening (gewijzigd)",        "required": False},
        {"id": "change_order", "label": "Wijzigingsopdracht / TWN",         "required": True},
        {"id": "machine_spec", "label": "Machinespecificatie fragment",     "required": False},
    ],
}
```

**Note on Claude's Discretion:** The exact doc types above are a research proposal. The planner MUST instruct the executor to read `gsd-docs-industrial/workflows/new-fds.md` (Step 4 — existing system information) and the DEFAULT_PROJECT_FOLDERS in `backend/app/config.py` to validate alignment before finalizing. The folder names already in use (e.g. "P&IDs", "Standaarden", "Bestaande FDS/SDS") provide the ground truth signal for what engineers actually upload per type.

### Pattern 2: Nullable doc_type column on File model

**What:** Add a `doc_type` nullable String(50) column to the `files` table.
**When to use:** Each file upload in wizard Step 4 and Referenties tab passes `doc_type` as a query param (or form field). The setup-state endpoint groups files by `doc_type`.

```python
# Source: backend/app/models/file.py (extend existing File model)
doc_type = Column(String(50), nullable=True, index=True)
```

Alembic migration adds the column with `nullable=True`, no default — existing file records get NULL.

### Pattern 3: Setup-state endpoint

**What:** New `GET /api/projects/{id}/setup-state` route added to `backend/app/api/projects.py` (or a new `setup.py` router).
**When to use:** Called by the CLI (one-shot) and polled by the GUI (5000ms interval via React Query).

Response schema (Pydantic — `setup_state.py`):

```python
# Source: derived from CONTEXT.md decisions + existing schema patterns
class DocTypeEntry(BaseModel):
    id: str
    label: str
    required: bool
    status: str           # "present" | "missing" | "skipped"
    file_count: int
    file_paths: list[str] # absolute filesystem paths (for CLI consumption)

class SetupStateResponse(BaseModel):
    project_id: int
    project_name: str
    project_type: str     # "A" | "B" | "C" | "D"
    language: str         # "nl" | "en"
    project_dir: str      # PROJECT_ROOT / str(project_id)
    doc_types: list[DocTypeEntry]
    has_scaffolding: bool # True if .planning/ dir exists in project_dir
    next_cli_command: str | None  # "/doc:new-fds" or phase-specific command
```

Endpoint logic: load project from DB, load DOC_TYPE_CONFIG for project type, query all non-deleted project files grouped by doc_type, check for skipped records (doc_type = "skipped__{type_id}"), compute status per entry, derive has_scaffolding from filesystem, derive next_cli_command using existing get_cli_command() helper.

### Pattern 4: React Query polling for setup-state

**What:** Custom hook `useSetupState(projectId)` using `refetchInterval`.
**When to use:** Used in `SetupStatusSection` (inside ProjectOverview) and optionally in `DocCoverageSection`.

```typescript
// Source: derived from useDocumentOutline.ts (Phase 11 pattern)
export function useSetupState(projectId: number) {
  return useQuery({
    queryKey: ['projects', projectId, 'setup-state'],
    queryFn: () => api.get<SetupStateResponse>(`/projects/${projectId}/setup-state`),
    refetchInterval: 5000,   // UI-SPEC IC-4: 5000ms
    staleTime: 3000,
    enabled: !!projectId,
  })
}
```

### Pattern 5: CliCommandBlock extraction

**What:** The `CliCommandBlock` function in `FaseringTab.tsx` (lines 14-34) is a pure display component. Extract it to `frontend/src/features/timeline/components/CliCommandBlock.tsx` as a named export. Import it in both `FaseringTab.tsx` and the new `SetupStatusSection.tsx`.

No visual changes. The component is self-contained (uses `navigator.clipboard`, `toast`, `Button`, `Copy` icon).

### Pattern 6: Wizard Step 4 replacement

**What:** Replace the content of `Step4ReferenceUpload.tsx` with `DocTypeChecklist`. The wizard already knows `formData.type` (from Step 2 `watch()`). Pass `projectType` as a prop.

**Key constraint:** The wizard creates the project on form submit (Step 4 "Project aanmaken" button). Files must be uploaded after project creation. The current wizard flow: Step 4 file selection → submit → create project → upload files → navigate. The doc-type checklist needs to buffer `{file, docType}` pairs in local state, then pass them to `useFileUpload` with doc_type as a query param on submit.

**Upload URL with doc_type:**
```
POST /api/projects/{projectId}/files?folder_id={folderId}&doc_type={typeId}
```

The existing `useFileUpload` hook needs a small extension: accept an optional `docType` param per file, append it to the upload URL.

### Pattern 7: Referenties tab — doc-type assignment on upload

**What:** Intercept the file selection event in `ProjectFilesTab` before calling `uploadFiles`. Show a `Select` dropdown (shadcn Select component — already installed) for doc-type classification. On confirmation, call uploadFiles with the `doc_type` param.

**State approach:** Local state `pendingFiles: {file: File, docType: string | null}[]`. After file selection, populate pendingFiles. Render Select per pending file. On "Uploaden" confirm, call uploadFiles with doc_type params. This is contained within `ProjectFilesTab` without changing the `useFileUpload` hook interface.

### Anti-Patterns to Avoid

- **Do not add doc_type as a required field on existing File schema**: Keep it nullable everywhere. Existing file records have no doc_type; backward compat is required.
- **Do not add a new upload endpoint for doc-type uploads**: Extend the existing `POST /api/projects/{project_id}/files` route with a `doc_type` optional query param instead.
- **Do not put DOC_TYPE_CONFIG in a separate file**: Add to `config_phases.py` (same pattern, same module, discoverable alongside PROJECT_TYPE_PHASES).
- **Do not have the CLI make API calls to the GUI backend**: CLI reads `GET /setup-state` only. GUI-to-CLI is one-way via filesystem.
- **Do not nest DocTypeChecklist inside the existing FileUploadZone**: DocTypeChecklist replaces the FileUploadZone in Step 4. FileUploadZone is used within each DocTypeChecklist row, not wrapping it.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File upload progress per doc type | Custom upload tracker | Existing `useFileUpload` hook (XHR-based) | Already handles progress, error, retry |
| Copy-to-clipboard CLI command | Custom clipboard handler | `navigator.clipboard.writeText` + sonner toast (existing CliCommandBlock pattern) | Already implemented and tested |
| Checklist row status icons | Custom icon components | lucide-react CheckCircle2, Clock, Circle (same as FaseringTab) | Consistent with established iconography |
| Polling for filesystem changes | WebSocket or SSE | React Query `refetchInterval` (same as Phase 11) | Proven pattern, no server infrastructure needed |
| Doc-type dropdown in upload flow | Custom select widget | shadcn Select (already installed) | Accessible, styled, consistent |
| Doc-type config lookup | Database table | Python dict in config_phases.py | Config changes don't need migrations; types are stable |

---

## Common Pitfalls

### Pitfall 1: Wizard submit timing with doc-type uploads

**What goes wrong:** The wizard creates the project in the submit handler, then uploads files. If the doc-type data is held in the DocTypeChecklist component's local state, it won't be accessible at submit time in the parent wizard without explicit wiring.

**Why it happens:** The wizard's `selectedFiles` state is in `ProjectWizard.tsx`. The current `handleFilesSelected` callback gets File[] from Step4. With doc-types, we need `{file: File, docType: string}[]`.

**How to avoid:** Change the Step 4 prop from `onFilesSelected: (files: File[]) => void` to `onFilesSelected: (entries: {file: File, docType: string | null}[]) => void`. Update `selectedFiles` state in ProjectWizard accordingly. Pass docType per file to `useFileUpload` when uploading after project creation.

**Warning signs:** Upload succeeds but doc_type is always null on created files.

### Pitfall 2: doc_type migration on existing files

**What goes wrong:** Alembic adds nullable column but existing SQL indexes query doc_type, causing issues on upgrade.

**Why it happens:** Adding a nullable String column is safe in SQLite; the migration is simple. But if any query filters on `doc_type IS NOT NULL` without the index, it table-scans.

**How to avoid:** Add `Index('ix_files_doc_type', 'doc_type')` in the migration (not in the model, because it's added retroactively). The File model `__table_args__` doesn't need updating since migration handles it.

### Pitfall 3: Project directory path resolution in setup-state endpoint

**What goes wrong:** `_get_project_dir()` in phases.py constructs `PROJECT_ROOT / str(project_id)`. If PROJECT_ROOT is relative (`./projects`), the path resolves relative to the process cwd. On the VM this is fine. In dev this is fine. But if the CLI runs from a different directory than the backend, the path returned by the API may not match.

**Why it happens:** The existing `_get_project_dir` uses `Path(settings.PROJECT_ROOT).expanduser().resolve()`. The resolve() call makes it absolute at call time, which is correct. Reuse this exact helper.

**How to avoid:** Reuse `_get_project_dir(project_id)` from `phases.py` verbatim in the setup-state endpoint. Do not reimplement path resolution.

### Pitfall 4: "Niet beschikbaar" toggle state not persisted to backend

**What goes wrong:** Engineer marks a doc type as "Niet beschikbaar". State lives only in React. On page refresh, the toggle reverts to unchecked.

**Why it happens:** The toggle needs to be persisted. The CONTEXT.md decision says "records the decision" — this must go to the database or the file.

**How to avoid:** Represent a "skipped" decision as a sentinel file record with `doc_type = "skipped__{type_id}"` and `is_deleted = false`, or use a dedicated `doc_type_skipped` boolean / separate table. The simplest approach: when toggling "Niet beschikbaar", POST a dummy file record with a special convention, or store the skipped state in a new nullable `doc_type_skipped` JSON column on the Project model. **Recommended**: Store skipped doc types as a JSON string on the Project model (new column `skipped_doc_types`), not as File records (to avoid contaminating the files list). This requires a second Alembic migration column on projects.

**Alternative (simpler but less clean):** Store skipped as a per-project in-memory state that resets. Per CONTEXT.md, the toggle "can be undone later" — this implies persistence. Use the Project model JSON column approach.

### Pitfall 5: CliCommandBlock copy button in wizard context

**What goes wrong:** CliCommandBlock uses `navigator.clipboard.writeText()`. In Safari or non-HTTPS contexts, clipboard API may fail silently.

**Why it happens:** Clipboard API requires secure context (HTTPS or localhost). On the internal VM with HTTP, this would fail.

**How to avoid:** Wrap in try/catch; fallback to `document.execCommand('copy')` or show the command in a text input for manual copy. The existing CliCommandBlock in FaseringTab already uses `async/await` on clipboard — check if any error handling is present. Currently there is none. Add a try/catch when extracting to the shared component.

### Pitfall 6: useFileUpload hook extension — breaking existing callers

**What goes wrong:** Adding `docType` param to `uploadFile()` could break the three existing call sites: wizard, ProjectFilesTab, SharedLibraryTab.

**Why it happens:** If the signature changes and old callers don't pass the new param, TypeScript will catch it — but runtime behavior won't break (optional param with default undefined).

**How to avoid:** Make `docType` optional in the `uploadFile` function signature and the URL construction. Only append `&doc_type=...` to the URL when `docType` is defined. Zero breaking changes to existing callers.

---

## Code Examples

### Existing polling pattern (Phase 11 — use this as template)

```typescript
// Source: frontend/src/features/documents/hooks/useDocumentOutline.ts
export function useDocumentOutline(projectId: number) {
  return useQuery({
    queryKey: documentKeys.outline(projectId),
    queryFn: () => api.get<DocumentOutlineResponse>(`/projects/${projectId}/documents/outline`),
    refetchInterval: 15000,
    staleTime: 10000,
  })
}
// For setup-state: use refetchInterval: 5000 per UI-SPEC IC-4
```

### Existing CliCommandBlock (extract this exactly)

```typescript
// Source: frontend/src/features/timeline/components/FaseringTab.tsx, lines 14-34
function CliCommandBlock({ command }: { command: string }) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(command)
    toast.success('Gekopieerd!')
  }
  return (
    <div className="flex items-center gap-2 bg-muted rounded px-3 py-2">
      <code className="text-xs font-mono flex-1 text-foreground">{command}</code>
      <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0"
        onClick={handleCopy} title="Kopieer naar klembord">
        <Copy className="h-3 w-3" />
      </Button>
    </div>
  )
}
```

### Existing status icon pattern (FaseringTab — reuse for doc-type checklist rows)

```typescript
// Source: frontend/src/features/timeline/components/FaseringTab.tsx, lines 43-51
const getStatusStyle = (status: string) => {
  if (status === 'completed') {
    return { color: 'text-green-500', bg: 'bg-green-500/10', Icon: CheckCircle2 }
  }
  if (['discussed', 'planned', 'written', 'verified', 'reviewed'].includes(status)) {
    return { color: 'text-amber-500', bg: 'bg-amber-500/10', Icon: CheckCircle2 }
  }
  return { color: 'text-muted-foreground', bg: 'bg-muted', Icon: Circle }
}
// For doc-type: map "present" -> green CheckCircle2, "skipped" -> amber Clock, "missing" -> gray Circle
```

### Existing Alembic migration pattern (use as template)

```python
# Source: backend/alembic/versions/73e05ffb68dc_initial_migration_create_projects_table.py
# Pattern for adding a nullable column:
def upgrade() -> None:
    op.add_column('files', sa.Column('doc_type', sa.String(length=50), nullable=True))
    op.create_index('ix_files_doc_type', 'files', ['doc_type'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_files_doc_type', table_name='files')
    op.drop_column('files', 'doc_type')
```

### Existing upload hook URL extension pattern

```typescript
// Source: frontend/src/features/files/hooks/useFileUpload.ts, lines 20-23
const baseUrl = projectId
  ? `/api/projects/${projectId}/files`
  : '/api/files/shared'
const url = folderId ? `${baseUrl}?folder_id=${folderId}` : baseUrl
// Extension: append &doc_type={docType} when provided
// url = folderId
//   ? `${baseUrl}?folder_id=${folderId}${docType ? `&doc_type=${encodeURIComponent(docType)}` : ''}`
//   : `${baseUrl}${docType ? `?doc_type=${encodeURIComponent(docType)}` : ''}`
```

### Existing project files endpoint (add doc_type query param)

```python
# Source: backend/app/api/files.py (extend upload_project_file)
async def upload_project_file(
    project_id: int,
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[int] = Query(None),
    doc_type: Optional[str] = Query(None, max_length=50),  # ADD THIS
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    # Pass doc_type to file_service.create_file()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic FileUploadZone in wizard Step 4 | Doc-type checklist with per-type rows | Phase 14 | Engineers can specify document intent during collection |
| No doc-type metadata on files | nullable `doc_type` String(50) on File model | Phase 14 (new Alembic migration) | Enables coverage tracking and CLI handoff |
| No setup-state endpoint | `GET /api/projects/{id}/setup-state` | Phase 14 | CLI gets everything in one call; GUI polls for auto-refresh |
| CLI has no visibility into GUI-uploaded files | Setup-state endpoint includes file paths per doc type | Phase 14 | CLI can use uploaded reference files without manual path specification |

**Deprecated/outdated after this phase:**
- `Step4ReferenceUpload.tsx` inner content (replaced by DocTypeChecklist)
- CliCommandBlock defined locally in FaseringTab.tsx (extracted to shared component)

---

## Integration Points (Implementation Order)

1. **Backend config**: Add `DOC_TYPE_CONFIG` to `config_phases.py`. Verify doc types against `gsd-docs-industrial/workflows/new-fds.md` Step 4 and `DEFAULT_PROJECT_FOLDERS` in `config.py` for correctness.

2. **Backend model + migration**: Add `doc_type` nullable String(50) to `File` model. Add `skipped_doc_types` JSON/String column to `Project` model for persisting "Niet beschikbaar" decisions. Write two Alembic migrations (can be one combined migration).

3. **Backend schemas**: Create `SetupStateResponse` Pydantic schema in `backend/app/schemas/setup_state.py`. Extend `FileResponse` and `FileUploadResponse` schemas to include `doc_type`.

4. **Backend endpoint**: Add `GET /api/projects/{id}/setup-state` route to `projects.py` (or `setup.py`). Add `doc_type` optional query param to existing `upload_project_file` endpoint.

5. **Shared frontend component**: Extract `CliCommandBlock` from `FaseringTab.tsx` to `frontend/src/features/timeline/components/CliCommandBlock.tsx`.

6. **Wizard Step 4**: Replace `Step4ReferenceUpload` content with `DocTypeChecklist`. Fetch doc types from `DOC_TYPE_CONFIG` via a new `GET /api/projects/doc-types/{project_type}` endpoint (or embed in setup-state). Change wizard `selectedFiles` state to `{file: File, docType: string | null}[]`. Extend `useFileUpload` to accept optional `docType` per file.

7. **ProjectOverview — SetupStatusSection**: Add new section below Metadata grid. Use `useSetupState` hook (React Query, 5000ms interval). Show doc-type checklist rows (read-only) + CliCommandBlock.

8. **Referenties tab — DocCoverageSection**: Add collapsible "Document dekking" section above FileUploadZone in `ProjectFilesTab`. Intercept file selection to show doc-type Select dropdown before upload. Invalidate `setup-state` query key on upload complete.

---

## Open Questions

1. **Exact doc type definitions per project type A/B/C/D**
   - What we know: `DEFAULT_PROJECT_FOLDERS` in config.py gives strong signal ("P&IDs", "Standaarden", "Bestaande FDS/SDS", "Bestaande documentatie"). The new-fds.md workflow Step 4 asks engineers for existing docs (FDS, P&ID, specs). CONTEXT.md mentions: old FDS, P&ID, machine spec, risk assessment.
   - What's unclear: Type A specifically mentions "standards scope docs" — does this map to a separate doc type beyond P&ID and machine spec?
   - Recommendation: Use the proposed `DOC_TYPE_CONFIG` dict as starting point. Executor MUST cross-reference `gsd-docs-industrial/workflows/new-fds.md` Step 4 section 4.3 and DEFAULT_PROJECT_FOLDERS before finalizing. Flag for engineer review if uncertain.

2. **Storing "Niet beschikbaar" decisions**
   - What we know: Must persist across page refresh. CONTEXT.md says "can be undone later."
   - What's unclear: Should skipped state live on the Project model (JSON column), as a sentinel File record, or as a separate table?
   - Recommendation: Add `skipped_doc_types` as a JSON-serialized String column on the Project model (e.g., `'["pid","risk_assess"]'`). Simplest, backward compatible, queryable. One additional Alembic migration column on projects.

3. **Doc-types endpoint for wizard (before project exists)**
   - What we know: The wizard is at Step 4 and the project type is known (Step 2). The project does NOT exist yet.
   - What's unclear: How does Step 4 fetch the doc-type definitions? The project doesn't exist, so setup-state can't be called.
   - Recommendation: Add a simple `GET /api/doc-types/{project_type}` endpoint (no auth, no DB query) that returns `DOC_TYPE_CONFIG[project_type]`. Or — even simpler — ship the entire DOC_TYPE_CONFIG as a static TypeScript constant in the frontend (since it changes rarely). This avoids a network round-trip in the wizard. Mark as Claude's discretion.

---

## Validation Architecture

> `workflow.nyquist_validation` is not set to false in `.planning/config.json` — section included.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Not yet detected — no pytest.ini, jest.config, or vitest.config found in project |
| Config file | None found — Wave 0 gap |
| Quick run command | `cd backend && python -m pytest tests/ -x -q` (if pytest is installed) |
| Full suite command | `cd backend && python -m pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROJ-01 | Wizard Step 4 renders doc-type checklist for project type | manual | — (UI interaction) | ❌ Wave 0 |
| PROJ-01 | Setup-state endpoint returns correct doc_types for project type | unit | `pytest tests/test_setup_state.py::test_doc_types_by_type -x` | ❌ Wave 0 |
| PROJ-01 | File upload with doc_type saves doc_type on File record | unit | `pytest tests/test_files.py::test_upload_with_doc_type -x` | ❌ Wave 0 |
| PROJ-04 | SetupStatusSection shows correct coverage after CLI completes | manual | — (requires CLI filesystem changes) | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && python -m pytest tests/ -x -q` (if test infrastructure exists)
- **Per wave merge:** `cd backend && python -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_setup_state.py` — covers setup-state endpoint, doc-type coverage computation
- [ ] `backend/tests/test_files.py` — extend with `doc_type` upload tests if file tests exist
- [ ] Verify pytest is in `backend/requirements.txt` or `pyproject.toml`

*(If test infrastructure is absent project-wide, mark all backend tests as manual-only during Wave 0)*

---

## Sources

### Primary (HIGH confidence)

All findings derived from direct source code reading:

- `backend/app/config_phases.py` — PROJECT_TYPE_PHASES pattern, STATUS_CLI_COMMANDS, get_cli_command()
- `backend/app/api/projects.py` — existing project endpoints, auth patterns
- `backend/app/api/phases.py` — _get_project_dir(), _derive_phase_status(), existing filesystem-based status detection
- `backend/app/api/files.py` — upload_project_file() signature, doc_type param extension point
- `backend/app/models/file.py` — File model schema, __table_args__ index pattern
- `backend/app/models/project.py` — Project model for skipped_doc_types column addition
- `backend/app/config.py` — DEFAULT_PROJECT_FOLDERS per type (doc-type config reference)
- `backend/alembic/versions/73e05ffb68dc_*.py` — Alembic migration pattern
- `frontend/src/features/wizard/ProjectWizard.tsx` — 4-step wizard, submit flow, selectedFiles state
- `frontend/src/features/wizard/components/Step4ReferenceUpload.tsx` — component to replace
- `frontend/src/features/files/hooks/useFileUpload.ts` — upload hook, URL construction, XHR pattern
- `frontend/src/features/files/components/FileUploadZone.tsx` — dropzone component, reuse pattern
- `frontend/src/features/files/components/ProjectFilesTab.tsx` — Referenties tab file browser
- `frontend/src/features/projects/components/ProjectOverview.tsx` — overview card structure to extend
- `frontend/src/features/projects/ProjectWorkspace.tsx` — workspace layout, section routing
- `frontend/src/features/timeline/components/FaseringTab.tsx` — CliCommandBlock definition (lines 14-34)
- `frontend/src/features/documents/hooks/useDocumentOutline.ts` — React Query polling pattern (refetchInterval: 15000)
- `.planning/phases/14-project-setup-cli-handoff/14-UI-SPEC.md` — visual contract, component inventory, interaction contracts, copywriting
- `gsd-docs-industrial/workflows/new-fds.md` — CLI project init workflow (doc types referenced in Step 4)

### Secondary (MEDIUM confidence)

- `backend/app/schemas/project.py` — schema patterns for new SetupStateResponse design
- `.planning/STATE.md` — project decisions and architecture choices

---

## Metadata

**Confidence breakdown:**
- Backend config/model pattern: HIGH — directly mirrors existing PROJECT_TYPE_PHASES pattern in same module
- Setup-state endpoint: HIGH — follows exact pattern of phases.py filesystem-reading endpoints
- Frontend polling: HIGH — documented in useDocumentOutline.ts, UI-SPEC specifies 5000ms
- CliCommandBlock extraction: HIGH — component is self-contained, 20 lines
- Wizard Step 4 replacement: HIGH — clear replacement target, prop interface change documented
- Referenties tab extension: HIGH — ProjectFilesTab structure fully understood
- Exact doc-type definitions per project type: MEDIUM — proposed from DEFAULT_PROJECT_FOLDERS + new-fds.md; executor must validate against v1.0 source before finalizing

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable stack — no fast-moving dependencies in scope)
