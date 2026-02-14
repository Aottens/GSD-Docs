# GSD-Docs Industrial

## What This Is

A Claude Code plugin that adapts the GSD (Get Shit Done) workflow for writing industrial FDS (Functional Design Specification) and SDS (Software Design Specification) documents. 14 commands under `/doc:*` cover the full lifecycle: project creation, structured discussion, section planning, parallel writing with context isolation, goal-backward verification, FDS assembly, SDS generation with typicals matching, and DOCX export with corporate styling. Runs alongside GSD without interference.

## Core Value

Engineers can go from project brief to complete, verified FDS document through a structured, AI-assisted workflow that maintains fresh context per section, verifies goals (not just task completion), and catches gaps before delivery.

## Requirements

### Validated

- ✓ `/doc:new-fds` -- classify project (Type A/B/C/D), generate all planning artifacts -- v1.0
- ✓ `/doc:discuss-phase N` -- identify gray areas, capture decisions in CONTEXT.md -- v1.0
- ✓ `/doc:plan-phase N` -- generate section PLANs with wave assignments -- v1.0
- ✓ `/doc:write-phase N` -- parallel-write CONTENT.md + SUMMARY.md with context isolation -- v1.0
- ✓ `/doc:verify-phase N` -- goal-backward 5-level verification with gap detection -- v1.0
- ✓ `/doc:review-phase N` -- client/engineer review with feedback capture -- v1.0
- ✓ `/doc:complete-fds` -- FDS assembly with cross-ref resolution and versioning -- v1.0
- ✓ `/doc:generate-sds` -- SDS scaffolding with typicals matching -- v1.0
- ✓ `/doc:export` -- DOCX export with Pandoc + Mermaid rendering -- v1.0
- ✓ `/doc:status` -- project progress overview from STATE.md + ROADMAP.md -- v1.0
- ✓ `/doc:resume` -- crash recovery with forward-only strategy -- v1.0
- ✓ `/doc:release` -- version management (internal/client) -- v1.0
- ✓ `/doc:expand-roadmap` -- dynamic ROADMAP evolution when >5 units discovered -- v1.0
- ✓ `/doc:check-standards` -- opt-in PackML/ISA-88 compliance checking -- v1.0
- ✓ 4 project types with distinct ROADMAP templates (A/B/C/D) -- v1.0
- ✓ Gap closure loop: verify -> plan --gaps -> write -> re-verify (max 2 cycles) -- v1.0
- ✓ Knowledge transfer: RATIONALE.md, EDGE-CASES.md, Fresh Eyes review -- v1.0
- ✓ FDS section templates (equipment module, state machine, interface) -- v1.0
- ✓ Bilingual Dutch/English output -- v1.0
- ✓ BASELINE.md for modification projects (Type C/D) -- v1.0
- ✓ Typicals library (CATALOG.json) for SDS matching -- v1.0

### Active

(None -- next milestone requirements TBD via `/gsd:new-milestone`)

### Out of Scope

- Modifying GSD itself -- GSD-Docs is a standalone plugin
- PLC code generation -- SDS describes design, not executable code; safety risk
- P&ID / electrical diagram generation -- Engineering Package items requiring CAD tools
- Real-time multi-user editing -- document generation is single-user; review-phase handles collaboration
- Full-auto mode (zero human input) -- equipment specifics cannot be inferred
- Database-backed state management -- STATE.md is human-readable, git-trackable
- Local LLM deployment -- deferred to v2 requirements
- Client-specific RAG system -- CATALOG.json + BASELINE.md handle reuse cleanly

## Context

Shipped v1.0 with 48,700 lines of Markdown across 194 files.
Tech stack: Claude Code plugin (.md commands with frontmatter), GSD architecture (subagent delegation, wave parallelization, @-reference context injection).
14 commands, 14 workflows, 3 subagents (doc-writer, doc-verifier, fresh-eyes).
30 templates consumed across 7 phases.
89/89 requirements satisfied, 7/7 E2E flows verified.

**Architecture:** Commands as frontmatter-driven .md files in `~/.claude/commands/doc/`, supporting files in `~/.claude/gsd-docs-industrial/`. SPECIFICATION.md v2.7.0 is the SSOT.

**Users:** Industrial automation engineers writing FDS/SDS documents for client projects, Type A (new + standards, 100+ motors) through Type D (small modifications/TWN).

## Constraints

- **Plugin architecture**: Must follow GSD's command registration pattern (frontmatter .md files in `~/.claude/commands/doc/`)
- **Context management**: Fresh context per write task (only PROJECT.md + CONTEXT.md + current PLAN.md + standards)
- **Subagent pattern**: Heavy operations delegated to subagents to protect main context window
- **Specification compliance**: SPECIFICATION.md v2.7.0 is the SSOT
- **Standards opt-in**: PackML/ISA-88 loaded conditionally, never hardcoded

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Standalone plugin, not GSD fork | Different output (docs vs code); forking = maintenance burden | ✓ Good -- clean separation, zero GSD interference |
| Commands under `/doc:*` prefix | Clear namespace separation from `/gsd:*` | ✓ Good -- 14 commands coexist with GSD |
| Configurable language (Dutch/English) | Framework supports international use | ✓ Good -- bilingual templates throughout |
| SUMMARY.md as completion proof | STATE.md can corrupt; file existence is atomic | ✓ Good -- reliable forward-only recovery |
| Forward-only error recovery | Simpler than rollback; idempotent resume is safer | ✓ Good -- crash recovery works reliably |
| 5-level verification cascade | Goal-backward checking catches gaps task-based QA misses | ✓ Good -- systematic gap detection |
| Context isolation for writers | Prevents cross-contamination between parallel sections | ✓ Good -- each writer gets focused context |
| Standards as opt-in verification level | Never push standards on projects that don't need them | ✓ Good -- PackML/ISA-88 only when enabled |
| SDS generation as scaffolding (not transform) | SDS needs discuss-plan-write-verify cycle too | ✓ Good -- reuses full pipeline |
| Typicals matching with confidence scoring | Prevents hallucinated SDS content for unknown equipment | ✓ Good -- NEW TYPICAL NEEDED for unmatched |
| Pandoc + huisstijl.docx for export | Industry-standard toolchain, corporate styling | ✓ Good -- graceful degradation with --draft/--skip-diagrams |
| Plugin files in project repo, installed via junctions | No admin required, version-controlled | ✓ Good -- install.ps1 handles setup |

---
*Last updated: 2026-02-14 after v1.0 milestone*
