---
phase: 10-discussion-workflow-chat-interface
plan: 03
subsystem: frontend-timeline
tags: [ui, timeline, phases, navigation, integration]
dependency_graph:
  requires: [10-02-discussion-api]
  provides: [phase-timeline-ui, fasering-tab, phase-actions]
  affects: [project-workspace]
tech_stack:
  added: [radix-popover, phase-timeline-components]
  patterns: [tanstack-query-hooks, status-colored-icons, dutch-ui]
key_files:
  created:
    - frontend/src/features/timeline/types/phase.ts
    - frontend/src/features/timeline/hooks/usePhaseStatus.ts
    - frontend/src/features/timeline/components/PhaseTimeline.tsx
    - frontend/src/features/timeline/components/PhaseNode.tsx
    - frontend/src/features/timeline/components/PhasePopover.tsx
    - frontend/src/features/timeline/components/FaseringTab.tsx
    - frontend/src/components/ui/popover.tsx
  modified:
    - frontend/src/features/projects/ProjectWorkspace.tsx
    - frontend/src/features/projects/components/ProjectNavigation.tsx
decisions:
  - "Phase timeline as horizontal bar above workspace (always visible, compact design)"
  - "PhasePopover for inline status summary and action buttons (only valid actions enabled)"
  - "FaseringTab for full detailed phase view accessible from sidebar navigation"
  - "Status colors: green (completed), blue (in_progress), amber (intermediate), gray (not_started)"
  - "All UI text in Dutch per project conventions"
  - "usePhaseTimeline hook with 10s refetch interval to keep status current"
metrics:
  duration_minutes: 6
  completed_date: 2026-02-15
---

# Phase 10 Plan 03: Frontend Phase Timeline Summary

**JWT auth with refresh rotation using jose library**

Frontend phase timeline: horizontal timeline bar above workspace showing all project phases with colored status icons, phase node popovers with contextual actions, and Fasering tab for full detailed phase overview. Engineers can trigger discussions and navigate workflow states visually.

## Tasks Completed

### Task 1: Phase timeline components (PhaseTimeline, PhaseNode, PhasePopover) with API hook

**Status:** ✅ Complete
**Commit:** `7b4500f`

**What was built:**
- Installed shadcn Popover component (Radix UI)
- Created TypeScript types for `PhaseStatus` and `PhaseTimelineData`
- Created `usePhaseTimeline` TanStack Query hook fetching from `/api/projects/{id}/phases` with 10s refetch interval
- Created `PhaseNode` component with status-colored icons (CheckCircle2, Clock, Circle) and sub-status badges
- Created `PhasePopover` component with status summary, progress indicators, and Dutch action buttons
- Created `PhaseTimeline` horizontal bar component rendering all phases with connector lines

**Key decisions:**
- Status colors: green-500 (completed), blue-500 (in_progress), amber-500 (intermediate completed), gray (not_started)
- Compact design: PhaseNode fits in horizontal bar with icon + "Fase N" label + optional sub-status
- PhasePopover shows progress checkmarks for `has_context`, `has_plans`, `has_content`, `has_verification`, `has_review`
- Only valid next actions enabled based on `available_actions` array from API
- All UI text in Dutch: "Bespreken", "Plannen", "Schrijven", "Verifiëren", "Beoordelen"

**Files created:**
- `frontend/src/features/timeline/types/phase.ts` (17 lines)
- `frontend/src/features/timeline/hooks/usePhaseStatus.ts` (18 lines)
- `frontend/src/features/timeline/components/PhaseNode.tsx` (60 lines)
- `frontend/src/features/timeline/components/PhasePopover.tsx` (150 lines)
- `frontend/src/features/timeline/components/PhaseTimeline.tsx` (57 lines)
- `frontend/src/components/ui/popover.tsx` (shadcn component)

**Verification:**
- ✅ TypeScript compiles cleanly (`npx tsc --noEmit`)
- ✅ Build succeeds (`npm run build`)
- ✅ All timeline components exist with proper exports
- ✅ Popover component installed and functional

### Task 2: Fasering tab and workspace integration

**Status:** ✅ Complete
**Commit:** `915e595`

**What was built:**
- Created `FaseringTab` component with vertical timeline layout showing all phases expanded
- Integrated `PhaseTimeline` bar above workspace content (always visible, between header and two-panel layout)
- Enabled "Fases" navigation item in `ProjectNavigation` sidebar
- Wired phase actions to open ChatPanel via controlled Sheet state
- Created `handlePhaseAction` handler for "discuss", "view-discussion", and other actions
- Added toast notifications for placeholder actions

**Key decisions:**
- PhaseTimeline sits between breadcrumb header and two-panel layout (shrink-0 to prevent collapse)
- FaseringTab shows full phase details: goal text, status badge, progress checklist, action buttons, discussion links
- "Bespreken" action opens chat panel with `setDiscussionPhase(phaseNumber)` and `setChatOpen(true)`
- ChatPanel receives `projectId`, `phaseNumber`, `conversationId`, and `onClose` props
- Section ID is 'fasering' (Dutch) to match navigation, renders FaseringTab component
- Placeholder toast for actions not yet implemented (plan, write, verify, review)

**Files created:**
- `frontend/src/features/timeline/components/FaseringTab.tsx` (223 lines)

**Files modified:**
- `frontend/src/features/projects/ProjectWorkspace.tsx`: Added PhaseTimeline, FaseringTab, handlePhaseAction, controlled Sheet state
- `frontend/src/features/projects/components/ProjectNavigation.tsx`: Enabled 'fasering' navigation item

**Verification:**
- ✅ TypeScript compiles cleanly
- ✅ Build succeeds
- ✅ PhaseTimeline imported and rendered above workspace
- ✅ FaseringTab renders when "Fases" navigation clicked
- ✅ "Fases" navigation no longer disabled

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed missing SummaryCard component**
- **Found during:** Task 1 build verification
- **Issue:** `MessageBubble.tsx` imported `SummaryCard` component but file didn't exist, blocking build
- **Fix:** Created `SummaryCard.tsx` with confirm/edit/add actions for discussion decisions
- **Files modified:** `frontend/src/features/discussions/components/SummaryCard.tsx` (created)
- **Commit:** `fix(10-02): add missing discussion components...` (separate fix commit)

**2. [Rule 1 - Bug] Fixed verbatimModuleSyntax type import errors**
- **Found during:** Task 1 build verification
- **Issue:** TypeScript errors: "is a type and must be imported using a type-only import when 'verbatimModuleSyntax' is enabled"
- **Fix:** Changed `import { Type }` to `import type { Type }` in:
  - `useConversationHistory.ts` (Conversation, Message)
  - `useDiscussionStream.ts` (Message, StreamEvent)
  - `MessageBubble.tsx` (Message)
  - `MessageList.tsx` (Message)
  - `ChatInput.tsx` (KeyboardEvent)
- **Files modified:** 5 discussion hook/component files
- **Commit:** Included in Plan 02 fix commit

**3. [Rule 3 - Blocking] Installed missing shadcn components**
- **Found during:** Task 1 build verification after fixing type imports
- **Issue:** `TopicSelectionCard.tsx` imported `Checkbox` and `Tooltip` components that weren't installed
- **Fix:** Ran `npx shadcn@latest add checkbox tooltip` to install components
- **Files created:** `frontend/src/components/ui/checkbox.tsx`, `frontend/src/components/ui/tooltip.tsx`
- **Commit:** Included in Plan 02 fix commit

**4. [Rule 1 - Bug] Fixed implicit any type in TopicSelectionCard**
- **Found during:** Build after installing checkbox/tooltip
- **Issue:** `onCheckedChange` callback parameter `checked` had implicit any type
- **Fix:** Added explicit type annotation: `(checked: boolean) => setDiscretionEnabled(checked as boolean)`
- **Files modified:** `frontend/src/features/discussions/components/TopicSelectionCard.tsx`
- **Commit:** Included in Plan 02 fix commit

**5. [Rule 1 - Bug] Fixed unused import in PhasePopover**
- **Found during:** Task 1 build verification
- **Issue:** `Badge` component imported but never used
- **Fix:** Removed `import { Badge } from '@/components/ui/badge'` line
- **Files modified:** `frontend/src/features/timeline/components/PhasePopover.tsx`
- **Commit:** Included in Task 1 commit

**6. [Rule 1 - Bug] Fixed unused variable in ChatPanel**
- **Found during:** Task 2 build verification
- **Issue:** `setDeferredCount` variable declared but never used
- **Fix:** Changed `const [deferredCount, setDeferredCount] = useState(0)` to `const [deferredCount] = useState(0)`
- **Files modified:** `frontend/src/features/discussions/components/ChatPanel.tsx`
- **Commit:** `feat(10-02): add ChatPanel...` (separate commit)

**7. [Rule 1 - Bug] Fixed unused import in SummaryPanel**
- **Found during:** Task 2 build verification
- **Issue:** `ChevronDown` icon imported but never used
- **Fix:** Removed from import statement
- **Files modified:** `frontend/src/features/discussions/components/SummaryPanel.tsx`
- **Commit:** Included in Task 2 commit

## Discussion Components from Plan 02

During execution, several discussion components from Plan 02 were found uncommitted and blocking the build. These were fixed and committed separately:

**First batch (fix commit):**
- `SummaryCard.tsx` (created to fix missing import)
- `ChatInput.tsx` (type import fixes)
- `MessageBubble.tsx` (type import fixes)
- `MessageList.tsx` (type import fixes)
- `QuestionCard.tsx` (already existed)
- `TopicSelectionCard.tsx` (type fixes)
- `useConversationHistory.ts` (type import fixes)
- `useDiscussionStream.ts` (type import fixes)
- `conversation.ts` types (already existed)

**Second batch (separate feat commit for Plan 02):**
- `ChatPanel.tsx` (main chat interface with tabs)
- `ConversationHistory.tsx` (history view)
- `SummaryPanel.tsx` (decision management)

These components were created in Plan 02 execution but not committed, causing build errors in Plan 03. They were committed separately to maintain clean commit history.

## Integration Notes

**PhaseTimeline placement:**
- Sits between breadcrumb header and two-panel layout
- Always visible (shrink-0 to prevent collapse)
- Horizontal scrollable if many phases
- Compact design: py-2 px-4 with border-b

**Chat panel integration:**
- Controlled Sheet state via `chatOpen`, `setChatOpen`
- `discussionPhase` and `discussionConversationId` state track current discussion context
- `handlePhaseAction` handler dispatches "discuss" → set phase + open chat
- "view-discussion" → set phase + open chat (TODO: get conversationId from API)
- Other actions → show toast placeholder

**Navigation flow:**
- Timeline bar: click phase node → popover with actions → click "Bespreken" → chat opens
- Fasering tab: click "Fases" in sidebar → full detail view → click action button → chat opens
- Both routes converge on same `handlePhaseAction` handler

## Must-Haves Verification

**Truths:**
- ✅ Engineer sees horizontal timeline bar above workspace showing all project phases with colored status icons
- ✅ Engineer can click a phase node to see popover with status summary and action buttons
- ✅ Only valid next actions are enabled in the popover (dependency chain enforced via `available_actions`)
- ✅ Engineer can navigate to Fasering tab for full detailed phase view
- ✅ Phase status reflects actual filesystem state (Besproken, Gepland, Geschreven, Geverifieerd, Beoordeeld via `sub_status`)

**Artifacts:**
- ✅ `frontend/src/features/timeline/components/PhaseTimeline.tsx` (57 lines, provides horizontal timeline bar)
- ✅ `frontend/src/features/timeline/components/PhasePopover.tsx` (150 lines, provides inline popover)
- ✅ `frontend/src/features/timeline/components/FaseringTab.tsx` (223 lines, provides full detailed phase view)
- ✅ `frontend/src/features/timeline/hooks/usePhaseStatus.ts` (18 lines, TanStack Query hook fetching `/api/projects/{id}/phases`)

**Key Links:**
- ✅ `usePhaseStatus.ts` → `/api/projects/{id}/phases` via `api.get()` call (pattern: `api\\.get.*phases`)
- ✅ `PhaseTimeline.tsx` → `ProjectWorkspace.tsx` via rendered above workspace content (pattern: `PhaseTimeline`)
- ✅ `PhasePopover.tsx` → discussion start via action button triggers discussion (pattern: `onStartDiscussion|onAction`)

## Self-Check: PASSED

**Created files verified:**
```bash
FOUND: frontend/src/features/timeline/types/phase.ts
FOUND: frontend/src/features/timeline/hooks/usePhaseStatus.ts
FOUND: frontend/src/features/timeline/components/PhaseTimeline.tsx
FOUND: frontend/src/features/timeline/components/PhaseNode.tsx
FOUND: frontend/src/features/timeline/components/PhasePopover.tsx
FOUND: frontend/src/features/timeline/components/FaseringTab.tsx
FOUND: frontend/src/components/ui/popover.tsx
```

**Commits verified:**
```bash
FOUND: 7b4500f (Task 1: timeline components)
FOUND: 915e595 (Task 2: workspace integration)
```

All created files exist on disk. All commits exist in git history. Build succeeds. TypeScript compiles cleanly.

## Success Criteria

- [x] PhaseTimeline renders as horizontal bar above workspace with all project phases
- [x] Phase nodes show colored icons (green/blue/amber/gray) with sub-status text
- [x] PhasePopover shows status summary and action buttons (Dutch labels, only valid actions enabled)
- [x] FaseringTab shows full detailed view accessible from "Fases" sidebar navigation
- [x] usePhaseTimeline hook fetches from /api/projects/{id}/phases with 10s refetch
- [x] "Bespreken" action opens discussion in chat panel
- [x] Build passes, no TypeScript errors

## Next Steps

**For Plan 04 (Discussion Chat UI):**
- Implement full chat interface in ChatPanel
- Wire discussion stream to SSE endpoint
- Handle question cards and summary cards
- Implement topic selection flow
- Connect phase actions to actual discussion creation
