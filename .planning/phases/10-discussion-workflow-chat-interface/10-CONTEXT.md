# Phase 10: Workflow Status & Cleanup - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove the superseded discussion engine code (backend + frontend), keep the phase timeline UI and status API, add CLI command guidance per phase, and display CONTEXT.md/VERIFICATION.md results in phase popovers. The GUI becomes a status cockpit — it shows where the project is and what CLI command to run next, but doesn't trigger AI operations.

</domain>

<decisions>
## Implementation Decisions

### Cleanup scope
- Remove ALL LLM infrastructure: `llm/` directory, `prompts/`, `services/llm_service.py`, and all LLM dependencies (litellm, sse-starlette for streaming, etc.)
- Remove ALL discussion code: `models/conversation.py`, `api/discussions.py`, `api/context.py`, `services/discussion_engine.py`, `services/conversation_state.py`, `services/decision_extractor.py`, `services/context_generator.py`, `services/structured_output_parser.py`
- Remove frontend discussion feature: entire `features/discussions/` directory (ChatPanel, ChatInput, MessageBubble, QuestionCard, CompletionCard, ContextPreview, ConversationHistory, SummaryCard, SummaryPanel, TopicSelectionCard)
- Create Alembic migration to DROP conversation and message tables — clean slate, no orphaned tables
- Remove the "Gesprekken" (Conversations) sidebar tab entirely — sidebar keeps only Fasering (phases) and Bestanden (files)
- Remove the assistant panel (slide-in Sheet from Phase 8) entirely — future phases add their own panels from scratch if needed
- Backend becomes pure file/project management API with zero LLM dependencies

### CLI command display
- Static mapping from phase status to recommended `/doc:*` command (e.g., 'not started' → `/doc:discuss-phase N`, 'discussed' → `/doc:plan-phase N`, etc.)
- Show in phase popover only — keeps timeline clean, users click phase node for details + next action
- CLI command displayed as monospace code block with click-to-copy button
- Remove old action buttons from phase popover (e.g., "Start Discussie") — GUI doesn't trigger operations anymore

### Context file display
- Backend reads CONTEXT.md and VERIFICATION.md directly from project filesystem (no DB sync, no filesystem watching)
- Display in phase popover (not sidebar, not separate tab)
- CONTEXT.md: show key decisions only (extract `<decisions>` section as bullet list, skip canonical_refs/code_context/deferred)
- VERIFICATION.md: show score + gap count (e.g., "4/5 levels passed, 2 gaps") with severity breakdown — quick health indicator

### Phase status rework
- Phase status derived from filesystem: CONTEXT.md exists → 'discussed', PLAN files exist → 'planned', CONTENT.md exists → 'written', VERIFICATION.md exists → 'verified'
- Backend knows v1.0 FDS directory structure (hardcoded layout: phases/, ROADMAP.md, STATE.md, etc.) — if CLI changes, update backend
- Configurable PROJECT_ROOT via .env — projects stored at PROJECT_ROOT/{project_id}/
- Keep existing PROJECT_TYPE_PHASES mapping for phase list per project type (A/B/C/D) — no ROADMAP.md parsing needed

### Claude's Discretion
- Exact implementation of filesystem status detection logic
- How to handle edge cases (e.g., partial files, corrupted CONTEXT.md)
- Phase popover layout and styling for the new content
- Migration ordering and backward compatibility

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.0 FDS directory structure
- `gsd-docs-industrial/SPECIFICATION.md` — SSOT for document generation logic, defines project directory layout and phase structure
- `gsd-docs-industrial/templates/` — Project type templates (A/B/C/D) with ROADMAP structures

### Existing backend code (to understand what to remove)
- `backend/app/models/conversation.py` — Conversation/Message SQLAlchemy models (TO REMOVE)
- `backend/app/api/discussions.py` — Discussion API endpoints (TO REMOVE)
- `backend/app/api/context.py` — Context generation endpoints (TO REMOVE)
- `backend/app/services/discussion_engine.py` — Core discussion engine (TO REMOVE)
- `backend/app/llm/` — LLM provider abstraction (TO REMOVE)
- `backend/app/prompts/discuss_phase.py` — Discussion prompts (TO REMOVE)

### Existing frontend code (to understand what to remove vs keep)
- `frontend/src/features/discussions/` — Entire discussion feature (TO REMOVE)
- `frontend/src/features/timeline/` — Phase timeline components (TO KEEP + MODIFY)
- `frontend/src/features/timeline/components/PhasePopover.tsx` — Phase popover (TO MODIFY for CLI commands + context display)
- `frontend/src/features/timeline/components/FaseringTab.tsx` — Sidebar tab (TO KEEP, remove Gesprekken tab reference)

### Existing phase status logic
- `backend/app/models/phase.py` — Phase status model, PhaseInfo Pydantic schema (TO REWORK)
- `backend/app/api/phases.py` — Phase timeline API (TO REWORK for filesystem-based status)
- `backend/app/schemas/` — Pydantic schemas for phase/conversation (TO CLEAN UP)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `features/timeline/PhaseTimeline.tsx` — Horizontal phase timeline bar (keep, works well)
- `features/timeline/PhaseNode.tsx` — Phase node with status-colored icons (keep, modify status logic)
- `features/timeline/PhasePopover.tsx` — Phase detail popover (keep, rework content for CLI commands + context)
- `features/timeline/FaseringTab.tsx` — Sidebar phase detail tab (keep, simplify)
- `components/ui/` — shadcn/ui components (Button, Popover, Badge, etc.)
- `lib/api.ts` — API client with error handling and 204 explicit check
- Tailwind v4 with @theme — CSS-first configuration
- Sonner for toast notifications

### Established Patterns
- All UI in Dutch — maintain this
- Fixed sidebar + workspace layout (Phase 8 pattern) — stays
- Phase status colored icons in timeline (Phase 10 pattern) — stays, update colors for new statuses
- PROJECT_TYPE_PHASES mapping for deriving phases per project type — stays

### Integration Points
- Workspace component — remove assistant Sheet, keep sidebar with Fasering + Bestanden tabs
- Phase timeline bar — update PhasePopover content
- Backend API router — remove discussion/context routes, rework phase routes for filesystem-based status
- Alembic migration chain — new migration to drop conversation tables
- Backend dependencies — remove litellm, sse-starlette, and other LLM-related packages

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for the cleanup and new features.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 10-workflow-status-cleanup*
*Context gathered: 2026-03-20*
