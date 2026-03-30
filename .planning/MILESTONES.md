# Milestones

## v2.0 GUI (Shipped: 2026-03-30)

**Phases completed:** 11 phases, 26 plans, 56 tasks
**Requirements:** 31/33 satisfied (94% — SYST-02/SYST-03 deferred, Phase 15 ON HOLD)
**Timeline:** 43 days (2026-02-15 to 2026-03-30)
**Files:** 155 source files (37 Python + 118 TypeScript/TSX), ~14,652 LOC
**Git range:** 236 commits (25f539f..05b516b)

**Delivered:** A web-based cockpit that provides status, preview, review, and export for the v1.0 CLI workflow. FastAPI backend as file/project management API; React frontend as engineer's cockpit. AI operations stay in CLI; GUI handles visual tasks.

**Key accomplishments:**

1. FastAPI + React cockpit with project dashboard, guided wizard (type A/B/C/D + language), and tabbed workspace layout
2. Reference library with drag-and-drop upload, shared/per-project management, PDF/DOCX preview, admin interface
3. Document preview with outline tree, Mermaid diagram rendering, plan/wave display, scroll-spy navigation
4. Section review with approve/reject/request-changes workflow, per-section verification display, PackML/ISA-88 standards compliance
5. FDS assembly + DOCX export with SSE progress + SDS scaffolding with typicals matching confidence scoring
6. CLI-GUI integration: phase timeline with CLI command guidance, setup state tracking, change notifications, export safety gates

**Known gaps (deferred):**

- SYST-02: VM deployment with Nginx + systemd (Phase 15 ON HOLD)
- SYST-03: CLI compatibility verification (Phase 15 ON HOLD)

**Tech debt carried forward:**

- Phase 8/9 SUMMARYs lack requirements_completed frontmatter (early-phase pattern)
- Settings nav item ("Instellingen") exists as disabled placeholder

**Archive:** See `milestones/v2.0-ROADMAP.md`, `milestones/v2.0-REQUIREMENTS.md`, `milestones/v2.0-MILESTONE-AUDIT.md`

---

## v1.0 MVP (Shipped: 2026-02-14)

**Phases completed:** 7 phases, 33 plans
**Requirements:** 89/89 satisfied (100%)
**Timeline:** 8 days (2026-02-07 to 2026-02-14)
**Files:** 194 files, 50,263 lines inserted
**Git range:** 28f5797..4e6d257

**Delivered:** A complete Claude Code plugin for writing industrial FDS/SDS documents, with 14 commands under the `/doc:*` namespace covering the full lifecycle from project creation through DOCX export.

**Key accomplishments:**

1. Plugin framework with 14 commands under /doc:* namespace, running alongside GSD without interference
2. FDS section templates (equipment module, state machine, interface) with bilingual Dutch/English support
3. Parallel write + goal-backward verify loop with context isolation and self-correcting gap closure
4. Crash-resilient state management with forward-only recovery and partial write detection
5. Full FDS assembly with cross-reference resolution, opt-in standards compliance (PackML/ISA-88), and versioning
6. Knowledge transfer pipeline (RATIONALE.md, EDGE-CASES.md, Fresh Eyes review, review-phase)
7. SDS generation with typicals matching and DOCX export with corporate styling (Pandoc + huisstijl.docx)

**Tech debt carried forward:**

- install.ps1 incomplete command listing (cosmetic, all commands functional)
- REQUIREMENTS.md traceability table not maintained (resolved by archival)

**Archive:** See `milestones/v1.0-ROADMAP.md`, `milestones/v1.0-REQUIREMENTS.md`, `milestones/v1.0-MILESTONE-AUDIT.md`

---
