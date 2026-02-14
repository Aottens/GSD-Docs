<!-- REFERENCE: PackML Unit Modes (ISA-TR88.00.02)
     Purpose: Authoritative source for valid PackML unit operating modes and mode-state relationships
     Used by: gsd-docs-industrial/workflows/check-standards.md for mode validation
     Loaded when: standards.packml.enabled: true in PROJECT.md

     This file contains FIXED reference data based on ISA-TR88.00.02 standard.
     Unit modes define operational context for state machines.

     Content is structured markdown (tables) parsed at load time for validation checks.
     DO NOT modify mode names unless ISA standard changes. -->

# PackML Unit Modes Reference

**Standard:** ISA-TR88.00.02-2022 (Machine and Unit States)
**Version:** 2022
**Purpose:** Normative PackML unit mode definitions for industrial automation

## Valid Unit Modes

PackML defines standard unit modes that determine which states and operations are available:

| Mode | Purpose | Typical Use Case |
|------|---------|------------------|
| PRODUCTION | Normal automated operation | Continuous production run with full automation |
| MAINTENANCE | Maintenance and service mode | Equipment servicing, calibration, cleaning |
| MANUAL | Manual control mode | Operator-driven individual actuator control |
| SETUP | Setup and changeover mode | Product changeover, recipe setup, tooling changes |
| DRY_RUN | Simulation without material | Testing state machine logic without actual production |
| CLEAN | Cleaning mode | CIP (Clean-In-Place) or manual cleaning cycles |

**Note:** Not all modes are required for every unit. PROJECT.md configuration specifies which modes are implemented (e.g., `modes: [PRODUCTION, MANUAL, MAINTENANCE]`).

## Mode-to-State Mapping

Different modes allow different state transitions and operations:

| State | PRODUCTION | MAINTENANCE | MANUAL | SETUP | DRY_RUN | CLEAN |
|-------|-----------|-------------|--------|-------|---------|-------|
| IDLE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| STARTING | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| EXECUTE | ✓ | ✓ | ✓ (limited) | ✓ | ✓ | ✓ |
| COMPLETING | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| COMPLETE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| RESETTING | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| HOLDING | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| HELD | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| UNHOLDING | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| SUSPENDING | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| SUSPENDED | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| UNSUSPENDING | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| STOPPING | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| STOPPED | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ABORTING | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ABORTED | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CLEARING | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Legend:**
- ✓ = State available in this mode
- ✗ = State not available (transitions blocked)
- ✓ (limited) = State available but with restricted operations

## Mode Transition Rules

Standard rules for transitioning between unit modes:

| From Mode | To Mode | Allowed When | Typical Trigger |
|-----------|---------|--------------|-----------------|
| PRODUCTION | MAINTENANCE | Unit in IDLE or STOPPED | Scheduled maintenance, fault requiring service |
| PRODUCTION | MANUAL | Unit in IDLE or STOPPED | Troubleshooting, manual operation needed |
| PRODUCTION | SETUP | Unit in IDLE or STOPPED | Product changeover, recipe change |
| PRODUCTION | CLEAN | Unit in IDLE or STOPPED | Cleaning cycle required |
| MAINTENANCE | PRODUCTION | Maintenance complete, unit in IDLE | Service complete, return to production |
| MANUAL | PRODUCTION | Unit in IDLE or STOPPED | Manual operation complete |
| SETUP | PRODUCTION | Setup complete, unit in IDLE | Changeover complete, ready for production |
| CLEAN | PRODUCTION | Cleaning complete, unit in IDLE | CIP cycle complete |
| Any Mode | DRY_RUN | Unit in IDLE | Testing/simulation required |
| DRY_RUN | Previous Mode | Unit in IDLE | Testing complete |

**Key constraint:** Mode changes are ONLY allowed when unit is in a stable Wait state (IDLE, STOPPED, ABORTED). Mode transitions during Acting states or EXECUTE state are prohibited for safety.

## Common Mode Errors

Validation should flag these common incorrect mode usages:

| Incorrect Variant | Correct PackML Mode | Context |
|-------------------|---------------------|---------|
| AUTO | PRODUCTION | Auto is ambiguous - PRODUCTION is explicit |
| AUTOMATIC | PRODUCTION | Too generic |
| SERVICE | MAINTENANCE | Service is activity, MAINTENANCE is mode |
| TEST | DRY_RUN or SETUP | Depends on context - specify which |
| DEBUG | MANUAL or MAINTENANCE | Debug is activity, not a mode |
| CLEANING | CLEAN | Use noun form CLEAN, not gerund |
| WASHING | CLEAN | Too specific - CLEAN covers all cleaning |

## Mode-Specific Operational Constraints

Each mode has specific operational behaviors:

### PRODUCTION Mode
- Full automation enabled
- All interlocks active
- Recipe parameters locked during execution
- Hold/Suspend available for production interruption
- Performance metrics tracked

### MAINTENANCE Mode
- Safety interlocks remain active (mandatory)
- Production interlocks may be bypassable (with explicit authorization)
- Hold/Suspend not available (not production context)
- Manual actuator access allowed
- Lockout/tagout integration required

### MANUAL Mode
- Individual actuator control (jog, step)
- Reduced speed limits enforced
- Safety interlocks active (mandatory)
- Automatic sequences disabled
- Two-hand operation or deadman switch may be required

### SETUP Mode
- Recipe editing allowed
- Test runs without material tracking
- Hold/Suspend available for setup testing
- Reduced speed for changeover safety
- Sequence testing enabled

### DRY_RUN Mode
- State machine logic executes
- Physical outputs inhibited (simulated)
- Useful for PLC logic verification
- Material flow not tracked

### CLEAN Mode
- CIP sequences enabled
- Production sequences disabled
- Chemical dosing interlocks active
- Hold not available (cleaning is continuous cycle)
- Cleaning validation tracking

---

*Reference Data Version: 2022 (based on ISA-TR88.00.02-2022)*
*Last Updated: 2026-02-14*
