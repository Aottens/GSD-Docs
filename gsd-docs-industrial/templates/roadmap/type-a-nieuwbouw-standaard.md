# ROADMAP.md - {PROJECT_NAME}

**Project:** {PROJECT_NAME}
**Client:** {CLIENT}
**Type:** A - Nieuwbouw + Standaarden
**Created:** {DATE}
**Language:** {LANGUAGE}
**Phases:** 6

## Overview

Type A project: new installation with formal standards compliance (PackML, ISA-88). Full FDS structure covering foundation through appendices. Standards are enforced from the start and verified at each phase.

## Phase 1: Foundation

**Goal:** Establish project context, definitions, references, and standards scope.
- Introductie, project scope, and document conventions
- Definities, afkortingen, and referentiedocumenten
- Standaarden scope: PackML state model, ISA-88 equipment hierarchy

**Success Criteria:**
- All referenced standards are identified and scoped
- Terminology definitions cover all domain-specific terms
- Document structure and conventions are established

**Dependencies:** None (entry point)

## Phase 2: System Architecture

**Goal:** Define the complete system structure, equipment hierarchy, and operating modes.
- Systeem overzicht with process description and system boundaries
- Equipment hierarchy following ISA-88 (Unit > Equipment Module > Control Module)
- Operating modes following PackML (Production, Manual, Maintenance)

**Success Criteria:**
- All equipment modules are identified and placed in hierarchy
- Operating modes are defined with transition conditions
- System boundaries and external interfaces are identified

**Dependencies:** Phase 1 (Foundation)

## Phase 3: Equipment Modules

**Goal:** Fully describe each equipment module with states, parameters, interlocks, and I/O.
- Per EM: functional description, operating states (PackML compliant)
- Per EM: parameters with ranges/units, interlocks with conditions/actions
- Per EM: I/O interface list (DI, DO, AI, AO)

**Success Criteria:**
- Every EM has a complete state table with entry/exit conditions
- All parameters have range, unit, and default value
- All interlocks have condition, action, and priority

**Dependencies:** Phase 2 (System Architecture)

## Phase 4: Control & HMI

**Goal:** Define the control philosophy and HMI requirements for operator interaction.
- Control philosophy: automatic sequences, manual overrides, mode transitions
- HMI requirements: screen hierarchy, navigation, alarm management
- Screen descriptions per operator view with elements and actions

**Success Criteria:**
- Control philosophy covers all operating modes
- Every EM has at least one associated HMI screen or panel
- Alarm categories and priorities are defined

**Dependencies:** Phase 3 (Equipment Modules)

## Phase 5: Interfaces & Safety

**Goal:** Define all external interfaces and safety requirements.
- External interfaces: protocols, signal lists, communication parameters
- Safety requirements: risk categories, safety functions, SIL levels
- Interlocks overview: cross-EM interlocks, emergency stop behavior

**Success Criteria:**
- Every external interface has protocol, signals, and error handling defined
- Safety functions are mapped to equipment and risk categories
- E-stop behavior is defined for every actuator

**Dependencies:** Phase 3 (Equipment Modules), Phase 4 (Control & HMI)

## Phase 6: Appendices

**Goal:** Compile reference tables and cross-phase data for implementation.
- Signaallijst: complete I/O list across all EMs
- Parameterlijst: all configurable parameters with defaults
- State transition tables: consolidated PackML states per EM

**Success Criteria:**
- Signal list covers every I/O point from Phase 3
- Parameter list matches all parameters from Phase 3
- State transition tables are consistent with EM descriptions

**Dependencies:** Phase 3-5 (all content phases)

## Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation | Pending |
| 2 | System Architecture | Pending |
| 3 | Equipment Modules | Pending |
| 4 | Control & HMI | Pending |
| 5 | Interfaces & Safety | Pending |
| 6 | Appendices | Pending |

*Roadmap created: {DATE}*
