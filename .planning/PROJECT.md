# GSD-Docs Industrial

## What This Is

A Claude Code plugin that adapts the GSD (Get Shit Done) workflow for writing industrial FDS (Functional Design Specification) and SDS (Software Design Specification) documents. Same architecture as GSD — frontmatter-driven Markdown commands, subagent delegation, wave-based parallelization — but producing technical documentation instead of code. Commands live under `/doc:*` and run alongside GSD without interference.

## Core Value

Engineers can go from project brief to complete, verified FDS document through a structured, AI-assisted workflow that maintains fresh context per section, verifies goals (not just task completion), and catches gaps before delivery.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] `/doc:new-fds` — classify project (Type A/B/C/D), generate ROADMAP.md, PROJECT.md, REQUIREMENTS.md, STATE.md
- [ ] `/doc:discuss-phase N` — identify gray areas for a phase, capture decisions in CONTEXT.md
- [ ] `/doc:plan-phase N` — generate section PLANs with wave assignments and verification criteria
- [ ] `/doc:write-phase N` — parallel-write CONTENT.md + SUMMARY.md per plan with fresh context
- [ ] `/doc:verify-phase N` — goal-backward verification, gap detection, VERIFICATION.md
- [ ] `/doc:review-phase N` — optional client/engineer review, REVIEW.md
- [ ] `/doc:complete-fds` — merge all phases into final FDS document, cross-ref validation
- [ ] `/doc:generate-sds` — transform FDS to SDS with typicals matching
- [ ] `/doc:export` — DOCX export with corporate styling (Pandoc + huisstijl.docx)
- [ ] `/doc:status` — project progress overview from STATE.md + ROADMAP.md
- [ ] `/doc:resume` — recover from interrupts, detect incomplete operations
- [ ] `/doc:release` — version management (internal drafts → client releases)
- [ ] 4 project types with distinct ROADMAP templates (A: new+standards, B: new flex, C: mod large, D: mod small/TWN)
- [ ] Dynamic ROADMAP evolution after System Overview phase (>5 units → expand into grouped phases)
- [ ] Gap closure loop: verify → plan --gaps → write → re-verify
- [ ] STATE.md checkpoint system with crash recovery (forward-only strategy)
- [ ] Cross-reference registry (CROSS-REFS.md) with strict validation at complete-fds
- [ ] Knowledge transfer: RATIONALE.md (at discuss), EDGE-CASES.md (at write), Fresh Eyes (at verify)
- [ ] SUMMARY.md per section — compact AI-readable summaries (max 150 words, facts only)
- [ ] Standards integration as opt-in (PackML, ISA-88) — never pushed, loaded only when enabled
- [ ] Typicals library (CATALOG.json) for SDS generation matching
- [ ] Configurable output language (Dutch/English) via config setting
- [ ] BASELINE.md for modification projects (Type C/D) — existing system as given, describe only delta
- [ ] ENGINEER-TODO.md generated at complete-fds for diagrams too complex for Mermaid
- [ ] Mermaid diagram support (state, flowchart, sequence) with fallback for complex diagrams
- [ ] FDS section templates (equipment module, state machine, interface) with structured tables
- [ ] Versioning: v0.x internal drafts, vN.0 client releases, FDS and SDS versioned independently

### Out of Scope

- Modifying GSD itself — GSD-Docs is a standalone plugin that follows GSD's patterns
- P&ID / electrical diagram generation — these are external Engineering Package items, referenced as attachments
- Real PLC code generation — SDS describes software design, doesn't produce executable code
- Local LLM deployment (Mac Studio / Llama 405B) — Phase 2 future consideration, not part of this build
- Pandoc/mermaid-cli installation — assumed as system dependencies, documented but not automated

## Context

- **Architecture model:** Identical to GSD — commands as frontmatter-driven .md files in `~/.claude/commands/doc/`, supporting files (references, templates) in `~/.claude/gsd-docs-industrial/`
- **Specification:** SPECIFICATION.md v2.7.0 is the SSOT for all behavior, covering workflow, project types, commands, folder structure, standards, export, knowledge transfer, error recovery, and versioning
- **CLAUDE-CONTEXT.md:** Condensed version of the specification for quick Claude context loading
- **GSD reference implementation:** GSD v1.6.4 at `~/.claude/get-shit-done/` — 24 commands in `~/.claude/commands/gsd/`, frontmatter-driven with subagent spawning, wave parallelization, and @-reference context injection
- **Domain:** Industrial automation documentation — FDS/SDS documents describe functional behavior of machinery/production lines for PLC/SCADA programming
- **Users:** Industrial automation engineers writing documentation for client projects, ranging from small modifications (Type D, ~30 min) to large new installations (Type A, 100+ motors)

## Constraints

- **Plugin architecture**: Must follow GSD's command registration pattern (frontmatter .md files in `~/.claude/commands/doc/`) — this is how Claude Code discovers and executes custom commands
- **Context management**: Fresh context per write task (only PROJECT.md + CONTEXT.md + current PLAN.md + standards) — no cross-contamination between sections
- **Subagent pattern**: Heavy operations (writing, verification) delegated to subagents to protect main context window
- **Specification compliance**: SPECIFICATION.md v2.7.0 is the SSOT — all behavior must match the spec
- **Standards opt-in**: PackML/ISA-88 content loaded conditionally based on PROJECT.md config — never hardcoded

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Standalone plugin, not GSD fork | GSD-Docs has fundamentally different output (docs vs code); forking would create maintenance burden | — Pending |
| Commands under `/doc:*` prefix | Clear namespace separation from GSD's `/gsd:*` commands | — Pending |
| Defer standards content to later milestone | Core workflow is independent of PackML/ISA-88 content; focus on command structure first | — Pending |
| Configurable language (Dutch/English) | Framework supports international use; Dutch is primary but not hardcoded | — Pending |
| 7 milestones matching spec §11 roadmap | Natural decomposition; each milestone delivers testable capability | — Pending |
| Forward-only error recovery | Simpler than rollback; idempotent resume is safer for document generation | — Pending |

---
*Last updated: 2026-02-06 after initialization*
