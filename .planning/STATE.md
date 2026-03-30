---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: GUI
status: unknown
stopped_at: Completed 16-01-PLAN.md
last_updated: "2026-03-30T19:20:55.277Z"
progress:
  total_phases: 12
  completed_phases: 11
  total_plans: 26
  completed_plans: 26
  percent: 100
---

# STATE.md -- GSD-Docs Industrial

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-14)

**Core value:** Engineers can create, manage, and review FDS/SDS projects through a visual web cockpit that handles status, preview, review, and export — AI operations stay in CLI
**Current focus:** Phase 16 — per-section-verification-display

## Current Position

Phase: 16 (per-section-verification-display) — EXECUTING
Plan: 1 of 1

## Progress

Progress: [██████████] 100% (Phase 14 complete — all 20 plans done)

v1.0 milestone: 7 phases, 33 plans - Complete ✓
v2.0 milestone: 7 phases — Phases 8, 9, 10 complete. Old 10/10.1 superseded by cockpit pivot. Phases 11-14 not started.

## Performance Metrics

**Velocity (v1.0):**

- Total plans completed: 33
- Total execution time: 8 days
- 89/89 requirements satisfied

**v2.0 (in progress):**

- Phase 8: 3/3 plans complete ✓
- Phase 9: 2/2 plans complete ✓
- Phase 10 (old): 4/4 plans complete — superseded by cockpit pivot
- Phase 10.1: 7/9 plans complete — superseded by cockpit pivot
- New phases 10-14: Phases 10, 11, 12 complete; phases 13-14 not started
- Files created: ~160
- Last completed: Phase 14 Plan 03 — SetupStatusSection, DocCoverageSection, doc-type upload prompt (2026-03-22)

## Accumulated Context

**From v1.0:**

- 14 `/doc:*` commands with proven workflow (discuss → plan → write → verify → review → assemble → export)
- Domain knowledge in 194 files: templates, section structures, verification criteria, prompt patterns
- SPECIFICATION.md v2.7.0 is SSOT for document generation logic
- 4 project types (A/B/C/D) with distinct workflow templates
- Typicals library (CATALOG.json) for SDS matching
- Bilingual Dutch/English support throughout

**v2.0 architecture (post-cockpit pivot):**

- FastAPI backend as file/project management API (no LLM orchestration)
- React frontend as companion cockpit (status, preview, review, export)
- AI operations stay in CLI (/doc:* commands via GitHub Copilot)
- SQLite for project/file metadata
- VM deployment with Nginx + systemd

**Phase 8 deliverables (now available):**

- FastAPI backend: project CRUD, health check, LLM provider abstraction (LiteLLM)
- React frontend: dashboard with filters/search/sort, 3-step wizard, workspace
- Workspace: fixed sidebar + slide-in Sheet for assistant panel
- All UI in Dutch, dark/light theme with FOUC prevention
- Tailwind v4 with shadcn/ui components

**Phase 9 deliverables (now available):**

- Backend: File/Folder models, defense-in-depth validation (5 layers), filesystem storage, complete REST API
- Frontend: Drag-and-drop upload with progress, file browser with folder navigation, inline PDF/DOCX/image preview
- File actions: delete (with confirmation), rename, replace, download, move between folders
- Project files and shared library tabs with override mechanism
- Admin library page at /admin/library
- 4-step project creation wizard with reference upload
- Toast notification system (sonner) for all file operations
- Default folder auto-creation per project type (A/B/C/D)

**Phase 10 deliverables (now available):**

- Backend: Conversation/Message models, discussion engine with v1.0 pattern extraction (40 keywords, 7 content types)
- Backend: Phase timeline API (status from DB), SSE streaming endpoints, context generator
- Frontend: Horizontal phase timeline bar with colored status nodes and popovers
- Frontend: ChatPanel with SSE streaming, question cards, summary panel, conversation history
- Frontend: FaseringTab with detailed phase view, "Gesprekken" tab in sidebar
- Phase dependency chain enforcement (locked phases until previous completes)
- Phases derived from PROJECT_TYPE_PHASES per project type (A/B/C/D)

## Decisions

See PROJECT.md Key Decisions table for full list.

Recent decisions affecting v2.0:

- **Cockpit pivot (2026-03-20)**: GUI is companion cockpit, not AI wrapper. Discussion engine (phases 10/10.1) proved that embedded chat feels forced vs CLI. Team has Claude via GitHub Copilot. GUI handles visual tasks; AI stays in CLI. 7 requirements dropped, phases 10-17 restructured to 10-14.
- **FastAPI + React stack**: Full control over UI, proper web architecture
- **No LLM orchestration in GUI**: Backend is file/project management API only
- **SQLite for metadata**: Lightweight, sufficient for 5-20 users
- **VM deployment**: No Docker per company policy
- **SQLite async with aiosqlite** (08-01): Async operations throughout, check_same_thread=False for compatibility
- **App starts without API key** (08-01): Development workflow before external service config
- **CORS origins localhost:5173** (08-01): Vite default port, configurable via env for production
- **Tailwind CSS v4 with @theme** (08-02): CSS-first configuration, cleaner than JS config
- **FOUC prevention inline script** (08-02): Apply dark class before React loads
- **Motion for spring animations** (08-02): Lightweight alternative to Framer Motion
- **Fixed sidebar + slide-in Sheet** (08-03): Replaces resizable panels — cleaner layout, no sizing constraints
- **All UI in Dutch** (08-03): Target engineering team preference, future phase adds language toggle
- **Type definitions from SPECIFICATION.md** (08-03): Domain-accurate A/B/C/D descriptions
- **Mock + Ollama for dev, no paid API**: MockLLMProvider for canned FDS responses + Ollama/LiteLLM for local models. Paid API only at production deploy
- **v1.0 fidelity (HARD RULE)**: Plans must reference specific v1.0 source files (path + section) for domain content. Executors must read v1.0 files before implementing. Verifiers must cross-check against v1.0 originals. No paraphrasing or simplifying domain content.
- **python-multipart 0.0.20** (09-01): Latest version compatible with Python 3.9.6 venv
- **Defense-in-depth file validation** (09-01): 5 layers (extension, sanitization, size, magic number, image verification)
- **Filesystem storage** (09-01): Files at uploads/{scope}/{project_id}/{folder}/{uuid}.ext, not BLOBs
- **Soft delete preserves files** (09-01): is_deleted flag only, files remain on disk
- **Admin auth via X-Admin-Key** (09-01): Simple header-based auth, empty key = dev mode
- **Sonner for toasts** (09-02): Lightweight toast notifications, fits shadcn/ui ecosystem
- **XHR for uploads** (09-02): Enables real per-file progress via upload.onprogress (fetch doesn't support this)
- **DeleteConfirmation inside SheetContent** (09-02): Radix Dialog focus trap requires nested rendering
- **204 explicit check in API client** (09-02): FastAPI sends content-type on empty 204 responses
- **JSON columns for conversation data** (10-01): summary_data and metadata_json use JSON for flexible schema evolution
- **PhaseInfo as Pydantic not SQLAlchemy** (10-01): Phase status derived from conversation records, not stored in DB
- **sse-starlette for streaming** (10-01): Server-Sent Events support for streaming discussion responses
- **Phase timeline as horizontal bar** (10-03): Always visible above workspace, compact design with status-colored icons
- **Phases from PROJECT_TYPE_PHASES** (10): Phase structure comes from project type definition (A/B/C/D), matching v1.0
- **Phase dependency chain** (10): Subsequent phases locked until previous completes
- **Discussion behavior needs rework** (10): Phase 10.1 planned for deeper discussion UX design
- **Chip selections as starting points** (10.1-02): Chip clicks send message but keep card open for follow-up questions (not final answers)
- **Reject reopens question in chat** (10.1-02): Rejecting a decision removes it and sends message to reopen discussion (no inline editing)
- **Freeform input always visible** (10.1-02): Text input always shown below chips for simpler interface (engineer can always type detailed answer)
- **Verbatim decision extraction is rule-based** (10.1-03): NEVER calls LLM, uses rule-based filler removal to preserve engineer's exact words (honors "no interpretation" requirement)
- **4-question rhythm enforced by state machine** (10.1-03): increment_question() returns string ('continue'/'check_in'/'force_check_in') with hard cap at 12 questions
- **Foundation phase auto-detected** (10.1-03): phase_number == 1 OR phase_goal contains foundation/intake/scope keywords, creates open-ended greeting instead of topic selection
- **CONTEXT.md compression uses 3-tier priority** (10.1-04): Priority 1 (prescriptive keywords: should, must, will, not) > Priority 2 (numeric values with units) > Priority 3 (general notes get compressed)
- **Preview endpoint has no side effects** (10.1-04): Returns CONTEXT.md content without saving to disk or changing conversation status
- **Finalize workflow suggests next step, no auto-advance** (10.1-04): Saves CONTEXT.md, marks conversation completed, returns "next_step: planning" message (engineer manually starts planning)
- **Completion detection works for both phase types** (10.1-04): Structured phases use all_topics_complete() trigger, Foundation phases use LLM completion_signal XML tag
- **Silent decision accumulation + check-in reveal** (10.1-08): No decision_captured SSE events during discussion; check-in event carries decisions + all_decisions payload for Beslissingen tab
- **Foundation area detection with fallback** (10.1-08): detect_covered_area_with_fallback() keyword matches first, cycles uncovered areas after 2+ questions when keywords don't match
- **Foundation questions with option chips** (10.1-08): GENERATE_FOUNDATION_QUESTION_PROMPT now generates options field matching regular topic JSON format
- **loadConversation pattern** (10.1-09): Fetches conversation + messages sequentially, filters system messages, populates all state atomically; extracted from hook as named function for direct calling
- **Completion detection via completionData state** (10.1-09): loadConversation sets completionData for completed convs; ChatPanel useEffect watches completionData to set viewMode='readonly'
- **Check-in card uses ReactMarkdown** (10.1-09): Backend _build_checkin_message() returns markdown bullets; check-in card renders via ReactMarkdown for correct display
- [Phase 10-discussion-workflow-chat-interface]: Filesystem status detection replaces conversation DB queries: phase status derived from CONTEXT.md/PLAN.md/SUMMARY.md/VERIFICATION.md/REVIEW.md presence
- [Phase 10-01]: STATUS_CLI_COMMANDS maps each phase status to next /doc:* CLI command via get_cli_command() helper
- [Phase 10-01]: config_phases.py is standalone module for project type definitions extracted from deleted prompts module
- [Phase 10]: PhaseNode uses plain button element wrapped by PopoverTrigger — no onClick prop needed
- [Phase 10]: usePhaseContextFiles enabled guard: isOpen AND has_context/has_verification — avoids API calls for phases without context files
- [Phase 10]: CliCommandBlock defined locally in PhasePopover and FaseringTab — small component, no shared coupling needed
- [Phase 11-01]: section_id:path type for FastAPI /sections/{section_id}/content route — dots in IDs handled correctly
- [Phase 11-01]: _build_outline_sections returns list[dict] for testability; Pydantic conversion at endpoint boundary
- [Phase 11-document-preview-outline]: SectionContent extracted as inner component in SectionBlock to isolate useSectionContent hook per section
- [Phase 11-document-preview-outline]: mermaid initialized once via module-level mermaidInitialized flag — prevents re-init bugs with multiple diagrams
- [Phase 12-review-interface]: useReviewContext returns ReviewContextValue | null (not throws) — avoids React Rules of Hooks violation when called outside provider
- [Phase 12-review-interface]: exportAsJson maps Dutch: goedgekeurd->Approved, opmerking->Comment, afgewezen->Flag (REVIEW.md template format)
- [Phase 12-review-interface]: Standards violations extracted via regex matching PackML/ISA-88/IEC/EN/NEN references in gap description text
- [Phase 12-review-interface]: Collapsible collapsed by default — engineer expands on demand, preserves reading flow
- [Phase 12-review-interface]: Phase-level truths shown on all leaf sections by design — VERIFICATION.md verifies phase-level truths, evidence_files filtering deferred
- [Phase 12-03]: Review status takes precedence over backend node.status in OutlineNode badge display per UI-SPEC Interaction Contract 5
- [Phase 12-03]: ProjectWorkspace selects most recent phase with has_verification=true via usePhaseTimeline — automatic review activation, no mode switch needed
- [Phase 12-03]: Conditional ReviewProvider in DocumentsTab — wraps content tree only when phaseNumber is defined, preserving backward compat for phases without verification
- [Phase 12-03]: overflow-auto (not overflow-hidden) required on ProjectWorkspace tab panels to preserve scroll on Overview/Fases tabs
- [Phase 13]: Draft mode injects CONCEPT header text into assembled markdown (not Pandoc watermark background)
- [Phase 13]: Version scheme FDS-v{major}.{minor}_{mode}_{language}.docx: minor increments per same mode+language run
- [Phase 13-export-assembly]: BOOL=DI/DO, INT/REAL=AI/AO for CATALOG interface I/O counting (sds-service)
- [Phase 13-export-assembly]: load_catalog returns None for empty typicals — triggers skeleton mode (sds-service)
- [Phase 13-export-assembly]: Expandable table rows use sibling TableRow (colSpan=5) instead of Collapsible wrapper for cleaner HTML table structure
- [Phase 13-export-assembly]: SdsTab uses overflow-auto without p-6 in workspace — component manages its own padding
- [Phase 13-export-assembly]: ExportTab owns mode/exportLanguage state — pipeline is single-tab, no cross-tab sharing needed (13-03)
- [Phase 13-export-assembly]: useAssemblyStream uses EventSource with eventSourceRef for cancel/cleanup, onerror sets isRunning=false (13-03)
- [Phase 14]: DOC_TYPE_CONFIG defines document type metadata for 4 project types (A/B/C/D) in config_phases.py
- [Phase 14]: skipped_doc_types stored as JSON string in String(500) column for 'Niet beschikbaar' persistence
- [Phase 14]: DocTypeRow extracted as local render function inside DocCoverageSection — avoids shared module for 5-line pattern
- [Phase 14]: projectType threaded from ProjectWorkspace through ReferenceManager to ProjectFilesTab as optional prop — backward compat preserved
- [Phase 14]: uploadFile exposed from useFileUpload return — needed for per-entry doc_type upload in wizard onSubmit
- [Phase 14]: DocTypeFileEntry exported from Step4DocTypeChecklist — consumed by ProjectWizard for typed selectedFiles state
- [Phase 14]: DocTypeRow extracted as local render component inside DocCoverageSection — avoids shared module for a 5-line render pattern
- [Phase 15.1]: CliCommandBlock deduplication: remove private copies from PhasePopover and EmptySectionCard, import shared component from @/features/timeline/components/CliCommandBlock
- [Phase 15.1]: Discussie starten button removed entirely (not disabled) — cockpit pivot makes discussion engine obsolete
- [Phase 15.1]: Bekijk documenten link in PhasePopover: shown only when phase.has_content AND onNavigateToDocs truthy, closes popover on click, prop threaded ProjectWorkspace -> PhaseTimeline -> PhasePopover
- [Phase 15.1]: Wrapper hook pattern for polling change-notification: wraps existing query hook, tracks prev fingerprint via useRef, returns same query object unchanged
- [Phase 15.1]: PhaseTimeline.tsx retains usePhaseTimeline directly — only ProjectWorkspace uses notification wrapper to prevent duplicate phase status toasts
- [Phase 15.2]: countAllRejected iterates Object.keys(localStorage) with prefix filter — works across all phases without knowing phase count
- [Phase 15.2]: Warning banner in AssemblyPipeline is non-blocking with local dismissed state that resets on re-mount
- [Phase 15.2]: selectedPhaseNumber is user-controlled state — useEffect only syncs activePhaseNumber prop when undefined, polling never overrides manual selection
- [Phase 15.2]: ReviewProvider key stability via selectedPhaseNumber: phaseNumber prop derived from user selection, not polling-derived activePhaseNumber, eliminating mid-session re-mount instability (QUAL-06)
- [Phase 15.3]: project_id appended as URL query string in useOverrideFile — FastAPI Query(...) reads from URL, not FormData body
- [Phase 16]: Regex /(?:sectie|section)\s+([\d.]+)/i with strict equality prevents substring false-positives (2.1 vs 2.10)
- [Phase 16]: IIFE pattern in JSX to scope sectionTruths variable within conditional render block
- [Phase 16]: ReviewActionBar renders outside ternary branches — always shown for leaf sections with verification

### Roadmap Evolution

- Phase 10.1 inserted after Phase 10: Discussion behavior rework (URGENT) — superseded by cockpit pivot
- **Cockpit pivot (2026-03-20)**: Phases 10-17 restructured to 10-14. Old phases 10/10.1 (discussion engine) superseded. New Phase 10 = Workflow Status & Cleanup (remove discussion code, keep timeline).

## Blockers

None — cockpit pivot clears all previous discussion-engine blockers.

## Session Continuity

Last session: 2026-03-30T19:17:46.358Z
Stopped at: Completed 16-01-PLAN.md

**Next step:** v2.0 milestone complete. All 8 phases, 20 plans delivered. Ready for production deployment or next milestone planning.

---
*Last updated: 2026-03-20*
