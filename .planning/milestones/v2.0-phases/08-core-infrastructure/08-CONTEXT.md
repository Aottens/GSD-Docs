# Phase 8: Core Infrastructure & Project Management - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Foundation web GUI with project management — engineers can create FDS projects through a step-by-step wizard, browse all projects in a dashboard, and open projects into a three-panel working view. Backend provides FastAPI foundation with LLM abstraction. Reference file management, discussion workflows, and document generation are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Dashboard & project browsing
- Card grid layout (not table) — each card shows project name, type badge (A/B/C/D), language, current phase, progress bar, and last modified date
- Filter tabs for status slicing: Active, Completed, All
- Search bar with sort dropdown (by date, name, type) within each tab
- Recent projects section at top showing 3-4 most recently accessed projects

### Project creation flow
- 3-step wizard:
  - Step 1: Project name + description
  - Step 2: Type classification (A/B/C/D) presented as visual selectable cards with title, short description, and example use case per type
  - Step 3: Language selection (Dutch/English) + confirm
- After wizard completes, engineer lands directly in the project working view

### Project working view
- Three-panel layout: left sidebar (navigation) + center (main content) + right panel (context/chat)
- Right panel is always visible — chat and context always accessible alongside main content
- When a project is first opened, center panel shows a project overview: summary card with project name, type, language, progress, and quick actions
- Left sidebar contents: Claude's discretion based on what makes sense for the workflow

### Visual identity & design
- Modern & polished aesthetic — Vercel/Stripe-style with bold typography, smooth animations, dark accents
- Both light and dark mode with toggle
- Brandable design system — neutral base with a theming system so company can plug in their colors/logo later
- Tailwind CSS + shadcn/ui for styling and components

### Claude's Discretion
- Left sidebar navigation structure and contents
- Exact card layout dimensions and spacing
- Animation details and transitions
- Loading states and skeleton designs
- Error state handling and messaging
- Backend architecture details (FastAPI structure, SQLite schema, LLM abstraction layer)

</decisions>

<specifics>
## Specific Ideas

- Dashboard cards should feel like Vercel's project dashboard — modern, clean, informative at a glance
- Type classification step should use visual cards similar to how Stripe presents pricing tiers — each option clearly differentiated
- Three-panel layout inspired by IDE layouts (VS Code) — persistent panels, not modal overlays

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-core-infrastructure*
*Context gathered: 2026-02-15*
