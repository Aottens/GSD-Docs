---
phase: 10-discussion-workflow-chat-interface
plan: 02
subsystem: api
tags: [fastapi, sse, discussion-workflow, v1.0-extraction, prompts]

# Dependency graph
requires:
  - phase: 10-01
    provides: Conversation and Message models, PhaseInfo Pydantic schema
provides:
  - Phase timeline API with filesystem-derived status
  - Discussion API with SSE streaming for chat interface
  - Context API for CONTEXT.md generation
  - DiscussionEngine service orchestrating v1.0 workflow
  - ContextGenerator service with 100-line limit
  - Chat-optimized prompts extracted from v1.0 source files
affects: [10-03, 10-04]

# Tech tracking
tech-stack:
  added: [sse-starlette, EventSourceResponse]
  patterns: [SSE streaming for chat, filesystem-derived status, v1.0 pattern extraction]

key-files:
  created:
    - backend/app/prompts/__init__.py
    - backend/app/prompts/discuss_phase.py
    - backend/app/services/discussion_engine.py
    - backend/app/services/context_generator.py
    - backend/app/api/phases.py
    - backend/app/api/discussions.py
    - backend/app/api/context.py
  modified:
    - backend/app/api/__init__.py
    - backend/app/main.py

key-decisions:
  - "Extracted 40 content type keywords mapping to 9 content types from v1.0 discuss-phase.md"
  - "Extracted gray area patterns for 7 content types with probe questions from v1.0"
  - "Phase status derived from filesystem artifacts (CONTEXT.md, PLAN.md, SUMMARY.md) not database"
  - "SSE streaming via sse-starlette EventSourceResponse for real-time chat"
  - "ContextGenerator enforces 100-line limit per v1.0 Pitfall 7 mitigation"

patterns-established:
  - "Pattern 1: Content type detection using keyword mapping from v1.0"
  - "Pattern 2: Gray area topic selection with probe questions at functional spec depth"
  - "Pattern 3: SSE event streaming for chat with message_delta, message_complete, error, done events"
  - "Pattern 4: Filesystem-derived status instead of database status fields"

# Metrics
duration: 6 min
completed: 2026-02-15
---

# Phase 10 Plan 02: Discussion API Routes Summary

**FastAPI discussion workflow APIs with SSE streaming, v1.0 pattern extraction (40 keywords, 7 content types), and filesystem-derived phase status**

## Performance

- **Duration:** 6 min
- **Started:** 2026-02-15T20:38:43Z
- **Completed:** 2026-02-15T20:45:19Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Extracted v1.0 content type keywords (40 keywords for 9 content types) and gray area patterns (7 content types with probe questions)
- Created DiscussionEngine service orchestrating v1.0 workflow with chat-optimized prompts
- Created ContextGenerator service enforcing 100-line limit
- Built phase timeline API with filesystem-derived status
- Built discussion API with SSE streaming for real-time chat responses
- Built context API for CONTEXT.md generation and retrieval
- All routers registered and server starts cleanly

## Task Commits

Each task was committed atomically:

1. **Task 1: Discussion prompts module and discussion engine service** - `1a9d356` (feat)
   - backend/app/prompts/__init__.py
   - backend/app/prompts/discuss_phase.py (40 keywords, 7 content types, chat-optimized prompt builder)
   - backend/app/services/discussion_engine.py (v1.0 workflow orchestration)
   - backend/app/services/context_generator.py (100-line limit enforcement)

2. **Task 2: Phase timeline API, discussion API with SSE, context API, and router registration** - `c44bf12` (feat)
   - backend/app/api/phases.py (filesystem-derived status)
   - backend/app/api/discussions.py (SSE streaming via EventSourceResponse)
   - backend/app/api/context.py (CONTEXT.md generation)
   - backend/app/api/__init__.py (router exports)
   - backend/app/main.py (router registration)

## Files Created/Modified

**Created:**
- `backend/app/prompts/__init__.py` - Prompts package
- `backend/app/prompts/discuss_phase.py` - V1.0 extracted patterns (CONTENT_TYPE_KEYWORDS, GRAY_AREA_PATTERNS, system prompt builder)
- `backend/app/services/discussion_engine.py` - Discussion workflow orchestration with v1.0 patterns
- `backend/app/services/context_generator.py` - CONTEXT.md generation with 100-line limit
- `backend/app/api/phases.py` - Phase timeline API with filesystem-derived status
- `backend/app/api/discussions.py` - Discussion CRUD + SSE streaming endpoints
- `backend/app/api/context.py` - CONTEXT.md generation and retrieval endpoints

**Modified:**
- `backend/app/api/__init__.py` - Added phases, discussions, context to exports
- `backend/app/main.py` - Registered new routers

## Decisions Made

1. **V1.0 fidelity in extraction**: Read v1.0 source files FIRST before implementing any discussion logic. Extracted exact patterns:
   - Content type keywords from discuss-phase.md lines 128-140 (40 keywords mapping to 9 content types)
   - Gray area patterns from discuss-phase.md lines 164-214 (7 content types with specific probe questions)
   - CONTEXT.md structure from templates/context.md (XML tags: domain, decisions, specifics, deferred)
   - Project type phases from CLAUDE-CONTEXT.md

2. **Chat-optimized prompts**: Built `DISCUSSION_SYSTEM_PROMPT` by extracting core patterns from v1.0, not verbatim injection:
   - Role and phase boundary enforcement
   - Content type detection results
   - Gray area probing at FULL functional spec depth
   - Scope creep redirection to deferred ideas
   - Summary after each topic
   - Questions in project language (Dutch/English)
   - Delta framing for Type C/D projects

3. **Filesystem-derived phase status**: Phase status is NOT stored in database. Derived from artifact existence:
   - CONTEXT.md → "discussed"
   - PLAN.md → "planned"
   - SUMMARY.md → "written"
   - VERIFICATION.md → "verified"
   - REVIEW.md → "reviewed"

4. **SSE streaming for chat**: Use sse-starlette EventSourceResponse for real-time streaming:
   - Events: message_delta (chunks), message_complete, question_card, summary_card, error, done
   - Persistent connection for continuous updates during AI response generation

5. **100-line CONTEXT.md limit**: ContextGenerator enforces v1.0 Pitfall 7 mitigation with priority tiers:
   - Priority 1: Decisions that change what gets written (keep)
   - Priority 2: Specific technical values (keep)
   - Priority 3: General approach notes (compress or omit)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Backend APIs complete for discussion workflow. Ready for Phase 10 Plan 03 (Frontend Timeline Component).

Provides:
- Phase timeline API at `/api/projects/{project_id}/phases`
- Discussion API at `/api/projects/{project_id}/discussions` with SSE streaming
- Context API at `/api/projects/{project_id}/context/{phase_number}`

Frontend can now:
- Display phase timeline with status derived from filesystem
- Create discussions and stream AI responses via SSE
- Show real-time chat interface with message deltas
- Generate and retrieve CONTEXT.md files

## Self-Check: PASSED

All created files verified:
- backend/app/prompts/__init__.py ✓
- backend/app/prompts/discuss_phase.py ✓
- backend/app/services/discussion_engine.py ✓
- backend/app/services/context_generator.py ✓
- backend/app/api/phases.py ✓
- backend/app/api/discussions.py ✓
- backend/app/api/context.py ✓

All commits verified:
- 1a9d356 (Task 1) ✓
- c44bf12 (Task 2) ✓

---
*Phase: 10-discussion-workflow-chat-interface*
*Completed: 2026-02-15*
