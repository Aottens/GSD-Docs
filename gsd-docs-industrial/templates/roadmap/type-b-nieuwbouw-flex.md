# ROADMAP.md - {PROJECT_NAME}

**Project:** {PROJECT_NAME}
**Client:** {CLIENT}
**Type:** B - Nieuwbouw Flex
**Created:** {DATE}
**Language:** {LANGUAGE}
**Phases:** 5

## Overview

Type B project: new installation with flexible standards approach. Pragmatic structure without strict ISA-88/PackML enforcement. Standards are considered and applied where beneficial, not mandated.

## Phase 1: Foundation

**Goal:** Establish project context, definitions, and scope boundaries.
- Introductie, project scope, and document conventions
- Definities and afkortingen
- System boundaries and exclusions (no formal standards section)

**Success Criteria:**
- Project scope and boundaries are clearly defined
- All domain-specific terms are defined
- Document structure is established

**Dependencies:** None (entry point)

## Phase 2: System Overview

**Goal:** Describe the complete system with functional blocks and process flow.
- System description: purpose, capacity, main components
- Functional blocks: logical grouping of system functions
- Process flow: material/data flow through the system

**Success Criteria:**
- All functional units are identified and described
- Process flow covers normal operation end-to-end
- System boundaries match Phase 1 scope

**Dependencies:** Phase 1 (Foundation)

## Phase 3: Functional Units

**Goal:** Describe each functional unit with operation, parameters, and interlocks.
- Per unit: functional description and operating principle
- Per unit: parameters with ranges, interlocks with conditions
- Per unit: interfaces and dependencies on other units

**Success Criteria:**
- Every unit has a complete functional description
- All parameters have range, unit, and default value
- All interlocks have condition and action defined

**Dependencies:** Phase 2 (System Overview)

## Phase 4: HMI & Interfaces

**Goal:** Define operator interaction and external system connections.
- Bediening: operator screens, controls, and indicators
- External connections: communication with other systems
- Communication: protocols, data exchange, error handling

**Success Criteria:**
- Every unit has operator interaction defined
- All external interfaces have protocol and signal details
- Error handling is defined for each interface

**Dependencies:** Phase 3 (Functional Units)

## Phase 5: Appendices

**Goal:** Compile reference lists for implementation (optional based on project needs).
- Signaallijst: I/O overview across all units
- Parameterlijst: all configurable parameters

**Success Criteria:**
- Signal list covers all I/O from Phase 3
- Parameter list matches Phase 3 parameters

**Dependencies:** Phase 3-4 (all content phases)

## Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation | Pending |
| 2 | System Overview | Pending |
| 3 | Functional Units | Pending |
| 4 | HMI & Interfaces | Pending |
| 5 | Appendices | Pending |

*Roadmap created: {DATE}*
