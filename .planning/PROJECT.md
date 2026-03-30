# GSD-Docs Industrial

## What This Is

A dual-interface system for managing industrial FDS (Functional Design Specification) and SDS (Software Design Specification) document projects. The CLI (`/doc:*` commands via Claude Code) handles AI-driven operations — discuss, plan, write, verify. The web-based GUI cockpit handles visual tasks — dashboard, preview, review, export. FastAPI backend serves as file/project management API; React frontend provides the engineer's cockpit.

## Core Value

Engineers can create, manage, and review FDS/SDS projects through a visual web interface that guides them through the full document lifecycle — from project setup through verified export — with human-in-the-loop quality gates and team-accessible reference management.

## Current State

**v2.0 GUI shipped** (2026-03-30). 11 phases, 26 plans, 56 tasks, ~14,652 LOC across 155 source files. 31/33 requirements satisfied — deployment (SYST-02/SYST-03) deferred.

**What's built:**
- Project dashboard with guided wizard (type A/B/C/D, language, reference upload)
- Phase timeline with CLI command guidance and change notifications
- Document outline tree with rendered preview (markdown, Mermaid diagrams)
- Section review with approve/reject/request-changes, per-section verification display
- FDS assembly + DOCX export with SSE progress
- SDS scaffolding with typicals matching and confidence scoring
- Reference library with drag-and-drop, shared/per-project management
- Export safety gates (unreviewed content warning)

**Not deployed yet:** VM deployment (Nginx, systemd) is ON HOLD. Running locally.

## Requirements

### Validated

- ✓ `/doc:new-fds` — classify project (Type A/B/C/D), generate all planning artifacts — v1.0
- ✓ `/doc:discuss-phase N` — identify gray areas, capture decisions in CONTEXT.md — v1.0
- ✓ `/doc:plan-phase N` — generate section PLANs with wave assignments — v1.0
- ✓ `/doc:write-phase N` — parallel-write CONTENT.md + SUMMARY.md with context isolation — v1.0
- ✓ `/doc:verify-phase N` — goal-backward 5-level verification with gap detection — v1.0
- ✓ `/doc:review-phase N` — client/engineer review with feedback capture — v1.0
- ✓ `/doc:complete-fds` — FDS assembly with cross-ref resolution and versioning — v1.0
- ✓ `/doc:generate-sds` — SDS scaffolding with typicals matching — v1.0
- ✓ `/doc:export` — DOCX export with Pandoc + Mermaid rendering — v1.0
- ✓ `/doc:status` — project progress overview from STATE.md + ROADMAP.md — v1.0
- ✓ `/doc:resume` — crash recovery with forward-only strategy — v1.0
- ✓ `/doc:release` — version management (internal/client) — v1.0
- ✓ `/doc:expand-roadmap` — dynamic ROADMAP evolution when >5 units discovered — v1.0
- ✓ `/doc:check-standards` — opt-in PackML/ISA-88 compliance checking — v1.0
- ✓ 4 project types with distinct ROADMAP templates (A/B/C/D) — v1.0
- ✓ Gap closure loop: verify → plan --gaps → write → re-verify (max 2 cycles) — v1.0
- ✓ Knowledge transfer: RATIONALE.md, EDGE-CASES.md, Fresh Eyes review — v1.0
- ✓ FDS section templates (equipment module, state machine, interface) — v1.0
- ✓ Bilingual Dutch/English output — v1.0
- ✓ BASELINE.md for modification projects (Type C/D) — v1.0
- ✓ Typicals library (CATALOG.json) for SDS matching — v1.0
- ✓ Web-based cockpit with project wizard, phase timeline, document preview, and review — v2.0
- ✓ FastAPI backend as file/project management API — v2.0
- ✓ React frontend with dashboard, document preview, review interface, and export — v2.0
- ✓ Reference library with shared + per-project file management — v2.0

### Active

- [ ] VM deployment with Nginx reverse proxy and systemd services (deferred from v2.0)
- [ ] CLI compatibility verification (deferred from v2.0)

### Out of Scope

- Modifying GSD itself — GSD-Docs is a standalone plugin
- PLC code generation — SDS describes design, not executable code; safety risk
- P&ID / electrical diagram generation — Engineering Package items requiring CAD tools
- Real-time collaborative editing — single-engineer workflow; review-phase handles collaboration
- Full-auto mode (zero human input) — equipment specifics cannot be inferred
- Database-backed state management — STATE.md is human-readable, git-trackable
- Local LLM deployment — deferred to v3.0; architecture supports provider swap
- Inline Markdown editing in GUI — creates divergence from file-backed state; breaks CLI compatibility

## Context

**v1.0 foundation:** Shipped CLI plugin with 48,700 lines of Markdown across 194 files. 14 commands, 14 workflows, 3 subagents, 30 templates, 89/89 requirements satisfied.

**v2.0 GUI:** FastAPI backend (37 Python files, 5,563 LOC) + React frontend (118 TSX/TS files, 9,089 LOC). SQLite for project/file metadata. Tailwind CSS + shadcn/ui. Mermaid diagram rendering. SSE for export progress.

**Users:** Industrial automation engineering team writing FDS/SDS documents for client projects. Currently running locally; team server deployment planned.

**CLI coexistence:** v1.0 `/doc:*` commands remain functional. GUI reads CLI output files (VERIFICATION.md, CONTEXT.md) and displays results. AI operations stay in CLI.

## Constraints

- **Tech stack**: FastAPI (Python) backend + React (TypeScript) frontend
- **Deployment**: VM-based, no Docker. Nginx reverse proxy, systemd services (when deployed)
- **No LLM orchestration in GUI**: AI operations handled by CLI; backend is a file/project management API
- **CLI compatibility**: Project file format must remain compatible with v1.0 `/doc:*` commands
- **Domain knowledge reuse**: v1.0 templates, section structures, and prompt patterns are the SSOT for document generation logic
- **v1.0 fidelity (HARD RULE)**: GUI must faithfully reproduce all v1.0 behavior and domain content
- **Standards opt-in**: PackML/ISA-88 loaded conditionally, never hardcoded

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Standalone plugin, not GSD fork | Different output (docs vs code); forking = maintenance burden | ✓ Good — clean separation, zero GSD interference |
| Commands under `/doc:*` prefix | Clear namespace separation from `/gsd:*` | ✓ Good — 14 commands coexist with GSD |
| Configurable language (Dutch/English) | Framework supports international use | ✓ Good — bilingual templates throughout |
| SUMMARY.md as completion proof | STATE.md can corrupt; file existence is atomic | ✓ Good — reliable forward-only recovery |
| Forward-only error recovery | Simpler than rollback; idempotent resume is safer | ✓ Good — crash recovery works reliably |
| 5-level verification cascade | Goal-backward checking catches gaps task-based QA misses | ✓ Good — systematic gap detection |
| Context isolation for writers | Prevents cross-contamination between parallel sections | ✓ Good — each writer gets focused context |
| Standards as opt-in verification level | Never push standards on projects that don't need them | ✓ Good — PackML/ISA-88 only when enabled |
| SDS generation as scaffolding (not transform) | SDS needs discuss-plan-write-verify cycle too | ✓ Good — reuses full pipeline |
| Typicals matching with confidence scoring | Prevents hallucinated SDS content for unknown equipment | ✓ Good — NEW TYPICAL NEEDED for unmatched |
| Pandoc + huisstijl.docx for export | Industry-standard toolchain, corporate styling | ✓ Good — graceful degradation with --draft/--skip-diagrams |
| Plugin files in project repo, installed via junctions | No admin required, version-controlled | ✓ Good — install.ps1 handles setup |
| GUI as cockpit, not AI wrapper | Phase 10/10.1 proved embedded chat feels forced vs CLI. GUI handles visual tasks; AI stays in CLI | ✓ Good — eliminates 7 requirements, simplifies backend |
| FastAPI + React for v2.0 GUI | Full control over UI, proper web app architecture | ✓ Good — clean API boundaries, component reuse |
| SQLite for metadata | Lightweight, zero-config, sufficient for single-server deployment | ✓ Good — no ops overhead, Alembic migrations |
| LLM abstraction removed from GUI | Cockpit pivot (Phase 10) — GUI doesn't need LLM; CLI handles all AI | ✓ Good — simpler backend, no provider complexity |
| Per-section truth filtering | Phase 12 passed phase-level truths to every section; Phase 16 added regex-based section matching | ✓ Good — clean UX, no false positives |
| Defer VM deployment | Local development priority; deployment is separate concern | — Pending |

---
*Last updated: 2026-03-30 — v2.0 GUI milestone shipped*
