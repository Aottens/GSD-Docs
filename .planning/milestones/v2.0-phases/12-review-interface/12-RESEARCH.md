# Phase 12: Review Interface - Research

**Researched:** 2026-03-21
**Domain:** React frontend review/verification UI + FastAPI filesystem-read backend
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Review workflow UX:**
- Review controls overlay directly onto existing document preview (Phase 11 SectionBlock) — no separate tab or mode switch
- Review buttons (Goedkeuren / Opmerking / Afwijzen) appear automatically on any section that has verification results (VERIFICATION.md exists for the phase)
- No explicit "start review" action — controls appear as soon as CLI completes verification
- Outline tree status badge evolves: G1 (geschreven) → V1 (geverifieerd) → ✓ (goedgekeurd) / ⚠ (opmerking) / ✗ (afgewezen) — single badge, replaces previous
- After all sections reviewed, show summary (X goedgekeurd, Y opmerking, Z afgewezen) with suggested CLI command: `/doc:review-phase N` to generate REVIEW.md

**Verification display:**
- Per-section inline: verification status on each SectionBlock — green check (passed), amber warning (gaps), red (failed)
- Click to expand verification detail block below section content showing: cycle counter (Cyclus 1/2), truth-by-truth pass/gap status, gap descriptions
- Gap closure cycle shown as badge "Cyclus 1/2" on phase timeline and in verification panel
- If cycle 2 still has gaps: show "GEBLOKKEERD" warning
- Verification display is purely read-only — if gaps found, show CLI hint: `/doc:plan-phase N --gaps`

**Standards compliance:**
- Standards violations displayed inline per section, under a "Normen" heading within the verification block
- Each violation shows: standard reference badge (e.g. "ISA-88 §4.3"), what was expected, what was found
- Standard reference badges are subtle — tooltip or expand to show full requirement text on hover/click
- Not a separate tab — integrated into the per-section verification view

**Feedback capture:**
- Inline textarea expands below review buttons when engineer clicks "Opmerking" or "Afwijzen"
- Textarea for free-text feedback, "Opslaan" button to save
- Feedback stored in browser during review session — exported for CLI to generate REVIEW.md

### Claude's Discretion
- Feedback storage mechanism (localStorage vs React state vs backend write) — pick what fits the architecture best
- Exact layout of verification detail block (accordion, collapsible card, or inline)
- How "export for CLI" works (JSON file, clipboard copy, or backend endpoint)
- Loading/error states for verification data
- Animation/transition when review controls appear

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| QUAL-01 | Engineer can view verification results from CLI output in the GUI | Backend VERIFICATION.md parsing + new `/verification` endpoint; frontend `useVerificationData` hook |
| QUAL-02 | Engineer can view gaps, severity, and recommendations from verification | VERIFICATION.md template parsing: truth table + gap descriptions + 5-level cascade |
| QUAL-03 | Engineer can see gap closure cycle status (verify → re-plan → re-write) | VERIFICATION.md header: `Cycle: N of 2`, `Status: PASS/GAPS_FOUND` — parse and display as badge |
| QUAL-04 | Engineer can approve or reject verification results before proceeding | SectionBlock review action bar: Goedkeuren / Opmerking / Afwijzen buttons; feedback textarea |
| QUAL-05 | Engineer can conduct review-phase with approve/reject/request-changes per section | Same as QUAL-04 — review controls per section, post-review summary with CLI command |
| QUAL-06 | Engineer can provide text feedback during review that feeds back into the workflow | Feedback textarea on Opmerking/Afwijzen, stored in React state or localStorage, exported as JSON for `/doc:review-phase N` |
| QUAL-07 | Engineer can view PackML/ISA-88 standards compliance results in the GUI | Level 5 (Standards) in VERIFICATION.md truth table — already captured in gap descriptions |
| QUAL-08 | Engineer can view standards violations with references to standard sections | Gap descriptions in VERIFICATION.md contain standard references ("ISA-88 §4.3") — parse + display as badges |
</phase_requirements>

---

## Summary

Phase 12 extends the Phase 11 document preview with three overlapping capabilities: verification result display (reading VERIFICATION.md from filesystem), per-section review action controls (Goedkeuren / Opmerking / Afwijzen), and standards compliance display. The key architectural principle is "GUI displays, CLI acts" — the frontend is read-only for verification data and captures but does not write review decisions directly to disk.

The VERIFICATION.md file is already partially parsed by the existing `phases.py` backend (`_extract_verification_summary`), but only for aggregate scores and gap counts. Phase 12 needs a new backend endpoint to serve per-section verification detail: which truths apply to each section, their 5-level cascade results, gap descriptions, and standards violations. This data must be parsed from the flat VERIFICATION.md format (which references section IDs in its detailed findings).

The frontend must extend `SectionBlock.tsx` (189 lines, Phase 11) with: (a) a verification status bar that appears when `has_verification` is true, (b) an expandable verification detail panel per section, and (c) review action buttons plus feedback textarea. The `OutlineNode.tsx` badge logic needs a new `reviewed` status branch. All UI is in Dutch per established project convention.

**Primary recommendation:** Add a single new backend endpoint `/api/projects/{project_id}/phases/{phase_number}/verification-detail` that parses VERIFICATION.md into per-section structured data. Store review feedback in React context (lifted to DocumentsTab level) with localStorage persistence. Export via clipboard-copyable JSON that maps directly to the REVIEW.md template format CLI expects.

---

## Standard Stack

### Core (all already in use — no new packages required)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React Query (`@tanstack/react-query`) | existing | Data fetching + polling | Already drives all document/phase data |
| shadcn/ui Collapsible | existing | Expandable verification detail block | Already available, used elsewhere |
| shadcn/ui Badge | existing | Status indicators, standard reference pills | Already imported in OutlineNode, SectionBlock |
| shadcn/ui Tooltip + TooltipProvider | existing | Standard reference full text on hover | Already in OutlineNode |
| shadcn/ui Textarea | existing | Feedback input | Already available in shadcn/ui |
| shadcn/ui Button | existing | Goedkeuren / Opmerking / Afwijzen | Already used throughout |
| ReactMarkdown + remark-gfm | existing | Gap description rendering | Already in SectionBlock markdown components |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| localStorage | browser native | Persist review session across page reload | Claude's discretion: fits architecture better than backend write |
| lucide-react | existing | CheckCircle2, AlertTriangle, XCircle for review status icons | Already imported in OutlineNode |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| localStorage for feedback | Backend POST endpoint | Backend write adds complexity; review is session-level, not permanent until CLI runs |
| Clipboard copy for export | File download | Clipboard is simpler, no file API needed; CLI command is what acts |
| React context for review state | Zustand/Jotai | Context is sufficient for single-phase review session, no global state needed |

**Installation:** No new packages required. All needed libraries are already installed.

---

## Architecture Patterns

### Recommended Project Structure

Extensions to existing document feature:

```
frontend/src/features/documents/
├── components/
│   ├── SectionBlock.tsx          # EXTEND: add VerificationBar + ReviewActionBar
│   ├── OutlineNode.tsx           # EXTEND: add reviewed/verified badge branches
│   ├── VerificationDetailPanel.tsx  # NEW: collapsible truth-by-truth detail
│   ├── ReviewActionBar.tsx          # NEW: Goedkeuren/Opmerking/Afwijzen + textarea
│   └── StandardsBadge.tsx           # NEW: "ISA-88 §4.3" pill with tooltip
├── hooks/
│   ├── useVerificationData.ts    # NEW: fetch + cache phase verification detail
│   └── useReviewSession.ts       # NEW: manage review state + localStorage persistence
├── types/
│   └── verification.ts           # NEW: VerificationDetail, TruthResult, StandardsViolation
└── context/
    └── ReviewContext.tsx          # NEW: lifted review state for DocumentsTab scope
```

```
backend/app/
├── api/
│   └── phases.py                 # EXTEND: add /verification-detail endpoint
├── schemas/
│   └── verification.py           # NEW: VerificationDetailResponse, TruthResult, etc.
```

### Pattern 1: Conditional Review Controls on SectionBlock

Review controls appear automatically when `has_verification` is true at the phase level (not per section). The backend's `/phases/{n}` endpoint already returns `has_verification`. The frontend passes this as a prop down from DocumentsTab → ContentPanel → SectionBlock.

**What:** `SectionBlock` receives `phaseHasVerification: boolean` prop. When true, it renders `VerificationBar` (status indicator) and `ReviewActionBar` (buttons + textarea) below section content.

**When to use:** Always — no mode switch, no "start review" button.

```typescript
// SectionBlock.tsx extension pattern
interface SectionBlockProps {
  node: OutlineNode
  language: 'nl' | 'en'
  projectId: number
  phaseNumber?: number           // NEW: needed to scope verification data
  phaseHasVerification?: boolean // NEW: drives review control visibility
  depth?: number
}

export function SectionBlock({ node, language, projectId, phaseNumber, phaseHasVerification, depth = 1 }: SectionBlockProps) {
  // ...existing render...
  return (
    <div id={`section-${node.id}`} className="mb-8">
      {/* ...existing header + content... */}
      {phaseHasVerification && (
        <VerificationBar
          sectionId={node.id}
          projectId={projectId}
          phaseNumber={phaseNumber!}
        />
      )}
      {phaseHasVerification && node.children.length === 0 && (
        <ReviewActionBar sectionId={node.id} />
      )}
    </div>
  )
}
```

### Pattern 2: VERIFICATION.md Parsing for Per-Section Data

VERIFICATION.md is a flat markdown file. The "Detailed Findings" section uses `### Truth N: {description}` headings. The gap descriptions reference section IDs via file paths in the Evidence block. The backend must parse this into structured per-truth data.

**Key parsing logic for backend:**

```python
# backend/app/api/phases.py — new _parse_verification_detail()

def _parse_verification_truths(content: str) -> list[dict]:
    """
    Parse VERIFICATION.md Detailed Findings into truth-level dicts.

    Each truth block has:
    - truth_number: int
    - description: str
    - status: "PASS" | "GAP"
    - failed_level: str | None  (e.g. "Level 3 - Complete")
    - levels: dict with keys exists/substantive/complete/consistent/standards
    - gap_description: str | None
    - standards_violations: list[dict] with ref, expected, found
    """
    # Split on ### Truth N: pattern
    truth_blocks = re.split(r'(?=### Truth \d+:)', content)
    ...
```

The Summary table at the top of VERIFICATION.md provides quick pass/gap status per truth:

```
| {Truth N} | ✓/⚠ | ✓/⚠/- | ✓/⚠/- | ✓/⚠/- | ✓/⚠/-/N/A | PASS/GAP |
```

This is easier to parse for the quick status display. Use the summary table for the `VerificationBar` indicator, and the detailed findings for the expandable `VerificationDetailPanel`.

### Pattern 3: Review State via React Context + localStorage

Review feedback is session-level. Lifted to `DocumentsTab` scope so the post-review summary can aggregate across sections.

```typescript
// ReviewContext.tsx
interface SectionReview {
  sectionId: string
  status: 'goedgekeurd' | 'opmerking' | 'afgewezen'
  feedback: string   // empty string for goedgekeurd
  timestamp: number
}

interface ReviewContextValue {
  reviews: Record<string, SectionReview>   // keyed by sectionId
  setReview: (sectionId: string, status: SectionReview['status'], feedback: string) => void
  clearReviews: () => void
  exportAsJson: () => string  // for clipboard copy → CLI input
}
```

localStorage key: `review-session-{projectId}-{phaseNumber}` — survives page reload, scoped to project+phase.

### Pattern 4: Standards Violation Badge

Standards violations appear in VERIFICATION.md gap descriptions as references like "ISA-88 §4.3" or "PackML states.md". Parse these with regex and render as `StandardsBadge` with tooltip.

```typescript
// StandardsBadge.tsx
interface StandardsBadgeProps {
  reference: string      // e.g. "ISA-88 §4.3"
  expected?: string
  found?: string
}
// Renders as: subtle pill "ISA-88 §4.3" — Tooltip shows expected vs found on hover
```

Regex pattern to extract from gap descriptions:
```typescript
const STANDARD_REF_PATTERN = /(PackML|ISA-88)\s+[§#]?[\d.]+/g
```

### Pattern 5: Outline Badge Evolution

`OutlineNode.tsx` currently uses `status: 'empty' | 'planned' | 'written' | 'verified'`. The review status is stored in `ReviewContext` (frontend-only, not in backend `OutlineNode` type). The badge must combine backend `node.status` with frontend `ReviewContext`.

```typescript
// In OutlineNode.tsx — derive display badge from both sources
function getDisplayStatus(
  nodeStatus: OutlineNode['status'],
  reviewStatus: SectionReview['status'] | undefined
) {
  if (reviewStatus === 'goedgekeurd') return 'approved'    // ✓ green
  if (reviewStatus === 'opmerking') return 'comment'       // ⚠ amber
  if (reviewStatus === 'afgewezen') return 'rejected'      // ✗ red
  if (nodeStatus === 'verified') return 'verified'         // V1 green
  if (nodeStatus === 'written') return 'written'           // G1 amber
  ...
}
```

The badge text from CONTEXT.md: G1 (geschreven), V1 (geverifieerd), ✓ / ⚠ / ✗ for reviewed states.

### Anti-Patterns to Avoid

- **Per-section verification polling:** Don't fetch VERIFICATION.md once per section. Fetch the whole phase verification detail once and distribute via context or prop drilling.
- **Writing REVIEW.md from GUI:** The GUI must never write REVIEW.md. Only export as JSON/clipboard for CLI to consume.
- **Separate verification tab:** CONTEXT.md locks this as inline overlay on SectionBlock, not a tab.
- **Triggering AI/CLI from GUI:** All AI operations stay in CLI. Verification display is read-only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Expandable detail block | Custom collapse animation | shadcn/ui `Collapsible` | Already in project, handles a11y + animation |
| Tooltip on badge hover | Custom tooltip div | shadcn/ui `Tooltip` + `TooltipProvider` | Already used in OutlineNode, consistent |
| Feedback text input | Raw `<textarea>` | shadcn/ui `Textarea` | Consistent styling with project |
| Markdown in gap descriptions | Custom renderer | ReactMarkdown (already in SectionBlock) | Gap descriptions may contain backticks, tables |
| Status icons for review states | SVG hand-coded | lucide-react `CheckCircle2`, `MessageSquare`, `XCircle` | Already in project |

**Key insight:** This phase is almost entirely composition of existing shadcn/ui components + extension of existing files. No new library installs required.

---

## Common Pitfalls

### Pitfall 1: VERIFICATION.md Parsing Breaks on Edge Cases

**What goes wrong:** VERIFICATION.md is markdown generated by an LLM. Its structure is mostly consistent but can have slight variations (extra newlines, different whitespace, truncated gap descriptions).

**Why it happens:** The template shows a canonical format but LLM output varies. The existing `_extract_verification_summary` in phases.py already shows this is fragile (looks for `(\d+)/(\d+)\s+levels?\s+passed` pattern that may not match the actual VERIFICATION.md format, which uses `PASS`/`GAPS_FOUND` status, not a score ratio).

**How to avoid:** Parse defensively — always provide fallback values. The summary table at the top of VERIFICATION.md is more reliably structured than the detailed findings. Parse the summary table for status; parse detailed findings for detail. Never throw if parsing fails — return empty/null data.

**Warning signs:** `_extract_verification_summary` returns `score: None` even for completed verifications — check current regex against actual VERIFICATION.md format.

### Pitfall 2: Review State Lost on Navigation

**What goes wrong:** Engineer reviews 5 sections, navigates away, returns to find all review decisions gone.

**Why it happens:** Review state in component local state is lost on unmount.

**How to avoid:** Use `ReviewContext` at `DocumentsTab` level + persist to localStorage on every state change. Key: `review-session-{projectId}-{phaseNumber}`.

### Pitfall 3: Phase-Level vs Section-Level Verification

**What goes wrong:** VERIFICATION.md is a per-phase file, but the UI needs per-section data. The mapping from "truth" to "section" is not explicit in the VERIFICATION.md format — truths are about the phase goal, not individual sections.

**Why it happens:** The verification workflow verifies truths (derived from phase goals), not sections directly. Evidence in gap descriptions references section files/IDs, but the primary structure is truth-centric.

**How to avoid:** Accept that the section-truth mapping is fuzzy. Display verification results at the phase level (phase banner) and only show section-level status if the evidence block in a truth explicitly mentions that section ID. When no section-specific truth is found, show the phase-level overall status on each section.

**Recommendation:** Parse Evidence blocks for section ID references (e.g. `File: 03-02-CONTENT.md`) to attribute truths to sections. For sections with no referenced truths, show phase-level pass/fail.

### Pitfall 4: `has_verification` vs Section Status

**What goes wrong:** `OutlineNode.status` already has `'verified'` as a value, and `_enrich_node_status` in documents.py sets it when VERIFICATION.md is found. But VERIFICATION.md may have `Status: GAPS_FOUND` — a section could be "verified" (VERIFICATION.md exists) but actually have gaps.

**Why it happens:** The existing status detection only checks file existence, not VERIFICATION.md content.

**How to avoid:** The new verification detail endpoint must expose the overall `Status: PASS/GAPS_FOUND` and per-section gap status. In `SectionBlock`, the verification status bar should show green (PASS) or amber/red (GAPS_FOUND) based on parsed status, not just `node.status === 'verified'`.

### Pitfall 5: OutlineNode Type Doesn't Include Review Status

**What goes wrong:** `OutlineNode` TypeScript type (and backend schema) only has `status: 'empty' | 'planned' | 'written' | 'verified'`. Adding `'reviewed'` requires backend + frontend type changes.

**How to avoid:** Keep review status in `ReviewContext` (frontend-only). Don't add `'reviewed'` to `OutlineNode` status — the reviewed state is session-level, not persisted to the backend. The `OutlineNode` in the badge display merges `node.status` (from backend) with `reviewStatus` (from context).

### Pitfall 6: Textarea Focus and Collapsible State Conflicts

**What goes wrong:** When the verification detail block is open (Collapsible), and the engineer clicks a review button to reveal the textarea, the Collapsible may interfere with focus or layout.

**How to avoid:** Review action bar (buttons + textarea) is always rendered below the section content, separate from the verification detail Collapsible. They are sibling elements, not nested.

---

## Code Examples

### Backend: Parse VERIFICATION.md summary table

```python
# Source: verification.md template analysis
import re

def _parse_verification_status(content: str) -> dict:
    """
    Parse VERIFICATION.md for status, cycle, and per-truth summary.
    Returns dict safe to use even if parsing partially fails.
    """
    status_match = re.search(r'^\*\*Status:\*\*\s*(PASS|GAPS_FOUND(?:\s+\(ESCALATED\))?)', content, re.MULTILINE)
    cycle_match = re.search(r'^\*\*Cycle:\*\*\s*(\d+)\s+of\s+(\d+)', content, re.MULTILINE)

    status = status_match.group(1) if status_match else "UNKNOWN"
    current_cycle = int(cycle_match.group(1)) if cycle_match else 1
    max_cycles = int(cycle_match.group(2)) if cycle_match else 2

    # Parse summary table: | Truth name | ✓/⚠ | ... | PASS/GAP |
    truth_rows = re.findall(
        r'^\|\s*(.+?)\s*\|(?:\s*[✓⚠-]\s*\|){4,5}\s*(PASS|GAP)\s*\|',
        content, re.MULTILINE
    )
    truths = [{"description": t[0], "status": t[1]} for t in truth_rows]

    return {
        "status": status,
        "current_cycle": current_cycle,
        "max_cycles": max_cycles,
        "truths": truths,
        "is_blocked": "ESCALATED" in status,
    }
```

### Backend: New verification detail endpoint

```python
# Source: phases.py extension pattern
@router.get("/{phase_number}/verification-detail")
async def get_phase_verification_detail(
    project_id: int,
    phase_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Parse VERIFICATION.md and return structured verification data."""
    project_dir = _get_project_dir(project_id)
    planning_dir = project_dir / ".planning" / "phases"
    phase_dirs = list(planning_dir.glob(f"{phase_number:02d}-*")) if planning_dir.exists() else []

    if not phase_dirs:
        return {"has_verification": False, "status": None, "truths": [], "current_cycle": 1}

    phase_dir = phase_dirs[0]
    verif_files = list(phase_dir.glob(f"{phase_number:02d}-VERIFICATION.md"))
    if not verif_files:
        return {"has_verification": False, "status": None, "truths": [], "current_cycle": 1}

    content = verif_files[0].read_text(encoding="utf-8")
    return {
        "has_verification": True,
        **_parse_verification_status(content),
    }
```

### Frontend: useVerificationData hook

```typescript
// Source: existing hook patterns (useDocumentOutline, useSectionContent)
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useVerificationData(projectId: number, phaseNumber: number, enabled: boolean) {
  return useQuery({
    queryKey: ['projects', projectId, 'phases', phaseNumber, 'verification-detail'],
    queryFn: () => api.get(`/projects/${projectId}/phases/${phaseNumber}/verification-detail`),
    enabled,
    refetchInterval: 30000,   // consistent with existing document polling
    staleTime: 25000,
  })
}
```

### Frontend: ReviewContext with localStorage persistence

```typescript
// Source: React context pattern
import { createContext, useContext, useReducer, useEffect } from 'react'

const STORAGE_KEY = (projectId: number, phaseNumber: number) =>
  `review-session-${projectId}-${phaseNumber}`

export function ReviewProvider({ projectId, phaseNumber, children }) {
  const storageKey = STORAGE_KEY(projectId, phaseNumber)

  const [reviews, dispatch] = useReducer(reviewReducer, {}, () => {
    try {
      const stored = localStorage.getItem(storageKey)
      return stored ? JSON.parse(stored) : {}
    } catch {
      return {}
    }
  })

  // Persist on change
  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(reviews))
  }, [reviews, storageKey])

  // Export for CLI: maps to REVIEW.md template format
  const exportAsJson = () => JSON.stringify({
    phaseNumber,
    exportedAt: new Date().toISOString(),
    sections: Object.values(reviews),
  }, null, 2)

  return (
    <ReviewContext.Provider value={{ reviews, dispatch, exportAsJson }}>
      {children}
    </ReviewContext.Provider>
  )
}
```

### Frontend: Post-review summary with CLI command hint

```typescript
// Source: PhasePopover/CliCommandBlock pattern from Phase 10
// After all leaf sections reviewed, show in ContentPanel footer:
function ReviewSummary({ phaseNumber, reviews }) {
  const approved = Object.values(reviews).filter(r => r.status === 'goedgekeurd').length
  const comments = Object.values(reviews).filter(r => r.status === 'opmerking').length
  const rejected = Object.values(reviews).filter(r => r.status === 'afgewezen').length

  return (
    <div className="border rounded-md p-4 mt-6">
      <p>{approved} goedgekeurd · {comments} opmerking · {rejected} afgewezen</p>
      <code className="text-sm">/doc:review-phase {phaseNumber}</code>
      <Button onClick={() => navigator.clipboard.writeText(exportAsJson())}>
        Exporteer als JSON
      </Button>
    </div>
  )
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate review tab/mode | Inline overlay on SectionBlock | Phase 12 CONTEXT decision | No mode switch, controls appear automatically |
| Review status in OutlineNode backend status | Frontend-only ReviewContext + localStorage | Phase 12 research finding | Avoids backend type changes; review is session-level |
| Aggregate verification score only | Per-truth structured parsing | Phase 12 new endpoint | QUAL-02 requires gaps/severity detail, not just score |
| `has_verification` = file exists | `has_verification` = file exists + parse status | Phase 12 extension | Distinguishes PASS vs GAPS_FOUND for UI states |

**Deprecated/outdated:**
- `_extract_verification_summary` in phases.py: Uses `(\d+)/(\d+)\s+levels?\s+passed` regex which does NOT match VERIFICATION.md format (`**Status:** PASS/GAPS_FOUND`). The new endpoint must use corrected parsing.

---

## Open Questions

1. **Section-to-truth mapping accuracy**
   - What we know: VERIFICATION.md truths reference section file paths in Evidence blocks
   - What's unclear: Whether all truths have explicit section references or some are phase-level
   - Recommendation: Parse Evidence blocks for file paths like `03-02-CONTENT.md` to attribute truths; fall back to phase-level display when no section match found

2. **Standards violation parsing**
   - What we know: Level 5 (Standards) gap descriptions mention standard names ("PackML", "ISA-88") and section references
   - What's unclear: Whether format is consistent enough to reliably parse into `{reference, expected, found}` triples
   - Recommendation: Use simple regex for standard name detection; display full gap text in tooltip rather than structured fields

3. **REVIEW.md consumption by CLI**
   - What we know: CLI `/doc:review-phase N` generates REVIEW.md from interactive session; the GUI wants to feed back into this
   - What's unclear: Whether the CLI can accept a pre-populated JSON/structured input or always runs interactively
   - Recommendation: The CONTEXT.md answer is "export for CLI" — the GUI exports session data (clipboard or JSON download), engineer provides it context when running CLI. Don't expect CLI API integration.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No test framework detected in project |
| Config file | None found |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUAL-01 | Backend returns verification data from VERIFICATION.md | manual-only | N/A | N/A |
| QUAL-02 | Gaps, severity, recommendations render in UI | manual-only | N/A | N/A |
| QUAL-03 | Cycle badge "Cyclus 1/2" renders correctly | manual-only | N/A | N/A |
| QUAL-04 | Approve/reject/request-changes controls appear when VERIFICATION.md present | manual-only | N/A | N/A |
| QUAL-05 | Section-by-section review workflow completes | manual-only | N/A | N/A |
| QUAL-06 | Feedback saved to localStorage, survives reload | manual-only | N/A | N/A |
| QUAL-07 | Standards compliance section renders | manual-only | N/A | N/A |
| QUAL-08 | Standard reference badges render with tooltip | manual-only | N/A | N/A |

No automated test infrastructure exists in this project. All verification is manual browser testing against a project with an existing VERIFICATION.md.

### Wave 0 Gaps
None — no test infrastructure required. Manual testing procedure:
1. Ensure a test project has a VERIFICATION.md with `Status: GAPS_FOUND`
2. Verify review controls appear on section blocks
3. Verify feedback persists across reload
4. Verify standards violation badges appear if Level 5 gaps exist

---

## Integration Points: Concrete Changes Required

### Backend Changes

**1. Extend `_parse_verification_status` / add new parser (phases.py)**
- Fix existing `_extract_verification_summary` — current regex `(\d+)/(\d+)\s+levels?\s+passed` does not match VERIFICATION.md format which uses `**Status:** PASS` — this is an existing bug
- Add `_parse_verification_detail()` for full truth table + gap descriptions

**2. New endpoint in phases.py**
- `GET /api/projects/{project_id}/phases/{phase_number}/verification-detail`
- Returns: `{has_verification, status, current_cycle, max_cycles, is_blocked, truths: [{description, status, failed_level, gap_description}]}`
- No new schema file needed if added inline; OR add `backend/app/schemas/verification.py`

### Frontend Changes

**3. New types: `frontend/src/features/documents/types/verification.ts`**
- `VerificationDetail`, `TruthResult`, `VerificationStatus`

**4. New hook: `useVerificationData.ts`**
- React Query, 30s refetchInterval, `enabled` flag

**5. New context: `ReviewContext.tsx`**
- `ReviewProvider` wrapping `DocumentsTab`
- localStorage persistence
- `exportAsJson()` method

**6. New components**
- `VerificationDetailPanel.tsx` — collapsible, truth-by-truth list
- `ReviewActionBar.tsx` — Goedkeuren/Opmerking/Afwijzen + textarea
- `StandardsBadge.tsx` — reference pill + tooltip

**7. Extend `SectionBlock.tsx`**
- Add `phaseNumber` and `phaseHasVerification` props
- Render `VerificationDetailPanel` and `ReviewActionBar` conditionally

**8. Extend `OutlineNode.tsx`**
- Consume `ReviewContext` for per-section status display
- Add badge variants for approved (✓), comment (⚠), rejected (✗)
- The `OutlineNode` TypeScript type does NOT change — review status stays in context

**9. Extend `DocumentsTab.tsx`**
- Wrap with `ReviewProvider`
- Pass `phaseNumber` and `has_verification` down the component tree
- Render `ReviewSummary` when all leaf sections are reviewed

**10. Extend `ContentPanel.tsx`** (if it exists as wrapper for SectionBlocks)
- Pass verification props to SectionBlock children

---

## Sources

### Primary (HIGH confidence)
- Direct code reading: `frontend/src/features/documents/components/SectionBlock.tsx` — Phase 11 component to extend
- Direct code reading: `frontend/src/features/documents/components/OutlineNode.tsx` — badge logic to extend
- Direct code reading: `backend/app/api/phases.py` — existing verification parsing + endpoint pattern
- Direct code reading: `backend/app/api/documents.py` — filesystem reading patterns
- Direct code reading: `backend/app/schemas/phase.py` — PhaseStatusResponse fields
- Direct code reading: `gsd-docs-industrial/templates/verification.md` — VERIFICATION.md canonical format
- Direct code reading: `gsd-docs-industrial/templates/review.md` — REVIEW.md canonical format
- Direct code reading: `gsd-docs-industrial/workflows/verify-phase.md` — verification cycle logic
- Direct code reading: `gsd-docs-industrial/workflows/review-phase.md` — review workflow

### Secondary (MEDIUM confidence)
- shadcn/ui docs (confirmed available in project): Collapsible, Badge, Tooltip, Textarea, Button
- React Query patterns: consistent with existing hooks (useDocumentOutline, useSectionContent)

### Tertiary (LOW confidence)
- None required — all research from direct project code reading

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed, verified in existing files
- Architecture: HIGH — extension of Phase 11 code, patterns verified in existing codebase
- Pitfalls: HIGH — derived from direct code reading (existing parsing bugs, type constraints)
- Parsing details: MEDIUM — based on VERIFICATION.md template; actual LLM output may vary slightly

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable stack, no fast-moving dependencies)
