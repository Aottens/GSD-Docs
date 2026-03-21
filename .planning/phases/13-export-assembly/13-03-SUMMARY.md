---
phase: 13-export-assembly
plan: 03
subsystem: ui
tags: [react, typescript, shadcn, sse, export, tanstack-query]

requires:
  - phase: 13-export-assembly plan 01
    provides: TypeScript types (export.ts), backend API endpoints for export/stream/versions/readiness/pandoc-status

provides:
  - Export tab with three-stage FDS pipeline (Samenstellen, Exporteren, Downloaden)
  - SSE consumer hook (useAssemblyStream) for real-time named step progress
  - React Query hooks (useExportVersions, useAssemblyReadiness, usePandocStatus)
  - ExportOptions component with Concept/Definitief mode and NL/EN language selectors
  - PipelineStage component with Collapsible inline error detail
  - ExportProgressBar with named step labels and Progress component
  - VersionHistory table with download buttons, empty state, skeleton loading
  - AssemblyPipeline with Pandoc/readiness alerts, cancel button, toast on complete
  - Export and SDS navigation items wired into ProjectNavigation sidebar
  - Export rendering case in ProjectWorkspace activeSection switch

affects: [13-04-sds-tab]

tech-stack:
  added: [shadcn Table component]
  patterns:
    - SSE consumer with useRef<EventSource> for cleanup, useState for stage statuses
    - React Query manual invalidation on export complete via queryClient.invalidateQueries
    - Sonner toast.success on export complete
    - ExportTab owns mode/language state; passes down to AssemblyPipeline and ExportOptions

key-files:
  created:
    - frontend/src/components/ui/table.tsx
    - frontend/src/features/export/hooks/useAssemblyStream.ts
    - frontend/src/features/export/hooks/useExportApi.ts
    - frontend/src/features/export/components/ExportOptions.tsx
    - frontend/src/features/export/components/PipelineStage.tsx
    - frontend/src/features/export/components/ExportProgressBar.tsx
    - frontend/src/features/export/components/VersionHistory.tsx
    - frontend/src/features/export/components/AssemblyPipeline.tsx
    - frontend/src/features/export/components/ExportTab.tsx
  modified:
    - frontend/src/features/projects/components/ProjectNavigation.tsx
    - frontend/src/features/projects/ProjectWorkspace.tsx

key-decisions:
  - "ExportTab owns mode and exportLanguage state — passed down as props to avoid prop drilling via context for single-tab use"
  - "useAssemblyStream uses INITIAL_STAGES constant for clean reset on cancel or new run"
  - "AssemblyPipeline stage cards use stage step indices 0-3 mapped to UI labels Samenstellen/Exporteren/Downloaden (3 cards show first 3 of 4 SSE steps)"
  - "Export/SDS nav items added before Settings, both enabled in isEnabled check"
  - "Overflow class ternary extended: documents=overflow-hidden, export/sds=overflow-auto, others=overflow-auto p-6"

patterns-established:
  - "SSE hook pattern: eventSourceRef.current?.close() in cancel(), onerror sets isRunning=false"
  - "React Query invalidation: queryClient.invalidateQueries in useEffect watching completedFilename"
  - "Dutch date format: dd-MM-yyyy HH:mm formatted inline without date-fns"

requirements-completed: [OUTP-02, OUTP-03, OUTP-04, OUTP-07]

duration: 3min
completed: 2026-03-21
---

# Phase 13 Plan 03: Export Assembly Summary

**React Export tab with three-stage FDS pipeline, SSE real-time progress via EventSource, version history table, and workspace navigation integration using shadcn Table + Sonner toasts**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T19:05:35Z
- **Completed:** 2026-03-21T19:08:34Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments

- Created full export feature directory with 2 hooks and 5 components, all TypeScript-clean
- Wired Export tab into workspace navigation (sidebar + content area) with correct overflow handling
- shadcn Table installed and used for version history with empty state and skeleton loading

## Task Commits

Each task was committed atomically:

1. **Task 1: Install Table component + Export hooks + Export components** - `c03d349` (feat)
2. **Task 2: Wire Export tab into workspace navigation** - `58b24b6` (feat)

**Plan metadata:** (pending — final docs commit)

## Files Created/Modified

- `frontend/src/components/ui/table.tsx` - shadcn Table component installed via CLI
- `frontend/src/features/export/hooks/useAssemblyStream.ts` - EventSource SSE hook with start/cancel/stages
- `frontend/src/features/export/hooks/useExportApi.ts` - React Query hooks for versions, readiness, pandoc status
- `frontend/src/features/export/components/ExportOptions.tsx` - Mode and language Select components
- `frontend/src/features/export/components/PipelineStage.tsx` - Stage card with Collapsible error detail
- `frontend/src/features/export/components/ExportProgressBar.tsx` - Progress bar with named step labels
- `frontend/src/features/export/components/VersionHistory.tsx` - Version history table with download buttons
- `frontend/src/features/export/components/AssemblyPipeline.tsx` - Pipeline orchestrator with alerts and cancel
- `frontend/src/features/export/components/ExportTab.tsx` - Top-level tab composing all sub-components
- `frontend/src/features/projects/components/ProjectNavigation.tsx` - Added Export and SDS nav items
- `frontend/src/features/projects/ProjectWorkspace.tsx` - Added ExportTab import and export rendering case

## Decisions Made

- ExportTab owns mode/exportLanguage state, passes down as props — pipeline is single-tab, no cross-tab sharing needed
- AssemblyPipeline maps 3 stage cards to SSE step indices (first 3 of 4 steps); Downloaden uses completedFilename for download URL
- isFinalBlocked computed in AssemblyPipeline from readiness.unreviewed_phases — disables Samenstellen button
- Dutch date formatting done inline (dd-MM-yyyy HH:mm) without adding date-fns dependency

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

ProjectWorkspace.tsx had already been partially modified by plan 13-02 (SdsTab import was present). The ExportTab import and export case were added on top of the existing 13-02 changes cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Export tab is fully functional, ready for backend integration testing
- SDS tab placeholder exists via SdsTab component from plan 13-02
- Plan 13-04 (SDS tab implementation) can now build on top of the navigation and workspace wiring established here

---
*Phase: 13-export-assembly*
*Completed: 2026-03-21*
