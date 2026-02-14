# Phase 6: Knowledge Transfer + Review - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Enhance the existing pipeline (discuss-phase, write-phase, verify-phase) with knowledge capture artifacts (RATIONALE.md, EDGE-CASES.md), add a configurable Fresh Eyes review after verification, and introduce /doc:review-phase for structured section-by-section engineer review with feedback capture. The goal is that FDS documentation preserves the "why" behind decisions, captures edge cases discovered during writing, and survives engineer turnover.

</domain>

<decisions>
## Implementation Decisions

### Rationale capture
- Every decision from discuss-phase is logged — completeness over curation
- Full context per entry: decision, reasoning, alternatives considered, and what was ruled out (4-6 sentences)
- Single project-wide RATIONALE.md in .planning/ (not per phase)
- Entries organized by FDS section — a new engineer can find all decisions about a specific section in one place
- discuss-phase workflow updates RATIONALE.md automatically after each discussion area completes

### Edge case documentation
- Capture everything notable — failure modes, unusual sequences, boundary conditions, and minor quirks
- Entry format: situation, system behavior, recovery steps, AND design reason (why the system behaves this way)
- Per-phase EDGE-CASES.md in the phase directory — edge cases stay close to the content that surfaced them
- 3 severity levels: CRITICAL (safety/equipment), WARNING (operational impact), INFO (notable quirk)
- After write-phase completes, show summary: "N edge cases captured in EDGE-CASES.md"
- Edge cases referencing equipment from other phases add entries to CROSS-REFS.md automatically

### Fresh Eyes review
- Checks both comprehension gaps (undefined terms, assumed knowledge) AND completeness gaps (missing context, logical jumps)
- Three perspectives via --perspective flag: engineer (technical clarity), customer (jargon/scope/commitments), operator (procedures/recovery/daily use)
- Offered after verify-phase PASS — engineer can accept or skip
- Output goes to standalone FRESH-EYES.md per phase — distinct from formal verification
- Customer perspective is strict on jargon — flag all internal jargon, unexplained abbreviations, overly technical language
- Operator perspective checks both procedural clarity AND operational completeness (states, alarms, sequences)
- 3 severity levels: MUST-FIX (genuinely confusing), SHOULD-FIX (improvement), CONSIDER (nice-to-have)
- Separate sections per perspective in FRESH-EYES.md (Engineer / Customer / Operator)
- Default informational only — --actionable flag routes findings to gap closure pipeline (plan-phase --gaps)

### Review workflow (/doc:review-phase)
- Primary audience: engineer handover — present for a colleague taking over the project
- Interactive section-by-section flow — show one section at a time, collect feedback, then next
- Each section presentation includes: content, SUMMARY.md key facts, and cross-references
- Per-section status: Approved (no issues), Comment (minor note), Flag (needs revision)
- Feedback captured in REVIEW.md per phase — structured with section, finding, severity, suggested action
- Resolution configurable: default manual, --route-gaps flag sends findings to gap closure pipeline

### Claude's Discretion
- Severity classification calibration for Fresh Eyes (stricter for safety-critical sections, lighter for overview)
- How to present sections during review (formatting, context level)
- RATIONALE.md entry boundaries (when one discussion answer produces multiple entries vs. one)
- Gap closure integration details when --actionable or --route-gaps flags are used

</decisions>

<specifics>
## Specific Ideas

- RATIONALE.md serves as the "design decisions log" — a new engineer should be able to read it and understand not just "what" but "why" for every FDS section
- Edge cases with CRITICAL severity should stand out visually (not just a label) so they're impossible to miss
- Fresh Eyes customer perspective simulates a customer reading the FDS for the first time and flagging anything that would make them ask "what does this mean?"
- Operator perspective simulates someone who runs the system daily and needs to follow procedures during normal operation and fault recovery

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-knowledge-transfer-review*
*Context gathered: 2026-02-14*
