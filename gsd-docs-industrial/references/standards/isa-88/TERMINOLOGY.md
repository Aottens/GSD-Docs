<!-- REFERENCE: ISA-88 Canonical Terminology (ISA-88.01-1995)
     Purpose: Authoritative source for correct ISA-88 terminology and common incorrect alternatives
     Used by: gsd-docs-industrial/workflows/check-standards.md for terminology validation
     Loaded when: standards.isa88.enabled: true in PROJECT.md

     This file contains FIXED reference data based on ISA-88.01 standard.
     Terminology enforcement ensures consistent, standards-compliant language in FDS documents.

     Content is structured markdown (tables) parsed at load time for validation checks.
     DO NOT modify canonical terms unless ISA standard changes. -->

# ISA-88 Canonical Terminology Reference

**Standard:** ISA-88.01-1995 (Batch Control Part 1: Models and Terminology)
**Version:** 1995 (reaffirmed 2006)
**Purpose:** Normative ISA-88 terminology for batch control and industrial automation

## Canonical Equipment Terms

Official ISA-88 terms for equipment hierarchy levels:

| Canonical Term | Definition | Usage Context |
|----------------|------------|---------------|
| **Process Cell** | Manufacturing area containing units and equipment | Top level of equipment hierarchy |
| **Unit** | Collection of equipment modules and control modules that can independently execute batch operations | Level 2 of hierarchy |
| **Equipment Module** | Functional group of control modules performing specific processing activity | Level 3 of hierarchy |
| **Control Module** | Lowest level equipment entity controlling a single piece of equipment | Level 4 of hierarchy (leaf) |

## Common Incorrect Alternatives

Validation should flag these common non-standard terms and suggest ISA-88 canonical replacements:

### Process Cell Alternatives

| Incorrect Term | Correct ISA-88 Term | Context/Note |
|----------------|---------------------|--------------|
| Production Area | Process Cell | Too generic - use ISA-88 term |
| Manufacturing Zone | Process Cell | Zone is not ISA-88 terminology |
| Work Cell | Process Cell | Work Cell is lean manufacturing term, not ISA-88 |
| Production Line | Process Cell | Line implies continuous, Process Cell is batch-oriented |
| Section | Process Cell | Too generic |
| Area | Process Cell | Area is descriptive but not standard term |

### Unit Alternatives

| Incorrect Term | Correct ISA-88 Term | Context/Note |
|----------------|---------------------|--------------|
| Machine | Unit | Machine is too generic and implies mechanical focus |
| Equipment | Unit | Equipment is broader category, Unit is specific ISA-88 level |
| System | Unit | System is ambiguous - can refer to any level |
| Station | Unit | Station is assembly/packaging term, not batch control |
| Asset | Unit | Asset is maintenance term, not ISA-88 |
| Device | Unit | Device is too low-level, usually refers to Control Module |

### Equipment Module Alternatives

| Incorrect Term | Correct ISA-88 Term | Context/Note |
|----------------|---------------------|--------------|
| Component | Equipment Module | Component is too generic |
| Subsystem | Equipment Module | Subsystem is not ISA-88 term |
| Assembly | Equipment Module | Assembly is mechanical engineering term |
| Module (without "Equipment") | Equipment Module | "Module" alone is ambiguous - specify "Equipment Module" |
| Subunit | Equipment Module | Subunit suggests hierarchy under Unit, but EM is functional grouping |

### Control Module Alternatives

| Incorrect Term | Correct ISA-88 Term | Context/Note |
|----------------|---------------------|--------------|
| Device | Control Module | Device is generic hardware term |
| Component | Control Module | Component is too generic |
| Element | Control Module | Element is not ISA-88 term |
| Module (without "Control") | Control Module | "Module" alone is ambiguous - specify "Control Module" |
| Instrument | Control Module | Instrument is subset of Control Module (sensors/analyzers) |
| Actuator | Control Module | Actuator is subset of Control Module (valves/motors) |

## Canonical Procedural Terms

Official ISA-88 terms for procedural model elements:

| Canonical Term | Definition | Equipment Level Relationship |
|----------------|------------|------------------------------|
| **Procedure** | Complete sequence of operations to produce a batch | Coordinates multiple Units in Process Cell |
| **Unit Procedure** | Operations performed by a single Unit | Executes within one Unit |
| **Operation** | Major processing activity within a Unit Procedure | Performed by Equipment Module or Unit |
| **Phase** | Smallest element of procedural control | Executed by Control Module or Equipment Module |

**Note:** Procedural terms are separate from equipment terms. A Unit (equipment) executes a Unit Procedure (procedural). Do not confuse the two models.

## Common Procedural Term Errors

| Incorrect Term | Correct ISA-88 Term | Context/Note |
|----------------|---------------------|--------------|
| Recipe | Procedure or Formula | Recipe is colloquial - use Procedure for control, Formula for ingredients |
| Program | Procedure | Program is PLC/software term, Procedure is ISA-88 control term |
| Sequence | Procedure or Operation | Sequence is generic - specify Procedure or Operation |
| Step | Phase | Step is generic - Phase is ISA-88 term for smallest procedural element |
| Task | Phase or Operation | Task is not ISA-88 term |
| Routine | Procedure or Operation | Routine is software term, not ISA-88 |

## Additional ISA-88 Canonical Terms

Other important ISA-88 terms that should be used consistently:

| Canonical Term | Definition | Common Incorrect Alternative |
|----------------|------------|------------------------------|
| **Batch** | Quantity of material produced in single execution of procedure | Lot, Run, Production Cycle |
| **Campaign** | Series of batches of same product | Production Run, Batch Series |
| **Recipe** | Information defining how to produce a batch (Formula + Procedure) | Program, Sequence, Method |
| **Formula** | List of ingredients and quantities | Ingredients List, BOM (Bill of Materials) |
| **Process Input** | Material entering process | Raw Material, Feed, Input Material |
| **Process Output** | Material produced by process | Product, Output Material, Finished Goods |
| **Equipment Entity** | General term for any equipment hierarchy level | (Use specific term: Unit, Equipment Module, Control Module) |
| **Process Action** | Processing activity executed by equipment | (Use specific procedural term: Procedure, Operation, Phase) |

## Validation Approach

When checking FDS content for ISA-88 terminology compliance:

1. **Extract equipment-related terms:** Scan section headings, equipment descriptions, hierarchy diagrams
2. **Compare against canonical terms:** Match found terms to this reference table
3. **Flag incorrect alternatives:** Report usage of non-standard terms with location (file, line, context)
4. **Suggest remediation:** Provide correct ISA-88 term from this table
5. **Allow technical exceptions:** Engineer-defined equipment-specific names (e.g., "Reactor R-101") are allowed - validation targets ISA-88 level terminology only

**Example validation finding:**

```
STND-04a: Terminology enforcement
Status: ⚠ Warning
Location: 03-02-CONTENT.md, Section "Equipment Description"
Finding: Uses term "Machine" (4 occurrences) instead of canonical ISA-88 term "Unit"
Remediation: Replace "Machine" with "Unit" per ISA-88.01-1995 equipment hierarchy terminology
Context: See gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md "Unit Alternatives" table
```

## Mixed Terminology Patterns

Some terms are acceptable in specific contexts but should be ISA-88 when referring to hierarchy:

| Term | Acceptable Context | ISA-88 Context (Use Canonical Term) |
|------|-------------------|-------------------------------------|
| Machine | Mechanical engineering discussion, vendor documentation | When referring to ISA-88 Unit level |
| Device | I/O lists, communication protocols, vendor catalogs | When referring to Control Module in hierarchy |
| Component | Spare parts lists, maintenance procedures | When referring to Equipment Module in hierarchy |
| System | Enterprise/IT context (MES, ERP) | When referring to specific ISA-88 hierarchy level |

**Validation rule:** Context matters. If term appears in heading structure, hierarchy diagram, or equipment classification discussion, enforce ISA-88 canonical terminology. If term appears in I/O table, vendor reference, or spare parts context, allow engineering-standard usage.

---

*Reference Data Version: 1995 (based on ISA-88.01-1995)*
*Last Updated: 2026-02-14*
