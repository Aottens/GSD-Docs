# Phase 3: Write + Verify (Core Value) - Context

**Gathered:** 2026-02-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Commands that generate substantive FDS section content through parallel writing with fresh context per section, verify content against phase goals at 5 levels, and close gaps through a self-correcting loop (max 2 cycles). After this phase, an engineer can run the full discuss-plan-write-verify cycle and produce verified FDS sections. Creating the complete assembled FDS document, standards enforcement, and state management are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Content depth & completeness
- Best-effort with markers: writers infer reasonable values from CONTEXT.md but mark inferred content with [VERIFY] so engineer can confirm — never silently guess
- I/O tables: generate complete rows with industry-typical signal ranges (e.g., 4-20mA, 0-100%), mark inferred values with [VERIFY]
- State machines: high-level overview first (Mermaid stateDiagram-v2 + summary transition table), flag complex transitions as [DETAIL NEEDED] for engineer review
- Quality bar: all required template sections (5 for equipment modules) must have real content — optional sections can be empty if not relevant to the equipment
- [VERIFY] markers are acceptable in required sections; empty required sections are not

### Verification feedback
- VERIFICATION.md format: summary pass/gap table at top for quick scan, detailed findings per section below
- Gap descriptions only — describe what's missing or wrong, don't suggest fixes (leave fix approach to plan-phase --gaps)
- All 5 verification levels always run: exists, substantive, complete, consistent with CONTEXT.md, standards-compliant
- Cross-references to unwritten sections in verification: Claude's discretion on whether to warn or flag as deferred gap, with reasoning documented in VERIFICATION.md

### Gap closure autonomy
- Gap closure trigger: Claude decides whether to auto-fix or ask based on gap severity (Claude's discretion)
- Escalation after max 2 cycles: remaining gaps added to ENGINEER-TODO.md AND phase completion blocked — gaps are both tracked and blocking
- Re-verification scope: Claude decides based on whether fixes touched cross-references (full phase) or isolated content (fixed sections only)
- Gap preview: before generating fix plans, show engineer the list of gaps that will be addressed and let them confirm

### Cross-reference handling
- Reference format in CONTENT.md: Claude's discretion — picks format that works best for downstream assembly resolution
- Reference creation: Claude's discretion — decides based on how obvious the relationship is between sections
- CROSS-REFS.md captures full context per reference: source section, target section, status (resolved/pending), context sentence, and reference type (depends-on, related-to, see-also)
- Undocumented equipment references: Claude's discretion based on available info from CONTEXT.md about the target

### Claude's Discretion
- Cross-reference format (symbolic tags vs descriptive placeholders) — choose what works best for assembly
- Whether to proactively create cross-references beyond what PLAN.md specifies — based on obviousness of relationship
- Verification treatment of references to unwritten sections (warn vs deferred gap) — document reasoning
- Gap closure: auto-fix vs ask engineer — based on gap severity
- Re-verification scope after fixes — based on whether fixes affect cross-references
- How much to capture about undocumented referenced equipment — based on available info

</decisions>

<specifics>
## Specific Ideas

- Writers load ONLY PROJECT.md + phase CONTEXT.md + own PLAN.md + standards (if enabled) — strict isolation, no cross-contamination from other sections' content
- Each section produces both CONTENT.md (substantive) and SUMMARY.md (max 150 words, facts only: counts, key decisions, dependencies, cross-references)
- Writers in the same wave execute in parallel
- The gap closure loop is: verify → preview gaps → engineer confirms → plan-phase --gaps → write-phase → re-verify (max 2 cycles)
- STATE.md checkpoint before and after each wave

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-write-verify-core-value*
*Context gathered: 2026-02-10*
