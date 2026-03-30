# Phase 16: Per-Section Verification Display - Research

**Researched:** 2026-03-30
**Domain:** React frontend — verification display filtering in VerificationDetailPanel / SectionBlock
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| QUAL-01 | Engineer can view verification results from CLI output in the GUI | Fix ensures verification results displayed per section are semantically correct — engineers see only truths relevant to the section they are reading |
| QUAL-02 | Engineer can view gaps, severity, and recommendations from verification | Fix ensures gap details shown on a section come from truths that actually reference that section, not phase-level noise |

</phase_requirements>

---

## Summary

The current VerificationDetailPanel receives the **full phase-level `truths` array** (all truths from VERIFICATION.md) and renders every truth on every leaf section. This means a document with 15 truths shows all 15 on every leaf section regardless of relevance. The semantic gap was explicitly deferred in Phase 12-02 as "evidence_files filtering deferred to future iteration."

The fix is a **pure frontend filter** — no backend changes are needed. Each `TruthResult` already carries an `evidence_files: string[]` field populated by the Phase 12-01 backend parser. The evidence files contain section-specific references in the format `"02-01-CONTENT.md, sectie 2.3, regel 45-78"`. The frontend can extract section IDs from these strings and filter the truths array before passing it to `VerificationDetailPanel`.

For sections with no matching truths (evidence_files either empty or referencing other sections), the panel should show a "geen bevindingen" (no findings) state instead of the full phase list.

**Primary recommendation:** Add a `filterTruthsForSection(truths, sectionId)` utility function in the frontend; call it in `SectionBlock` before passing `truths` to `VerificationDetailPanel`; add an empty-state rendering path to `VerificationDetailPanel` for zero-truth cases.

---

## Standard Stack

### Core (all already installed — no new dependencies needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 18.x | Component rendering | Already in project |
| TypeScript | 5.x | Type safety | Already in project |
| `@radix-ui/react-collapsible` | via shadcn | Collapsible panel | Already installed (Phase 12-02) |
| `lucide-react` | current | Icons (CheckCircle2, AlertTriangle, Info) | Already in project |

No new packages are required. This is a pure logic + rendering change within existing components.

---

## Architecture Patterns

### Current Data Flow (the problem)

```
DocumentsTab
  -> useVerificationData(projectId, phaseNumber)     # fetches VerificationDetail
  -> ContentPanel (verificationData = full phase object)
    -> SectionBlock (verificationData = same full object, unfiltered)
      -> VerificationDetailPanel(truths = ALL truths from phase)   ← PROBLEM
```

Every leaf section gets the full `truths` array. There is no filtering step.

### Proposed Data Flow (the fix)

```
DocumentsTab
  -> useVerificationData(projectId, phaseNumber)     # unchanged
  -> ContentPanel (verificationData = full phase object)  # unchanged
    -> SectionBlock
      -> filterTruthsForSection(verificationData.truths, node.id)  ← NEW
      -> VerificationDetailPanel(truths = filtered per-section truths)
         OR <empty-state> when filtered list is empty               ← NEW
```

### Key Files

| File | Role | Change Type |
|------|------|-------------|
| `frontend/src/features/documents/components/SectionBlock.tsx` | Passes truths to VerificationDetailPanel | Add filter call before prop pass |
| `frontend/src/features/documents/components/VerificationDetailPanel.tsx` | Renders truth list | Add empty-state path |
| `frontend/src/features/documents/types/verification.ts` | TruthResult type | Read-only (no change needed) |
| `backend/app/api/phases.py` | Populates evidence_files | Read-only (no change needed) |

### Recommended Project Structure (no new directories needed)

The filter function can live as a local utility inside `SectionBlock.tsx` or as a named export in a new `utils/verification.ts` file. Given the project pattern of keeping small utilities local (see Phase 14 decision: "DocTypeRow extracted as local render function — avoids shared module for 5-line pattern"), a local function inside `SectionBlock.tsx` is appropriate unless reuse is anticipated.

---

## Pattern 1: Evidence-Based Truth Filtering

**What:** Extract section IDs referenced in `evidence_files` strings and filter the truths array to only those that mention the current section.

**Evidence file format** (from live VERIFICATION.md in `backend/projects/2`):
```
"02-01-CONTENT.md, sectie 2.3, regel 45-78"
"02-01-CONTENT.md, sectie 2.4, regel 80-110"
```

The section ID is embedded as `sectie {ID}` within the evidence string. A regex like `/sectie\s+([\d.]+)/i` will extract it.

**Filter logic:**
```typescript
// Source: derived from backend/app/api/phases.py _parse_verification_detail
function filterTruthsForSection(truths: TruthResult[], sectionId: string): TruthResult[] {
  return truths.filter(truth => {
    // If no evidence files, truth is phase-level only — don't show on any section
    if (truth.evidence_files.length === 0) return false

    // Check if any evidence file references this section ID
    return truth.evidence_files.some(file => {
      const match = file.match(/sectie\s+([\d.]+)/i)
      if (!match) return false
      return match[1] === sectionId
    })
  })
}
```

**Fallback for truths without evidence_files:** If `evidence_files` is empty, the truth has no section anchor. These should NOT appear on any section (they are phase summary items, not per-section findings). This is consistent with the audit report's description: "phase-level truths."

### Pattern 2: "No Issues" Empty State in VerificationDetailPanel

When `truths.length === 0` after filtering, show a non-alarming state. The engineer seeing "Verificatieresultaten" expand to show nothing is confusing; better to either hide the panel or show a positive indicator.

**Options:**
- **Option A (recommended):** Skip rendering `VerificationDetailPanel` entirely when filtered truths list is empty. Show a small "geen verificatiebevindingen" inline note instead.
- **Option B:** Pass an empty array and add empty-state rendering inside `VerificationDetailPanel`.

Option A is cleaner — the Collapsible trigger label "Verificatieresultaten" implies there are results to show. If there are none, don't show the trigger. The `ReviewActionBar` still renders (review controls are always relevant).

**Implementation in SectionBlock:**
```typescript
// Source: SectionBlock.tsx leaf section rendering block (line 184)
{phaseHasVerification && verificationData?.has_verification && node.children.length === 0 && (
  <div className="transition-all duration-150">
    {sectionTruths.length > 0 ? (
      <VerificationDetailPanel
        truths={sectionTruths}
        currentCycle={verificationData.current_cycle}
        maxCycles={verificationData.max_cycles}
        isBlocked={verificationData.is_blocked}
        phaseNumber={phaseNumber!}
      />
    ) : (
      <p className="text-xs text-muted-foreground mt-4">
        Geen verificatiebevindingen voor deze sectie.
      </p>
    )}
    <ReviewActionBar sectionId={node.id} />
  </div>
)}
```

### Anti-Patterns to Avoid

- **Do not add a new API endpoint.** The evidence_files data is already in the frontend via `useVerificationData`. No backend call needed.
- **Do not filter in the backend** (adding a `?sectionId=` query param to the verification-detail endpoint). The phase-level response is correct for the overview; filtering is a display concern.
- **Do not filter in VerificationDetailPanel.** The component should be a pure renderer. Filtering belongs in the caller (SectionBlock).
- **Do not hide ReviewActionBar** when truths are empty — review buttons are independent of verification findings.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Section ID matching | Custom fuzzy matcher | Simple regex on `evidence_files` strings | Evidence files already have `sectie X.Y` format |
| Empty state UI | Custom component | Inline `<p className="text-xs text-muted-foreground">` | Matches established project pattern (see EmptySectionCard) |
| New data fetching | New API endpoint | Existing `useVerificationData` hook | Data already fetched; this is a display filter only |

---

## Common Pitfalls

### Pitfall 1: Matching "2.1" against "2.10" or "2.11"

**What goes wrong:** A naive string `includes()` check for `"2.1"` also matches `"2.10"` and `"2.11"`.
**Why it happens:** Section IDs are dot-delimited numerics without trailing terminators.
**How to avoid:** Use exact match after regex extraction: `match[1] === sectionId` (strict equality), not `includes()`.
**Warning signs:** Section 2.1 showing truths that belong to 2.10.

### Pitfall 2: Evidence files with different formats

**What goes wrong:** Not all VERIFICATION.md files may use `sectie X.Y` Dutch format — some may use English `section X.Y` or no section reference at all.
**Why it happens:** VERIFICATION.md files are generated by v1.0 CLI which may vary format.
**How to avoid:** The regex should handle both Dutch and English: `/(?:sectie|section)\s+([\d.]+)/i`. If neither matches, the truth is treated as phase-level (not shown on any section).
**Warning signs:** All truths disappearing from all sections with no matches.

### Pitfall 3: ReviewActionBar losing its section context

**What goes wrong:** If the conditional rendering wrapping is refactored carelessly, `ReviewActionBar` might be gated behind the `sectionTruths.length > 0` check.
**Why it happens:** ReviewActionBar is a sibling element (Phase 12-02 pattern: "sibling rendering, never nested").
**How to avoid:** Keep `ReviewActionBar` outside any truths-length conditional. The existing structure (`<VerificationDetailPanel />` OR empty-state, THEN `<ReviewActionBar />`) maintains this.

### Pitfall 4: Prop name collision if VerificationDetailPanel signature changes

**What goes wrong:** The `truths` prop currently accepts all phase truths. If VerificationDetailPanel is changed to accept a new `sectionId` prop and does its own filtering, both code paths may coexist and produce inconsistency.
**Why it happens:** Dual-responsibility creep.
**How to avoid:** Filter in SectionBlock only. Keep VerificationDetailPanel as a pure display component that renders whatever truths array it receives.

---

## Code Examples

### Current SectionBlock leaf rendering (the call site to change)

```typescript
// Source: frontend/src/features/documents/components/SectionBlock.tsx lines 183-197
{phaseHasVerification && verificationData?.has_verification && node.children.length === 0 && (
  <div className="transition-all duration-150">
    <VerificationDetailPanel
      truths={verificationData.truths}     // <-- currently passes ALL truths
      currentCycle={verificationData.current_cycle}
      maxCycles={verificationData.max_cycles}
      isBlocked={verificationData.is_blocked}
      phaseNumber={phaseNumber!}
    />
    <ReviewActionBar sectionId={node.id} />
  </div>
)}
```

### Fixed SectionBlock leaf rendering

```typescript
// After fix: filter truths before passing
const sectionTruths = filterTruthsForSection(verificationData.truths, node.id)

{phaseHasVerification && verificationData?.has_verification && node.children.length === 0 && (
  <div className="transition-all duration-150">
    {sectionTruths.length > 0 ? (
      <VerificationDetailPanel
        truths={sectionTruths}
        currentCycle={verificationData.current_cycle}
        maxCycles={verificationData.max_cycles}
        isBlocked={verificationData.is_blocked}
        phaseNumber={phaseNumber!}
      />
    ) : (
      <p className="text-xs text-muted-foreground mt-4">
        Geen verificatiebevindingen voor deze sectie.
      </p>
    )}
    <ReviewActionBar sectionId={node.id} />
  </div>
)}
```

### filterTruthsForSection utility

```typescript
// Source: derived from evidence_files format in backend/projects/2/.planning/phases/02-system-overview/02-VERIFICATION.md
function filterTruthsForSection(truths: TruthResult[], sectionId: string): TruthResult[] {
  return truths.filter(truth => {
    if (truth.evidence_files.length === 0) return false
    return truth.evidence_files.some(file => {
      const match = file.match(/(?:sectie|section)\s+([\d.]+)/i)
      return match ? match[1] === sectionId : false
    })
  })
}
```

### Current TruthResult type (no changes needed)

```typescript
// Source: frontend/src/features/documents/types/verification.ts
export interface TruthResult {
  description: string
  status: 'PASS' | 'GAP'
  levels: { exists: ...; substantive: ...; complete: ...; consistent: ...; standards: ... }
  failed_level: string | null
  gap_description: string | null
  evidence_files: string[]      // e.g. ["02-01-CONTENT.md, sectie 2.3, regel 45-78"]
  standards_violations: Array<{ reference: string; text: string }>
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase-level truths on all sections (by design, deferred) | Per-section filtered truths | Phase 16 (now) | Sections show only relevant verification findings |
| Always show VerificationDetailPanel trigger | Conditionally show based on truths.length > 0 | Phase 16 (now) | Cleaner UX: no misleading "Verificatieresultaten" on sections with no findings |

---

## Open Questions

1. **What if a VERIFICATION.md has no evidence_files at all (e.g., earlier v1.0 format)?**
   - What we know: The backend parser `_parse_verification_detail` uses regex `r'-\s*File:\s*(.+)'` to populate `evidence_files`. If no `**Evidence:**` block exists in the truth block, the list will be empty.
   - What's unclear: How common is this pattern in real project VERIFICATION.md files?
   - Recommendation: Treat empty `evidence_files` as "phase-level truth, not section-specific." The section shows no truths, and the empty-state message appears. This is the correct behavior for verification files that predate the section-reference format.

2. **Should the GEBLOKKEERD alert appear even on sections with no truths?**
   - What we know: `isBlocked` is phase-level (not per-truth). The alert currently appears inside VerificationDetailPanel.
   - What's unclear: Does an engineer need to see GEBLOKKEERD on every section, or only sections with gaps?
   - Recommendation: If `sectionTruths.length === 0`, skip the entire VerificationDetailPanel (including the GEBLOKKEERD alert). The GEBLOKKEERD state is visible in the phase timeline and on sections that do have gap truths.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Vitest (frontend) |
| Config file | `frontend/vite.config.ts` or `frontend/vitest.config.ts` if present |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUAL-01 | `filterTruthsForSection` returns only truths matching section ID | unit | `npx vitest run src/features/documents/utils/filterTruthsForSection.test.ts` | Wave 0 |
| QUAL-01 | `filterTruthsForSection` returns empty array for truths with no evidence_files | unit | same file | Wave 0 |
| QUAL-02 | VerificationDetailPanel renders empty-state message when truths=[] | unit | `npx vitest run src/features/documents/components/VerificationDetailPanel.test.tsx` | Wave 0 |
| QUAL-02 | SectionBlock does not pass GEBLOKKEERD to empty-truths sections | unit | same file | Wave 0 |

### Sampling Rate

- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `frontend/src/features/documents/utils/filterTruthsForSection.test.ts` — covers QUAL-01 section filtering logic
- [ ] `frontend/src/features/documents/components/VerificationDetailPanel.test.tsx` — covers QUAL-02 empty-state rendering

*(Note: If the project uses a different test file location convention, adjust paths. Check for existing test files near these components before creating new ones.)*

---

## Sources

### Primary (HIGH confidence)

- Direct code read: `frontend/src/features/documents/components/VerificationDetailPanel.tsx` — confirmed current props and rendering
- Direct code read: `frontend/src/features/documents/components/SectionBlock.tsx` — confirmed where truths are passed and leaf-node guard condition
- Direct code read: `frontend/src/features/documents/types/verification.ts` — confirmed `evidence_files: string[]` field on `TruthResult`
- Direct code read: `backend/app/api/phases.py` lines 351-394 — confirmed how `evidence_files` are populated from VERIFICATION.md
- Direct file read: `backend/projects/2/.planning/phases/02-system-overview/02-VERIFICATION.md` — confirmed live evidence file format (`sectie X.Y`)
- `.planning/v2.0-MILESTONE-AUDIT.md` — confirmed exact gap description and QUAL-01/QUAL-02 scope

### Secondary (MEDIUM confidence)

- `.planning/STATE.md` line 171 — "evidence_files filtering deferred" decision from Phase 12
- `.planning/phases/12-review-interface/12-02-SUMMARY.md` line 99 — same decision, confirmed deferred scope

### Tertiary (LOW confidence)

None — all findings are from direct code reads with no external sources required.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all components already exist; no new dependencies
- Architecture: HIGH — data flow traced end-to-end through live source code
- Pitfalls: HIGH — section ID matching pitfall identified from live data format; others from code structure
- Filter logic: HIGH — evidence_files format confirmed from real VERIFICATION.md file

**Research date:** 2026-03-30
**Valid until:** Stable — no external dependencies; valid until SectionBlock or VerificationDetailPanel is refactored
