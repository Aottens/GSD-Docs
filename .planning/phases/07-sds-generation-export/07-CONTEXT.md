# Phase 7: SDS Generation + DOCX Export + Pilot - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Transform a completed FDS into an SDS with typicals matching, export both FDS and SDS to client-ready DOCX with corporate styling, and validate the full pipeline on a test project. The SDS gets its own discuss-plan-write-verify cycle (not a single-pass transform). Typicals are TIA Portal function blocks at control module level, loaded from a project-specific library.

</domain>

<decisions>
## Implementation Decisions

### Typicals catalog & matching
- Library is **project-specific**, not a global catalog — different projects may use different libraries (own or customer's)
- Two loading modes required: (1) path reference in PROJECT.md pointing to an external library, (2) import/copy into project's references/ folder for self-containment
- Typicals are at **control module level** — building blocks like FB_AnalogIn, FB_ValveCtrl, FB_MotorCtrl
- MVP scope: **TIA Portal library only** — other platforms (Omron, Allen-Bradley) are future work
- Matching method: **suggest + confirm** — system proposes typical matches based on equipment type/function, engineer confirms or overrides
- Unmatched equipment modules: generate **skeleton SDS section from FDS** (I/O, parameters, states) marked as "NEW TYPICAL NEEDED" — not a stub, but a structured starting point

### SDS content derivation
- SDS follows a **hybrid structure**: equipment modules as primary sections, software structure (FB hierarchy, instantiation, data flow) within each
- NOTE: SDS structure may be revisited — this is a preliminary decision, not fully locked
- SDS focus is on **software structure** — which FBs compose each equipment module, how the program is organized — not on documenting typical internals
- Content depth is **both prescriptive and specification**: some sections prescribe structure and FB selection, others specify behavior and timing
- When referencing typicals: **summary + reference** — brief description of purpose and key interfaces, with library reference for full details
- TRACEABILITY.md is an **internal quality check** — not part of client deliverables
- SDS uses **same language** as FDS (inherited from PROJECT.md)
- SDS gets its **own discuss-plan-write-verify cycle** — /doc:generate-sds scaffolds the SDS project (like /doc:new-fds does for FDS), then engineer runs the full workflow per SDS phase
- SDS generates a **complete document**, not a skeleton — engineer reviews and adjusts

### DOCX export & styling
- One corporate **huisstijl.docx template exists** — used for all projects (not per-client)
- Export must include **table of contents, list of figures, and list of tables** — auto-generated, standard for formal engineering documents
- External diagrams: **both embed and reference supported** — if PNG exists in diagrams/external/, embed it; if not, show text reference. Engineer's choice.
- Conversion tool and diagram rendering approach: Claude's discretion

### Pilot project scope
- Pilot uses a **fictional but realistic test project** — not a real client project
- Project type: **Type B (Nieuwbouw Flex)** — realistic scope without standards overhead
- Pilot must exercise **full pipeline**: FDS + SDS + DOCX export (new-fds through export)
- Success bar: **client-ready quality** — output should be close to what you'd actually send to a client, minimal manual cleanup needed

### Claude's Discretion
- SDS project separation (same .planning/ folder vs separate subfolder)
- SDS-specific templates (new vs adapted from FDS)
- Conversion tool choice (Pandoc or alternative)
- Mermaid rendering approach
- Test project content (fictional but representative Type B industrial scenario)

</decisions>

<specifics>
## Specific Ideas

- "A typical is a building block in software — a piece of software in TIA Portal that handles an analog input, or a digital input"
- "The typicals are most of the time control module level, so we advise on what typicals to use where, furthermore the structure of the software is the most important. Not specifically what typicals."
- "Sometimes we need to use a library from a customer" — library flexibility is essential
- SDS structure decision is preliminary — engineer wants flexibility to revisit after seeing first results

</specifics>

<deferred>
## Deferred Ideas

- Multi-platform typical libraries (Omron, Allen-Bradley) — future milestone
- Per-client huisstijl templates — future enhancement
- SDS structure refinement — may need iteration after MVP experience

</deferred>

---

*Phase: 07-sds-generation-export*
*Context gathered: 2026-02-14*
