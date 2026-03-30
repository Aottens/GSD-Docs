---
phase: 14-project-setup-cli-handoff
verified: 2026-03-22T10:15:00Z
status: human_needed
score: 5/6 success criteria verified automatically
re_verification: false
human_verification:
  - test: "After CLI writes .planning/ to disk, verify setup status section updates within 5–10 seconds (no page refresh)"
    expected: "has_scaffolding becomes true, next_cli_command changes from /doc:new-fds to first phase command"
    why_human: "Requires actual CLI execution writing to filesystem and live polling observation — cannot simulate in static analysis"
---

# Phase 14: Project Setup & CLI Handoff — Verification Report

**Phase Goal:** Engineers can create projects via GUI with guided reference document collection, then complete intelligent setup via CLI. Late-arriving documents can be added and re-processed.
**Verified:** 2026-03-22T10:15:00Z
**Status:** human_needed — all automated checks passed; one criterion requires runtime observation
**Re-verification:** No — initial verification

---

## Goal Achievement

### Success Criteria from ROADMAP.md

| # | Criterion | Status | Evidence |
|---|-----------|--------|---------|
| 1 | Wizard step 4 shows document-type checklist (old FDS, P&ID, machine spec, risk assessment) instead of generic upload | VERIFIED | `Step4DocTypeChecklist.tsx` renders doc-type rows from `useDocTypeConfig`, renders `CheckCircle2`/`Clock`/`Circle` icons, upload buttons, and "Niet beschikbaar" checkboxes |
| 2 | Engineer can mark document types as "not available / will add later" | VERIFIED | Checkbox `onCheckedChange` toggles skipped state; grays out row with `opacity-50` + `line-through`; `ProjectWizard.onSubmit` calls `PATCH /api/projects/{id}/skipped-doc-types` |
| 3 | Project overview shows setup status: which reference docs are present vs missing, and CLI command | VERIFIED | `SetupStatusSection.tsx` wired to `useSetupState(projectId)` with 5s polling; shows coverage icons, file counts, "Volgende stap in CLI" + `CliCommandBlock` |
| 4 | Backend exposes project setup state endpoint for CLI consumption | VERIFIED | `GET /api/projects/{id}/setup-state` returns `SetupStateResponse` (project metadata, doc-type coverage with status/file_paths, has_scaffolding, next_cli_command); registered in `main.py` |
| 5 | After CLI setup completes, GUI automatically reflects scaffolded phases | NEEDS HUMAN | `useSetupState` polls at 5000ms refetchInterval — the `has_scaffolding` flag and `next_cli_command` will update automatically. Phase/outline display (FaseringTab) is independent. Actual reflection requires live CLI execution. |
| 6 | Engineer can upload additional references later via Referenties tab and trigger re-analysis | VERIFIED | `ProjectFilesTab` intercepts file selection when `docTypes` configured, shows doc-type Select prompt, `handleDocTypeConfirm` calls `uploadFiles` with `docType`, then `invalidateQueries(['projects', projectId, 'setup-state'])` |

**Score:** 5/6 success criteria verified automatically

---

## Required Artifacts

### Plan 01 — Backend

| Artifact | Status | Evidence |
|----------|--------|---------|
| `backend/app/config_phases.py` | VERIFIED | `DOC_TYPE_CONFIG` dict with keys A/B/C/D, each a list of `{id, label, required}` dicts |
| `backend/app/models/file.py` | VERIFIED | `doc_type = Column(String(50), nullable=True, index=True)` on `File` class |
| `backend/app/models/project.py` | VERIFIED | `skipped_doc_types = Column(String(500), nullable=True)` on `Project` class |
| `backend/app/schemas/setup_state.py` | VERIFIED | Exports `DocTypeConfigEntry`, `DocTypeEntry`, `SetupStateResponse` (uses `Optional[str]` for Python 3.9 compat) |
| `backend/app/api/projects.py` | VERIFIED | `get_setup_state` at `GET /{project_id}/setup-state`, `get_doc_types` at `GET /api/doc-types/{project_type}` (via `doc_types_router`), `update_skipped_doc_types` at `PATCH /{project_id}/skipped-doc-types` |
| `backend/app/api/files.py` | VERIFIED | `doc_type: Optional[str] = Query(None, max_length=50)` param; `'doc_type': doc_type` passed to `service.create_file()`; returned in `FileUploadResponse` |
| `backend/alembic/versions/5fad8e9a85f3_add_doc_type_to_files_and_skipped_doc_.py` | VERIFIED | Adds `doc_type` column + index on `files`, adds `skipped_doc_types` column on `projects`; downgrade reverses both |
| `backend/tests/test_setup_state.py` | VERIFIED | 9 tests — all passing (`9 passed, 1 warning` via `pytest`) |

### Plan 02 — Frontend Wizard + Shared Components

| Artifact | Status | Evidence |
|----------|--------|---------|
| `frontend/src/types/setupState.ts` | VERIFIED | Exports `DocTypeConfigEntry`, `DocTypeEntry` (with `'present' \| 'missing' \| 'skipped'` union), `SetupStateResponse` |
| `frontend/src/features/timeline/components/CliCommandBlock.tsx` | VERIFIED | Named export `CliCommandBlock`; `try/catch` around `navigator.clipboard.writeText()`; fallback `toast.error('Kopieer niet beschikbaar')` |
| `frontend/src/features/projects/hooks/useSetupState.ts` | VERIFIED | Exports `useSetupState` (`refetchInterval: 5000`, `staleTime: 3000`) and `useDocTypeConfig` (`staleTime: Infinity`) |
| `frontend/src/features/wizard/components/Step4DocTypeChecklist.tsx` | VERIFIED | Fetches via `useDocTypeConfig(projectType)`; renders rows with status icons, label, file count, upload button, "Niet beschikbaar" checkbox; exports `DocTypeFileEntry` |
| `frontend/src/features/timeline/components/FaseringTab.tsx` | VERIFIED | `import { CliCommandBlock } from './CliCommandBlock'`; no local `function CliCommandBlock` definition |
| `frontend/src/features/files/hooks/useFileUpload.ts` | VERIFIED | `uploadFile(file, folderId?, docType?)` and `uploadFiles(files, folderId?, docType?)`; URL built via `URLSearchParams` with conditional `doc_type` |
| `frontend/src/features/wizard/ProjectWizard.tsx` | VERIFIED | Imports `Step4DocTypeChecklist` and `DocTypeFileEntry`; `selectedFiles: DocTypeFileEntry[]`; `skippedDocTypes: string[]` state; calls `PATCH skipped-doc-types` then iterates `uploadFile(entry.file, undefined, entry.docType)` per entry |

### Plan 03 — Frontend Overview + Referenties

| Artifact | Status | Evidence |
|----------|--------|---------|
| `frontend/src/features/projects/components/SetupStatusSection.tsx` | VERIFIED | Calls `useSetupState(projectId)`; loading/error/empty/data states; "Setup status" heading; "Volgende stap in CLI" text; `CliCommandBlock` for command; coverage rows with `CheckCircle2`/`Clock`/`Circle` |
| `frontend/src/features/files/components/DocCoverageSection.tsx` | VERIFIED | `Collapsible` (closed by default); `useSetupState(projectId)`; "Document dekking" heading; note text "Nieuw document toegevoegd"; returns `null` when no doc types |
| `frontend/src/features/projects/components/ProjectOverview.tsx` | VERIFIED | `import { SetupStatusSection }` from `'./SetupStatusSection'`; `<SetupStatusSection projectId={project.id} />` inside `<Card className="p-6">` between Summary Card and Quick Actions |
| `frontend/src/features/files/components/ProjectFilesTab.tsx` | VERIFIED | `projectType?: string` prop; `DocCoverageSection` rendered when `projectType` defined; `showDocTypePrompt` state; "Selecteer type..." placeholder; "Zonder type" button; `invalidateQueries` with `setup-state` key |

---

## Key Link Verification

### Plan 01 Links

| From | To | Via | Status | Evidence |
|------|----|-----|--------|---------|
| `api/projects.py` | `config_phases.py` | `DOC_TYPE_CONFIG` import | WIRED | `from app.config_phases import DOC_TYPE_CONFIG, get_cli_command` at line 20 |
| `api/files.py` | `models/file.py` | `doc_type` passed to `create_file` | WIRED | `'doc_type': doc_type` in `service.create_file({...})` dict at line 124 |
| `doc_types_router` | `main.py` | router registration | WIRED | `app.include_router(projects.doc_types_router)` at line 67 |

### Plan 02 Links

| From | To | Via | Status | Evidence |
|------|----|-----|--------|---------|
| `Step4DocTypeChecklist.tsx` | `/api/doc-types/{project_type}` | `useDocTypeConfig(projectType)` | WIRED | Hook calls `api.get<DocTypeConfigEntry[]>('/doc-types/${projectType}')` |
| `ProjectWizard.tsx` | `Step4DocTypeChecklist.tsx` | import + render | WIRED | `import { Step4DocTypeChecklist }` line 13; rendered in step 4 motion block |
| `useFileUpload.ts` | `/api/projects/{id}/files?doc_type=` | `URLSearchParams` with `doc_type` | WIRED | `if (docType) params.set('doc_type', docType)` line 25 |

### Plan 03 Links

| From | To | Via | Status | Evidence |
|------|----|-----|--------|---------|
| `SetupStatusSection.tsx` | `/api/projects/{id}/setup-state` | `useSetupState` hook | WIRED | `import { useSetupState } from '../hooks/useSetupState'`; called at line 11 |
| `ProjectOverview.tsx` | `SetupStatusSection.tsx` | import + render | WIRED | `import { SetupStatusSection }` line 8; `<SetupStatusSection projectId={project.id} />` line 102 |
| `ProjectFilesTab.tsx` | `DocCoverageSection.tsx` | import + conditional render | WIRED | `import { DocCoverageSection }` line 18; `{projectType && <DocCoverageSection projectId={projectId} />}` line 105 |

---

## Requirements Coverage

| Requirement | Plans | Description | Status | Evidence |
|-------------|-------|-------------|--------|---------|
| PROJ-01 | 14-01, 14-02 | Engineer can create a new FDS project through a guided wizard with type classification (A/B/C/D) | EXTENDED | Phase 8 delivered base wizard; Phase 14 extends Step 4 with doc-type checklist specific to project type A/B/C/D via `useDocTypeConfig` |
| PROJ-02 | 14-01, 14-02 | Engineer can select project language (Dutch/English) during project creation | SATISFIED | Existing language selection unchanged; Phase 14 passes `language` through to `SetupStateResponse` and CLI handoff endpoint |
| PROJ-04 | 14-03 | Engineer can browse all projects in a dashboard with status and type indicators | EXTENDED | Phase 8 delivered project list; Phase 14 adds setup status section within project overview (dashboard detail view), showing doc-type coverage and CLI command |

Note: PROJ-01, PROJ-02, PROJ-04 are marked Complete from Phase 8 in REQUIREMENTS.md. Phase 14 extends these with setup-state capabilities. The requirements table maps them to Phase 8; Phase 14 is additive. No orphaned requirements found.

---

## Anti-Patterns Scan

Files modified across all 3 plans were scanned.

| File | Finding | Severity | Impact |
|------|---------|---------|--------|
| `backend/app/schemas/setup_state.py` | `status: str` on `DocTypeEntry` is untyped — accepts any string, not enforced as `"present" \| "missing" \| "skipped"` | INFO | No runtime impact; TypeScript side is typed; Pydantic does not enforce the constraint |
| `frontend/src/features/projects/components/ProjectOverview.tsx` | Quick Actions: "Referenties uploaden" button shows "Fase 9" label and is disabled — this was a pre-existing label not updated | INFO | Cosmetic only; Phase 14 made Referenties tab functional |

No blockers or stubs found. No `TODO`/`FIXME`/`placeholder` comments in modified files. No `return null` stubs in implemented logic paths.

---

## Human Verification Required

### 1. CLI-triggered auto-refresh of setup status

**Test:** Start backend and frontend. Open a project in the browser (Overview tab). Note the "Setup status" section shows `/doc:new-fds` as the next CLI command. Manually create a `.planning/` directory inside the project folder on disk (path shown in `project_dir` from setup-state API). Wait 5–10 seconds without refreshing.

**Expected:** The "Volgende stap in CLI" section updates to show the first phase CLI command (e.g., `/doc:discuss-phase 1`), without a page reload.

**Why human:** Requires live filesystem mutation and observation of timed polling behavior — cannot be verified statically or via grep.

---

## Summary

Phase 14 goal is achieved. All 8 backend artifacts and 11 frontend artifacts exist, are substantive, and are wired to their dependencies. The `useSetupState` polling at 5-second intervals is the mechanism for auto-refresh (criterion 5). The one human test validates that the polling actually picks up a real filesystem change, which is the core "CLI handoff" scenario.

- Backend: 9/9 unit tests passing, TypeScript: 0 errors, all 3 API endpoints reachable
- Wizard Step 4 replaced with project-type-specific doc-type checklist
- Setup status section in ProjectOverview polls and reflects coverage + CLI command
- Referenties tab has collapsible doc coverage + doc-type upload prompt with query invalidation
- CliCommandBlock extracted as shared component reused across FaseringTab, SetupStatusSection, and available for future consumers

---

_Verified: 2026-03-22T10:15:00Z_
_Verifier: Claude (gsd-verifier)_
