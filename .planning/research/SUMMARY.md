# Project Research Summary

**Project:** GSD-Docs Industrial v2.0 — Web GUI for FDS/SDS Document Generation
**Domain:** Industrial automation engineering documentation (Web-based AI-powered document generation)
**Researched:** 2026-02-14
**Confidence:** HIGH

## Executive Summary

GSD-Docs v2.0 wraps the proven v1.0 CLI workflow with a modern web interface to make industrial document generation accessible to engineering teams. The v1.0 CLI foundation (Claude Code commands, templates, domain knowledge) is validated and remains the source of truth. The v2.0 web GUI adds a FastAPI backend that orchestrates the same workflows and a React frontend that provides visual project management, real-time progress feedback, and document preview capabilities.

The recommended approach is **orchestration over reimplementation**: The backend reads existing workflow .md files and executes their logic in Python, the frontend provides the interface layer, and all domain knowledge (templates, standards, typicals) remains file-based. This preserves CLI compatibility while adding the usability benefits of a web interface. The architecture separates concerns cleanly: FastAPI backend replaces Claude Code as orchestrator, React frontend handles visualization, SQLite stores only metadata, and the filesystem remains the source of truth for documents.

Key risks center on real-time communication reliability and context management. Long-running LLM tasks (2-5 minutes) require persistent task storage with WebSocket reconnection logic to survive network hiccups and browser refreshes. Multi-step document generation workflows must implement checkpoint-based resumption to recover from failures without restarting from scratch. Context window budgeting is critical to prevent token limit failures on large technical documents. These risks are mitigated through Redis-backed task persistence, SSE for one-way streaming with automatic reconnection, and explicit token counting with context summarization.

## Key Findings

### Recommended Stack

The v2.0 stack adds web infrastructure around the proven v1.0 CLI foundation. Backend uses FastAPI 0.129+ with async/await throughout, Anthropic SDK 0.79+ for Claude API integration, and SQLite 3.45+ with SQLAlchemy async for metadata. Real-time updates use sse-starlette 3.2+ for server-to-client streaming (simpler than WebSockets for one-way communication). Frontend uses React 18.3+ with TypeScript 5.7+, Vite 6.1+ for build tooling (40x faster than Create React App), shadcn/ui for accessible copy-paste components, TanStack Query 6.1+ for server state, and Zustand 5.0+ for minimal client state. Deployment is VM-based with systemd service management and Nginx reverse proxy (no Docker per requirement).

**Core technologies:**
- **FastAPI 0.129+**: Async API orchestration — industry standard with automatic OpenAPI docs and native Pydantic validation
- **Anthropic SDK 0.79+**: Claude API integration — official SDK with streaming, fast-mode, and structured outputs
- **sse-starlette 3.2+**: Server-Sent Events — simpler than WebSockets for unidirectional server-to-client streaming with built-in browser auto-reconnect
- **SQLite 3.45+ + SQLAlchemy 2.1+**: Metadata storage — no server required, perfect for team server (5-20 users), stores projects/files/sessions not documents
- **React 18.3+ + TypeScript 5.7+**: UI framework — industry standard with excellent TypeScript support and mature ecosystem
- **Vite 6.1+**: Build tool — 40x faster than CRA, HMR in milliseconds, first-class TypeScript support
- **shadcn/ui + Radix UI 1.2+**: Component library — copy-paste ownership model, built on accessible headless primitives
- **TanStack Query 6.1+**: Server state — automatic caching, background refetching, eliminates API boilerplate
- **Zustand 5.0+**: Client state — minimal API for UI state only (sidebar, theme, selected panel)

**Critical version requirements:**
- Pydantic 2.10+ (v2 is 5-50x faster, FastAPI requires v2)
- Node.js 20.19+ (required for Vite 6 and Tailwind 4)
- Tailwind CSS 4.1+ (5x faster builds, requires Safari 16.4+, Chrome 111+, Firefox 128+)

### Expected Features

Web GUI features split into three priority tiers based on user value vs implementation cost analysis.

**Must have (v2.0 launch — table stakes):**
- **Project wizard with guided setup** — 3-5 step flow for Type A/B/C/D classification, language selection, reference upload, and baseline selection; reduces errors during initialization
- **Phase timeline/progress visualization** — Linear timeline showing 3-phase FDS workflow (Discuss → Plan → Write → Verify → Review) with completion status; primary navigation
- **Embedded chat panel for discussion phases** — AI discussion interface inline with workflow; maintains context, differentiates from generic chatbot by being workflow-aware
- **Real-time progress feedback** — SSE streaming for long-running LLM calls (30s-3min); prevents "is it frozen?" anxiety with section-level granularity
- **Human-in-the-loop review gates** — Approve/reject/request-changes workflow for verify-phase and review-phase; non-negotiable for professional document generation
- **Basic document preview** — Markdown rendering with Mermaid diagram support; engineers need to see output without exporting to DOCX
- **Reference file upload** — Drag-and-drop for per-project files (PDFs, DOCX, images); discuss-phase useless without reference context
- **DOCX export** — Download button wrapping existing Pandoc export with huisstijl.docx template
- **Error recovery/resume** — Detect incomplete state from STATE.md and offer resume; critical for 3-hour generation runs that crash
- **Project list dashboard** — Browse existing projects with status, last modified, project type; engineers need access point

**Should have (v2.x after validation):**
- **Shared reference library** — Global library with admin management plus per-project overrides; team knowledge accumulation
- **Confidence-based SDS typicals matching display** — Surface CATALOG.json matching scores, show "NEW TYPICAL NEEDED" for unknown equipment; builds trust
- **Gap closure loop visualization** — Show verify → re-plan → re-write cycles transparently; max 2 iterations per v1.0 logic
- **Standards compliance panel** — Opt-in PackML/ISA-88 verification overlay with violation indicators
- **Phase-specific context visualization** — Debug view showing which reference docs/baseline sections fed each writer; transparency builds trust
- **Document outline tree with navigation** — Expandable/collapsible tree for large FDS; linear scroll works for MVP

**Defer (v3.0+ future consideration):**
- **Local LLM support** — Provider abstraction ready but requires v3.0 milestone; API costs manageable, model quality unproven for technical docs
- **Multi-user team features** — Role-based access, project sharing, activity logs; v2.0 single-engineer per project
- **Client portal** — Read-only review access for external clients; email PDF works for now
- **Version comparison UI** — Diff view between FDS versions; engineers use Word's compare feature
- **Mobile/tablet UI** — Responsive design for field access; engineering work is desktop-based

**Anti-features (avoid):**
- **Real-time collaborative editing** — Document generation is single-engineer per v1.0 design; use async review-phase instead
- **Full auto-generation (zero human input)** — Equipment details cannot be inferred; results in hallucinated/unsafe content
- **Inline Markdown editing in GUI** — Creates divergence from file-backed state; breaks CLI compatibility
- **Database-backed document storage** — STATE.md must remain human-readable and git-trackable
- **Live DOCX preview** — Requires Word rendering engine; Markdown preview sufficient

### Architecture Approach

The architecture implements **orchestration over reimplementation**: the backend becomes the orchestrator (replacing Claude Code), the frontend is the interface, and domain knowledge (templates, standards, workflows) remains in files. The workflow engine reads .md files from v1.0 and executes equivalent Python logic rather than embedding workflow steps in API routes. The LLM provider abstraction allows swapping Claude → local models via config change, not code rewrite.

**Major components:**
1. **FastAPI Backend** — Replaces Claude Code as orchestrator; loads v1.0 templates/workflows, calls Anthropic SDK, streams progress via SSE
2. **Workflow Engine** — Reads .md workflow files, translates steps to Python execution, maintains STATE.md checkpoints, implements wave-based parallelization
3. **LLM Provider Abstraction** — `LLMProvider` interface with `ClaudeProvider` (v2.0) and `LocalProvider` stub (v3.0); entire codebase calls `get_llm_provider().complete()`
4. **React Frontend** — Visual interface for workflows; Zustand stores for projects/phases, TanStack Query for API data, SSE EventSource for real-time updates
5. **Domain Knowledge Loader** — Loads templates (equipment-module.md), standards (PackML/ISA-88), prompts (doc-writer.md) from v1.0 file structure unchanged
6. **State Manager** — Reads/writes STATE.md for checkpoint/resume; detects crashes, enables forward-only recovery
7. **SQLite Metadata Store** — Projects table, files table, sessions table; NOT documents (documents remain file-based for CLI compatibility)
8. **File Storage** — `/projects/{id}/.planning/` for state, `/references/shared/` for global library, `/references/projects/{id}/` for per-project uploads

**Data flow (Phase Writing example):**
```
Engineer clicks "Write Phase 3"
  → POST /api/phases/3/write
    → Workflow Engine loads write-phase.md
      → Discover PLAN.md files, group by wave
        → Background Task Queue (ARQ + Redis) spawns parallel writers per wave
          → Each writer: Domain Knowledge Loader builds isolated context
            → LLM Provider calls Claude with streaming
              → SSE broadcasts progress per section
                → React EventSource updates progress UI
          → Write CONTENT.md + SUMMARY.md to filesystem
        → State Manager checkpoints wave completion in STATE.md
      → Aggregate CROSS-REFS.md
    → Return success
  → Frontend updates phase timeline
```

**Key architectural patterns:**
- **Workflow translation**: .md files are SSOT; Python reads and executes them
- **Provider abstraction**: Model-agnostic `LLMProvider` interface for future local models
- **SSE over WebSockets**: One-way streaming simpler than bidirectional; browser auto-reconnect built-in
- **Hybrid storage**: SQLite for searchable metadata, filesystem for human-readable documents
- **Wave-based parallelization**: Group plans by wave number, execute waves sequentially, plans within wave parallel
- **Context isolation**: Each section writer receives only relevant context (no cross-plan leakage)

### Critical Pitfalls

From PITFALLS.md, the five highest-impact risks requiring upfront architectural decisions:

1. **WebSocket connection drops during long LLM tasks** — Engineers start 2-5 minute generation, connection drops (network hiccup, browser refresh), backend continues burning API tokens, user sees frozen UI and restarts duplicating work. **Prevention:** Decouple task execution from connection lifecycle. Use Redis Streams for persistent chunk storage, Redis Pub/Sub for notifications, client auto-reconnection with task ID fetches missed chunks. Add heartbeat keepalive every 15 seconds. **Phase:** Phase 1 (Core Infrastructure) — architectural decision that must be made upfront.

2. **Blocking FastAPI event loop with synchronous file operations** — Uploading 50MB reference document uses `open().write()`, blocks worker thread for seconds, entire app becomes unresponsive under concurrent load. **Prevention:** Use `aiofiles` for all file operations, async context managers, chunked streaming for large files. Set file size limits (100MB max). Real-world measurements show 40% throughput gain with async I/O. **Phase:** Phase 1 (Core Infrastructure) — establish file handling patterns from start.

3. **Claude API rate limits without retry-after header handling** — Multiple concurrent calls hit rate limit (50 req/min Tier 1), naive retry ignores `retry-after` header, thundering herd makes congestion worse. **Prevention:** Read and respect `retry-after` header, exponential backoff with jitter as fallback, request queuing with rate tracking, per-user quotas, circuit breakers. **Phase:** Phase 1 (Core Infrastructure) — LLM client service must implement correctly upfront.

4. **Shared state divergence between CLI and web** — CLI uses file-based locking, web needs concurrent access, developers duplicate state logic, projects created via CLI don't appear correctly in web UI. **Prevention:** Create shared state management library used by both CLI and web, abstract storage interface (file-based for CLI, Redis for web), unified validation, transactional updates. **Phase:** Phase 1 (Core Infrastructure) — foundational architecture, retrofitting extremely costly.

5. **Unvalidated file uploads with content-type spoofing** — Accept user files checking only `Content-Type` header (client-controlled), malicious PDF with spoofed header creates RCE/SSRF/DoS vulnerabilities. **Prevention:** Defense-in-depth validation: magic number validation with `python-magic`, file extension whitelist, size limits, UUID-based storage filenames, sandboxed parsing, virus scanning. **Phase:** Phase 2 (File Management) — security gate, cannot be deferred.

**Additional high-impact pitfalls:**
- **Missing resumption points for interrupted workflows** — Multi-step workflow fails mid-process, restarts from scratch wasting time/tokens. **Prevention:** Workflow state machines with persistent checkpoints, manual override support, resumption from any completed checkpoint. **Phase:** Phase 3 (Phase Orchestration).
- **Context window limits in multi-step generation** — Accumulate context across steps, exceed 200K token limit, API fails. **Prevention:** Explicit token counting with `anthropic.count_tokens()`, context budgeting, summarization of previous steps, prompt caching for 60-90% cost reduction. **Phase:** Phase 3 (Phase Orchestration).
- **SSE vs WebSocket mismatch** — Use WebSockets for one-way streaming, unnecessary complexity. **Prevention:** Use SSE for server-to-client (LLM tokens, progress), reserve WebSockets for bidirectional (collaborative editing). **Phase:** Phase 1 (Core Infrastructure).

## Implications for Roadmap

Based on combined research, the roadmap should follow an **infrastructure-first, features-incremental** approach. The critical architectural decisions (real-time communication, file handling, state management, LLM abstraction) must be in place before building user-facing workflows. Each phase delivers a vertical slice of functionality that can be validated independently.

### Phase 1: Core Infrastructure & Project Management
**Rationale:** Foundational architecture must support all subsequent phases. WebSocket reconnection logic, async file I/O patterns, LLM provider abstraction, and shared CLI/web state management are architectural decisions that cannot be retrofitted. Establishing these upfront prevents costly refactoring later. Project creation and listing provides immediate user value for testing infrastructure.

**Delivers:**
- FastAPI skeleton with CORS, Pydantic settings, async SQLAlchemy
- SQLite metadata store (projects, files, sessions tables)
- LLM provider abstraction (`LLMProvider` interface, `ClaudeProvider` implementation with retry-after handling)
- File storage structure (`/projects/`, `/references/`)
- SSE infrastructure with Redis-backed task persistence and reconnection logic
- Async file handling utilities with `aiofiles`
- Shared state management library (abstract storage, unified validation)
- Workflow engine foundation (load .md files, parse steps)
- React + Vite setup with routing, Zustand stores, TanStack Query
- Project creation API (wraps `new-fds.md` workflow)
- Project list dashboard UI
- Basic error handling and logging

**Addresses features:**
- Project list dashboard (table stakes)
- Project creation with Type A/B/C/D classification

**Avoids pitfalls:**
- Pitfall 1: WebSocket connection drops (Redis-backed persistence + SSE)
- Pitfall 2: Blocking file I/O (aiofiles from start)
- Pitfall 3: Claude rate limits (retry-after header handling in LLM client)
- Pitfall 4: CLI/web state divergence (shared state library)
- Pitfall 7: SSE vs WebSocket mismatch (choose SSE for one-way)

**Needs research:** No — web infrastructure patterns well-documented

---

### Phase 2: Reference Library & File Management
**Rationale:** Reference files are critical input for discuss-phase and write-phase workflows. File upload must have proper security validation (magic numbers, not just Content-Type) before allowing any uploads. This phase also establishes the shared/per-project library architecture that supports discuss-phase context assembly.

**Delivers:**
- File upload API with defense-in-depth validation (magic numbers via `python-magic`, extension whitelist, size limits, UUID storage)
- Reference library storage (`/references/shared/`, `/references/projects/{id}/`)
- File metadata in SQLite (files table with project_id, category, path, mime_type)
- Reference library UI (drag-and-drop upload, file listing, categorization)
- File download endpoint (proxy, not direct serving)
- Reference file context loading for workflows
- File cleanup on project deletion

**Addresses features:**
- Reference file upload (table stakes)
- Shared reference library (should-have, foundation for v2.x global library)

**Avoids pitfalls:**
- Pitfall 5: File upload security (magic number validation, sandboxed storage)

**Needs research:** No — file handling patterns established

---

### Phase 3: Discussion Workflow & Chat Interface
**Rationale:** Discuss-phase is the first interactive workflow, establishing patterns for all subsequent phase workflows. Chat panel is a key differentiator vs generic document tools. This phase validates the workflow engine, LLM integration, and real-time communication under real user interaction.

**Delivers:**
- `discuss-phase.md` workflow implementation in Python
- `/api/phases/{phase}/discuss` endpoint
- Workflow execution: load ROADMAP goals, call LLM to identify gray areas, stream questions via SSE
- Chat panel component (WebSocket-connected, displays questions, captures answers)
- Discussion state management (conversation history in CONTEXT.md)
- Phase timeline component (visualization of ROADMAP phases)
- SSE event handling in React (EventSource hook)
- Discussion completion triggers plan-phase enablement

**Addresses features:**
- Embedded chat panel (table stakes, differentiator)
- Phase timeline visualization (table stakes)

**Uses stack:**
- Anthropic SDK for Claude API
- sse-starlette for streaming questions
- React EventSource for real-time updates

**Implements architecture:**
- Workflow Engine executing .md workflows
- Domain Knowledge Loader providing ROADMAP context
- State Manager updating STATE.md checkpoints

**Needs research:** No — workflow patterns from v1.0, chat UI well-documented

---

### Phase 4: Planning Workflow & Section Organization
**Rationale:** Plan-phase establishes the section structure that write-phase executes. This phase implements wave-based section dependencies (frontmatter parsing) and generates PLAN.md files that drive subsequent writing. Validation of wave logic critical before parallel execution in Phase 5.

**Delivers:**
- `plan-phase.md` workflow implementation
- `/api/phases/{phase}/plan` endpoint
- Workflow: load section templates, generate PLAN.md files with frontmatter (wave, depends_on)
- PLAN.md frontmatter parsing (YAML)
- Wave dependency validation (no circular deps)
- Document outline component (tree view of planned sections)
- Plan editing UI (adjust wave assignments, dependencies)
- Plan completion enables write-phase

**Addresses features:**
- Document outline tree view (should-have foundation, enhanced in v2.x)

**Uses stack:**
- Domain Knowledge Loader for section templates
- State Manager for plan file tracking

**Implements architecture:**
- Wave-based parallelization foundation (groups plans by wave)

**Needs research:** No — planning logic from v1.0

---

### Phase 5: Writing Workflow & Real-Time Progress
**Rationale:** Write-phase is the most complex workflow: wave-based parallel execution, long-running LLM calls, context isolation per section, progress streaming. This phase validates the entire architecture under production-like load. Background task queue (ARQ + Redis) enables parallel writers.

**Delivers:**
- `write-phase.md` workflow implementation
- `/api/phases/{phase}/write` endpoint
- Background task queue setup (ARQ + Redis)
- Parallel section writing (spawn tasks per wave, await wave completion)
- Context isolation (each writer receives only relevant PLAN, CONTEXT, standards)
- Progress streaming via SSE (section start/progress/complete events)
- CONTENT.md and SUMMARY.md file generation
- CROSS-REFS.md aggregation
- Progress indicator component (wave/section progress bars)
- Document preview component (react-markdown + Mermaid rendering)
- Write completion enables verify-phase

**Addresses features:**
- Real-time progress feedback (table stakes)
- Basic document preview (table stakes)

**Uses stack:**
- ARQ + Redis for background tasks
- sse-starlette for progress streaming
- react-markdown + remark-gfm for preview
- Mermaid rendering in browser

**Implements architecture:**
- Wave-based parallelization (sequential waves, parallel within wave)
- Context isolation (no cross-plan leakage)
- SSE progress broadcasting from background tasks

**Avoids pitfalls:**
- Pitfall 6: Missing resumption points (checkpoint after each wave in STATE.md)
- Pitfall 8: Context window limits (context budget per section, no full document context)

**Needs research:** No — wave parallelization patterns established

---

### Phase 6: Verification & Gap Closure
**Rationale:** Verify-phase implements the 5-level quality checks (goals, standards, completeness, safety, cross-references). Gap detection and closure loop (re-plan → re-write, max 2 iterations) validates workflow resumption logic. This phase exercises error recovery and checkpoint resumption.

**Delivers:**
- `verify-phase.md` workflow implementation
- `/api/phases/{phase}/verify` endpoint
- 5-level verification (goal-backward, standards-forward, completeness, safety, cross-ref)
- VERIFICATION.md generation with gap details
- Gap closure loop (detect gaps → re-plan → re-write → re-verify, max 2 iterations)
- Verification results UI (display gaps, severity, recommendations)
- Fix trigger (human initiates re-plan/re-write)
- Verification completion or gap-fix-needed state

**Addresses features:**
- Gap closure loop visualization (should-have)
- Standards compliance panel foundation (opt-in in v2.x)

**Implements architecture:**
- Workflow resumption from checkpoints (verify → re-plan → re-write)

**Avoids pitfalls:**
- Pitfall 6: Missing resumption points (test checkpoint recovery in gap closure)

**Needs research:** No — verification logic from v1.0

---

### Phase 7: Review & Human-in-the-Loop
**Rationale:** Review-phase captures client feedback and engineer approval before FDS assembly. Human-in-the-loop gates are non-negotiable for professional document generation. This phase validates the approve/reject/request-changes workflow and feedback storage in CONTEXT.md.

**Delivers:**
- `review-phase.md` workflow implementation
- `/api/phases/{phase}/review` endpoint
- Review UI (approve/reject/request-changes buttons)
- Feedback capture form (client comments, engineer notes)
- Feedback storage in CONTEXT.md
- Review status tracking (pending → approved → changes-requested)
- Review completion enables complete-fds
- Approve triggers next phase, request-changes triggers re-write

**Addresses features:**
- Human-in-the-loop review gates (table stakes)

**Needs research:** No — review workflow from v1.0

---

### Phase 8: FDS Assembly & Export
**Rationale:** Assembles complete FDS from phase sections, resolves cross-references, integrates diagrams, and exports to DOCX via Pandoc. This phase delivers the final output format and validates the entire end-to-end workflow from project creation to export.

**Delivers:**
- `complete-fds.md` workflow implementation
- `/api/export/fds` endpoint
- FDS.md assembly (merge sections in order)
- Cross-reference resolution (CROSS-REFS.md → final links)
- Mermaid diagram rendering (mmdc CLI → PNG)
- DOCX export via Pandoc subprocess (huisstijl.docx template)
- Export UI (format options, download)
- Export progress streaming
- Export history tracking

**Addresses features:**
- DOCX export (table stakes)
- Document preview with Mermaid (enhanced from Phase 5)

**Uses stack:**
- Pandoc for DOCX export
- Mermaid CLI (mmdc) for diagram rendering

**Needs research:** No — export logic from v1.0

---

### Phase 9: SDS Generation
**Rationale:** SDS generation is post-FDS workflow, leverages completed FDS as input. Typicals matching (CATALOG.json) and confidence scoring are SDS-specific features. This phase can be developed after FDS workflow proven.

**Delivers:**
- `generate-sds.md` workflow implementation
- `/api/export/sds` endpoint
- Typicals matching (CATALOG.json lookup, confidence scoring)
- SDS scaffolding from FDS equipment modules
- "NEW TYPICAL NEEDED" detection for unknown equipment
- SDS preview UI
- SDS export to DOCX

**Addresses features:**
- Confidence-based SDS typicals matching (should-have)

**Needs research:** Potentially — if typicals matching algorithm unclear from v1.0

---

### Phase 10: Error Recovery & Production Hardening
**Rationale:** Crash recovery, graceful shutdown, monitoring, and production deployment patterns. This phase validates resilience under failure conditions and prepares for multi-user deployment.

**Delivers:**
- Resume detection (`/api/projects/{id}/resume` endpoint)
- STATE.md parsing to detect incomplete phases
- Resume UI (offer resume from last checkpoint)
- Graceful shutdown (SIGTERM handler, complete in-flight requests)
- systemd service files (FastAPI, ARQ worker)
- Nginx reverse proxy config (SSL, static files, WebSocket upgrade, SSE)
- Monitoring (token usage tracking, error logging, performance metrics)
- Backup scripts (SQLite, project files)
- Production checklist verification

**Addresses features:**
- Error recovery/resume (table stakes)

**Avoids pitfalls:**
- Pitfall 1: Connection drops (validate reconnection and resumption)
- Pitfall 6: Missing resumption (test crash recovery)

**Needs research:** No — systemd/Nginx deployment well-documented

---

### Phase Ordering Rationale

- **Infrastructure first (Phase 1-2):** Architectural decisions (SSE, async I/O, LLM abstraction, state management, file security) must be in place before workflows. Retrofitting these is prohibitively expensive.
- **Workflows incremental (Phase 3-9):** Each workflow phase builds on previous (discuss → plan → write → verify → review → complete → SDS). This matches the natural document generation sequence and allows validation at each step.
- **Production last (Phase 10):** Hardening happens after core workflows proven. Error recovery patterns discovered during Phase 3-9 inform Phase 10 implementation.
- **Architecture dependencies drive order:** Phase 3 (discussion) requires Phase 1 (SSE + LLM client), Phase 5 (writing) requires Phase 4 (planning), Phase 6 (verification) requires Phase 5 (content exists), Phase 8 (export) requires Phase 7 (review completion).

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 9 (SDS Generation):** If typicals matching algorithm unclear from v1.0 CATALOG.json, may need research on confidence scoring heuristics and "NEW TYPICAL NEEDED" detection rules.

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Core Infrastructure):** FastAPI + React patterns well-documented, SSE/async I/O established best practices
- **Phase 2 (File Management):** File upload security patterns clear from PITFALLS.md research
- **Phase 3-8 (Workflows):** Logic already exists in v1.0 .md workflows, implementation is translation not discovery
- **Phase 10 (Production):** systemd/Nginx deployment patterns mature and documented

**Overall:** Minimal additional research needed. The v1.0 workflows are the specification; research already covered stack, features, architecture, and pitfalls comprehensively.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Official documentation for FastAPI, React, Anthropic SDK. Version compatibility verified. Deployment patterns proven (systemd/Nginx). |
| Features | HIGH | Table stakes vs differentiators grounded in web UI patterns, AI document tools, and engineering workflows. v1.0 CLI provides feature reference. |
| Architecture | HIGH | Patterns sourced from production FastAPI+LLM deployments, real-time communication guides, and agentic workflow systems. Orchestration-over-reimplementation aligns with v1.0 constraint. |
| Pitfalls | HIGH | Based on official docs, production guides, and 2026 best practices. Critical pitfalls backed by multiple sources (WebSocket reliability, async I/O, rate limits, security). |

**Overall confidence:** HIGH

The research is comprehensive across all four dimensions (stack, features, architecture, pitfalls). Sources include official documentation (Anthropic SDK, FastAPI, React, SQLAlchemy), production guides (deployment, monitoring, security), and domain-specific research (AI document tools, engineering workflows, LLM integration patterns). The v1.0 CLI provides a validated reference implementation that de-risks workflow logic. The only uncertainty is whether typicals matching needs deeper research (Phase 9), but this can be deferred until FDS workflow is proven.

### Gaps to Address

- **Typicals matching confidence algorithm (Phase 9):** If CATALOG.json matching logic unclear from v1.0 code, may need research during Phase 9 planning on confidence scoring heuristics and equipment identification patterns.
- **Production monitoring specifics:** While monitoring patterns clear, specific metrics to track (token usage per user, API latency percentiles, error rates by phase) should be defined during Phase 10 based on operational needs discovered in Phase 1-9.
- **Multi-user concurrency patterns:** v2.0 targets 5-20 users, but concurrent editing edge cases (two engineers editing same project) deferred to v2.x. If concurrent access issues emerge, may need locking/conflict resolution research.

**How to handle:**
- **Typicals matching:** Review v1.0 CATALOG.json implementation during Phase 9 planning. If algorithm unclear, run `/gsd:research-phase` to research equipment identification and confidence scoring patterns.
- **Monitoring:** Define initial metric set in Phase 1 (basic health checks), expand incrementally in Phase 3-9 based on discovered failure modes, finalize in Phase 10.
- **Concurrency:** Document "single engineer per project" constraint in v2.0. If multi-user demand emerges, defer to v2.x with proper research on optimistic locking / conflict resolution.

## Sources

### Primary (HIGH confidence)
- **Anthropic SDK releases** (https://github.com/anthropics/anthropic-sdk-python/releases) — Official Python SDK, latest v0.79.0 (Feb 2026), streaming, structured outputs, prompt caching
- **FastAPI documentation** (https://fastapi.tiangolo.com/) — Official docs for async API, background tasks, WebSockets, deployment
- **React documentation** (https://react.dev/) — Official React 18 docs, hooks, TypeScript patterns
- **Vite documentation** (https://vite.dev/) — Official build tool docs, v6 with Node.js 20+ requirement
- **TanStack Query documentation** (https://tanstack.com/query/latest) — Official docs for server state management, caching, mutations
- **shadcn/ui** (https://ui.shadcn.com/) — Official component library, Radix UI + Tailwind, copy-paste ownership
- **Tailwind CSS v4** (https://tailwindcss.com/blog/tailwindcss-v4) — Official v4 release, 5x faster builds, CSS-first config
- **Zustand documentation** (https://zustand.docs.pmnd.rs/) — Official minimal state library docs
- **SQLAlchemy 2.1** (https://docs.sqlalchemy.org/en/21/) — Official ORM docs, async support, improved typing
- **Alembic documentation** (https://alembic.sqlalchemy.org/en/latest/) — Official migration tool docs

### Secondary (MEDIUM confidence)
- **FastAPI production deployment** (https://render.com/articles/fastapi-production-deployment-best-practices) — Server workers, Gunicorn + Uvicorn patterns
- **Building SSE MCP Server with FastAPI** (https://www.ragie.ai/blog/building-a-server-sent-events-sse-mcp-server-with-fastapi) — SSE vs WebSocket comparison, streaming patterns
- **Vite React TypeScript setup** (https://medium.com/@robinviktorsson/complete-guide-to-setting-up-react-with-typescript-and-vite-2025-468f6556aaf2) — Project initialization, tooling config
- **FastAPI CORS configuration** (https://davidmuraya.com/blog/fastapi-cors-configuration/) — Production CORS setup, security considerations
- **Deploy FastAPI with Nginx** (https://docs.vultr.com/how-to-deploy-a-fastapi-application-with-gunicorn-and-nginx-on-ubuntu-2404) — systemd services, reverse proxy config
- **FastAPI systemd deployment** (https://ashfaque.medium.com/deploy-fastapi-app-on-debian-with-nginx-uvicorn-and-systemd-2d4b9b12d724) — Unix socket, service files
- **Web wizard design patterns** (https://www.nngroup.com/articles/wizards/) — NN/G guidelines for multi-step flows
- **Human-in-the-loop AI patterns** (https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo) — Review queues, approval workflows
- **Document generation tools comparison** (https://www.templafy.com/what-is-document-generation/) — Generic doc gen vs AI writing vs engineering DMS
- **LLM provider abstraction** (https://www.entrio.io/blog/implementing-llm-agnostic-architecture-generative-ai-module) — Model-agnostic patterns, API gateway
- **Agentic workflow architectures** (https://www.stack-ai.com/blog/the-2026-guide-to-agentic-workflow-architectures) — Checkpointing, resumption, state machines
- **Claude API rate limits** (https://docs.claude.com/en/api/rate-limits) — Official rate limit docs, retry-after header
- **How to Fix Claude API 429 Error** (https://www.aifreeapi.com/en/posts/fix-claude-api-429-rate-limit-error) — Retry strategies, backoff patterns
- **Prompt caching cost reduction** (https://medium.com/tr-labs-ml-engineering-blog/prompt-caching-the-secret-to-60-cost-reduction-in-llm-applications-6c792a0ac29b) — 60-90% cost savings patterns
- **FastAPI file upload security** (https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/) — Magic number validation, chunked streaming
- **Building secure file upload API** (https://noone-m.github.io/2025-12-10-fastapi-file-upload/) — Defense-in-depth validation, sandboxing
- **How to Handle LLM Streams That Survive Reconnects** (https://upstash.com/blog/resumable-llm-streams) — Redis-backed persistence, reconnection patterns

### Tertiary (LOW confidence)
- None — all sources verified with official docs or multiple corroborating sources

---
*Research completed: 2026-02-14*
*Ready for roadmap: yes*
