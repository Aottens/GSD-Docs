<!-- REFERENCE: PackML State Model (ISA-TR88.00.02)
     Purpose: Authoritative source for valid PackML states, transitions, and state categories
     Used by: gsd-docs-industrial/workflows/check-standards.md for state validation
     Loaded when: standards.packml.enabled: true in PROJECT.md

     This file contains FIXED reference data based on ISA-TR88.00.02 standard.
     All state names, transitions, and categories are normative.

     Content is structured markdown (tables) parsed at load time for validation checks.
     DO NOT modify state names or transitions unless ISA standard changes. -->

# PackML State Model Reference

**Standard:** ISA-TR88.00.02-2022 (Machine and Unit States)
**Version:** 2022
**Purpose:** Normative PackML state definitions for industrial automation

## Valid PackML States

All 17 valid states per ISA-TR88.00.02 specification:

| State | Category | Description |
|-------|----------|-------------|
| IDLE | Wait | Machine ready to start, waiting for command |
| STARTING | Acting | Transitioning from IDLE to EXECUTE |
| EXECUTE | Dual | Running production mode (can be stable or transitioning) |
| COMPLETING | Acting | Finalizing current operation before COMPLETE |
| COMPLETE | Wait | Operation completed, awaiting reset |
| RESETTING | Acting | Returning to IDLE from COMPLETE |
| HOLDING | Acting | Transitioning from EXECUTE to HELD |
| HELD | Wait | Production suspended, can resume |
| UNHOLDING | Acting | Transitioning from HELD back to EXECUTE |
| SUSPENDING | Acting | Transitioning from EXECUTE to SUSPENDED |
| SUSPENDED | Wait | Production paused, outside disturbance |
| UNSUSPENDING | Acting | Transitioning from SUSPENDED back to EXECUTE |
| STOPPING | Acting | Controlled stop to STOPPED |
| STOPPED | Wait | Stopped state, requires reset to return |
| ABORTING | Acting | Emergency transition to ABORTED |
| ABORTED | Wait | Aborted due to fault, requires clear |
| CLEARING | Acting | Clearing faults, transitioning to STOPPED |

## State Categories

PackML states fall into three functional categories:

| Category | Behavior | States |
|----------|----------|--------|
| **Acting** | Transient states (active transition) | STARTING, COMPLETING, RESETTING, HOLDING, UNHOLDING, SUSPENDING, UNSUSPENDING, STOPPING, ABORTING, CLEARING |
| **Wait** | Stable states (waiting for command) | IDLE, COMPLETE, HELD, SUSPENDED, STOPPED, ABORTED |
| **Dual** | Can be stable or transitioning | EXECUTE (stable during production, transitioning during mode changes) |

## Valid State Transitions

Standard PackML state transition table:

| From State | To State | Trigger | Transition Type |
|------------|----------|---------|-----------------|
| IDLE | STARTING | Start command | Normal |
| STARTING | EXECUTE | Startup complete | Normal |
| EXECUTE | COMPLETING | Stop command (during production) | Normal |
| COMPLETING | COMPLETE | Completion logic done | Normal |
| COMPLETE | RESETTING | Reset command | Normal |
| RESETTING | IDLE | Reset complete | Normal |
| EXECUTE | HOLDING | Hold command | Normal |
| HOLDING | HELD | Hold complete | Normal |
| HELD | UNHOLDING | Unhold command | Normal |
| UNHOLDING | EXECUTE | Unhold complete | Normal |
| EXECUTE | SUSPENDING | External suspend signal | Normal |
| SUSPENDING | SUSPENDED | Suspend complete | Normal |
| SUSPENDED | UNSUSPENDING | Suspend cleared | Normal |
| UNSUSPENDING | EXECUTE | Unsuspend complete | Normal |
| EXECUTE | STOPPING | Stop command | Normal |
| STOPPING | STOPPED | Stop complete | Normal |
| STOPPED | RESETTING | Reset command | Normal |
| IDLE | ABORTING | Abort condition | Fault |
| STARTING | ABORTING | Abort condition | Fault |
| EXECUTE | ABORTING | Abort condition | Fault |
| COMPLETING | ABORTING | Abort condition | Fault |
| COMPLETE | ABORTING | Abort condition | Fault |
| RESETTING | ABORTING | Abort condition | Fault |
| HOLDING | ABORTING | Abort condition | Fault |
| HELD | ABORTING | Abort condition | Fault |
| UNHOLDING | ABORTING | Abort condition | Fault |
| SUSPENDING | ABORTING | Abort condition | Fault |
| SUSPENDED | ABORTING | Abort condition | Fault |
| UNSUSPENDING | ABORTING | Abort condition | Fault |
| STOPPING | ABORTING | Abort condition | Fault |
| STOPPED | ABORTING | Abort condition | Fault |
| ABORTING | ABORTED | Abort complete | Fault |
| ABORTED | CLEARING | Clear command | Fault |
| CLEARING | STOPPED | Clear complete | Fault |

**Note:** Any state can transition to ABORTING when abort condition occurs (fault path).

## State Model Diagram Description

The PackML state model forms a hierarchical flow with three operational modes:

1. **Normal Operation Loop:** IDLE → STARTING → EXECUTE → COMPLETING → COMPLETE → RESETTING → IDLE
2. **Pause Paths:**
   - Hold: EXECUTE ⇄ HOLDING ⇄ HELD ⇄ UNHOLDING ⇄ EXECUTE
   - Suspend: EXECUTE ⇄ SUSPENDING ⇄ SUSPENDED ⇄ UNSUSPENDING ⇄ EXECUTE
3. **Stop Path:** EXECUTE → STOPPING → STOPPED → RESETTING → IDLE
4. **Fault Path:** Any State → ABORTING → ABORTED → CLEARING → STOPPED

**Mermaid complexity:** The full state diagram with 17 states, 40+ transitions, and fault paths exceeds recommended Mermaid node limits for documentation. For visualization in FDS, use simplified subset diagrams per equipment module or reference this specification textually.

## Common Synonyms and Incorrect Variants

Standards validation should flag these common incorrect state names:

| Incorrect Variant | Correct PackML State | Context |
|-------------------|---------------------|---------|
| RUNNING | EXECUTE | Most common error - legacy terminology |
| RUN | EXECUTE | Too generic, not standard |
| OPERATING | EXECUTE | Descriptive but not PackML |
| ACTIVE | EXECUTE | Too generic |
| PAUSED | HELD or SUSPENDED | Ambiguous - specify hold vs suspend |
| PAUSE | HOLDING or SUSPENDING | Ambiguous |
| WAIT | IDLE or STOPPED | Ambiguous - specify which wait state |
| READY | IDLE | Descriptive but not standard |
| FINISHED | COMPLETE | Past tense not used in PackML |
| DONE | COMPLETE | Too informal |
| ERROR | ABORTED | Generic - PackML uses ABORTED |
| FAULT | ABORTED | Condition vs state - ABORTED is the state |
| ALARM | ABORTED | Alarm is event, ABORTED is state |
| INIT | STARTING or RESETTING | Ambiguous - specify which initialization |
| INITIALIZE | STARTING or RESETTING | Ambiguous |

**Validation approach:** Exact match for standard PackML states required. Common synonyms should be flagged with remediation hint referencing this table.

---

*Reference Data Version: 2022 (based on ISA-TR88.00.02-2022)*
*Last Updated: 2026-02-14*
