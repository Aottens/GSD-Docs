# Roadmap: GSD-Docs Industrial

**Created:** 2026-02-06
**Depth:** Comprehensive
**Phases:** 7
**Requirements:** 89 mapped / 89 total

## Overview

GSD-Docs Industrial is a Claude Code plugin that adapts the GSD workflow for writing industrial FDS/SDS documents. The build decomposes into 7 phases following the natural dependency chain: foundation scaffolding enables discuss/plan, which feeds write/verify (the core value loop), robustness features make it production-ready, standards and assembly complete the FDS pipeline, knowledge transfer and review add engineering quality, and SDS generation + export deliver the final client artifacts.

Phases 1-3 are the minimum viable pipeline. After Phase 3, an engineer can run the full discuss-plan-write-verify cycle and produce verified FDS sections. Everything after Phase 3 makes it better; Phases 1-3 make it work.

---

## Phase 1: Framework Foundation + /doc:new-fds

**Goal:** Engineer can create a new FDS project, classify it by type, and receive a scaffolded workspace with all planning artifacts ready for the discuss-plan-write-verify cycle.

**Dependencies:** None (entry point)

**Requirements:** INIT-01, INIT-02, INIT-03, INIT-04, INIT-05, INIT-06, INIT-07, PLUG-01, PLUG-02, PLUG-04, PLUG-05, PLUG-06

**Plans:** 4 plans

Plans:
- [x] 01-01-PLAN.md -- Plugin directory structure + CLAUDE-CONTEXT.md + shared references
- [x] 01-02-PLAN.md -- ROADMAP templates (4 types) + planning artifact templates
- [x] 01-03-PLAN.md -- /doc:new-fds command + workflow (core deliverable)
- [x] 01-04-PLAN.md -- End-to-end verification checkpoint

**Success Criteria:**

1. Engineer runs `/doc:new-fds`, answers classification questions, and sees the project correctly classified as Type A, B, C, or D with the corresponding ROADMAP template generated (6 phases for Type A, 4-5 for B, 3-4 for C, 2 for D)
2. After `/doc:new-fds` completes, the `.planning/` directory contains PROJECT.md (with project config, standards settings, language), REQUIREMENTS.md, ROADMAP.md, and STATE.md -- all populated with project-specific content, not empty stubs
3. For a Type C or D project, BASELINE.md is generated alongside the other artifacts, capturing the existing system as an immutable reference with clear scope boundaries (what changes vs. what does not)
4. All command files are registered as `.md` files in `~/.claude/commands/doc/` with proper frontmatter, the supporting file structure exists in `~/.claude/gsd-docs-industrial/`, and running any `/doc:*` command does not interfere with existing `/gsd:*` commands
5. Engineer can set output language (Dutch or English) during project creation, and the setting persists in PROJECT.md for downstream commands

**Pitfalls to mitigate:**
- Pitfall 5 (template explosion): Establish template composition pattern here -- base templates with type-specific overrides, not 4x copy-paste
- Pitfall 4 (STATE.md corruption): Establish SUMMARY.md = completion proof pattern from the start

---

## Phase 2: Discuss + Plan Commands

**Goal:** Engineer can front-load decisions for a phase through structured gray area identification, and generate section plans with wave assignments ready for parallel writing.

**Dependencies:** Phase 1 (ROADMAP.md, PROJECT.md, folder structure must exist)

**Requirements:** DISC-01, DISC-02, DISC-03, DISC-04, DISC-06, PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05, TMPL-01, TMPL-02, TMPL-03, TMPL-04

**Plans:** 4 plans

Plans:
- [x] 02-01-PLAN.md -- FDS section templates (equipment module, state machine, interface) + CONTEXT.md template
- [x] 02-02-PLAN.md -- /doc:discuss-phase command + workflow
- [x] 02-03-PLAN.md -- /doc:plan-phase command + workflow
- [x] 02-04-PLAN.md -- End-to-end verification checkpoint

**Success Criteria:**

1. Engineer runs `/doc:discuss-phase N` and receives gray area questions grouped by topic and specific to the phase content type (equipment: capacities/tolerances/failure modes, interfaces: protocols/rates, HMI: layout/navigation, safety: risk categories) -- items marked "Claude's Discretion" are documented but not asked
2. After completing discussion, phase-N/CONTEXT.md contains all captured decisions in a structured format that downstream plan and write commands can consume without re-asking the engineer
3. Engineer runs `/doc:plan-phase N` and receives one PLAN.md per section (NN-MM-PLAN.md format), each containing goal, sections, context from CONTEXT.md, standards references (if enabled), and a verification checklist
4. Plans have wave assignments based on dependency analysis, and the engineer can see which sections will execute in parallel vs. sequentially
5. FDS section templates (equipment module with states/parameters/interlocks/I/O tables, state machine with Mermaid stateDiagram-v2 + transition tables, interface with signal lists + protocol details) produce structured output in the configured language (Dutch/English)

**Pitfalls to mitigate:**
- Pitfall 7 (CONTEXT.md overload): Enforce size limits and priority tiers so writer subagents get focused context

---

## Phase 3: Write + Verify (Core Value)

**Goal:** Engineer can generate substantive FDS content through parallel writing with fresh context per section, verify it against phase goals (not just task completion), and close gaps through a self-correcting loop.

**Dependencies:** Phase 2 (PLAN.md files and CONTEXT.md must exist)

**Requirements:** PLAN-06, WRIT-01, WRIT-02, WRIT-03, WRIT-04, WRIT-05, WRIT-06, WRIT-08, VERF-01, VERF-02, VERF-03, VERF-04, VERF-06, VERF-07, PLUG-03

**Plans:** 5 plans

Plans:
- [ ] 03-01-PLAN.md -- Subagent definitions (doc-writer, doc-verifier) + output templates (SUMMARY, VERIFICATION, CROSS-REFS)
- [ ] 03-02-PLAN.md -- /doc:write-phase command + workflow (parallel writing with context isolation)
- [ ] 03-03-PLAN.md -- /doc:verify-phase command + workflow (5-level goal-backward verification)
- [ ] 03-04-PLAN.md -- Gap closure enhancement (plan-phase --gaps VERIFICATION.md parsing) + ENGINEER-TODO template
- [ ] 03-05-PLAN.md -- End-to-end verification checkpoint

**Success Criteria:**

1. Engineer runs `/doc:write-phase N` and each section is written by a subagent that loads ONLY PROJECT.md + phase CONTEXT.md + its own PLAN.md + standards (if enabled) -- no cross-contamination from other sections' content
2. Each completed section produces both a CONTENT.md (substantive documentation with structured tables, not stubs) and a SUMMARY.md (max 150 words, facts only: counts, key decisions, dependencies, cross-references), with writers in the same wave executing in parallel
3. Engineer runs `/doc:verify-phase N` and receives a VERIFICATION.md showing pass/gap status for each must-have truth, checked at 5 levels (exists, substantive, complete, consistent with CONTEXT.md, standards-compliant), with cross-references warn-only for targets not yet written
4. When gaps are found, engineer runs `/doc:plan-phase N --gaps` to generate targeted fix plans from VERIFICATION.md, then `/doc:write-phase N` to execute fixes, then `/doc:verify-phase N` to re-verify -- and this loop terminates after max 2 cycles, escalating to human_needed if gaps persist
5. STATE.md is updated before and after each wave (checkpoint), and cross-references created during writing are logged in CROSS-REFS.md

**Pitfalls to mitigate:**
- Pitfall 1 (context cross-contamination): Strict context loading rules -- orchestrator never reads other plans' CONTENT.md before spawning writers
- Pitfall 2 (infinite verification loops): Max 2 gap-closure cycles + scoped re-verification (check only targeted gaps)
- Pitfall 9 (SUMMARY.md quality): Mandatory structure + validation

---

## Phase 4: State Management + Recovery + Dynamic ROADMAP

**Goal:** Engineer can resume work after any interruption without losing progress, track project status across sessions, and have the ROADMAP adapt to project complexity discovered during writing.

**Dependencies:** Phase 3 (write/verify infrastructure must exist for recovery to have something to recover)

**Requirements:** INIT-08, INIT-09, VERF-08, STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, STAT-06

**Plans:** 5 plans

Plans:
- [ ] 04-01-PLAN.md -- STATE.md checkpoint enhancement + partial write detection (foundation)
- [ ] 04-02-PLAN.md -- /doc:status command + workflow (progress display + next action)
- [ ] 04-03-PLAN.md -- /doc:resume command + workflow + auto-detect in write-phase/verify-phase
- [ ] 04-04-PLAN.md -- /doc:expand-roadmap command + workflow + verify-phase auto-trigger
- [ ] 04-05-PLAN.md -- End-to-end verification checkpoint

**Success Criteria:**

1. Engineer runs `/doc:status` and sees a progress table showing per-phase status (pending, active, verified), current position (phase, plan, operation), and overall completion percentage -- derived from STATE.md + ROADMAP.md + actual file system state
2. After a crash or session break during `/doc:write-phase`, engineer runs `/doc:resume` and is offered options to resume (picking up at the incomplete wave), view status, or start a different operation -- with completed work preserved and only incomplete items retried (forward-only recovery)
3. Partial writes are detected automatically (CONTENT.md < 200 chars, "[TO BE COMPLETED]" marker, or abrupt ending) and flagged for retry, while completed writes (with matching SUMMARY.md) are never re-executed
4. After System Overview phase verification passes and >5 units are identified, the system proposes a ROADMAP expansion with units grouped into manageable phases (3-5 units each, max 7), and the engineer can accept, adjust, or reject the proposed expansion
5. STATE.md tracks current operation details (command, phase, wave, plans done/pending, started timestamp, status) with checkpoints before and after each operation, providing reliable crash recovery across sessions

**Pitfalls to mitigate:**
- Pitfall 4 (STATE.md corruption): SUMMARY.md existence is the ONLY completion proof, not STATE.md
- Pitfall 6 (ROADMAP evolution): Use directory names not just numbers; migrate artifacts when phases renumber

---

## Phase 5: Complete-FDS + Standards + Assembly

**Goal:** Engineer can assemble all verified phases into a single FDS document with proper section numbering, validated cross-references, and opt-in standards compliance, and manage document versions for internal and client releases.

**Dependencies:** Phase 3 (verified content must exist), Phase 4 (STATE.md tracking must work for assembly progress)

**Requirements:** STND-01, STND-02, STND-03, STND-04, STND-05, STND-06, ASBL-01, ASBL-02, ASBL-03, ASBL-04, ASBL-05, ASBL-06, ASBL-07, ASBL-08, ASBL-09, ASBL-10, ASBL-11, ASBL-12, KNOW-04

**Success Criteria:**

1. Engineer runs `/doc:complete-fds` and all phases are verified as PASS before assembly proceeds; the output is a single FDS document with proper section numbering, symbolic cross-references resolved to final section numbers, and phase files archived to `.planning/archive/vN.M/`
2. Cross-reference validation at assembly time catches broken references (blocking completion unless `--force` is used, which generates with [BROKEN REF] placeholders and DRAFT suffix) and detects orphan sections not referenced by any other section
3. When PackML is enabled in PROJECT.md, exact state names are enforced and transitions are validated; when ISA-88 is enabled, terminology and hierarchy depth are enforced -- and these checks run as a verification level, never pushed on projects that have not enabled them
4. Engineer can run `/doc:release --type client` to promote a draft to a client release (v0.x to v1.0) or `/doc:release --type internal` to bump internal version, with FDS and SDS versioned independently and the SDS always referencing its source FDS version
5. ENGINEER-TODO.md is generated listing diagrams that exceed Mermaid complexity limits, with section reference, diagram type, description, and priority -- so the engineer knows exactly what needs manual creation

**Pitfalls to mitigate:**
- Pitfall 3 (section numbering collapse): Symbolic references during writing, numbering applied only at complete-fds time
- Pitfall 8 (standards terminology drift): Composable standards modules, terminology enforcement, verification checks against reference lists

---

## Phase 6: Knowledge Transfer + Review

**Goal:** Engineer can capture and retrieve the "why" behind decisions, edge cases discovered during writing, and get a fresh perspective on completed documentation through structured review.

**Dependencies:** Phase 2 (discuss-phase exists for RATIONALE.md integration), Phase 3 (write-phase exists for EDGE-CASES.md integration, verify-phase exists for Fresh Eyes trigger)

**Requirements:** DISC-05, WRIT-07, VERF-05, REVW-01, REVW-02, REVW-03, KNOW-01, KNOW-02, KNOW-03

**Success Criteria:**

1. During `/doc:discuss-phase`, each significant decision automatically updates RATIONALE.md with the decision, reasoning, alternatives considered, and section reference -- so a new engineer can understand not just "what" but "why"
2. During `/doc:write-phase`, edge cases and failure modes detected by the writer are automatically captured in EDGE-CASES.md with situation, trigger, system behavior, and recovery steps
3. After `/doc:verify-phase` returns PASS, a Fresh Eyes review is offered that simulates a new engineer reading the documentation for the first time, flagging ambiguities, undefined terms, and missing context
4. Engineer can run `/doc:review-phase N` to present completed content section-by-section for client or engineer review, with feedback captured in REVIEW.md and issues routed to `/doc:plan-phase N --gaps` for resolution

**Pitfalls to mitigate:**
- Knowledge transfer documents accumulate incrementally (RATIONALE during discuss, EDGE-CASES during write) rather than being generated all at once at the end

---

## Phase 7: SDS Generation + DOCX Export + Pilot

**Goal:** Engineer can transform a completed FDS into an SDS with typicals matching, export both to client-ready DOCX with corporate styling, and validate the full pipeline on a real project.

**Dependencies:** Phase 5 (complete FDS must exist for SDS transformation and export)

**Requirements:** SDS-01, SDS-02, SDS-03, SDS-04, SDS-05, EXPT-01, EXPT-02, EXPT-03, EXPT-04, EXPT-05, EXPT-06

**Success Criteria:**

1. Engineer runs `/doc:generate-sds` on a completed FDS and receives an SDS document where equipment modules are matched against CATALOG.json typicals -- matched modules get SDS content derived from the typical, unmatched modules are flagged as "NEW TYPICAL NEEDED" (never hallucinated)
2. TRACEABILITY.md is generated linking every FDS functional requirement to its SDS implementation section, and the SDS carries an independent version number with "Based on: FDS vX.Y" on its frontpage
3. Engineer runs `/doc:export` and receives a DOCX file with corporate styling from huisstijl.docx (heading styles, header with logo, footer with page numbers, table formatting), with Mermaid diagrams rendered to PNG and embedded
4. Export supports `--draft` flag for work-in-progress exports and `--skip-diagrams` flag when mermaid-cli is not installed; diagrams exceeding complexity limits are routed to ENGINEER-TODO.md instead of producing broken renders
5. The full pipeline (new-fds through export) can be run on a real project, producing a complete FDS and SDS that an industrial automation engineer would recognize as professional documentation

**Pitfalls to mitigate:**
- Pitfall 10 (export fragility): Pin Pandoc version, test with reference document, complexity budget per diagram
- Pitfall 13 (typicals catalog staleness): Version tracking per typical in CATALOG.json

---

## Progress

| Phase | Name | Requirements | Status |
|-------|------|:------------:|--------|
| 1 | Framework Foundation + /doc:new-fds | 12 | Complete |
| 2 | Discuss + Plan Commands | 14 | Complete |
| 3 | Write + Verify (Core Value) | 15 | Planned |
| 4 | State Management + Recovery + Dynamic ROADMAP | 9 | Planned |
| 5 | Complete-FDS + Standards + Assembly | 19 | Pending |
| 6 | Knowledge Transfer + Review | 9 | Pending |
| 7 | SDS Generation + DOCX Export + Pilot | 11 | Pending |
| **Total** | | **89** | |

---
*Roadmap created: 2026-02-06*
*Last updated: 2026-02-13 -- Phase 4 planned (5 plans in 4 waves)*
