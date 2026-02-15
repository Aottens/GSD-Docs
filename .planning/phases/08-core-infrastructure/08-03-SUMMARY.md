---
phase: 08-core-infrastructure
plan: 03
subsystem: frontend-wizard-workspace
tags: [wizard, workspace, sheet, project-creation, slide-in]
dependency-graph:
  requires:
    - "08-01: Backend API for project CRUD"
    - "08-02: React/Tailwind/shadcn setup, dashboard, API client"
  provides:
    - "3-step project creation wizard (name → type → language)"
    - "Project working view with fixed sidebar + slide-in assistant"
    - "Full project lifecycle: dashboard → create → workspace → back"
  affects:
    - "Phase 9: Reference upload integrates into wizard step and workspace"
    - "Phase 10: Chat panel content replaces slide-in placeholder"
    - "Phase 11: Document outline populates sidebar navigation"
tech-stack:
  added:
    - "react-hook-form - Multi-step wizard form management"
    - "shadcn/ui Sheet - Slide-in panel for assistant"
    - "Motion (framer-motion) - Step transitions and card animations"
  patterns:
    - "Multi-step wizard with single form instance across steps"
    - "Fixed sidebar + full-width content + slide-in overlay"
    - "TypeCard visual selection (Stripe pricing tier style)"
key-files:
  created:
    - "frontend/src/features/wizard/ProjectWizard.tsx - 3-step wizard container"
    - "frontend/src/features/wizard/components/StepIndicator.tsx - Step progress bar"
    - "frontend/src/features/wizard/components/Step1NameDescription.tsx - Name/description input"
    - "frontend/src/features/wizard/components/Step2TypeClassification.tsx - Type A/B/C/D cards"
    - "frontend/src/features/wizard/components/Step3LanguageConfirm.tsx - Language + confirm"
    - "frontend/src/features/wizard/components/TypeCard.tsx - Visual type selection card"
    - "frontend/src/features/wizard/types.ts - Wizard form types"
    - "frontend/src/features/projects/ProjectWorkspace.tsx - Two-panel layout + sheet"
    - "frontend/src/features/projects/components/ProjectNavigation.tsx - Sidebar nav"
    - "frontend/src/features/projects/components/ProjectOverview.tsx - Project summary"
    - "frontend/src/features/projects/components/ChatContextPanel.tsx - Assistant placeholder"
    - "frontend/src/features/projects/queries.ts - useProject, useCreateProject hooks"
    - "frontend/src/features/projects/types.ts - Project workspace types"
    - "frontend/src/components/ui/sheet.tsx - shadcn Sheet component"
  modified:
    - "frontend/src/index.css - Added @utility container for Tailwind v4"
    - "frontend/src/components/layout/ThemeToggle.tsx - Dutch labels"
    - "frontend/src/features/dashboard/Dashboard.tsx - Dutch UI text"
    - "frontend/src/features/dashboard/components/DashboardFilters.tsx - Dutch labels"
    - "frontend/src/features/dashboard/components/ProjectCard.tsx - Dutch labels"
decisions:
  - decision: "Fixed sidebar + slide-in Sheet instead of resizable 3-panel layout"
    rationale: "Resizable panels had sizing constraints that prevented full use. Fixed sidebar gives clean navigation, Sheet overlay gives assistant full height without competing for space."
    alternatives: ["Resizable panels (too constrained)", "Collapsible sidebar (unnecessary complexity)"]
  - decision: "All UI text in Dutch"
    rationale: "User explicitly requested Dutch for target engineering team. Future phase adds language toggle."
    alternatives: ["English-first (not user preference)", "i18n from start (premature)"]
  - decision: "Type definitions from SPECIFICATION.md §3.1-3.2"
    rationale: "Plan had simplified English descriptions; real FDS types needed domain-accurate Dutch descriptions"
    alternatives: ["Use plan's simplified types (inaccurate)"]
  - decision: "@utility container in index.css"
    rationale: "Tailwind v4 CSS-first config doesn't include centered container utility by default"
    alternatives: ["Custom wrapper div (inconsistent with Tailwind patterns)"]
metrics:
  duration: "checkpoint across 2 sessions"
  completed: "2026-02-15"
  files-created: 14
  files-modified: 14
  commits: 4
---

# Phase 8 Plan 03: Project Wizard + Working View Summary

**One-liner:** 3-step project creation wizard with visual type cards (A/B/C/D) and project working view with fixed sidebar navigation + slide-in assistant panel, all in Dutch.

## What Was Built

**1. Project Creation Wizard (`/projects/new`)**
- 3-step flow: Project Info → Type Classification → Language & Confirm
- Step indicator with active/completed states
- Step 2: Four type cards (Stripe pricing tier style) with domain-accurate Dutch descriptions:
  - A: Nieuwbouw + Standaarden
  - B: Nieuwbouw Flex
  - C: Modificatie Groot
  - D: Modificatie Klein/TWN
- Step 3: Language selection (NL/EN) with creation summary
- React Hook Form manages single form instance across all steps
- On creation: POST to API, navigate to workspace

**2. Project Working View (`/projects/:id`)**
- Fixed 256px sidebar with navigation (Overzicht, Fases, Documenten, Referenties, Instellingen)
- Full-width content area showing project overview
- "Assistent" button in breadcrumb header opens Sheet slide-in from right (400-540px)
- Sheet contains Chat/Context tabs as placeholders for Phase 10
- Breadcrumb: Projecten / {project name}
- Error/loading/404 states handled

**3. Dutch Translation**
- All 14 UI files translated to Dutch (dashboard, wizard, workspace, filters, cards)

## Deviations from Plan

### User-Requested Changes

**1. Layout: Resizable panels → Fixed sidebar + Sheet slide-in**
- Plan specified three resizable panels (ResizablePanelGroup)
- Initial implementation had sizing constraints preventing panels from expanding
- User requested slide-in approach for assistant panel
- Result: cleaner layout, better UX, simpler code

### Auto-fixed Issues

**1. Type definitions corrected from SPECIFICATION.md**
- Plan had simplified English descriptions
- Fixed to match SPECIFICATION.md §3.1-3.2 Dutch terminology

**2. Tailwind v4 container utility**
- Tailwind v4 CSS-first config doesn't auto-include container
- Added `@utility container` to index.css

## Verification Results

Human visual verification passed (2026-02-15):
- Dashboard loads with Dutch UI
- Wizard creates projects through all 3 steps
- Type cards show correct A/B/C/D descriptions
- Working view displays with fixed sidebar + full content
- Assistant slides in from right on button click
- Dark mode renders correctly throughout
- Build passes clean

## Self-Check: PASSED

**Commits:**
- [x] 01d84e5 - feat(08-03): 3-step project creation wizard
- [x] f1dfc5f - feat(08-03): three-panel project working view
- [x] 4ca41bc - wip: 08-core-infrastructure paused at checkpoint verification
- [x] af519cb - feat(08-03): replace resizable panels with fixed sidebar + slide-in assistant
