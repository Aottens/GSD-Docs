---
phase: 12-review-interface
plan: 01
subsystem: api
tags: [fastapi, pydantic, react, react-query, typescript, localstorage, context]

# Dependency graph
requires:
  - phase: 10-workflow-status-cleanup
    provides: phases.py API router pattern, _get_project_dir helper
  - phase: 11-document-preview-outline
    provides: useQuery hook pattern, api.get TypeScript client

provides:
  - GET /api/projects/{id}/phases/{n}/verification-detail endpoint
  - VerificationDetailResponse and TruthResult Pydantic schemas
  - VERIFICATION.md parser (_parse_verification_detail, _parse_verification_summary_table)
  - TypeScript interfaces: TruthResult, VerificationDetail, SectionReview, ReviewContextValue
  - useVerificationData React Query hook (30s polling, enabled flag)
  - ReviewProvider with localStorage persistence keyed by project+phase
  - useReviewContext returning null (not throws) outside provider
  - exportAsJson mapping Dutch status names to REVIEW.md template format

affects: [12-02, 12-03, review-interface]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verification parsing: _parse_verification_summary_table + _parse_verification_detail as pure functions for testability"
    - "Endpoint: additive pattern alongside existing context-files endpoint, no modification to existing code"
    - "ReviewContext: useReducer + useEffect for localStorage persistence + lazy initializer for hydration"
    - "useReviewContext returns null instead of throwing — consumers null-check, no try/catch wrapping hooks"

key-files:
  created:
    - backend/app/schemas/verification.py
    - frontend/src/features/documents/types/verification.ts
    - frontend/src/features/documents/hooks/useVerificationData.ts
    - frontend/src/features/documents/context/ReviewContext.tsx
  modified:
    - backend/app/api/phases.py

key-decisions:
  - "useReviewContext returns ReviewContextValue | null (not throws) — avoids React Rules of Hooks violation when called outside provider"
  - "ReviewContext lazy initializer reads localStorage on mount, useEffect persists on every change (storageKey as dependency)"
  - "exportAsJson maps Dutch: goedgekeurd->Approved, opmerking->Comment, afgewezen->Flag (REVIEW.md template format)"
  - "Standards violations extracted via regex matching PackML/ISA-88/IEC/EN/NEN references in gap description text"
  - "_parse_verification_summary_table handles multiple checkmark Unicode variants: U+2713, U+2714, U+2705"

patterns-established:
  - "verificationKeys query key factory follows documentKeys pattern from useDocumentOutline"
  - "ReviewContext: createContext<T | null>(null) pattern for optional provider wrapping"

requirements-completed: [QUAL-01, QUAL-02, QUAL-03, QUAL-06]

# Metrics
duration: 2min
completed: 2026-03-21
---

# Phase 12 Plan 01: Review Interface Data Layer Summary

**FastAPI verification-detail endpoint parsing VERIFICATION.md into structured truths, plus TypeScript types, React Query hook, and ReviewContext with localStorage persistence**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-21T13:47:02Z
- **Completed:** 2026-03-21T13:49:14Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Backend GET endpoint at `/api/projects/{id}/phases/{n}/verification-detail` parsing VERIFICATION.md into per-truth structured data (status, levels, gap descriptions, standards violations, evidence files)
- TypeScript type contracts mirroring backend schemas exactly, enabling type-safe frontend consumption
- `useVerificationData` React Query hook with 30s polling and `enabled` guard matching existing project hook pattern
- `ReviewProvider` with `useReducer` + `useEffect` localStorage persistence, lazy hydration on mount, and JSON export mapping Dutch status names to REVIEW.md template format

## Task Commits

Each task was committed atomically:

1. **Task 1: Backend verification-detail endpoint with Pydantic schemas** - `319ea39` (feat)
2. **Task 2: Frontend type contracts, verification hook, and ReviewContext** - `878a34b` (feat)

**Plan metadata:** (pending docs commit)

## Files Created/Modified

- `backend/app/schemas/verification.py` - TruthResult and VerificationDetailResponse Pydantic models
- `backend/app/api/phases.py` - Added _parse_verification_summary_table, _parse_verification_detail, and GET verification-detail endpoint
- `frontend/src/features/documents/types/verification.ts` - TypeScript interfaces: TruthResult, VerificationDetail, SectionReview, ReviewContextValue
- `frontend/src/features/documents/hooks/useVerificationData.ts` - React Query hook for fetching verification detail with 30s polling
- `frontend/src/features/documents/context/ReviewContext.tsx` - ReviewProvider with localStorage persistence and exportAsJson

## Decisions Made

- `useReviewContext` returns `ReviewContextValue | null` instead of throwing — consumers use null-check or optional chaining. Prevents React Rules of Hooks violation from calling hooks inside try/catch.
- `exportAsJson()` maps Dutch status names to REVIEW.md template English equivalents (goedgekeurd->Approved, opmerking->Comment, afgewezen->Flag)
- Standards violations extracted via regex matching `PackML|ISA-88|IEC|EN|NEN` references in gap description text; each match recorded with the full gap description as context
- `_parse_verification_summary_table` handles multiple Unicode checkmark variants (U+2713, U+2714, U+2705) to be robust across different VERIFICATION.md authoring tools

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Data layer complete: backend endpoint verified, TypeScript types defined, hook and context ready
- Phase 12 Plan 02 can import from `types/verification`, `hooks/useVerificationData`, and `context/ReviewContext` directly
- No blockers

---
*Phase: 12-review-interface*
*Completed: 2026-03-21*
