<!-- REFERENCE: ISA-88 Equipment Hierarchy (ISA-88.01-1995)
     Purpose: Authoritative source for valid ISA-88 equipment hierarchy levels and nesting rules
     Used by: gsd-docs-industrial/workflows/check-standards.md for hierarchy validation
     Loaded when: standards.isa88.enabled: true in PROJECT.md

     This file contains FIXED reference data based on ISA-88.01 standard (Batch Control Part 1: Models and Terminology).
     Equipment hierarchy defines the physical model for batch control.

     Content is structured markdown (tables) parsed at load time for validation checks.
     DO NOT modify hierarchy levels unless ISA standard changes. -->

# ISA-88 Equipment Hierarchy Reference

**Standard:** ISA-88.01-1995 (Batch Control Part 1: Models and Terminology)
**Version:** 1995 (reaffirmed 2006)
**Purpose:** Normative ISA-88 equipment hierarchy definitions for batch control and industrial automation

## Equipment Hierarchy Levels

ISA-88 defines a four-level equipment hierarchy from process to control:

| Level | Name | Definition | Typical Example |
|-------|------|------------|-----------------|
| 1 | **Process Cell** | Manufacturing area containing units and equipment for one or more batches | Mixing area, packaging line, fermentation room |
| 2 | **Unit** | Collection of equipment modules and control modules that can independently execute batch operations | Reactor vessel, filling station, labeling unit |
| 3 | **Equipment Module** | Functional group of control modules performing specific processing activity | Agitator assembly, dosing pump with valve, temperature control loop |
| 4 | **Control Module** | Lowest level - controls a single piece of equipment or collection of related equipment | Motor, valve, sensor, heater |

**Maximum depth:** 4 levels (Process Cell → Unit → Equipment Module → Control Module)

## Valid Nesting Rules

ISA-88 hierarchy has strict containment rules:

| Parent Level | Can Contain (Children) | Cannot Contain |
|--------------|------------------------|----------------|
| **Process Cell** | Units | Equipment Modules, Control Modules directly (must be within Unit) |
| **Unit** | Equipment Modules, Control Modules | Process Cells, other Units, physical equipment not organized into modules |
| **Equipment Module** | Control Modules | Process Cells, Units, other Equipment Modules (no nesting of EMs) |
| **Control Module** | (None - leaf level) | Any hierarchy level (lowest level of abstraction) |

**Key rules:**
1. Equipment Modules do NOT nest within other Equipment Modules (flat structure within Unit)
2. Control Modules can exist directly in a Unit (if not grouped into Equipment Module)
3. Process Cell is the top level for equipment hierarchy (above this is enterprise/site, out of scope for control)
4. Maximum 4 levels deep: Process Cell > Unit > Equipment Module > Control Module

## Correct Hierarchy Examples

### Example 1: Batch Reactor (Full 4-level hierarchy)

```
Process Cell: Reactor Area
├── Unit: Reactor R-101
    ├── Equipment Module: Agitator Assembly
    │   ├── Control Module: Agitator Motor M-101-A
    │   ├── Control Module: Agitator VFD
    │   └── Control Module: Vibration Sensor VS-101
    ├── Equipment Module: Heating System
    │   ├── Control Module: Steam Valve HV-101
    │   ├── Control Module: Temperature Sensor TE-101
    │   └── Control Module: Temperature Controller TIC-101
    ├── Equipment Module: Dosing System
    │   ├── Control Module: Dosing Pump P-101
    │   ├── Control Module: Flow Meter FIT-101
    │   └── Control Module: Dosing Valve DV-101
    └── Control Module: Reactor Pressure Sensor PT-101 (direct in Unit, not in EM)
```

### Example 2: Simpler System (3-level hierarchy)

```
Process Cell: Packaging Line
├── Unit: Filling Station 1
    ├── Equipment Module: Fill Head Assembly
    │   ├── Control Module: Fill Valve FV-201
    │   ├── Control Module: Flow Meter FM-201
    │   └── Control Module: Level Sensor LS-201
    └── Control Module: Conveyor Motor M-201 (direct in Unit)
```

**Note:** Not all systems require all 4 levels. Simpler systems may use 3 levels (Process Cell > Unit > Control Module) if equipment modules are not functionally necessary.

## Incorrect Hierarchy Examples

### ✗ Incorrect: Nested Equipment Modules

```
Unit: Reactor R-101
├── Equipment Module: Complete Reactor System (TOO BROAD)
    └── Equipment Module: Agitator Assembly (NESTED EM - INVALID)
        └── Control Module: Agitator Motor
```

**Problem:** Equipment Modules cannot nest within other Equipment Modules per ISA-88.

**Fix:** Flatten Equipment Modules to same level within Unit:
```
Unit: Reactor R-101
├── Equipment Module: Complete Reactor System
└── Equipment Module: Agitator Assembly
```

Or better, use semantically meaningful grouping:
```
Unit: Reactor R-101
├── Equipment Module: Agitator Assembly
├── Equipment Module: Heating System
└── Equipment Module: Dosing System
```

### ✗ Incorrect: Equipment Module directly in Process Cell

```
Process Cell: Reactor Area
└── Equipment Module: Agitator Assembly (SKIPPED UNIT LEVEL)
    └── Control Module: Agitator Motor
```

**Problem:** Equipment Modules must be contained within a Unit, not directly in Process Cell.

**Fix:** Add Unit level:
```
Process Cell: Reactor Area
└── Unit: Reactor R-101
    └── Equipment Module: Agitator Assembly
        └── Control Module: Agitator Motor
```

### ✗ Incorrect: Exceeding 4 levels

```
Process Cell: Production Facility (level 1)
└── Unit: Reactor R-101 (level 2)
    └── Equipment Module: Agitator System (level 3)
        └── Equipment Module: Gearbox Assembly (level 4 - SHOULD BE CM)
            └── Control Module: Motor (level 5 - TOO DEEP)
```

**Problem:** Maximum depth is 4 levels. This example has 5.

**Fix:** Consolidate lower levels - Gearbox Assembly should be Control Module:
```
Process Cell: Production Facility
└── Unit: Reactor R-101
    └── Equipment Module: Agitator System
        ├── Control Module: Agitator Motor
        └── Control Module: Gearbox
```

## Hierarchy Depth Validation Rules

When validating FDS content for ISA-88 compliance:

| Depth | Structure | Status |
|-------|-----------|--------|
| 1 level | Process Cell only | ⚠ Incomplete (needs Units) |
| 2 levels | Process Cell > Unit | ✓ Minimal valid hierarchy |
| 3 levels | Process Cell > Unit > Equipment Module or Control Module | ✓ Valid |
| 4 levels | Process Cell > Unit > Equipment Module > Control Module | ✓ Valid and complete |
| 5+ levels | Any nesting deeper than 4 | ✗ Invalid per ISA-88 |

**Validation approach:** Parse heading structure in CONTENT.md to determine nesting depth. Flag hierarchies exceeding 4 levels. Warn if hierarchies are incomplete (e.g., Process Cell defined but no Units).

## Relationship to Procedural Model

The equipment hierarchy (physical model) is separate from but related to the procedural model:

| Equipment Level | Executes | Procedural Element |
|-----------------|----------|-------------------|
| Process Cell | Contains multiple procedures | (Procedures coordinated at this level) |
| Unit | Executes one procedure at a time | Unit Procedure |
| Equipment Module | Executes operations | Operations |
| Control Module | Executes phases | Phases |

**Note:** Procedural model validation is separate from equipment hierarchy validation. This reference focuses on equipment hierarchy only.

---

*Reference Data Version: 1995 (based on ISA-88.01-1995)*
*Last Updated: 2026-02-14*
