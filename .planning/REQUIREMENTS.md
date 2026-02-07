# Requirements: GSD-Docs Industrial

**Defined:** 2026-02-06
**Core Value:** Engineers can go from project brief to complete, verified FDS document through a structured, AI-assisted workflow

## v1 Requirements

### Project Initialization

- [ ] **INIT-01**: `/doc:new-fds` classifies project as Type A, B, C, or D based on user responses
- [ ] **INIT-02**: `/doc:new-fds` generates appropriate ROADMAP.md based on project type (6 phases Type A, 4-5 Type B, 3-4 Type C, 2 Type D)
- [ ] **INIT-03**: `/doc:new-fds` creates PROJECT.md with project config (name, type, client, standards settings, language)
- [ ] **INIT-04**: `/doc:new-fds` creates REQUIREMENTS.md with functional requirements derived from project scope
- [ ] **INIT-05**: `/doc:new-fds` creates STATE.md initialized at Phase 1
- [ ] **INIT-06**: `/doc:new-fds` scaffolds folder structure (.planning/, output/, diagrams/, export/)
- [ ] **INIT-07**: For Type C/D projects, `/doc:new-fds` generates BASELINE.md capturing existing system as immutable reference
- [ ] **INIT-08**: Dynamic ROADMAP evolution after System Overview phase — when >5 units identified, propose expanded phase grouping (3-5 units per phase, max 7)
- [ ] **INIT-09**: User can accept, adjust, or reject proposed ROADMAP expansion

### Phase Workflow — Discuss

- [ ] **DISC-01**: `/doc:discuss-phase N` reads ROADMAP.md to identify phase goals and scope
- [ ] **DISC-02**: `/doc:discuss-phase N` identifies gray areas specific to the phase content type (equipment: capacities/tolerances/failure modes, interfaces: protocols/rates, HMI: layout/navigation, safety: risk categories)
- [ ] **DISC-03**: `/doc:discuss-phase N` presents gray areas grouped by topic with structured questions
- [ ] **DISC-04**: `/doc:discuss-phase N` captures all decisions in phase-N/CONTEXT.md
- [ ] **DISC-05**: `/doc:discuss-phase N` updates RATIONALE.md with decision rationale for each significant choice
- [ ] **DISC-06**: Items explicitly marked as "Claude's Discretion" are documented but not asked

### Phase Workflow — Plan

- [ ] **PLAN-01**: `/doc:plan-phase N` reads CONTEXT.md decisions and ROADMAP.md phase goals
- [ ] **PLAN-02**: `/doc:plan-phase N` generates one PLAN.md per section (NN-MM-PLAN.md format)
- [ ] **PLAN-03**: Each PLAN.md includes: goal, sections, context (from CONTEXT.md), standards (if enabled), verification checklist
- [ ] **PLAN-04**: `/doc:plan-phase N` assigns wave numbers for parallel execution based on dependency analysis
- [ ] **PLAN-05**: `/doc:plan-phase N` self-verifies plans before completing
- [ ] **PLAN-06**: `/doc:plan-phase N --gaps` generates targeted fix plans from VERIFICATION.md gaps

### Phase Workflow — Write

- [ ] **WRIT-01**: `/doc:write-phase N` discovers all PLANs in phase and groups by wave
- [ ] **WRIT-02**: Each writer subagent loads only: PROJECT.md + phase CONTEXT.md + its own PLAN.md + standards (if enabled)
- [ ] **WRIT-03**: Each writer produces CONTENT.md with substantive documentation (not stubs)
- [ ] **WRIT-04**: Each writer produces SUMMARY.md (max 150 words, facts only: counts, key decisions, dependencies, cross-refs)
- [ ] **WRIT-05**: Writers in the same wave execute in parallel via subagent spawning
- [ ] **WRIT-06**: STATE.md updated before and after each wave (checkpoint for recovery)
- [ ] **WRIT-07**: Edge cases and failure modes detected during writing are captured in EDGE-CASES.md
- [ ] **WRIT-08**: Cross-references created during writing are logged in CROSS-REFS.md

### Phase Workflow — Verify

- [ ] **VERF-01**: `/doc:verify-phase N` reads phase goals from ROADMAP.md and derives must-have truths
- [ ] **VERF-02**: Verification checks 5 levels: exists, substantive (not stub), complete, consistent (with CONTEXT.md), standards-compliant
- [ ] **VERF-03**: Verification produces VERIFICATION.md with pass/gap status per truth and evidence
- [ ] **VERF-04**: Cross-references checked with warn-only for targets not yet written
- [ ] **VERF-05**: PASS result offered with optional Fresh Eyes review
- [ ] **VERF-06**: GAPS_FOUND result routes to `/doc:plan-phase N --gaps`
- [ ] **VERF-07**: Verification loop terminates after max 2 gap-closure cycles, then escalates to human_needed
- [ ] **VERF-08**: After System Overview phase verify PASS, trigger ROADMAP evolution check (>5 units → propose expansion)

### Phase Workflow — Review

- [ ] **REVW-01**: `/doc:review-phase N` presents CONTENT per section for client/engineer review
- [ ] **REVW-02**: Feedback captured in phase-N/REVIEW.md
- [ ] **REVW-03**: Issues from review route to `/doc:plan-phase N --gaps`

### Content Templates

- [ ] **TMPL-01**: Equipment module template with structured tables: description, operating states (entry/exit conditions), parameters (range/unit/default), interlocks (condition/action/priority), I/O (tag/type/description)
- [ ] **TMPL-02**: State machine template with Mermaid stateDiagram-v2 + state descriptions + transition tables
- [ ] **TMPL-03**: Interface template with overview table, signal list (name/type/description/direction), protocol details (polling/timeout/error handling)
- [ ] **TMPL-04**: Templates support configurable language (Dutch/English)

### State Management & Recovery

- [ ] **STAT-01**: STATE.md tracks: current phase, current plan, operation status, completed items, decisions, blockers
- [ ] **STAT-02**: STATE.md updated before and after each operation (checkpoint for crash recovery)
- [ ] **STAT-03**: `/doc:status` reads STATE.md + ROADMAP.md and displays progress table with per-phase status
- [ ] **STAT-04**: `/doc:resume` detects incomplete operations from STATE.md and offers: resume, view status, start other operation
- [ ] **STAT-05**: Partial write detection: CONTENT.md < 200 chars, [TO BE COMPLETED] marker, or abrupt ending
- [ ] **STAT-06**: Forward-only recovery — completed work is never rolled back, only incomplete items are retried

### Standards Integration

- [ ] **STND-01**: PackML state model reference loaded only when `standards.packml.enabled: true` in PROJECT.md
- [ ] **STND-02**: ISA-88 equipment hierarchy reference loaded only when `standards.isa88.enabled: true` in PROJECT.md
- [ ] **STND-03**: When PackML enabled: exact state names enforced, transitions validated, modes checked
- [ ] **STND-04**: When ISA-88 enabled: terminology enforced (Unit, Equipment Module, Control Module), hierarchy depth validated
- [ ] **STND-05**: Standards compliance checked as verification level in `/doc:verify-phase`
- [ ] **STND-06**: Standards never pushed — disabled by default, only enabled via explicit PROJECT.md config

### Document Assembly & Versioning

- [ ] **ASBL-01**: `/doc:complete-fds` verifies all phases PASS before assembly
- [ ] **ASBL-02**: `/doc:complete-fds` concatenates all CONTENT.md files with proper section numbering
- [ ] **ASBL-03**: `/doc:complete-fds` resolves cross-references (symbolic → final section numbers)
- [ ] **ASBL-04**: `/doc:complete-fds` performs final cross-reference validation — broken refs block completion (unless --force)
- [ ] **ASBL-05**: `/doc:complete-fds` detects orphan sections (not referenced by any other section)
- [ ] **ASBL-06**: `/doc:complete-fds --force` generates with [BROKEN REF] placeholders and DRAFT suffix
- [ ] **ASBL-07**: `/doc:complete-fds` generates ENGINEER-TODO.md for diagrams exceeding Mermaid complexity limits
- [ ] **ASBL-08**: `/doc:complete-fds` archives phase files to `.planning/archive/vN.M/`
- [ ] **ASBL-09**: Version management: v0.x internal drafts, vN.0 client releases
- [ ] **ASBL-10**: `/doc:release --type client` promotes draft to client release (v0.x → v1.0)
- [ ] **ASBL-11**: `/doc:release --type internal` bumps internal version (v1.2 → v1.3)
- [ ] **ASBL-12**: FDS and SDS versioned independently; SDS references source FDS version on frontpage

### Knowledge Transfer

- [ ] **KNOW-01**: RATIONALE.md updated automatically during `/doc:discuss-phase` with decision + why + alternatives + reference
- [ ] **KNOW-02**: EDGE-CASES.md updated automatically during `/doc:write-phase` with situation + trigger + system behavior + recovery
- [ ] **KNOW-03**: Fresh Eyes review offered after `/doc:verify-phase` PASS — simulates new engineer reading documentation, flags ambiguities
- [ ] **KNOW-04**: ENGINEER-TODO.md lists diagrams too complex for Mermaid with section reference, type, description, priority

### SDS Generation

- [ ] **SDS-01**: `/doc:generate-sds` reads completed FDS and transforms to SDS structure
- [ ] **SDS-02**: Equipment modules matched against CATALOG.json typicals library
- [ ] **SDS-03**: Unmatched equipment flagged as "NEW TYPICAL NEEDED" (not hallucinated)
- [ ] **SDS-04**: TRACEABILITY.md generated linking FDS requirements to SDS implementation
- [ ] **SDS-05**: SDS has independent version number with "Based on: FDS vX.Y" on frontpage

### Export

- [ ] **EXPT-01**: `/doc:export` renders Mermaid diagrams to PNG
- [ ] **EXPT-02**: `/doc:export` converts FDS/SDS markdown to DOCX via Pandoc with huisstijl.docx template
- [ ] **EXPT-03**: Exported DOCX includes: heading styles, header with logo, footer with page numbers, table formatting
- [ ] **EXPT-04**: `--draft` flag available for work-in-progress exports
- [ ] **EXPT-05**: `--skip-diagrams` flag available when mermaid-cli not installed
- [ ] **EXPT-06**: Diagrams exceeding complexity limits → ENGINEER-TODO.md (not broken renders)

### Plugin Infrastructure

- [ ] **PLUG-01**: All commands registered as .md files in `~/.claude/commands/doc/` with proper frontmatter
- [ ] **PLUG-02**: Supporting files (references, templates) in `~/.claude/gsd-docs-industrial/`
- [ ] **PLUG-03**: Subagent definitions for doc-writer, doc-verifier, doc-planner, doc-researcher
- [ ] **PLUG-04**: @-reference pattern for context injection from templates and references
- [ ] **PLUG-05**: Configurable output language (Dutch/English) via PROJECT.md setting
- [ ] **PLUG-06**: GSD-Docs runs alongside GSD without interference (separate /doc: namespace)

## v2 Requirements

### Advanced Features (Deferred)

- **ADV-01**: Client-specific typicals library expansion (CATALOG.json grows with each project)
- **ADV-02**: Local LLM deployment (Mac Studio M3 Ultra + Llama 405B for air-gapped environments)
- **ADV-03**: Multi-project dashboard across active FDS projects
- **ADV-04**: Automated intake folder management (INTAKE-INDEX.md with client documents, drawings, meeting notes)

## Out of Scope

| Feature | Reason |
|---------|--------|
| PLC code generation | SDS describes design, not executable code; safety risk |
| P&ID / electrical diagram generation | Engineering Package items requiring CAD tools (AutoCAD, EPLAN) |
| Real-time multi-user editing | Document generation is single-user; review-phase handles collaboration |
| NL requirements extraction from meetings | Unvalidated requirements worse than missing; discuss-phase is the mechanism |
| Full-auto mode (zero human input) | Equipment specifics cannot be inferred; human-in-the-loop is the quality mechanism |
| Database-backed state management | STATE.md is human-readable, git-trackable, manually editable |
| BPM approval workflows | Document management system feature, not generation; out of scope |
| Client-specific RAG system | CATALOG.json + BASELINE.md handle reuse cleanly without vector DB infrastructure |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INIT-01 | Phase 1 | Pending |
| INIT-02 | Phase 1 | Pending |
| INIT-03 | Phase 1 | Pending |
| INIT-04 | Phase 1 | Pending |
| INIT-05 | Phase 1 | Pending |
| INIT-06 | Phase 1 | Pending |
| INIT-07 | Phase 1 | Pending |
| INIT-08 | Phase 4 | Pending |
| INIT-09 | Phase 4 | Pending |
| DISC-01 | Phase 2 | Pending |
| DISC-02 | Phase 2 | Pending |
| DISC-03 | Phase 2 | Pending |
| DISC-04 | Phase 2 | Pending |
| DISC-05 | Phase 6 | Pending |
| DISC-06 | Phase 2 | Pending |
| PLAN-01 | Phase 2 | Pending |
| PLAN-02 | Phase 2 | Pending |
| PLAN-03 | Phase 2 | Pending |
| PLAN-04 | Phase 2 | Pending |
| PLAN-05 | Phase 2 | Pending |
| PLAN-06 | Phase 3 | Pending |
| WRIT-01 | Phase 3 | Pending |
| WRIT-02 | Phase 3 | Pending |
| WRIT-03 | Phase 3 | Pending |
| WRIT-04 | Phase 3 | Pending |
| WRIT-05 | Phase 3 | Pending |
| WRIT-06 | Phase 3 | Pending |
| WRIT-07 | Phase 6 | Pending |
| WRIT-08 | Phase 3 | Pending |
| VERF-01 | Phase 3 | Pending |
| VERF-02 | Phase 3 | Pending |
| VERF-03 | Phase 3 | Pending |
| VERF-04 | Phase 3 | Pending |
| VERF-05 | Phase 6 | Pending |
| VERF-06 | Phase 3 | Pending |
| VERF-07 | Phase 3 | Pending |
| VERF-08 | Phase 4 | Pending |
| REVW-01 | Phase 6 | Pending |
| REVW-02 | Phase 6 | Pending |
| REVW-03 | Phase 6 | Pending |
| TMPL-01 | Phase 2 | Pending |
| TMPL-02 | Phase 2 | Pending |
| TMPL-03 | Phase 2 | Pending |
| TMPL-04 | Phase 2 | Pending |
| STAT-01 | Phase 4 | Pending |
| STAT-02 | Phase 4 | Pending |
| STAT-03 | Phase 4 | Pending |
| STAT-04 | Phase 4 | Pending |
| STAT-05 | Phase 4 | Pending |
| STAT-06 | Phase 4 | Pending |
| STND-01 | Phase 5 | Pending |
| STND-02 | Phase 5 | Pending |
| STND-03 | Phase 5 | Pending |
| STND-04 | Phase 5 | Pending |
| STND-05 | Phase 5 | Pending |
| STND-06 | Phase 5 | Pending |
| ASBL-01 | Phase 5 | Pending |
| ASBL-02 | Phase 5 | Pending |
| ASBL-03 | Phase 5 | Pending |
| ASBL-04 | Phase 5 | Pending |
| ASBL-05 | Phase 5 | Pending |
| ASBL-06 | Phase 5 | Pending |
| ASBL-07 | Phase 5 | Pending |
| ASBL-08 | Phase 5 | Pending |
| ASBL-09 | Phase 5 | Pending |
| ASBL-10 | Phase 5 | Pending |
| ASBL-11 | Phase 5 | Pending |
| ASBL-12 | Phase 5 | Pending |
| KNOW-01 | Phase 6 | Pending |
| KNOW-02 | Phase 6 | Pending |
| KNOW-03 | Phase 6 | Pending |
| KNOW-04 | Phase 5 | Pending |
| SDS-01 | Phase 7 | Pending |
| SDS-02 | Phase 7 | Pending |
| SDS-03 | Phase 7 | Pending |
| SDS-04 | Phase 7 | Pending |
| SDS-05 | Phase 7 | Pending |
| EXPT-01 | Phase 7 | Pending |
| EXPT-02 | Phase 7 | Pending |
| EXPT-03 | Phase 7 | Pending |
| EXPT-04 | Phase 7 | Pending |
| EXPT-05 | Phase 7 | Pending |
| EXPT-06 | Phase 7 | Pending |
| PLUG-01 | Phase 1 | Pending |
| PLUG-02 | Phase 1 | Pending |
| PLUG-03 | Phase 3 | Pending |
| PLUG-04 | Phase 1 | Pending |
| PLUG-05 | Phase 1 | Pending |
| PLUG-06 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 89 total
- Mapped to phases: 89
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-06*
*Last updated: 2026-02-06 after initial definition*
