# GSD-Docs Industrial

## What This Is

A web-based application for writing industrial FDS (Functional Design Specification) and SDS (Software Design Specification) documents. Built on the proven GSD-Docs workflow (v1.0 shipped as Claude Code plugin), the GUI provides a visual interface with project wizard, phase timeline, document preview, reference library, and embedded chat — making the FDS/SDS workflow accessible to engineering teams without CLI knowledge. FastAPI backend orchestrates Claude API calls using the domain knowledge from v1.0; React frontend provides the engineer's cockpit.

## Core Value

Engineers can create, manage, and review FDS/SDS projects through a visual web interface that guides them through the full document lifecycle — from project setup through verified export — with human-in-the-loop quality gates and team-accessible reference management.

## Current Milestone: v2.0 GUI

**Goal:** Build a web-based GUI that wraps the proven v1.0 FDS/SDS workflow in a visual, team-accessible interface.

**Target features:**
- Project wizard (type classification, language, reference file upload)
- Phase timeline + document outline as main working view
- Embedded chat panel for discussion phases
- Automated writing with progress feedback, human-in-the-loop verification
- Reference library (shared standards/typicals + per-project uploads/overrides)
- Rendered document preview (not raw Markdown)
- Full workflow coverage (all 14 /doc:* steps through the GUI)
- Team server deployment (VM, browser access)

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

- [ ] Web-based GUI with project wizard, phase timeline, and document preview
- [ ] FastAPI backend orchestrating Claude API calls with v1.0 workflow logic
- [ ] React frontend with dashboard, chat panel, and reference management
- [ ] Reference library with shared + per-project file management
- [ ] Team server deployment (VM, Nginx reverse proxy)

### Out of Scope

- Modifying GSD itself -- GSD-Docs is a standalone plugin
- PLC code generation -- SDS describes design, not executable code; safety risk
- P&ID / electrical diagram generation -- Engineering Package items requiring CAD tools
- Real-time multi-user editing -- document generation is single-user; review-phase handles collaboration
- Full-auto mode (zero human input) -- equipment specifics cannot be inferred
- Database-backed state management -- STATE.md is human-readable, git-trackable
- Local LLM deployment -- deferred to v3.0; architecture supports provider swap
- Client-specific RAG system -- CATALOG.json + BASELINE.md handle reuse cleanly
- Real-time collaborative editing -- v2.0 is single-engineer workflow; review handled through review phase

## Context

**v1.0 foundation:** Shipped CLI plugin with 48,700 lines of Markdown across 194 files. 14 commands, 14 workflows, 3 subagents, 30 templates, 89/89 requirements satisfied. Proven workflow for FDS/SDS document generation.

**v1.0 architecture:** Commands as frontmatter-driven .md files in `~/.claude/commands/doc/`, supporting files in `~/.claude/gsd-docs-industrial/`. SPECIFICATION.md v2.7.0 is the SSOT. Domain knowledge (templates, section structures, verification criteria, prompt patterns) transfers to v2.0 as API prompt context.

**v2.0 architecture:** FastAPI backend replaces Claude Code as workflow orchestrator. React frontend replaces terminal as user interface. Claude API (Anthropic SDK) replaces Claude Code's built-in LLM access. LLM provider abstracted behind interface for future local model support (v3.0). SQLite for project/file metadata. Deployed on VM with Nginx reverse proxy.

**Users:** Industrial automation engineering team writing FDS/SDS documents for client projects. Team server deployment — engineers access via browser. No Docker available; VM-based hosting.

**CLI coexistence:** v1.0 `/doc:*` commands remain functional. GUI and CLI produce compatible project files.

## Constraints

- **Tech stack**: FastAPI (Python) backend + React (TypeScript) frontend
- **Deployment**: VM-based, no Docker. Nginx reverse proxy, systemd services
- **API dependency**: Claude API (Anthropic) required for AI features; offline mode limited to review/export
- **LLM abstraction**: Provider interface must support future swap to local models (v3.0)
- **CLI compatibility**: Project file format must remain compatible with v1.0 `/doc:*` commands
- **Domain knowledge reuse**: v1.0 templates, section structures, and prompt patterns are the SSOT for document generation logic
- **v1.0 fidelity (HARD RULE)**: v2.0 must faithfully reproduce all v1.0 behavior and domain content. Plans MUST reference specific v1.0 source files (path + section) for any domain content — never paraphrase or simplify. Executors MUST read the referenced v1.0 files before implementing. Verifiers MUST cross-check against v1.0 originals. Key v1.0 sources: `gsd-docs-industrial/SPECIFICATION.md` (SSOT), `gsd-docs-industrial/templates/`, `gsd-docs-industrial/references/`
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
| FastAPI + React for v2.0 GUI | Full control over UI, proper web app architecture, model-agnostic | -- Pending |
| LLM provider abstraction | Enables local model support in v3.0 without rewriting orchestration | -- Pending |
| SQLite for metadata | Lightweight, zero-config, sufficient for single-server deployment | -- Pending |
| VM deployment (no Docker) | Company policy; systemd + Nginx is proven and maintainable | -- Pending |
| Mock + Ollama for dev, no paid API | Zero cost during development; MockLLMProvider for canned responses + Ollama/LiteLLM for local models (DeepSeek, Llama). Paid API only at production deploy | -- Pending |

---
*Last updated: 2026-02-14 after v2.0 milestone started*
