---
phase: 10-discussion-workflow-chat-interface
plan: 04
subsystem: frontend-discussions
tags: [ui, chat, sse, discussions, summary-panel]
dependency_graph:
  requires: [10-02-discussion-api, 10-03-timeline]
  provides: [chat-panel, discussion-stream, summary-panel, conversation-history]
  affects: [project-workspace, chat-context-panel]
tech_stack:
  - react-markdown
  - remark-gfm
  - sse (fetch ReadableStream)
---

# Plan 10-04: Frontend Chat Panel & Discussion UI

## Summary

Implemented the frontend chat interface for discussion workflow: ChatPanel with SSE streaming, hybrid question cards (option chips + text input), running summary panel with editable decisions, topic selection cards, conversation history, and workspace integration.

## Completed Tasks

| # | Task | Commit |
|---|------|--------|
| 1 | Chat infrastructure: types, SSE hook, message components, question cards | 5fd4b6f |
| 2 | ChatPanel, SummaryPanel, ConversationHistory, workspace integration | d177153 |
| 3 | Visual verification (human checkpoint) | Approved |

## Key Files

### Created
- `frontend/src/features/discussions/types/conversation.ts` — TypeScript types for conversations, messages, decisions, SSE events
- `frontend/src/features/discussions/hooks/useDiscussionStream.ts` — SSE streaming hook with ReadableStream
- `frontend/src/features/discussions/hooks/useConversationHistory.ts` — TanStack Query hooks for conversation CRUD
- `frontend/src/features/discussions/components/MessageBubble.tsx` — Chat message with markdown rendering
- `frontend/src/features/discussions/components/MessageList.tsx` — Scrollable message list with auto-scroll
- `frontend/src/features/discussions/components/QuestionCard.tsx` — Hybrid question card (chips + text)
- `frontend/src/features/discussions/components/TopicSelectionCard.tsx` — Multi-select topic card
- `frontend/src/features/discussions/components/SummaryCard.tsx` — Topic summary with confirm/edit/add
- `frontend/src/features/discussions/components/ChatInput.tsx` — Input with file attach button
- `frontend/src/features/discussions/components/ChatPanel.tsx` — Sheet-based panel with 3 tabs
- `frontend/src/features/discussions/components/SummaryPanel.tsx` — Editable decision panel with PATCH API
- `frontend/src/features/discussions/components/ConversationHistory.tsx` — Past discussions browser

### Modified
- `frontend/src/features/projects/ProjectWorkspace.tsx` — ChatPanel replaces ChatContextPanel, controlled Sheet state
- `frontend/src/features/projects/components/ProjectNavigation.tsx` — "Gesprekken" tab enabled

## Decisions
- react-markdown + remark-gfm for message rendering (tables, lists, code)
- fetch + ReadableStream for SSE (EventSource only supports GET)
- Optimistic updates for decision editing with rollback on error

## Deviations
- None

## Self-Check: PASSED
- [x] All components export and compile
- [x] Build passes
- [x] ChatPanel renders in Sheet
- [x] Human verification approved

## Post-Execution Fixes
- Fixed phases API to use PROJECT_TYPE_PHASES from project type (was hardcoded stub)
- Fixed phase locking (dependency chain enforcement)
- Fixed discussion creation endpoint (body parsing, project DB lookup)
- Fixed SSE format alignment between backend and frontend
- Fixed DISCUSSION_SYSTEM_PROMPT template escaping

---
*Completed: 2026-02-15*
*Duration: ~8 minutes + fixes*
