# ROADMAP.md - {PROJECT_NAME}

**Project:** {PROJECT_NAME}
**Client:** {CLIENT}
**Type:** C - Modificatie Groot
**Created:** {DATE}
**Language:** {LANGUAGE}
**Phases:** 4

## Overview

Type C project: large modification to an existing system. Documents only the DELTA against the BASELINE.md reference. The existing system is treated as immutable; this roadmap covers what changes and its impact.

## Phase 1: Scope & Baseline

**Goal:** Define modification scope and establish the existing system baseline.
- Wijzigingsomschrijving: what is changing and why
- BASELINE.md reference: existing system as immutable given (see BASELINE.md)
- Scope boundary: what changes YES vs what does NOT change

**Success Criteria:**
- BASELINE.md is populated with existing system description
- Change scope clearly separates modified from unmodified elements
- Every affected equipment module is identified with change type

**Dependencies:** None (entry point) | Requires: BASELINE.md

## Phase 2: Delta Functional

**Goal:** Describe all functional changes and additions to the existing system.
- Gewijzigde functionaliteit: changes to existing equipment/functions
- Nieuwe equipment/functies: additions not present in baseline
- Impact analysis: effects on unchanged parts of the system

**Success Criteria:**
- Every modified EM has before/after description (referencing BASELINE.md)
- New equipment has complete functional description
- Impact on unchanged system elements is assessed

**Dependencies:** Phase 1 (Scope & Baseline)

## Phase 3: Delta HMI & Interfaces

**Goal:** Describe all HMI and interface changes resulting from the modification.
- Gewijzigde schermen: modifications to existing operator screens
- Nieuwe schermen: new screens for added functionality
- Interface wijzigingen: changes to external system connections

**Success Criteria:**
- Every modified screen has before/after description
- New screens have complete layout and function description
- Interface changes include updated signal lists

**Dependencies:** Phase 2 (Delta Functional)

## Phase 4: Verification & Appendices

**Goal:** Define test criteria and compile delta reference data.
- Test criteria: acceptance tests for modified functionality
- Regression check: verification that unchanged functions still work
- Updated signal list: delta additions/changes to I/O

**Success Criteria:**
- Every functional change has at least one acceptance test
- Regression test plan covers critical unchanged functions
- Signal list delta is complete and consistent with Phase 2

**Dependencies:** Phase 2-3 (all delta phases)

## Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Scope & Baseline | Pending |
| 2 | Delta Functional | Pending |
| 3 | Delta HMI & Interfaces | Pending |
| 4 | Verification & Appendices | Pending |

*Roadmap created: {DATE}*
