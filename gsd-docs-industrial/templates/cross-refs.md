<!-- TEMPLATE: Phase CROSS-REFS.md
     Created/updated by: doc-writer subagents during writing (each writer appends)
     Consumed by: doc-verifier (cross-reference validation)
     Consumed by: /doc:complete-fds (assembly-time reference resolution)

     Each writer appends its references. First writer creates the file.
     Full context captured per reference for reliable assembly resolution.

     Context column: one sentence explaining the relationship (required, never empty)
     Types: depends-on | related-to | see-also (no other values)
     Status: resolved | pending (target exists or not yet written)

     Section ID format:
     - Same phase: NN-MM (e.g., "03-02")
     - Cross-phase: phase-N/NN-MM (e.g., "phase-4/04-02")
     - External: descriptive (e.g., "SCADA system documentation")

     Purpose: Enables assembly command to resolve symbolic references and
     verify all cross-references point to valid targets before generating
     final FDS document.

     Format matches existing template pattern: HTML comment doc block + markdown structure. -->

# Phase {N}: {Phase Name} - Cross-References

**Last updated:** {YYYY-MM-DD}
**Phase directory:** `.planning/phases/{NN}-{phase-slug}/`

## References

| Source Section | Target Section | Type | Context | Status |
|----------------|----------------|------|---------|--------|
| {NN-MM section name} | {NN-MM target or phase-N/NN-MM or external} | {depends-on/related-to/see-also} | {One sentence explaining the relationship} | {resolved/pending} |

<!-- Example rows:

| 03-02 Bovenloopkraan | 03-01 Waterbad | depends-on | Crane operation requires water bath level OK interlock before movement allowed | resolved |
| 03-03 Vulunit | 03-02 Bovenloopkraan | depends-on | Fill unit depends on crane position signal to start fill sequence | resolved |
| 03-05 Kettingbaan | phase-4/04-02 HMI Overview | related-to | Conveyor belt status displayed on main HMI screen for operator monitoring | pending |
| 03-06 General Interlocks | SCADA system | see-also | Emergency stop interlock signals communicated to SCADA for central alarm handling | pending |

-->

## Legend

**Reference types:**

- **depends-on:** Source requires target to be complete for functional dependency.
  - Example: EM-200 depends on EM-100 level sensor signal for interlock
  - Assembly impact: Critical reference - verify target exists before finalizing
  - Planning impact: Source should be in later wave than target

- **related-to:** Source references target for complementary information.
  - Example: Equipment module references HMI screen showing its data
  - Assembly impact: Important reference - link sections for navigation
  - Planning impact: No strict wave ordering required

- **see-also:** Source suggests target for additional context.
  - Example: Equipment module suggests external SCADA documentation
  - Assembly impact: Optional reference - include if target available
  - Planning impact: No wave impact

**Reference status:**

- **resolved:** Target section exists and is written (CONTENT.md present)
  - Verification: doc-verifier checks target file exists
  - Assembly: Reference can be resolved to concrete section number

- **pending:** Target section not yet written or in different phase
  - Verification: doc-verifier logs as warning (not gap if target is later phase)
  - Assembly: Reference placeholder retained, resolve in later assembly pass

## Validation Rules

These rules are enforced during verification (doc-verifier subagent):

1. **Type must be one of:** depends-on, related-to, see-also (no other values allowed)
2. **Status must be:** resolved or pending (no other values allowed)
3. **Context column:** Must contain one sentence, cannot be empty
4. **Source section format:** NN-MM for same phase, phase-N/NN-MM for cross-phase
5. **Target section format:** Same as source, or descriptive text for external references

## Usage Notes

**For doc-writer subagents:**
- Load this file when spawned (if exists)
- Append your cross-references to the table
- Create file if you're the first writer in the phase
- Mark status as "resolved" if you know target exists, "pending" otherwise
- Write substantive context sentence - it's used for assembly resolution

**For doc-verifier subagent:**
- Load this file during verification
- Check each "resolved" reference: verify target CONTENT.md exists
- Check each "pending" reference: decide warn-only vs gap based on ROADMAP.md
- Report cross-reference issues in VERIFICATION.md Cross-Reference Status section

**For assembly command:**
- Load this file during /doc:complete-fds
- Resolve all symbolic references to concrete section numbers
- Verify all "depends-on" references are satisfied
- Generate warnings for unresolved "related-to" and "see-also" references
