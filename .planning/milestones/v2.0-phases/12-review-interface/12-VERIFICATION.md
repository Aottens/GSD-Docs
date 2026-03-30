---
phase: 12-review-interface
verified: 2026-03-21T19:00:00Z
status: gaps_found
score: 9/11 must-haves verified
gaps:
  - truth: "Engineer can click Goedkeuren/Opmerking/Afwijzen buttons on each leaf section"
    status: failed
    reason: "ReviewActionBar calls useState after a conditional early return (if (!ctx) return null on line 15, useState calls on lines 20-24). This violates React Rules of Hooks — hooks must not be called conditionally or after an early return. ESLint confirms 3 errors in this file."
    artifacts:
      - path: "frontend/src/features/documents/components/ReviewActionBar.tsx"
        issue: "useState called after 'if (!ctx) return null' — React Rules of Hooks violation (3 ESLint errors: lines 20, 23, 24)"
    missing:
      - "Move all useState calls before the 'if (!ctx) return null' guard. Use ctx as nullable reference only in render/handlers, not as a hook-call gate."
  - truth: "Post-review summary shows counts and CLI command with JSON export"
    status: failed
    reason: "ReviewSummary calls useState after a conditional early return (if (!ctx) return null on line 12, useState call on line 15). This violates React Rules of Hooks — 1 ESLint error confirmed."
    artifacts:
      - path: "frontend/src/features/documents/components/ReviewSummary.tsx"
        issue: "useState called after 'if (!ctx) return null' — React Rules of Hooks violation (1 ESLint error: line 15)"
    missing:
      - "Move useState(false) call to before the 'if (!ctx) return null' guard. The early return for empty reviews (line 18) is fine because it comes after all hook calls."
human_verification:
  - test: "Open a project with a phase that has VERIFICATION.md. Navigate to Documents tab."
    expected: "Review controls appear automatically on leaf sections. VerificationDetailPanel is collapsible, shows cycle badge and truth list. Clicking Goedkeuren/Opmerking/Afwijzen captures review, outline badge updates."
    why_human: "End-to-end flow requires live backend + localStorage. The hooks violation may or may not cause visible failures in the current React version, but it creates unpredictable rendering behavior."
  - test: "After reviewing sections, refresh the page."
    expected: "Review decisions persist — outline badges still reflect prior review status."
    why_human: "localStorage persistence requires running browser environment."
  - test: "Click 'Exporteer als JSON' in ReviewSummary."
    expected: "Valid JSON copied to clipboard with section statuses mapped to Approved/Comment/Flag."
    why_human: "Clipboard API and JSON format correctness need live browser."
---

# Phase 12: Review Interface Verification Report

**Phase Goal:** Engineers can review sections with approve/reject/request-changes workflow, view verification results and standards compliance from CLI output.
**Verified:** 2026-03-21T19:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Backend returns structured verification data parsed from VERIFICATION.md | VERIFIED | `_parse_verification_detail` and `_parse_verification_summary_table` in `backend/app/api/phases.py` (lines 204–411); endpoint at `/{phase_number}/verification-detail`; Python imports resolve cleanly |
| 2 | Frontend can fetch per-phase verification detail via React Query hook | VERIFIED | `useVerificationData` in `frontend/src/features/documents/hooks/useVerificationData.ts` — fetches `/projects/${projectId}/phases/${phaseNumber}/verification-detail`, 30s polling, enabled guard, exports `verificationKeys` |
| 3 | Review session state persists across page reload via localStorage | VERIFIED | `ReviewContext.tsx` uses lazy initializer on `useReducer` to hydrate from localStorage on mount, `useEffect` persists on every `reviews` state change, keyed as `review-session-{projectId}-{phaseNumber}` |
| 4 | Export function produces JSON mapping to REVIEW.md template format | VERIFIED | `exportAsJson()` in `ReviewContext.tsx` maps `goedgekeurd->Approved`, `opmerking->Comment`, `afgewezen->Flag` — matches REVIEW.md template contract |
| 5 | Engineer can see verification status (pass/gap) per truth in an expandable panel | VERIFIED | `VerificationDetailPanel.tsx` — Collapsible panel with cycle badge, per-truth pass/gap icons (CheckCircle2/AlertTriangle), gap badge with `failed_level`, gap description via ReactMarkdown, "Normen" sub-section with StandardsBadge |
| 6 | GEBLOKKEERD alert appears when cycle 2 has remaining gaps | VERIFIED | `VerificationDetailPanel.tsx` lines 55–71 — `Alert variant="destructive"` with AlertTitle "GEBLOKKEERD" and CLI hint renders when `isBlocked === true` |
| 7 | Standards violations display as badge pills with tooltip | VERIFIED | `StandardsBadge.tsx` — `Badge variant="outline"` wrapped in `TooltipProvider > Tooltip` showing full gap text on hover |
| 8 | Engineer can click Goedkeuren/Opmerking/Afwijzen buttons on each leaf section | FAILED | `ReviewActionBar.tsx` calls `useState` (lines 20, 23, 24) after `if (!ctx) return null` (line 15) — React Rules of Hooks violation confirmed by ESLint (3 errors). Buttons and textarea are structurally complete, but the conditional hook calls can cause React to corrupt hook call order across renders. |
| 9 | Post-review summary shows counts and CLI command with JSON export | FAILED | `ReviewSummary.tsx` calls `useState(false)` (line 15) after `if (!ctx) return null` (line 12) — React Rules of Hooks violation confirmed by ESLint (1 error). Summary content is otherwise complete. |
| 10 | Outline node badges evolve to show review status from ReviewContext | VERIFIED | `OutlineNode.tsx` — `useReviewContext()` called unconditionally at top level (line 63), `reviewStatus` from `ctx?.reviews[node.id]?.status`, conditional rendering with Tooltip correctly after hook calls |
| 11 | Full review workflow works end-to-end: ProjectWorkspace -> DocumentsTab -> ContentPanel -> SectionBlock | VERIFIED | `ProjectWorkspace.tsx` uses `usePhaseTimeline`, derives `activePhaseForReview`, passes `activePhaseNumber` to `DocumentsTab`; `DocumentsTab` fetches verification data and conditionally wraps in `ReviewProvider`; `ContentPanel` threads props to `SectionBlock`; `SectionBlock` conditionally renders `VerificationDetailPanel` + `ReviewActionBar` on leaf nodes |

**Score:** 9/11 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `backend/app/schemas/verification.py` | Pydantic schemas for verification detail response | VERIFIED | `TruthResult` and `VerificationDetailResponse` present; `has_verification`, `standards_violations: list[dict]`, all required fields present |
| `backend/app/api/phases.py` | verification-detail endpoint + VERIFICATION.md parser | VERIFIED | `@router.get("/{phase_number}/verification-detail")`, `_parse_verification_detail`, `_parse_verification_summary_table`, `from app.schemas.verification import VerificationDetailResponse` all present |
| `frontend/src/features/documents/types/verification.ts` | TypeScript interfaces for verification + review | VERIFIED | Exports `TruthResult`, `VerificationDetail`, `SectionReview`, `ReviewContextValue` — exact mirror of backend Pydantic schemas |
| `frontend/src/features/documents/hooks/useVerificationData.ts` | React Query hook for verification data | VERIFIED | `useVerificationData(projectId, phaseNumber, enabled)` with `refetchInterval: 30000`, `staleTime: 25000`, query key factory exported |
| `frontend/src/features/documents/context/ReviewContext.tsx` | ReviewContext with localStorage persistence | VERIFIED | `ReviewProvider`, `useReviewContext` returning `ReviewContextValue | null` (no throw), `localStorage.setItem`, `exportAsJson` — all present and correct |
| `frontend/src/components/ui/collapsible.tsx` | Radix Collapsible shadcn component | VERIFIED | File exists |
| `frontend/src/features/documents/components/StandardsBadge.tsx` | Standard reference pill with tooltip | VERIFIED | `TooltipProvider`, `Badge variant="outline"`, exports `StandardsBadge` |
| `frontend/src/features/documents/components/VerificationDetailPanel.tsx` | Collapsible truth-by-truth verification detail | VERIFIED | `Collapsible`, "Verificatieresultaten", "GEBLOKKEERD", "Normen", "Cyclus" all present |
| `frontend/src/features/documents/components/ReviewActionBar.tsx` | Review buttons with feedback textarea | STUB/BROKEN | Structure complete (Goedkeuren, Opmerking, Afwijzen, textarea, Opslaan) but `useState` called after conditional return — React Rules of Hooks violation |
| `frontend/src/features/documents/components/ReviewSummary.tsx` | Post-review summary with counts and export | STUB/BROKEN | Content complete (counts, `/doc:review-phase`, `navigator.clipboard.writeText`, "Exporteer als JSON") but `useState` after conditional return — React Rules of Hooks violation |
| `frontend/src/features/documents/components/SectionBlock.tsx` | Extended with review props and conditional rendering | VERIFIED | `phaseNumber?: number`, `phaseHasVerification?: boolean`, `verificationData?: VerificationDetail`, imports `VerificationDetailPanel` and `ReviewActionBar`, conditional rendering on leaf nodes, prop threading to children |
| `frontend/src/features/documents/components/OutlineNode.tsx` | Badge evolution with review status | VERIFIED | `useReviewContext` called unconditionally, `getReviewIcon`/`getReviewTooltip`, `reviewStatus ? <Tooltip>` precedence logic |
| `frontend/src/features/documents/components/ContentPanel.tsx` | Verification prop threading + ReviewSummary footer | VERIFIED | Props `phaseNumber`, `phaseHasVerification`, `verificationData` threaded to `SectionBlock`; `<ReviewSummary phaseNumber={phaseNumber} />` renders conditionally |
| `frontend/src/features/documents/components/DocumentsTab.tsx` | ReviewProvider wrapper + useVerificationData + phaseNumber | VERIFIED | `<ReviewProvider>` wraps content conditionally, `useVerificationData` called, `activePhaseNumber` prop accepted |
| `frontend/src/features/projects/ProjectWorkspace.tsx` | Passes activePhaseNumber to DocumentsTab | VERIFIED | `usePhaseTimeline`, `activePhaseForReview` derived, `activePhaseNumber={activePhaseForReview}` passed to `DocumentsTab` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `backend/app/api/phases.py` | VERIFICATION.md filesystem | `_parse_verification_detail` reads file | WIRED | Function defined at line 288; endpoint reads file at line ~436, calls `_parse_verification_detail(content)` |
| `useVerificationData.ts` | `/api/projects/{id}/phases/{n}/verification-detail` | React Query fetch | WIRED | `api.get<VerificationDetail>(`/projects/${projectId}/phases/${phaseNumber}/verification-detail`)` — query key includes "verification-detail" |
| `ReviewContext.tsx` | localStorage | `useEffect` sync on reviews state | WIRED | `useEffect(() => { localStorage.setItem(storageKey, JSON.stringify(reviews)) }, [reviews, storageKey])` |
| `VerificationDetailPanel.tsx` | `useVerificationData` hook | receives `VerificationDetail` as props | WIRED | Props `truths: TruthResult[]`, `currentCycle`, `maxCycles`, `isBlocked` passed from `SectionBlock` which receives `verificationData` from `ContentPanel` |
| `ReviewActionBar.tsx` | ReviewContext | `useReviewContext()` with null-check | WIRED (structure) | `useReviewContext()` called, `if (!ctx) return null` guard present, `setReview` used — BUT hooks violation means conditional rendering may be unstable |
| `SectionBlock.tsx` | `VerificationDetailPanel` + `ReviewActionBar` | conditional rendering when `phaseHasVerification=true` | WIRED | `{phaseHasVerification && verificationData?.has_verification && node.children.length === 0 && (...)}` guards both components |
| `ProjectWorkspace.tsx` | `DocumentsTab.tsx` | passes `activePhaseNumber` prop | WIRED | `activePhaseNumber={activePhaseForReview}` on line 104 |
| `DocumentsTab.tsx` | `ReviewProvider` | wraps content tree | WIRED | `if (phaseNumber) { return <ReviewProvider ...>{content}</ReviewProvider> }` |
| `DocumentsTab.tsx` | `useVerificationData` | fetches verification detail, passes to ContentPanel | WIRED | `useVerificationData(projectId, phaseNumber ?? 0, !!phaseNumber)` called, result passed to `ContentPanel` as `verificationData={verificationData ?? null}` |
| `OutlineNode.tsx` | ReviewContext | `useReviewContext()` null-safe (no try/catch) | WIRED | `const ctx = useReviewContext()` at line 63, unconditional call (complies with Rules of Hooks), `ctx?.reviews[node.id]?.status` used |
| `ContentPanel.tsx` | `SectionBlock` | passes `phaseNumber`, `phaseHasVerification`, `verificationData` | WIRED | All three props passed in `sections.map` at lines 34-44 |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| QUAL-01 | 12-01, 12-03 | Engineer can view verification results from CLI output in the GUI | SATISFIED | Backend parses VERIFICATION.md into structured data; `VerificationDetailPanel` displays truth-by-truth results in DocumentsTab |
| QUAL-02 | 12-01, 12-02 | Engineer can view gaps, severity, and recommendations from verification | SATISFIED | `VerificationDetailPanel` shows gap status, `failed_level` badge, `gap_description` via ReactMarkdown, standards violations |
| QUAL-03 | 12-01, 12-03 | Engineer can see gap closure cycle status (verify -> re-plan -> re-write) | SATISFIED | `VerificationDetailPanel` shows "Cyclus N/M" badge and GEBLOKKEERD alert with CLI hint `/doc:plan-phase {N} --gaps` |
| QUAL-04 | 12-02, 12-03 | Engineer can approve or reject verification results before proceeding | PARTIAL | `ReviewActionBar` and `ReviewSummary` are structurally complete but have React Rules of Hooks violations — may work in current React version but is technically broken |
| QUAL-05 | 12-02, 12-03 | Engineer can conduct review-phase with approve/reject/request-changes per section | PARTIAL | Same as QUAL-04 — `ReviewActionBar` has hooks violation affecting Goedkeuren/Opmerking/Afwijzen buttons |
| QUAL-06 | 12-01, 12-03 | Engineer can provide text feedback during review that feeds back into workflow | PARTIAL | Textarea and `setReview` wiring exists; JSON export maps to REVIEW.md format; hooks violation in `ReviewActionBar` affects textarea rendering stability |
| QUAL-07 | 12-02 | Engineer can view PackML/ISA-88 standards compliance results in the GUI | SATISFIED | `StandardsBadge` renders PackML/ISA-88 references; backend extracts violations via regex; `VerificationDetailPanel` renders "Normen" section |
| QUAL-08 | 12-02 | Engineer can view standards violations with references to standard sections | SATISFIED | `StandardsBadge` shows `reference` as pill, tooltip shows full `gap_description` text with standard context |

**Orphaned requirements from REQUIREMENTS.md traceability table:** None. All 8 QUAL requirements (QUAL-01 through QUAL-08) are claimed by plan frontmatter and accounted for above.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ReviewActionBar.tsx` | 15, 20, 23, 24 | `if (!ctx) return null` before 3 `useState` calls | BLOCKER | React Rules of Hooks violation — hooks called after conditional return. ESLint confirms 3 errors. React may silently corrupt hook call order across conditional renders, causing state inconsistency in the review buttons and saved indicator. |
| `ReviewSummary.tsx` | 12, 15 | `if (!ctx) return null` before `useState(false)` | BLOCKER | React Rules of Hooks violation — hook called after conditional return. ESLint confirms 1 error. The "Gekopieerd!" toggle state for the JSON export button may behave unpredictably. |

Note: `ReviewSummary.tsx` line 18 (`if (allReviews.length === 0) return null`) comes AFTER all hook calls and is therefore valid.

### Human Verification Required

#### 1. End-to-End Review Workflow

**Test:** Navigate to a project with a phase that has VERIFICATION.md in its planning directory. Go to Documents tab. Expand a section with content.
**Expected:** "Verificatieresultaten" collapsible appears below section content. Clicking it shows cycle badge ("Cyclus N/2") and truth list with pass/gap icons. GEBLOKKEERD alert appears if `is_blocked=true`.
**Why human:** Requires live backend with real VERIFICATION.md file and running frontend.

#### 2. Review Buttons Functionality (Post-Hooks-Fix)

**Test:** After fixing the hooks violations, click "Goedkeuren" on a leaf section. Then try "Opmerking toevoegen" with feedback text and "Opslaan". Then "Afwijzen" with text.
**Expected:** Button highlights in correct color, outline badge updates to matching icon (checkmark/message/x), "Opgeslagen" confirmation appears briefly.
**Why human:** Interactive state transitions, localStorage writes, and React re-render correctness need live browser — especially important to retest after fixing the hooks violations.

#### 3. localStorage Persistence

**Test:** Review several sections. Hard-refresh the page.
**Expected:** All review decisions persist — outline badges remain, summary counts remain correct.
**Why human:** Requires browser localStorage access.

#### 4. JSON Export Format

**Test:** After reviewing sections, click "Exporteer als JSON" in the summary bar.
**Expected:** Clipboard contains valid JSON with sections array where statuses are "Approved", "Comment", or "Flag" (not the Dutch originals).
**Why human:** Clipboard API requires browser. Format correctness for REVIEW.md integration should be spot-checked.

### Gaps Summary

Two `gaps_found` items share the same root cause: the React Rules of Hooks pattern for null-guarding context was applied incorrectly in both `ReviewActionBar` and `ReviewSummary`.

The plan explicitly documented that `useReviewContext` returns `null` (not throws) so consumers can null-check safely. The intent was correct — `useReviewContext()` itself is called unconditionally at the top of each function (compliant). However, both components then call `useState` AFTER the `if (!ctx) return null` guard, which is the violation. The fix is mechanical: move all `useState` calls above the null guard in both files.

**`ReviewActionBar.tsx` fix pattern:**
```tsx
export function ReviewActionBar({ sectionId }: ReviewActionBarProps) {
  const ctx = useReviewContext()
  // Move useState calls ABOVE the early return
  const existing = ctx?.reviews[sectionId]
  const [activeAction, setActiveAction] = useState<SectionReview['status'] | null>(
    existing?.status ?? null
  )
  const [feedback, setFeedback] = useState<string>(existing?.feedback ?? '')
  const [saved, setSaved] = useState(false)

  if (!ctx) return null   // Guard AFTER all hooks
  // ... rest of component
}
```

**`ReviewSummary.tsx` fix pattern:**
```tsx
export function ReviewSummary({ phaseNumber }: ReviewSummaryProps) {
  const ctx = useReviewContext()
  const [copied, setCopied] = useState(false)  // Move ABOVE the early return

  if (!ctx) return null   // Guard AFTER all hooks
  // ... rest of component
}
```

Both fixes are 3-5 line moves with no logic changes. All other phase artifacts — backend endpoint, TypeScript types, hooks, context, UI components, and end-to-end wiring — verified as complete and correct.

---

_Verified: 2026-03-21T19:00:00Z_
_Verifier: Claude (gsd-verifier)_
