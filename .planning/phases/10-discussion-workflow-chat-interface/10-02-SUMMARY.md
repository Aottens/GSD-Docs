---
phase: 10-discussion-workflow-chat-interface
plan: 02
subsystem: ui
tags: [react, typescript, tanstack-query, shadcn, tailwind, lucide]

# Dependency graph
requires:
  - phase: 10-01
    provides: New backend phase API with filesystem-derived status, cli_command field, context-files endpoint, PhaseStatusResponse schema without conversation_id

provides:
  - Frontend cleanup: discussions feature directory deleted (14 files)
  - Updated PhaseStatus type: cli_command added, conversation_id/discussing/available_actions removed
  - ContextFilesData interface for context-files endpoint
  - ProjectWorkspace stripped of Sheet/ChatPanel/Bot/assistant panel code
  - ProjectNavigation with 5 tabs only (no Gesprekken)
  - PhasePopover reworked: CLI command with click-to-copy, CONTEXT decisions list, verification score
  - FaseringTab reworked: CLI command per phase card, no action buttons
  - usePhaseContextFiles hook for lazy context-files fetching
  - TypeScript compiles with zero errors

affects: [phase-11, phase-12, phase-13, phase-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CLI command display with click-to-copy using navigator.clipboard + sonner toast"
    - "Lazy context-files fetch: only when popover open AND phase has context/verification"
    - "PhasePopover wraps PhaseNode as PopoverTrigger — node is pure display, popover handles interaction"

key-files:
  created: []
  modified:
    - frontend/src/features/timeline/types/phase.ts
    - frontend/src/features/timeline/components/PhasePopover.tsx
    - frontend/src/features/timeline/components/FaseringTab.tsx
    - frontend/src/features/timeline/components/PhaseTimeline.tsx
    - frontend/src/features/timeline/components/PhaseNode.tsx
    - frontend/src/features/timeline/hooks/usePhaseStatus.ts
    - frontend/src/features/projects/ProjectWorkspace.tsx
    - frontend/src/features/projects/components/ProjectNavigation.tsx

key-decisions:
  - "PhaseNode uses plain <button> element wrapped by PopoverTrigger — no onClick prop needed, PopoverTrigger handles click"
  - "usePhaseContextFiles enabled guard: isOpen AND (has_context OR has_verification) — avoids unnecessary API calls for phases without context files"
  - "CliCommandBlock extracted as local component in both PhasePopover and FaseringTab — avoids cross-file dependency for a small UI piece"

patterns-established:
  - "CLI command display: monospace code block with ghost Copy button triggering navigator.clipboard and sonner toast"
  - "Lazy popover data: useQuery with enabled flag tied to popover open state"

requirements-completed: [WORK-01, WORK-02]

# Metrics
duration: 25min
completed: 2026-03-20
---

# Phase 10 Plan 02: Frontend Cleanup and Timeline Rework Summary

**Discussions feature deleted (14 files), PhasePopover and FaseringTab reworked to show CLI commands with click-to-copy replacing action buttons, TypeScript compiles clean**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-20T20:20:00Z
- **Completed:** 2026-03-20T20:45:00Z
- **Tasks:** 2 auto tasks complete, 1 checkpoint pending human verification
- **Files modified:** 8

## Accomplishments

- Deleted entire `frontend/src/features/discussions/` directory (14 files: ChatPanel, ConversationHistory, ChatInput, MessageBubble, MessageList, QuestionCard, SummaryCard, SummaryPanel, TopicSelectionCard, CompletionCard, ContextPreview, useDiscussionStream, useConversationHistory, conversation types)
- Updated `PhaseStatus` type: added `cli_command: string | null`, added `ContextFilesData` interface, removed `conversation_id`, `discussing` status, and `available_actions`
- Stripped `ProjectWorkspace` of all Sheet/ChatPanel/Bot/ConversationHistory/handlePhaseAction code
- Removed Gesprekken tab from `ProjectNavigation` (6 → 5 nav items, MessageSquare import removed)
- Reworked `PhasePopover`: CLI command with click-to-copy button, lazy-loaded CONTEXT.md decisions list, verification score badge — no more action buttons
- Reworked `FaseringTab`: CLI command per phase card with copy button — no action buttons, no discussion links
- Added `usePhaseContextFiles` hook to `usePhaseStatus.ts` for the new `context-files` backend endpoint
- Simplified `PhaseNode`: removed onClick prop and Clock icon, uses plain `<button>` wrapped by PopoverTrigger
- `PhaseTimeline`: removed `onAction` prop, passes `projectId` to `PhasePopover`
- Zero TypeScript compile errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete discussions, update types, clean workspace/navigation** - `8e1c9bd` (feat)
2. **Task 2: Rework PhasePopover, FaseringTab, PhaseTimeline, PhaseNode, usePhaseStatus** - `7eb5fc0` (feat)

**Plan metadata commit:** pending (after checkpoint)

## Files Created/Modified

- `frontend/src/features/timeline/types/phase.ts` - PhaseStatus type (cli_command added, conversation_id/discussing removed), ContextFilesData interface added
- `frontend/src/features/timeline/hooks/usePhaseStatus.ts` - Added usePhaseContextFiles hook for context-files endpoint
- `frontend/src/features/timeline/components/PhasePopover.tsx` - CLI command display with copy, context decisions, verification score; removed action buttons
- `frontend/src/features/timeline/components/FaseringTab.tsx` - CLI command per card, progress checklist only; removed action buttons and discussion links
- `frontend/src/features/timeline/components/PhaseTimeline.tsx` - Removed onAction prop, added projectId to PhasePopover
- `frontend/src/features/timeline/components/PhaseNode.tsx` - Simplified: no onClick, no Clock icon, plain button element
- `frontend/src/features/projects/ProjectWorkspace.tsx` - Removed Sheet/ChatPanel/Bot/ConversationHistory/handlePhaseAction
- `frontend/src/features/projects/components/ProjectNavigation.tsx` - Removed Gesprekken tab and MessageSquare import

## Decisions Made

- PhaseNode uses a plain `<button>` element instead of shadcn `Button` — PopoverTrigger from the parent PhasePopover handles the click interaction, so no `onClick` is needed on PhaseNode itself.
- `usePhaseContextFiles` enabled guard: `isOpen && (phase.has_context || phase.has_verification)` — context files are only fetched when popover is open AND the phase actually has context or verification artifacts. Prevents unnecessary API calls for phases that have no context files.
- `CliCommandBlock` is defined locally in both `PhasePopover.tsx` and `FaseringTab.tsx` rather than extracted to a shared utility. The component is small (15 lines) and the two use-sites have no other overlap, so extraction would add unnecessary coupling.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None — TypeScript compiled clean on first attempt.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Frontend is ready for visual verification (Task 3 checkpoint)
- Backend `context-files` endpoint (built in Plan 01) needs to be running for full popover experience
- After checkpoint approval: proceed to Phase 11 (next cockpit phase)
- Any pre-existing TypeScript warnings in unrelated files are out of scope

---
*Phase: 10-discussion-workflow-chat-interface*
*Completed: 2026-03-20*
