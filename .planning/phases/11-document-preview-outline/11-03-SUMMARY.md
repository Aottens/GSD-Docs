---
phase: 11-document-preview-outline
plan: 03
subsystem: ui
tags: [react, workspace, navigation, integration]

requires:
  - phase: 11-02
    provides: DocumentsTab component with split-pane layout
provides:
  - Documents navigation enabled in project sidebar
  - DocumentsTab wired into workspace activeSection switch
  - "Documenten bekijken" quick action button functional
  - Content duplication fix (per-section extraction)
  - Custom resizable split pane (replaces react-resizable-panels)
affects: [12-section-review]

tech-stack:
  added: []
  patterns:
    - Custom draggable divider (mousedown/mousemove/mouseup on document)

key-files:
  created: []
  modified:
    - frontend/src/features/projects/ProjectWorkspace.tsx
    - frontend/src/features/projects/components/ProjectNavigation.tsx
    - frontend/src/features/projects/components/ProjectOverview.tsx
    - frontend/src/features/documents/components/DocumentsTab.tsx
    - frontend/src/features/documents/components/ContentPanel.tsx
    - frontend/src/features/documents/components/SectionBlock.tsx
    - backend/app/api/documents.py

key-decisions:
  - "Replaced react-resizable-panels with custom draggable divider — library Separator only allowed shrinking, not enlarging"
  - "Backend _extract_section_content slices SUMMARY.md per-section to prevent content duplication"
  - "SectionBlock only renders SectionContent for leaf nodes (parent sections are structural containers)"
  - "ContentPanel hasContent check made recursive to handle nested empty-state detection"

patterns-established:
  - "Custom resize: mousedown on handle → mousemove/mouseup on document for reliable cross-element drag tracking"
  - "Leaf-only rendering: parent outline nodes are structural, only leaf nodes fetch and render content"
---

## What was built

Wired the Phase 11 document preview feature into the live application. Engineers can now access the document preview from the project workspace via sidebar navigation or the "Documenten bekijken" quick action button.

## Bug fixes during verification

Two bugs discovered and fixed during visual verification:

1. **Content duplication**: Multi-section SUMMARYs caused each child section to render the entire file. Fixed by adding `_extract_section_content()` to slice per-section, and restricting `SectionContent` rendering to leaf nodes only.

2. **Resize handle broken**: `react-resizable-panels` v4.6.4 `Separator` only allowed shrinking the outline panel, not enlarging. Replaced with a custom draggable divider using `mousedown`/`mousemove`/`mouseup` events on `document` — works reliably in both directions with min/max constraints (180px–480px).

## Verification

Human-verified in browser:
- Documenten nav item enabled, navigates to DocumentsTab
- Split-pane layout with working bidirectional resize
- Outline tree with section numbers and status badges
- Content rendering: markdown typography, tables, Mermaid diagrams as SVG
- Empty section cards with CLI command hint and copy button
- "Documenten bekijken" quick action works
- All text in Dutch
