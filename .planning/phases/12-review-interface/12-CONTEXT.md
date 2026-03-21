# Phase 12: Review Interface - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can review FDS sections with approve/reject/request-changes workflow, view verification results (gaps, severity, cycle status) from CLI output files, and see PackML/ISA-88 standards compliance results. All review intelligence comes from CLI-generated files (VERIFICATION.md, REVIEW.md) — the GUI displays and captures feedback, never runs AI.

</domain>

<decisions>
## Implementation Decisions

### Review workflow UX
- Review controls overlay directly onto existing document preview (Phase 11 SectionBlock) — no separate tab or mode switch
- Review buttons (Goedkeuren / Opmerking / Afwijzen) appear automatically on any section that has verification results (VERIFICATION.md exists for the phase)
- No explicit "start review" action — controls appear as soon as CLI completes verification
- Outline tree status badge evolves: G1 (geschreven) → V1 (geverifieerd) → ✓ (goedgekeurd) / ⚠ (opmerking) / ✗ (afgewezen) — single badge, replaces previous
- After all sections reviewed, show summary (X goedgekeurd, Y opmerking, Z afgewezen) with suggested CLI command: `/doc:review-phase N` to generate REVIEW.md

### Verification display
- Per-section inline: verification status on each SectionBlock — green check (passed), amber warning (gaps), red (failed)
- Click to expand verification detail block below section content showing: cycle counter (Cyclus 1/2), truth-by-truth pass/gap status, gap descriptions
- Gap closure cycle shown as badge "Cyclus 1/2" on phase timeline and in verification panel
- If cycle 2 still has gaps: show "GEBLOKKEERD" warning
- Verification display is purely read-only — if gaps found, show CLI hint: `/doc:plan-phase N --gaps`

### Standards compliance
- Standards violations displayed inline per section, under a "Normen" heading within the verification block
- Each violation shows: standard reference badge (e.g. "ISA-88 §4.3"), what was expected, what was found
- Standard reference badges are subtle — tooltip or expand to show full requirement text on hover/click
- Not a separate tab — integrated into the per-section verification view

### Feedback capture
- Inline textarea expands below review buttons when engineer clicks "Opmerking" or "Afwijzen"
- Textarea for free-text feedback, "Opslaan" button to save
- Feedback stored in browser during review session — exported for CLI to generate REVIEW.md

### Claude's Discretion
- Feedback storage mechanism (localStorage vs React state vs backend write) — pick what fits the architecture best
- Exact layout of verification detail block (accordion, collapsible card, or inline)
- How "export for CLI" works (JSON file, clipboard copy, or backend endpoint)
- Loading/error states for verification data
- Animation/transition when review controls appear

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.0 verification patterns
- `gsd-docs-industrial/templates/verification.md` — VERIFICATION.md structure: 5-level cascade, truth table, gap descriptions, cross-reference status, metrics
- `gsd-docs-industrial/workflows/verify-phase.md` — Verification workflow: cascade logic, gap closure cycle (max 2), escalation rules

### v1.0 review patterns
- `gsd-docs-industrial/templates/review.md` — REVIEW.md structure: reviewer info, summary table, per-section feedback (Approved/Comment/Flag), severity, routing
- `gsd-docs-industrial/workflows/review-phase.md` — Review workflow: section-by-section flow, resume support, gap routing

### Phase 11 output (integration base)
- `frontend/src/features/documents/components/SectionBlock.tsx` — Section rendering component to extend with review controls
- `frontend/src/features/documents/components/DocumentsTab.tsx` — Split-pane layout to extend
- `frontend/src/features/documents/hooks/useDocumentOutline.ts` — Outline data hook (already has status field)
- `backend/app/api/documents.py` — Document API to extend with verification data
- `backend/app/api/phases.py` — Phase API, already has verification_score/gaps fields
- `backend/app/schemas/phase.py` — PhaseStatusResponse with has_verification, has_review fields

### Standards references
- `gsd-docs-industrial/references/standards/` — PackML and ISA-88 standard files used in Level 5 cascade checks

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SectionBlock.tsx` (189 lines): Renders section content with markdown — extend with review action bar and verification detail block
- `OutlineNode.tsx` (119 lines): Shows status badges (G1/G2) — replace badge logic for review status
- `useDocumentOutline()`: Already returns section status — extend backend to include verification/review status
- `useSectionContent()`: Fetches per-section content — extend or add parallel hook for verification data
- `PhaseStatusResponse`: Already has verification_score, verification_gaps, has_verification, has_review fields
- shadcn/ui: Badge, Tooltip, Collapsible, Textarea, Button — all available

### Established Patterns
- Polling: React Query with 10-30s refetch interval for live updates from filesystem
- Split-pane: Custom draggable divider (mousedown/mousemove/mouseup) — 180-480px outline width
- Content rendering: ReactMarkdown + remark-gfm for markdown, MermaidDiagram for diagrams
- Status hierarchy: reviewed > verified > written > planned > discussed > not_started
- All UI in Dutch: labels, headings, empty states, error messages

### Integration Points
- `SectionBlock.tsx`: Add review action bar (buttons + feedback textarea) below content
- `OutlineNode.tsx`: Update status badge rendering for verified/reviewed states
- `documents.py`: Add verification data to section response or new endpoint
- `phases.py`: Extend phase endpoint with parsed VERIFICATION.md data (truths table, gaps, cycle count)
- Phase timeline popover: Add cycle badge and verification summary

</code_context>

<specifics>
## Specific Ideas

- Review controls should feel natural on the existing document preview — not a mode switch
- Verification detail block similar to the preview shown: truth-by-truth checklist with pass/gap indicators
- Standards badges like "ISA-88 §4.3" as subtle pills that expand on interaction
- Export flow: review session → summary → CLI command hint (consistent with "GUI displays, CLI acts")

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-review-interface*
*Context gathered: 2026-03-21*
