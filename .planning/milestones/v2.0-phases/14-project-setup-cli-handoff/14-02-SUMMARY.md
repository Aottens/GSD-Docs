---
phase: 14-project-setup-cli-handoff
plan: 02
subsystem: frontend
tags: [wizard, step4, doc-types, cli-command, typescript, react-query]
dependency_graph:
  requires:
    - 14-01 (backend doc-types API, setup-state endpoint, skipped-doc-types PATCH)
  provides:
    - Step4DocTypeChecklist component
    - CliCommandBlock shared component
    - useSetupState hook (5s polling)
    - useDocTypeConfig hook
    - TypeScript types for setup state API
    - useFileUpload doc_type support
  affects:
    - frontend/src/features/wizard/ProjectWizard.tsx
    - frontend/src/features/timeline/components/FaseringTab.tsx
tech_stack:
  added: []
  patterns:
    - React Query refetchInterval for polling
    - Programmatic file input via document.createElement for per-row upload
    - URLSearchParams for optional query param construction
    - DocTypeFileEntry typed entries coupling file with docType
key_files:
  created:
    - frontend/src/types/setupState.ts
    - frontend/src/features/timeline/components/CliCommandBlock.tsx
    - frontend/src/features/projects/hooks/useSetupState.ts
    - frontend/src/features/wizard/components/Step4DocTypeChecklist.tsx
  modified:
    - frontend/src/features/timeline/components/FaseringTab.tsx
    - frontend/src/features/files/hooks/useFileUpload.ts
    - frontend/src/features/wizard/ProjectWizard.tsx
decisions:
  - "uploadFile exposed from useFileUpload return value — needed for per-entry doc_type upload in wizard onSubmit"
  - "Programmatic input.createElement for per-row file picker — avoids ref array complexity with dynamic lists"
  - "DocTypeFileEntry exported from Step4DocTypeChecklist — consumed by ProjectWizard for typed state"
metrics:
  duration_minutes: 3
  tasks_completed: 2
  files_created: 4
  files_modified: 3
  completed_date: "2026-03-22"
---

# Phase 14 Plan 02: Frontend Wizard Step 4 Replacement and CliCommandBlock Extraction Summary

One-liner: Doc-type checklist replaces generic upload in wizard Step 4, CliCommandBlock extracted as shared component, useSetupState polls setup-state API at 5s, useFileUpload extended with docType param.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | TypeScript types, shared CliCommandBlock, useSetupState, useFileUpload doc_type | 1c0f926 | setupState.ts, CliCommandBlock.tsx, FaseringTab.tsx, useSetupState.ts, useFileUpload.ts |
| 2 | Wizard Step 4 DocTypeChecklist and ProjectWizard wiring | a6cc040 | Step4DocTypeChecklist.tsx, ProjectWizard.tsx |

## What Was Built

### TypeScript Types (`frontend/src/types/setupState.ts`)
Three interfaces matching backend Pydantic schemas: `DocTypeConfigEntry`, `DocTypeEntry` (with status union type `'present' | 'missing' | 'skipped'`), and `SetupStateResponse`.

### Shared CliCommandBlock (`frontend/src/features/timeline/components/CliCommandBlock.tsx`)
Extracted from FaseringTab.tsx local definition. Named export with `try/catch` around `navigator.clipboard.writeText()`, falling back to `toast.error('Kopieer niet beschikbaar')` per RESEARCH.md pitfall 5. FaseringTab now imports from shared location.

### useSetupState + useDocTypeConfig hooks (`frontend/src/features/projects/hooks/useSetupState.ts`)
- `useSetupState(projectId)`: React Query at 5000ms refetchInterval, 3000ms staleTime, enabled guard
- `useDocTypeConfig(projectType)`: Fetches `/api/doc-types/{projectType}` with `staleTime: Infinity` (config is stable)

### useFileUpload Extension
`uploadFile(file, folderId?, docType?)` and `uploadFiles(files, folderId?, docType?)` both accept optional `docType`. URL built via `URLSearchParams` — appends `doc_type` only when defined. Backward compatible. `uploadFile` now exposed in hook return value.

### Step4DocTypeChecklist (`frontend/src/features/wizard/components/Step4DocTypeChecklist.tsx`)
Fetches doc-type config via `useDocTypeConfig(projectType)`. Renders a Card with row per doc type:
- Status icon: `CheckCircle2` (green, files present) / `Clock` (amber, skipped) / `Circle` (muted, empty)
- Label with strikethrough when skipped, row at `opacity-50`
- File count: "1 bestand" / "{N} bestanden" / "—"
- Upload button: "Uploaden" / "Toevoegen" — opens programmatic file input per doc type
- "Niet beschikbaar" Checkbox with label
- Loading state: skeleton rows; empty state: fallback message

### ProjectWizard.tsx Wiring
- `selectedFiles` changed from `File[]` to `DocTypeFileEntry[]`
- Added `skippedDocTypes: string[]` state
- `handleFilesChanged` and `handleSkippedChanged` callbacks replace old `handleFilesSelected`
- `onSubmit`: PATCH skipped-doc-types before upload; iterate `selectedFiles` calling `uploadFile(entry.file, undefined, entry.docType)` per entry
- Step 4 renders `Step4DocTypeChecklist` instead of `Step4ReferenceUpload`

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Out-of-Scope Observations

Pre-existing modifications to `frontend/src/features/files/components/ProjectFilesTab.tsx` and an untracked `DocCoverageSection.tsx` were present in the working tree before this plan ran (from an earlier Plan 03 execution attempt). These were left unstaged as they are Plan 03 scope.

## Self-Check

### Files Exist
- [x] `frontend/src/types/setupState.ts` — exists
- [x] `frontend/src/features/timeline/components/CliCommandBlock.tsx` — exists
- [x] `frontend/src/features/projects/hooks/useSetupState.ts` — exists
- [x] `frontend/src/features/wizard/components/Step4DocTypeChecklist.tsx` — exists

### Commits Exist
- [x] 1c0f926 — Task 1
- [x] a6cc040 — Task 2

### TypeScript
- [x] `npx tsc --noEmit` exits 0

## Self-Check: PASSED
