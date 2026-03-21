---
phase: 11-document-preview-outline
plan: "02"
subsystem: ui
tags: [react, react-query, mermaid, react-markdown, resizable-panels, typescript, document-preview]

requires:
  - phase: 11-01
    provides: Backend API endpoints for document outline and section content, TypeScript types in document.ts

provides:
  - "DocumentsTab: root split-pane component with ResizablePanelGroup (25/75 default)"
  - "OutlinePanel + OutlineNode: recursive tree with status icons, wave badges, tooltips, preview snippets"
  - "ContentPanel + SectionBlock: document-style markdown rendering with react-markdown + remarkGfm"
  - "MermaidDiagram: async SVG rendering with module-level init flag and code block fallback"
  - "PlanCard: plan details with wave badge, dependencies, truths/vereisten, description"
  - "EmptySectionCard: Dutch CLI command card with copy button"
  - "useDocumentOutline: React Query hook polling at 15s"
  - "useSectionContent: React Query hook polling at 30s"
  - "useScrollSpy: IntersectionObserver with 600ms programmatic scroll suppression"

affects: [workspace-integration, tab-wiring]

tech-stack:
  added:
    - mermaid@11.13.0
  patterns:
    - "React Query polling with refetchInterval + staleTime pair"
    - "Module-level singleton flag for mermaid initialization (initMermaid)"
    - "IntersectionObserver scroll-spy with isScrolling.current ref guard"
    - "Wave color mapping function (wave 1=blue, 2=green, 3=amber, 4+=purple)"
    - "CliCommandBlock pattern (inline, not shared) per FaseringTab convention"

key-files:
  created:
    - frontend/src/features/documents/hooks/useDocumentOutline.ts
    - frontend/src/features/documents/hooks/useSectionContent.ts
    - frontend/src/features/documents/hooks/useScrollSpy.ts
    - frontend/src/features/documents/components/DocumentsTab.tsx
    - frontend/src/features/documents/components/OutlinePanel.tsx
    - frontend/src/features/documents/components/OutlineNode.tsx
    - frontend/src/features/documents/components/ContentPanel.tsx
    - frontend/src/features/documents/components/SectionBlock.tsx
    - frontend/src/features/documents/components/MermaidDiagram.tsx
    - frontend/src/features/documents/components/PlanCard.tsx
    - frontend/src/features/documents/components/EmptySectionCard.tsx
  modified:
    - frontend/package.json (mermaid added)

key-decisions:
  - "mermaid initialized once via module-level flag: prevents re-init bugs across multiple diagrams"
  - "SectionContent extracted as inner component in SectionBlock: isolates useSectionContent hook call per section, avoiding unconditional hook ordering issues"
  - "CliCommandBlock defined locally in EmptySectionCard (not shared): matches FaseringTab convention of small co-located utilities"

patterns-established:
  - "Document feature directory: hooks/ + components/ + types/ under features/documents/"
  - "Scroll-spy pattern: IntersectionObserver + isScrolling ref + 600ms timeout suppression"
  - "React Query document keys: documentKeys.outline(projectId) and documentKeys.sectionContent(projectId, sectionId)"

requirements-completed: [WORK-03, WORK-04, OUTP-01, DOCG-01]

duration: 3min
completed: 2026-03-21
---

# Phase 11 Plan 02: Frontend Document Preview Summary

**11-file split-pane document cockpit with ResizablePanelGroup, recursive outline tree, react-markdown typography, Mermaid SVG rendering, and React Query polling (15s outline / 30s content)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T07:51:47Z
- **Completed:** 2026-03-21T07:54:51Z
- **Tasks:** 3
- **Files modified:** 13 (11 created + package.json + package-lock.json)

## Accomplishments

- Installed mermaid@11.13.0 and created all 11 feature files in a single pass
- Split-pane document cockpit: ResizablePanelGroup with 25% outline tree (15-40% drag range) and 75% content panel
- Complete document rendering pipeline: outline tree with IntersectionObserver scroll-spy, react-markdown with document typography (leading-[1.7], max-width 720px), Mermaid SVG fallback to code block, PlanCard with truths/description, EmptySectionCard with CLI copy

## Task Commits

Each task was committed atomically:

1. **Task 1: Install mermaid + create hooks + OutlinePanel + OutlineNode** - `24ef649` (feat)
2. **Task 2: ContentPanel + SectionBlock + MermaidDiagram + PlanCard + EmptySectionCard** - `53b334a` (feat)
3. **Task 3: DocumentsTab wiring + ResizablePanelGroup** - `415cd83` (feat)

**Plan metadata:** (docs commit — TBD)

## Files Created/Modified

- `frontend/src/features/documents/hooks/useDocumentOutline.ts` - React Query hook: GET /documents/outline, 15s polling with documentKeys
- `frontend/src/features/documents/hooks/useSectionContent.ts` - React Query hook: GET /documents/sections/:id/content, 30s polling, encodeURIComponent for section IDs
- `frontend/src/features/documents/hooks/useScrollSpy.ts` - IntersectionObserver tracking active section with 600ms scroll suppression ref
- `frontend/src/features/documents/components/DocumentsTab.tsx` - Root: ResizablePanelGroup horizontal, collectSectionIds(), loading + error states
- `frontend/src/features/documents/components/OutlinePanel.tsx` - Left panel: scrollable tree with Documentstructuur heading, skeleton loading, Dutch error
- `frontend/src/features/documents/components/OutlineNode.tsx` - Tree node: Circle/Clipboard/FileText/CheckCircle2 status icons, wave badge with Tooltip, preview snippet, chevron expand/collapse with aria-labels
- `frontend/src/features/documents/components/ContentPanel.tsx` - Right panel: max-w-[720px], Nog geen inhoud empty state, SectionBlock rendering
- `frontend/src/features/documents/components/SectionBlock.tsx` - Section renderer: id=section-${id} scroll targets, ReactMarkdown + remarkGfm, PlanCard/EmptySectionCard for planned/empty
- `frontend/src/features/documents/components/MermaidDiagram.tsx` - Mermaid SVG via mermaid.render(), one-time module init, dark theme detection, error fallback to code pre
- `frontend/src/features/documents/components/PlanCard.tsx` - Plan details: wave badge (G1-G4), Afhankelijkheden (Geen fallback), Vereisten truths list, planInfo.description
- `frontend/src/features/documents/components/EmptySectionCard.tsx` - Border-dashed card: Dutch copy, CliCommandBlock with Gekopieerd! toast
- `frontend/package.json` - Added mermaid@11.13.0 dependency

## Decisions Made

- SectionContent extracted as inner component within SectionBlock to isolate the `useSectionContent` hook call per-section (prevents unconditional hook ordering violations)
- CliCommandBlock defined locally in EmptySectionCard (not a shared component), matching the FaseringTab.tsx convention of co-located small utilities
- mermaid initialized once via module-level `mermaidInitialized` flag — prevents re-initialization errors when multiple MermaidDiagram instances render on the same page

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All 11 document feature files compiled with zero TypeScript errors
- DocumentsTab is ready to be wired into the workspace tab router (next: integrate into WorkspaceLayout or equivalent tab container)
- Backend API from Plan 01 is the data source — no additional backend work needed for this feature
- Mermaid renders correctly with dark/light theme detection at init time

## Self-Check: PASSED

All 11 created files verified present. All 3 task commits verified in git log.

---
*Phase: 11-document-preview-outline*
*Completed: 2026-03-21*
