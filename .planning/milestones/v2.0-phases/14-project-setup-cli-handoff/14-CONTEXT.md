# Phase 14: Project Setup & CLI Handoff - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can create projects via GUI with guided reference document collection (document-type checklist per project type), then complete intelligent setup via CLI. Project overview shows setup status with doc coverage and CLI command. Late-arriving documents can be uploaded, classified by type, and the GUI hints at which CLI commands to re-run. GUI never runs AI — it guides the engineer to the right CLI command.

</domain>

<decisions>
## Implementation Decisions

### Document-type checklist (Wizard Step 4)
- Replace generic FileUploadZone with a document-type checklist specific to project type (A/B/C/D)
- Type-specific document type sets — different checklist per project type (e.g., Type C/D includes BASELINE.md, Type A includes standards scope docs)
- Each doc type is a checklist row with: label, inline upload button, file count, and "Niet beschikbaar" toggle
- "Niet beschikbaar" toggle grays out the row and records the decision; can be undone later
- Multiple files allowed per document type (e.g., multiple P&IDs per project)
- Doc-type definitions stored in backend config (like PROJECT_TYPE_PHASES pattern)

### Setup status display
- Setup status shown in ProjectOverview card — a new "Setup status" section within the existing overview
- Checklist with status icons per doc type: green check (uploaded), yellow warning (coming later/marked not available), gray dash (not needed)
- Shows file count per doc type
- CLI command shown as copy-ready code block with copy button (reuses CliCommandBlock pattern from Phase 10)
- The command shown is context-aware: `/doc:new-fds` for initial setup, phase-specific commands after setup

### CLI handoff endpoint
- Backend exposes `GET /api/projects/{id}/setup-state` endpoint
- Returns full setup bundle: project metadata (name, type, language) + reference file paths grouped by doc type + doc type coverage (present/missing/skipped) + project directory path
- Open endpoint (no auth) — read-only, internal team server, same pattern as existing project APIs
- CLI reads this endpoint to get everything it needs in one call

### CLI → GUI feedback loop
- CLI writes files to disk only (ROADMAP.md, STATE.md, CONTEXT.md, etc.) — no API callback to GUI
- GUI picks up changes via polling auto-refresh (React Query polling, same pattern as Phase 11 document outline)
- After CLI setup completes, GUI automatically reflects scaffolded phases, sections, and outline

### Re-analysis for late-arriving documents
- When engineer uploads a new doc via Referenties tab, a dropdown prompts for doc-type classification (same types as wizard checklist)
- Setup status card in overview updates automatically (new doc shows as covered)
- A note appears: "Nieuw document toegevoegd — voer /doc:discuss-phase N uit om opnieuw te analyseren." — guidance only, no action button
- Referenties tab gets a "Document dekking" checklist section above the existing file browser, showing doc-type coverage status
- Upload in file browser auto-prompts for doc-type assignment

### Claude's Discretion
- Exact document types per project type A/B/C/D (informed by v1.0 SPECIFICATION.md)
- Polling interval for auto-refresh
- Setup state endpoint response schema details
- Alembic migration for doc-type metadata on files
- "Document dekking" section layout within Referenties tab

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project type definitions
- `gsd-docs-industrial/SPECIFICATION.md` — SSOT for project types A/B/C/D, their phase structures, and required reference documents
- `backend/app/config_phases.py` — PROJECT_TYPE_PHASES and STATUS_CLI_COMMANDS definitions

### Existing wizard and file management
- `frontend/src/features/wizard/ProjectWizard.tsx` — Current 4-step wizard implementation
- `frontend/src/features/wizard/components/Step4ReferenceUpload.tsx` — Current generic upload step (to be replaced)
- `frontend/src/features/files/components/FileUploadZone.tsx` — Reusable upload component
- `frontend/src/features/files/hooks/useFileUpload.ts` — Upload hook with progress tracking

### Project overview and workspace
- `frontend/src/features/projects/components/ProjectOverview.tsx` — Current overview card (to be extended with setup status)
- `frontend/src/features/projects/ProjectWorkspace.tsx` — Workspace layout with tab navigation

### Backend models and schemas
- `backend/app/models/project.py` — Project model with type, language, status
- `backend/app/models/file.py` — File model for reference documents
- `backend/app/schemas/project.py` — Project response schemas

### Phase 10 CLI command pattern
- `frontend/src/features/timeline/components/FaseringTab.tsx` — CliCommandBlock pattern for copy-ready CLI commands

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FileUploadZone` component: drag-and-drop upload with progress bars — reuse for inline doc-type uploads
- `useFileUpload` hook: handles multi-file upload with XHR progress — reuse for wizard and Referenties tab
- `CliCommandBlock` pattern (FaseringTab): styled code block with copy — reuse for setup status CLI command
- `ProjectOverview` component: card layout with badges, progress, metadata — extend with setup status section
- React Query polling: established pattern from Phase 11 document outline — reuse for auto-refresh after CLI setup

### Established Patterns
- `PROJECT_TYPE_PHASES` in config_phases.py: type-specific config pattern — use same approach for document type definitions
- `config_phases.py` as standalone config module — add doc-type config alongside or in same module
- File model with folder association — extend with doc_type field or separate association table
- Defense-in-depth file validation (5 layers) — applies to all new upload paths
- All UI in Dutch — consistent with Phase 8/9 decisions

### Integration Points
- Wizard Step 4: replace `Step4ReferenceUpload` content with doc-type checklist
- ProjectOverview: add setup status card section
- Referenties tab: add "Document dekking" section above file browser
- File upload flow: add doc-type dropdown on upload in Referenties tab
- Backend: new `/api/projects/{id}/setup-state` endpoint
- Backend: doc-type metadata on file records (Alembic migration)

</code_context>

<specifics>
## Specific Ideas

- Wizard checklist rows should feel lightweight — not full cards, just compact rows with icon + label + upload button + toggle
- Setup status in overview should clearly communicate "what to do next" — the CLI command is the primary call-to-action
- Doc-type config should follow the same pattern as PROJECT_TYPE_PHASES — a dict keyed by project type

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 14-project-setup-cli-handoff*
*Context gathered: 2026-03-22*
