# STATE.md -- GSD-Docs Industrial

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-14)

**Core value:** Engineers can create, manage, and review FDS/SDS projects through a visual web interface that guides them through the full document lifecycle
**Current focus:** Phase 10.1 UAT found 5 issues (2 blockers, 2 major, 1 minor) — needs discuss → plan → fix cycle

## Current Position

- Phase: 10.1 of 17 (Discussion Behavior Rework) — COMPLETE
- Plan: 9 of 9 in current phase (all 9 plans complete)
- Status: Phase 10.1 complete — all 5 UAT issues resolved (Plans 08 + 09)
- Last activity: 2026-02-17 - Plan 09 complete (UAT fixes 1D + 1E: Gesprekken tab + chat history)

## Progress

Progress: [████████████░░░░░░░░] 59% (10 of 17 phases complete)

v1.0 milestone: 7 phases, 33 plans - Complete ✓
v2.0 milestone: 10 phases, 21 plans - Phase 10 complete

## Performance Metrics

**Velocity (v1.0):**
- Total plans completed: 33
- Total execution time: 8 days
- 89/89 requirements satisfied

**v2.0 (in progress):**
- Plans completed: 13 of 21
- Phase 8: 3/3 plans complete ✓
- Phase 9: 2/2 plans complete ✓
- Phase 10: 4/4 plans complete ✓
- Phase 10.1: 9/9 plans complete ✓
- Files created: ~155
- Last completed: Phase 10.1 Plan 09 (UAT fixes: Gesprekken tab + chat history)

## Accumulated Context

**From v1.0:**
- 14 `/doc:*` commands with proven workflow (discuss → plan → write → verify → review → assemble → export)
- Domain knowledge in 194 files: templates, section structures, verification criteria, prompt patterns
- SPECIFICATION.md v2.7.0 is SSOT for document generation logic
- 4 project types (A/B/C/D) with distinct workflow templates
- Typicals library (CATALOG.json) for SDS matching
- Bilingual Dutch/English support throughout

**v2.0 architecture:**
- FastAPI backend replaces Claude Code as orchestrator
- React frontend replaces terminal as UI
- Claude API (Anthropic SDK) for LLM access
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
- **FastAPI + React stack**: Full control over UI, proper web architecture, model-agnostic
- **LLM provider abstraction**: Enables local model swap in v3.0
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

### Roadmap Evolution

- Phase 10.1 inserted after Phase 10: Discussion behavior rework (URGENT)

## Blockers

None — Phase 10.1 UAT issues fully resolved:
- 1A: Question loop / repetition (blocker) — FIXED in Plan 08 (hard cap + anti-repetition)
- 1B: Decision summary timing (major) — FIXED in Plans 08 + 09 (silent accumulation + check-in payload + frontend batch reveal)
- 1C: Foundation question format (minor) — FIXED in Plan 08 (options field in prompt)
- 1D: Gesprekken tab not clickable (major) — FIXED in Plan 09 (loadConversation + tab switch)
- 1E: Chat history lost on reopen (blocker) — FIXED in Plan 09 (loadConversation fetches full history)

## Session Continuity

Last session: 2026-02-17
Stopped at: Phase 10.1 Plan 09 complete (UAT fixes 1D + 1E: Gesprekken tab + chat history)
Resume file: .planning/phases/10.1-discussion-behavior-rework/.continue-here.md

**Next step:** Phase 10.1 complete. Run UAT re-verification, then proceed to next phase.

---
*Last updated: 2026-02-17*
