---
phase: 12-review-interface
plan: 02
subsystem: ui
tags: [react, typescript, shadcn, collapsible, context, lucide-react, review-interface]

# Dependency graph
requires:
  - phase: 12-review-interface
    plan: 01
    provides: VerificationDetail types, useVerificationData hook, ReviewContext with useReviewContext

provides:
  - StandardsBadge component — reference pill with Tooltip showing full gap text
  - VerificationDetailPanel component — collapsible truth-by-truth detail with cycle badge and GEBLOKKEERD alert
  - ReviewActionBar component — 3 review buttons (Goedkeuren/Opmerking/Afwijzen) with feedback textarea
  - ReviewSummary component — counts + CLI hint + JSON clipboard export
  - SectionBlock extended with phaseNumber, phaseHasVerification, verificationData props
  - Collapsible shadcn component installed

affects: [12-03, review-interface]

# Tech tracking
tech-stack:
  added:
    - "@radix-ui/react-collapsible (via shadcn add collapsible)"
  patterns:
    - "Null-safe context pattern: useReviewContext() returns null outside ReviewProvider — all consumers null-check with `if (!ctx) return null`"
    - "Sibling rendering: VerificationDetailPanel and ReviewActionBar rendered as siblings inside a wrapper div, never nested — avoids Radix focus conflicts"
    - "Leaf-only rendering: review controls only mount when node.children.length === 0 and phaseHasVerification === true"
    - "Prop threading: SectionBlock passes phaseNumber/phaseHasVerification/verificationData to all child SectionBlocks recursively"

key-files:
  created:
    - frontend/src/components/ui/collapsible.tsx
    - frontend/src/features/documents/components/StandardsBadge.tsx
    - frontend/src/features/documents/components/VerificationDetailPanel.tsx
    - frontend/src/features/documents/components/ReviewActionBar.tsx
    - frontend/src/features/documents/components/ReviewSummary.tsx
  modified:
    - frontend/src/features/documents/components/SectionBlock.tsx

key-decisions:
  - "Collapsible collapsed by default (open=false) — engineer consciously expands to see truth detail, keeping reading flow uninterrupted"
  - "Phase-level truths shown on all leaf sections by design — VERIFICATION.md verifies phase-level truths, not per-section; evidence_files filtering is future iteration"
  - "ReviewActionBar uses useState initialized from ctx.reviews[sectionId] — survives re-renders without losing local draft state"

patterns-established:
  - "Null-safe context: createContext<T | null>(null) pattern, consumers use `if (!ctx) return null` — no try/catch around hooks"
  - "Review controls siblings not nested: VerificationDetailPanel + ReviewActionBar as sibling elements inside a wrapper div"

requirements-completed: [QUAL-02, QUAL-04, QUAL-05, QUAL-07, QUAL-08]

# Metrics
duration: 8min
completed: 2026-03-21
---

# Phase 12 Plan 02: Review Interface UI Components Summary

**Collapsible truth-by-truth VerificationDetailPanel, 3-button ReviewActionBar with feedback textarea, StandardsBadge pills with tooltips, ReviewSummary with JSON export, and SectionBlock extended to render review controls on leaf nodes**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-21T13:53:11Z
- **Completed:** 2026-03-21T14:01:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Four new UI components built: StandardsBadge, VerificationDetailPanel, ReviewActionBar, ReviewSummary — all in Dutch per copywriting contract
- `shadcn/ui Collapsible` installed and used in VerificationDetailPanel for expand/collapse truth list
- SectionBlock extended with three new optional props; review controls render conditionally on leaf nodes only when `phaseHasVerification === true`
- All components null-safe against `useReviewContext()` returning null outside ReviewProvider

## Task Commits

Each task was committed atomically:

1. **Task 1: Install Collapsible + create VerificationDetailPanel, StandardsBadge, ReviewActionBar, ReviewSummary** - `304cb8b` (feat)
2. **Task 2: Extend SectionBlock with verification and review controls** - `49c67b8` (feat)

**Plan metadata:** (pending docs commit)

## Files Created/Modified

- `frontend/src/components/ui/collapsible.tsx` - Radix Collapsible shadcn wrapper (installed via npx shadcn add)
- `frontend/src/features/documents/components/StandardsBadge.tsx` - Badge pill with TooltipProvider showing full gap text on hover
- `frontend/src/features/documents/components/VerificationDetailPanel.tsx` - Collapsible panel with cycle badge, GEBLOKKEERD alert, per-truth pass/gap list with Normen section
- `frontend/src/features/documents/components/ReviewActionBar.tsx` - Goedkeuren/Opmerking/Afwijzen buttons with conditional feedback textarea and Opslaan save
- `frontend/src/features/documents/components/ReviewSummary.tsx` - Count summary, CLI hint, and JSON clipboard export button
- `frontend/src/features/documents/components/SectionBlock.tsx` - Added phaseNumber, phaseHasVerification, verificationData props; conditional review controls rendering; prop threading to children

## Decisions Made

- Collapsible starts collapsed by default — preserves reading flow, engineer expands on demand
- Phase-level truths shown on all leaf sections (known trade-off documented in plan): VERIFICATION.md verifies phase-level truths, not per-section sections; evidence_files filtering deferred to future iteration
- `ReviewActionBar` initializes local state from `ctx.reviews[sectionId]` — persists existing review status across re-renders without requiring parent prop drilling

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All review UI components ready: VerificationDetailPanel, ReviewActionBar, StandardsBadge, ReviewSummary
- SectionBlock is review-ready — just pass `phaseHasVerification={true}`, `phaseNumber`, and `verificationData` from a parent (DocumentsTab or ContentPanel)
- Phase 12 Plan 03 can wire these components into the DocumentsTab layout, adding ReviewProvider wrapping and passing verification props down

---
*Phase: 12-review-interface*
*Completed: 2026-03-21*
