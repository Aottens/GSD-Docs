---
phase: 12-review-interface
plan: 03
subsystem: ui
tags: [react, review-interface, verification, outline, context-api, localstorage]

# Dependency graph
requires:
  - phase: 12-review-interface-01
    provides: ReviewContext, useVerificationData hook, VerificationDetail types
  - phase: 12-review-interface-02
    provides: SectionBlock with review controls, ReviewSummary, VerificationCollapsible

provides:
  - OutlineNode badge evolution showing review status (checkmark/warning/x) from ReviewContext
  - ContentPanel threaded with phaseNumber, phaseHasVerification, verificationData props
  - DocumentsTab wrapped in ReviewProvider with useVerificationData for active phase
  - ProjectWorkspace determines activePhaseForReview from usePhaseTimeline and passes to DocumentsTab
  - Full end-to-end review workflow: verification detail, review buttons, summary, JSON export

affects:
  - phase 13 (export interface): review decisions persisted in ReviewContext + localStorage available for export
  - phase 14 (deployment): review interface is core feature for production-ready GUI

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ReviewProvider wraps entire DocumentsTab content tree so OutlineNode and ContentPanel both share ReviewContext"
    - "Null-safe context access: useReviewContext() returns null outside provider — no try/catch, no React hooks violation"
    - "Conditional provider pattern: DocumentsTab conditionally wraps content in ReviewProvider only when phaseNumber is available"
    - "Prop threading from ProjectWorkspace -> DocumentsTab -> ContentPanel -> SectionBlock for verification data"

key-files:
  created: []
  modified:
    - frontend/src/features/documents/components/OutlineNode.tsx
    - frontend/src/features/documents/components/ContentPanel.tsx
    - frontend/src/features/documents/components/DocumentsTab.tsx
    - frontend/src/features/projects/ProjectWorkspace.tsx

key-decisions:
  - "OutlineNode uses null-safe useReviewContext() call (returns null, not throws) — avoids React Rules of Hooks violation"
  - "Review status takes precedence over backend node.status in outline badge display per UI-SPEC Interaction Contract 5"
  - "ProjectWorkspace selects most recent phase with has_verification=true via usePhaseTimeline — automatic review activation without mode switch"
  - "Conditional ReviewProvider: content tree only wrapped when phaseNumber is defined, ensuring backward compatibility for phases without verification"
  - "overflow-auto (not overflow-hidden) required on ProjectWorkspace tab panels to restore scroll on Overview/Fases tabs"
  - "Empty outline sections greyed out at 40% opacity (opacity-40) to distinguish from sections with content"

patterns-established:
  - "Context null-safety pattern: hooks that return null outside provider are safe for unconditional calls in leaf components"
  - "Phase data threading: ProjectWorkspace is the integration point that bridges phase timeline data with document view"

requirements-completed: [QUAL-01, QUAL-03, QUAL-04, QUAL-05, QUAL-06]

# Metrics
duration: 225min
completed: 2026-03-21
---

# Phase 12 Plan 03: Review Interface Wiring Summary

**End-to-end review interface: OutlineNode badge evolution, ReviewProvider context tree, verification prop threading, and human-verified review workflow with JSON export**

## Performance

- **Duration:** ~225 min (including human verification and post-checkpoint fixes)
- **Started:** 2026-03-21T13:56:36Z
- **Completed:** 2026-03-21T18:35:31Z
- **Tasks:** 2 (1 auto + 1 human-verify checkpoint)
- **Files modified:** 4

## Accomplishments

- OutlineNode badges now evolve to show review status (checkmark/warning/x) when reviews are captured in ReviewContext, with Dutch tooltips (Goedgekeurd / Opmerking toegevoegd / Afgewezen), taking precedence over backend node status
- DocumentsTab wraps the full content tree in ReviewProvider (OutlinePanel + ContentPanel) so outline badges and section review controls share the same ReviewContext
- ContentPanel threads phaseNumber, phaseHasVerification, and verificationData props to every SectionBlock and renders ReviewSummary at the bottom when verification is active
- ProjectWorkspace determines the active phase for review from usePhaseTimeline (most recent phase with has_verification=true) and passes it to DocumentsTab — review interface activates automatically without any mode switch
- Full end-to-end review workflow human-verified: verification detail expandable, review buttons with feedback, localStorage persistence, post-review summary with counts, JSON export

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire OutlineNode badge evolution, ContentPanel prop threading, DocumentsTab ReviewProvider, and ProjectWorkspace phaseNumber prop** - `26d2ef0` (feat)
2. **Task 2: Verify review interface end-to-end** - approved by user (checkpoint)
3. **Post-checkpoint fix: Restore scroll on overview/fases tabs, grey out empty outline sections** - `7e52aa2` (fix)

## Files Created/Modified

- `frontend/src/features/documents/components/OutlineNode.tsx` — Added useReviewContext, getReviewIcon/getReviewTooltip, badge precedence logic; fixed empty section opacity
- `frontend/src/features/documents/components/ContentPanel.tsx` — Extended props with phaseNumber/phaseHasVerification/verificationData; added ReviewSummary footer
- `frontend/src/features/documents/components/DocumentsTab.tsx` — Added ReviewProvider wrapper, useVerificationData hook, activePhaseNumber prop
- `frontend/src/features/projects/ProjectWorkspace.tsx` — Added usePhaseTimeline integration, activePhaseForReview derivation, activePhaseNumber prop pass-through; fixed overflow-auto on tab panels

## Decisions Made

- **Null-safe context access**: `useReviewContext()` returns `ReviewContextValue | null` (does not throw). Called unconditionally at top of OutlineNode component — null-checked result. No try/catch needed, no Rules of Hooks violation.
- **Automatic review activation**: ProjectWorkspace selects most recent phase with `has_verification=true` from `usePhaseTimeline`. No manual mode toggle needed — review controls appear when any phase has a VERIFICATION.md.
- **Conditional provider wrap**: DocumentsTab only wraps content in `<ReviewProvider>` when phaseNumber is defined. This preserves backward compatibility for projects/phases without verification data.
- **overflow-auto fix**: Tab panels in ProjectWorkspace were using `overflow-hidden` which blocked scrolling on Overview and Fases tabs. Changed to `overflow-auto` — resolved scroll regression introduced by review wiring.
- **Empty section opacity**: Outline nodes for sections with no content are rendered at 40% opacity (`opacity-40`) to provide visual disambiguation without hiding the structure.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored scroll on Overview/Fases tabs after overflow-hidden regression**
- **Found during:** Task 2 (human verification checkpoint)
- **Issue:** ProjectWorkspace tab panels had `overflow-hidden` on the containing div, which blocked vertical scrolling on the Overview and Fases tabs after the review wiring changes
- **Fix:** Changed `overflow-hidden` to `overflow-auto` on the tab panel container in ProjectWorkspace.tsx
- **Files modified:** `frontend/src/features/projects/ProjectWorkspace.tsx`
- **Verification:** Scroll works on all tabs (Overview, Fases, Documents) after fix
- **Committed in:** `7e52aa2`

**2. [Rule 2 - Missing Critical] Greyed out empty outline sections**
- **Found during:** Task 2 (human verification — empty sections looked identical to sections with content)
- **Issue:** Outline nodes for empty sections were rendered at full opacity, making them visually indistinguishable from sections that have content — poor UX for navigation
- **Fix:** Added `opacity-40` class to OutlineNode rendering for sections with `status === 'empty'` or no content
- **Files modified:** `frontend/src/features/documents/components/OutlineNode.tsx`
- **Verification:** Empty sections visually distinct, user confirmed improvement
- **Committed in:** `7e52aa2`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing UX clarity)
**Impact on plan:** Both fixes are direct improvements to the review interface. No scope creep — both discovered during human verification of the same interface.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 12 (review-interface) is complete: all 3 plans executed and human-verified
- Review decisions are persisted in localStorage (per projectId + phaseNumber key), ready for Phase 13 export interface
- JSON export format already maps to REVIEW.md template format (goedgekeurd->Approved, opmerking->Comment, afgewezen->Flag)
- Phase 13 (export interface) can build on the export foundation in ReviewContext.exportAsJson()

---
*Phase: 12-review-interface*
*Completed: 2026-03-21*
