---
phase: 14-project-setup-cli-handoff
plan: 03
subsystem: ui
tags: [react, setup-state, doc-types, polling, collapsible, file-upload, query-invalidation]

requires:
  - phase: 14-project-setup-cli-handoff
    plan: 01
    provides: useSetupState hook, CliCommandBlock, SetupStateResponse types, DocTypeConfigEntry types
  - phase: 14-project-setup-cli-handoff
    plan: 02
    provides: useSetupState hook, CliCommandBlock component, setupState types

provides:
  - SetupStatusSection in ProjectOverview with 5s polling
  - DocCoverageSection collapsible in Referenties tab
  - Doc-type upload prompt with Select dropdown
  - Query invalidation on upload to refresh setup state

affects:
  - ProjectOverview (modified)
  - ProjectFilesTab (modified)
  - ReferenceManager (modified)
  - ProjectWorkspace (modified — passes project.type)

tech-stack:
  added: []
  patterns:
    - useSetupState hook reused across two components (SetupStatusSection + DocCoverageSection)
    - Doc-type upload interception via pendingUploadFiles state before actual upload
    - queryClient.invalidateQueries on onUploadComplete to sync setup coverage
    - projectType threaded from ProjectWorkspace through ReferenceManager to ProjectFilesTab

key-files:
  created:
    - frontend/src/features/projects/components/SetupStatusSection.tsx
    - frontend/src/features/files/components/DocCoverageSection.tsx
  modified:
    - frontend/src/features/projects/components/ProjectOverview.tsx
    - frontend/src/features/files/components/ProjectFilesTab.tsx
    - frontend/src/features/files/components/ReferenceManager.tsx
    - frontend/src/features/projects/ProjectWorkspace.tsx
    - frontend/src/features/files/hooks/useFileUpload.ts

key-decisions:
  - "DocTypeRow extracted as local render component inside DocCoverageSection — small enough to not warrant shared module"
  - "projectType threaded from ProjectWorkspace through ReferenceManager to ProjectFilesTab as optional prop — backward compat preserved"
  - "DocCoverageSection returns null when no doc_types — cleaner than empty state for Referenties tab"
  - "showDocTypePrompt state in ProjectFilesTab intercepts files before upload — keeps upload logic in useFileUpload unchanged"

patterns-established:
  - "Setup state polling: useSetupState(projectId) with 5s refetchInterval auto-refreshes coverage"
  - "Doc-type upload interception: store pending files in state, show prompt, then upload with type"
  - "Query invalidation: invalidateQueries(['projects', projectId, 'setup-state']) after upload"

requirements-completed: [PROJ-04]

duration: 8min
completed: "2026-03-22"
---

# Phase 14 Plan 03: SetupStatusSection, DocCoverageSection, and Doc-Type Upload Prompt Summary

**SetupStatusSection with 5s polling checklist in ProjectOverview, collapsible DocCoverageSection in Referenties tab, and doc-type upload prompt intercepting file selection before upload.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-22T09:32:00Z
- **Completed:** 2026-03-22T09:40:00Z
- **Tasks:** 2 of 3 (Task 3 is human verification checkpoint)
- **Files modified:** 7

## Accomplishments
- SetupStatusSection renders doc-type coverage checklist with green/amber/gray icons and CLI command block, auto-refreshes every 5 seconds
- DocCoverageSection in Referenties tab as collapsible (collapsed by default) showing same coverage data with note text when docs are present
- ProjectFilesTab intercepts file selection when doc types are configured, shows Select dropdown with "Selecteer type..." and "Zonder type" escape
- setup-state query invalidated after each upload so coverage section updates immediately

## Task Commits

Each task was committed atomically:

1. **Task 1: SetupStatusSection and ProjectOverview integration** - `b259be4` (feat)
2. **Task 2: DocCoverageSection and Referenties tab doc-type upload prompt** - `ed915e5` (feat)
3. **Task 3: Human verification checkpoint** - awaiting human verification

**Plan metadata:** pending (after checkpoint)

## Files Created/Modified
- `frontend/src/features/projects/components/SetupStatusSection.tsx` - New: doc-type coverage checklist with loading/error/empty/data states, CliCommandBlock integration
- `frontend/src/features/files/components/DocCoverageSection.tsx` - New: collapsible wrapper around same checklist, collapsed by default
- `frontend/src/features/projects/components/ProjectOverview.tsx` - Added SetupStatusSection in Card after metadata section
- `frontend/src/features/files/components/ProjectFilesTab.tsx` - Added DocCoverageSection, doc-type prompt state, handleFilesSelected interception, query invalidation
- `frontend/src/features/files/components/ReferenceManager.tsx` - Added projectType prop, passed to ProjectFilesTab
- `frontend/src/features/projects/ProjectWorkspace.tsx` - Pass project.type to ReferenceManager
- `frontend/src/features/files/hooks/useFileUpload.ts` - Already had docType support (updated by Plan 02 or linter)

## Decisions Made
- DocTypeRow extracted as local named function inside DocCoverageSection — avoids shared module for a 5-line render pattern
- projectType passed as optional prop through ReferenceManager to preserve backward compatibility
- DocCoverageSection returns null when no doc_types — no empty state shown in Referenties tab
- showDocTypePrompt state in ProjectFilesTab intercepts files before actual upload, keeping useFileUpload unchanged

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] ReferenceManager needed projectType prop to pass to ProjectFilesTab**
- **Found during:** Task 2 (DocCoverageSection integration)
- **Issue:** Plan said to update caller of ProjectFilesTab — but ProjectFilesTab is wrapped by ReferenceManager, which doesn't have projectType. ProjectWorkspace renders ReferenceManager.
- **Fix:** Added optional `projectType` prop to ReferenceManager and passed it to ProjectFilesTab. Updated ProjectWorkspace to pass `project.type`.
- **Files modified:** frontend/src/features/files/components/ReferenceManager.tsx, frontend/src/features/projects/ProjectWorkspace.tsx
- **Verification:** TypeScript passes with no errors
- **Committed in:** ed915e5

---

**Total deviations:** 1 auto-fixed (1 blocking — prop chain needed one extra hop)
**Impact on plan:** Minimal scope addition. ReferenceManager is a thin wrapper so the change is trivial. No behavior change.

## Issues Encountered
None — TypeScript compilation passed cleanly after all changes.

## Next Phase Readiness
- Task 3 (human-verify checkpoint) awaits visual verification
- Backend server + frontend dev server must be started for verification
- After verification approval, plan is complete and Phase 14 is done

---
*Phase: 14-project-setup-cli-handoff*
*Completed: 2026-03-22*
