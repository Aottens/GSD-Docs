# Roadmap: GSD-Docs Industrial

**Created:** 2026-02-06

## Milestones

- ✅ **v1.0 CLI** - Phases 1-7 (shipped 2026-02-14)
- 🚧 **v2.0 GUI** - Phases 8-15 (in progress)

## Phases

<details>
<summary>✅ v1.0 CLI (Phases 1-7) - SHIPPED 2026-02-14</summary>

Complete Claude Code plugin for FDS/SDS document generation. 14 commands, 194 files, 50,263 lines. All 89 v1.0 requirements satisfied. See `milestones/v1.0-ROADMAP.md` for archived phase details.

</details>

### 🚧 v2.0 GUI (In Progress)

**Milestone Goal:** Web-based cockpit that provides status, preview, review, and export for the v1.0 CLI workflow. AI operations stay in CLI; GUI handles visual tasks that CLI can't do well. FastAPI backend serves as file/project management API; React frontend is the engineer's cockpit.

#### Phase 8: Core Infrastructure & Project Management

**Goal**: Foundation architecture supports all subsequent workflows with real-time communication, async file handling, LLM abstraction, and basic project management.

**Depends on**: Phase 7 (v1.0 shipped)

**Requirements**: PROJ-01, PROJ-02, PROJ-04, PROJ-05, SYST-04

**Success Criteria** (what must be TRUE):
  1. Engineer can create a new FDS project through the web GUI with type classification (A/B/C/D)
  2. Engineer can select project language (Dutch/English) during project creation
  3. Engineer can browse all projects in a dashboard with status and type indicators
  4. Engineer can open a project from the dashboard to its working view
  5. LLM provider abstracted behind interface for future local model support

**Plans**: 3 plans

Plans:
- [x] 08-01-PLAN.md — Backend foundation: FastAPI + SQLite + Alembic + Project CRUD API + LLM abstraction
- [x] 08-02-PLAN.md — Frontend foundation + Dashboard: Vite/React/Tailwind/shadcn setup + project card grid with filters
- [x] 08-03-PLAN.md — Project wizard + Working view: 3-step creation wizard + fixed sidebar workspace + slide-in assistant

#### Phase 9: Reference Library & File Management

**Goal**: Engineers can upload, browse, and manage reference files (shared and per-project) with defense-in-depth security validation.

**Depends on**: Phase 8

**Requirements**: PROJ-03, REFM-01, REFM-02, REFM-03, REFM-04, REFM-05

**Success Criteria** (what must be TRUE):
  1. Engineer can upload reference files during project creation
  2. Engineer can upload reference files via drag-and-drop (PDF, DOCX, images)
  3. Engineer can view and manage per-project reference files
  4. Engineer can access shared reference library (read-only, admin-managed)
  5. Engineer can override shared references with project-specific uploads
  6. Admin can manage shared reference library (add, remove, categorize files)

**Plans**: 2 plans

Plans:
- [x] 09-01-PLAN.md -- Backend: file/folder models, defense-in-depth validation, filesystem storage, complete REST API for uploads, downloads, management, and folder CRUD
- [x] 09-02-PLAN.md -- Frontend: drag-and-drop upload with progress, file browser with folders, PDF/DOCX/image preview panel, project files and shared library tabs, admin page, wizard step 4

#### Phase 10: Workflow Status & Cleanup

**Goal**: Clean up discussion engine code (superseded by CLI), keep phase timeline UI and status API, add CLI command guidance and context file display.

**Depends on**: Phase 9

**Requirements**: WORK-01, WORK-02

**Success Criteria** (what must be TRUE):
  1. Engineer can view phase timeline showing ROADMAP phases with completion status
  2. Engineer can see next recommended `/doc:*` CLI command per phase
  3. Engineer can view CONTEXT.md and VERIFICATION.md results when available
  4. Discussion engine code removed (backend conversation/chat models, frontend chat panel)
  5. Phase timeline and status API remain functional

**Historical note**: Phases 10 (original) and 10.1 built an embedded discussion chat engine. The cockpit pivot (2026-03-20) determined that recreating CLI conversation UX in a webapp doesn't work — it feels forced compared to the CLI. Discussion code will be removed in this phase. Phase 10/10.1 directories preserved as historical record.

**Plans**: 2 plans

Plans:
- [x] 10-01-PLAN.md — Backend cleanup + rework: remove discussion/LLM code, extract PROJECT_TYPE_PHASES, rework phase API for filesystem-based status, add CLI command mapping, add context-files endpoint, create Alembic migration
- [x] 10-02-PLAN.md — Frontend cleanup + rework: remove discussions feature, remove assistant panel, update phase types, rework PhasePopover with CLI command display + context/verification info, update FaseringTab

#### Phase 11: Document Preview & Outline

**Goal**: Engineers can view rendered FDS content, navigate section outlines, see generated section plans and wave assignments, with Mermaid diagram rendering.

**Depends on**: Phase 10

**Requirements**: WORK-03, WORK-04, OUTP-01, DOCG-01

**Success Criteria** (what must be TRUE):
  1. Engineer can view document outline tree with expandable/collapsible sections
  2. Engineer can navigate to a specific section from the outline tree
  3. Engineer can preview rendered document content (markdown → HTML, not raw files)
  4. Engineer can view Mermaid diagrams rendered inline
  5. Engineer can view generated section plans and wave assignments

**Plans**: 3 plans

Plans:
- [x] 11-01-PLAN.md — Backend document API + type contracts: outline endpoint (fds-structure.json tree builder with Type C/D baseline handling), section content endpoint, PLAN.md frontmatter parser, Pydantic schemas, TypeScript types, pytest test scaffolding
- [x] 11-02-PLAN.md — Frontend document components: DocumentsTab (ResizablePanelGroup), OutlinePanel + OutlineNode (tree with status icons/wave badges), ContentPanel + SectionBlock (markdown rendering), MermaidDiagram (SVG with fallback), PlanCard + EmptySectionCard, React Query hooks with polling, scroll-spy
- [x] 11-03-PLAN.md — Workspace integration: enable Documents navigation, wire DocumentsTab into ProjectWorkspace, enable "Documenten bekijken" quick action, human verification checkpoint

#### Phase 12: Review Interface

**Goal**: Engineers can review sections with approve/reject/request-changes workflow, view verification results and standards compliance from CLI output.

**Depends on**: Phase 11

**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06, QUAL-07, QUAL-08

**Success Criteria** (what must be TRUE):
  1. Engineer can conduct section-by-section approve/reject/request-changes review
  2. Engineer can provide text feedback per section
  3. Engineer can view verification results (gaps, severity, recommendations) from CLI output files
  4. Engineer can see gap closure cycle status (verify → re-plan → re-write)
  5. Engineer can approve or reject verification results before proceeding
  6. Engineer can view PackML/ISA-88 standards compliance results
  7. Engineer can view standards violations with references to standard sections

**Plans**: 3 plans

Plans:
- [x] 12-01-PLAN.md — Backend verification-detail endpoint + frontend type contracts, data hook, ReviewContext with localStorage persistence
- [x] 12-02-PLAN.md — Frontend review components: VerificationDetailPanel, ReviewActionBar, StandardsBadge, ReviewSummary, SectionBlock extension
- [x] 12-03-PLAN.md — Integration wiring: OutlineNode badge evolution, ContentPanel prop threading, DocumentsTab ReviewProvider, human verification

#### Phase 13: Export & Assembly

**Goal**: Engineers can assemble FDS with cross-reference resolution, export to DOCX with corporate styling, view SDS scaffolding with typicals matching.

**Depends on**: Phase 12

**Requirements**: OUTP-02, OUTP-03, OUTP-04, OUTP-05, OUTP-06, OUTP-07

**Success Criteria** (what must be TRUE):
  1. Engineer can trigger FDS assembly with cross-reference resolution (file processing, no AI)
  2. Engineer can export FDS/SDS to DOCX with corporate styling via Pandoc
  3. Engineer can see export progress during DOCX generation
  4. Engineer can view SDS scaffolding with typicals matching confidence scores
  5. Engineer can see "NEW TYPICAL NEEDED" indicators for unmatched equipment
  6. Engineer can generate documents in Dutch or English based on project setting

**Plans**: 4 plans

Plans:
- [ ] 13-01-PLAN.md — Backend assembly + export services: type contracts, FDS assembly (cross-ref resolution, section ordering), Pandoc DOCX export, SSE streaming endpoint, version history, pytest tests
- [ ] 13-02-PLAN.md — Backend SDS scaffolding service: typicals matching algorithm (I/O 40%, Jaccard 30%, states 20%, category 10%), confidence scoring, CATALOG.json loading, skeleton mode, pytest tests
- [ ] 13-03-PLAN.md — Frontend Export tab: three-stage pipeline (Samenstellen/Exporteren/Downloaden), SSE progress hook, export options (mode/language), version history table, workspace navigation wiring
- [ ] 13-04-PLAN.md — Frontend SDS tab: typicals matching table (sortable/filterable), confidence color coding, NIEUW TYPICAL NODIG badges, expandable match detail with CLI hints, workspace wiring

#### Phase 14: Project Setup & CLI Handoff

**Goal**: Engineers can create projects via GUI with guided reference document collection, then complete intelligent setup via CLI. Late-arriving documents can be added and re-processed.

**Depends on**: Phase 13

**Requirements**: PROJ-01, PROJ-02, PROJ-04

**Success Criteria** (what must be TRUE):
  1. Wizard step 4 shows document-type checklist (old FDS, P&ID, machine spec, risk assessment) instead of generic upload
  2. Engineer can mark document types as "not available / will add later"
  3. Project overview shows setup status: which reference docs are present vs missing, and CLI command to complete setup
  4. Backend exposes project setup state endpoint (metadata + reference file paths + document type coverage) for CLI consumption
  5. After CLI setup completes, GUI automatically reflects scaffolded phases, sections, and outline
  6. Engineer can upload additional references later via Referenties tab and trigger re-analysis

**Plans**: 3 plans

Plans:
- [ ] 14-01-PLAN.md — Backend: DOC_TYPE_CONFIG, File.doc_type + Project.skipped_doc_types columns, Alembic migration, setup-state endpoint, doc-types endpoint, upload doc_type extension, tests
- [ ] 14-02-PLAN.md — Frontend wizard + shared components: CliCommandBlock extraction, TypeScript types, useSetupState hook, useFileUpload doc_type extension, Step4DocTypeChecklist replacement
- [ ] 14-03-PLAN.md — Frontend overview + referenties: SetupStatusSection in ProjectOverview, DocCoverageSection in Referenties tab, doc-type upload prompt, human verification checkpoint

#### Phase 15.1: CLI ↔ GUI UX Polish (Gap Closure)

**Goal**: Smooth the CLI↔GUI handoff experience — add change notifications, clean up stale UI, deduplicate components.

**Depends on**: Phase 14

**Requirements**: SYST-01 (partial)

**Gap Closure**: Closes gaps from v2.0 milestone audit (2026-03-26)

**Success Criteria** (what must be TRUE):
  1. When polled data changes (setup-state, phase status, document outline), a toast notification appears alerting the engineer
  2. Phase popover includes "Bekijk documenten" link that navigates to Documenten tab filtered to that phase's sections
  3. ProjectOverview quick actions: "Discussie starten" button removed (feature deleted in cockpit pivot), "Referenties uploaden" navigates to Referenties tab
  4. EmptySectionCard and PhasePopover import shared CliCommandBlock instead of private duplicates
  5. Orphaned ChatContextPanel.tsx removed

**Plans**: 2 plans

Plans:
- [ ] 15.1-01-PLAN.md — UI cleanup: remove discussion button, wire referenties uploaden, deduplicate CliCommandBlock, add Bekijk documenten link, delete ChatContextPanel
- [ ] 15.1-02-PLAN.md — Change notification hooks: useRef-based polling change detection for setup-state, phase timeline, document outline with sonner toasts

#### Phase 15.2: Review Flow Safety (Gap Closure)

**Goal**: Prevent export of unreviewed content and enable multi-phase review.

**Depends on**: Phase 15.1

**Requirements**: QUAL-04, QUAL-05, QUAL-06

**Gap Closure**: Closes gaps from v2.0 milestone audit (2026-03-26)

**Success Criteria** (what must be TRUE):
  1. Export assembly shows warning banner when any section has "rejected" or "unreviewed" review status, with option to proceed or return to review
  2. DocumentsTab allows selecting which phase to review (dropdown or tabs) instead of only the highest-numbered verified phase
  3. Review decisions persist across tab navigation and page refresh (localStorage verified)

**Plans**: 2 plans

Plans:
- [ ] 15.2-01-PLAN.md — Export warning banner: reviewStorage utility, rejected-sections Alert in AssemblyPipeline, onNavigateToDocs prop threading
- [ ] 15.2-02-PLAN.md — Multi-phase selector + persistence: phase Select dropdown in DocumentsTab, user-controlled selectedPhaseNumber state, persistence indicator in ReviewSummary

#### Phase 15: Production Deployment (ON HOLD)

**Goal**: Application deployed on VM with Nginx reverse proxy, crash recovery, and CLI compatibility verification.

**Depends on**: Phase 15.2

**Requirements**: SYST-01, SYST-02, SYST-03

**Success Criteria** (what must be TRUE):
  1. System detects incomplete phases and offers resume from last checkpoint
  2. Application deploys on VM with Nginx reverse proxy and systemd services
  3. Project files remain compatible with v1.0 CLI /doc:* commands

**Plans**: TBD

Plans:
- [ ] 15-01: TBD
- [ ] 15-02: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Framework Foundation | v1.0 | 4/4 | Complete | 2026-02-07 |
| 2. Discuss + Plan | v1.0 | 4/4 | Complete | 2026-02-08 |
| 3. Write + Verify | v1.0 | 5/5 | Complete | 2026-02-10 |
| 4. State Management | v1.0 | 5/5 | Complete | 2026-02-13 |
| 5. Complete-FDS + Standards | v1.0 | 5/5 | Complete | 2026-02-14 |
| 6. Knowledge Transfer | v1.0 | 5/5 | Complete | 2026-02-14 |
| 7. SDS + Export | v1.0 | 5/5 | Complete | 2026-02-14 |
| 8. Core Infrastructure | v2.0 | 3/3 | Complete | 2026-02-15 |
| 9. File Management | v2.0 | 2/2 | Complete | 2026-02-15 |
| ~~10. Discussion Workflow~~ | v2.0 | 4/4 | Superseded | 2026-02-15 |
| ~~10.1 Discussion behavior rework~~ | v2.0 | 7/9 | Superseded | - |
| 10. Workflow Status & Cleanup | 2/2 | Complete    | 2026-03-20 | - |
| 11. Document Preview & Outline | 3/3 | Complete    | 2026-03-21 | - |
| 12. Review Interface | 3/3 | Complete    | 2026-03-21 | - |
| 13. Export & Assembly | 4/4 | Complete    | 2026-03-21 | - |
| 14. Project Setup & CLI Handoff | 3/3 | Complete   | 2026-03-22 | - |
| 15.1 CLI ↔ GUI UX Polish | 2/2 | Complete    | 2026-03-26 | - |
| 15.2 Review Flow Safety | v2.0 | 0/2 | Gap closure | - |
| 15. Production Deployment | v2.0 | 0/2 | On hold | - |

---
*Roadmap created: 2026-02-06*
*Last updated: 2026-03-30 -- Phase 15.2 plans created*
