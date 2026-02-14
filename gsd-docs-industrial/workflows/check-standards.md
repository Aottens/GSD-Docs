<workflow>

# Check Standards Workflow

Composable standards validation workflow for PackML and ISA-88 compliance checks. Usable both standalone (via /doc:check-standards) and as integrated logic (via verify-phase Level 5).

**Target:** ~350 lines
**Pattern:** Conditional loading → discover content → validate per standard → generate report

---

## Step 1: Load PROJECT.md and Check Standards Configuration

Read PROJECT.md and extract standards configuration block.

**Read PROJECT.md:**
```bash
cat .planning/PROJECT.md
```

**Parse standards block:**
Look for `standards:` YAML section with structure:
```yaml
standards:
  packml:
    enabled: true|false
    severity: error|warning
    modes: [PRODUCTION, MAINTENANCE, MANUAL]
  isa88:
    enabled: true|false
    severity: error|warning
    hierarchy_depth: 3|4
```

**Extract configuration:**
- `standards.packml.enabled` (boolean, default: false)
- `standards.packml.severity` (string, default: "warning" if enabled)
- `standards.packml.modes` (array, optional - if omitted, validate all standard modes)
- `standards.isa88.enabled` (boolean, default: false)
- `standards.isa88.severity` (string, default: "warning" if enabled)
- `standards.isa88.hierarchy_depth` (integer, default: 4 if enabled)

**Exit condition - No standards enabled:**
If both `standards.packml.enabled` and `standards.isa88.enabled` are false (or standards block absent):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > STANDARDS CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No standards enabled in PROJECT.md.

Standards compliance checks are opt-in. To enable, add to PROJECT.md:

  standards:
    packml:
      enabled: true
      severity: warning
    isa88:
      enabled: true
      severity: warning

Exiting (no checks to run).
```

Exit cleanly (no error). Standards are NEVER pushed.

---

## Step 2: Load Enabled Reference Data

Conditionally load reference data files ONLY for enabled standards. Lazy loading for performance.

### 2a. Load PackML Reference Data (if enabled)

**Only execute if `standards.packml.enabled: true`:**

**Read STATE-MODEL.md:**
```bash
cat ~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
```

**Extract from STATE-MODEL.md:**
1. **Valid states list** from "Valid PackML States" table (State column):
   - Parse markdown table rows
   - Extract state names: IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, RESETTING, HOLDING, HELD, UNHOLDING, SUSPENDING, SUSPENDED, UNSUSPENDING, STOPPING, STOPPED, ABORTING, ABORTED, CLEARING
   - Store as array: `VALID_PACKML_STATES[]`

2. **Valid transitions** from "Valid State Transitions" table:
   - Parse table rows: From State | To State | Trigger | Transition Type
   - Store as array of objects: `VALID_TRANSITIONS[]` with {from, to, trigger, type}

3. **State categories** from "Valid PackML States" table (Category column):
   - Store mapping: state → category (Acting, Wait, Dual)

4. **Common synonyms** from "Common Synonyms and Incorrect Variants" table:
   - Store mapping: incorrect_variant → correct_state
   - Used for remediation hints

**Read UNIT-MODES.md:**
```bash
cat ~/.claude/gsd-docs-industrial/references/standards/packml/UNIT-MODES.md
```

**Extract from UNIT-MODES.md:**
1. **Valid modes list** from "Valid Unit Modes" table (Mode column):
   - Parse table rows
   - Extract mode names: PRODUCTION, MAINTENANCE, MANUAL, SETUP, DRY_RUN, CLEAN
   - If PROJECT.md specifies `standards.packml.modes`, filter to that subset
   - Store as array: `VALID_PACKML_MODES[]`

2. **Mode-state mapping** from "Mode-to-State Mapping" table:
   - Parse table: State | PRODUCTION | MAINTENANCE | MANUAL | ...
   - Store which states are valid in which modes (✓ vs ✗)

**Store in memory:** Structured data ready for Step 4 validation checks.

### 2b. Load ISA-88 Reference Data (if enabled)

**Only execute if `standards.isa88.enabled: true`:**

**Read EQUIPMENT-HIERARCHY.md:**
```bash
cat ~/.claude/gsd-docs-industrial/references/standards/isa-88/EQUIPMENT-HIERARCHY.md
```

**Extract from EQUIPMENT-HIERARCHY.md:**
1. **Valid hierarchy levels** from "Equipment Hierarchy Levels" table (Name column):
   - Process Cell, Unit, Equipment Module, Control Module
   - Store as array: `VALID_HIERARCHY_LEVELS[]`

2. **Nesting rules** from "Valid Nesting Rules" table:
   - Store parent → allowed children mapping
   - Process Cell can contain: Units
   - Unit can contain: Equipment Modules, Control Modules
   - Equipment Module can contain: Control Modules
   - Control Module: (leaf level, no children)

3. **Maximum depth:** 4 levels (from text)

**Read TERMINOLOGY.md:**
```bash
cat ~/.claude/gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md
```

**Extract from TERMINOLOGY.md:**
1. **Canonical equipment terms** from "Canonical Equipment Terms" table:
   - Process Cell, Unit, Equipment Module, Control Module
   - Store with definitions

2. **Incorrect alternatives** from all "Alternatives" tables:
   - Parse: Incorrect Term | Correct ISA-88 Term | Context
   - Store mapping: incorrect_term → {correct_term, context}
   - Used for remediation hints

3. **Canonical procedural terms** from "Canonical Procedural Terms" table:
   - Procedure, Unit Procedure, Operation, Phase
   - Store for separate validation (if needed)

**Store in memory:** Structured data ready for Step 5 validation checks.

---

## Step 3: Discover and Read Target Content

Determine scope (phase-specific or all phases) and read target CONTENT.md files.

### 3a. Determine Scope

**Check for phase argument:**
```bash
# From command invocation: /doc:check-standards [phase]
PHASE_ARG="$1"
```

**If phase argument provided:**
- Scope: Single phase (e.g., `.planning/phases/03-equipment-modules/`)
- Target files: All `*-CONTENT.md` files in that phase directory

**If no argument:**
- Scope: All phases
- Target files: All `*-CONTENT.md` files in all phase directories under `.planning/phases/`

### 3b. Discover CONTENT.md Files

**For phase-specific:**
```bash
find .planning/phases/${PHASE_NUMBER}-*/ -name "*-CONTENT.md" -type f
```

**For all phases:**
```bash
find .planning/phases/ -name "*-CONTENT.md" -type f
```

**Store list:** Array of file paths to validate.

### 3c. Read Content Files

For each discovered CONTENT.md file:

**Read file:**
```bash
CONTENT=$(cat <file-path>)
```

**Parse content structure:**
1. Extract headings (## and ### levels) for hierarchy analysis
2. Extract tables (detect markdown tables with | delimiters) for state/transition tables
3. Extract text paragraphs for terminology scanning
4. Track line numbers for precise location reporting

**Store parsed content:** Array of content structures with {file, headings, tables, text, line_map}

---

## Step 4: Run PackML Checks (if enabled)

Execute PackML validation checks ONLY if `standards.packml.enabled: true`.

### STND-03a: State Name Enforcement

**Objective:** Verify all state references use exact PackML canonical state names.

**Scan for state references:**
1. **In tables:** Look for tables with "State" column header
   - Extract state names from table rows
   - Common patterns: State Transition tables, State Description tables

2. **In headings:** Look for section headings mentioning states
   - Pattern: `### State: <state-name>` or `## <state-name> State`

3. **In text:** Look for state name mentions in prose
   - Pattern: "unit enters <state-name> state" or "transitions to <state-name>"
   - Case-insensitive scanning

**Validation:**
For each found state reference:
- Compare against `VALID_PACKML_STATES[]` (exact match, case-insensitive)
- If not found: check `SYNONYMS_MAP` for common incorrect variant
- If synonym found: Flag as error/warning (per severity config) with remediation hint
- If completely unknown: Flag as error/warning

**Result structure:**
```
{
  check: "STND-03a: PackML state name enforcement",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>:line <N>",
      context: "<surrounding text>",
      found: "<incorrect-state-name>",
      expected: "<correct-state-name>",
      remediation: "Use PackML standard state '<correct>' instead of '<found>'. See STATE-MODEL.md for all valid states."
    }
  ]
}
```

### STND-03b: Transition Validation

**Objective:** Verify state transitions described in content match valid PackML transitions.

**Scan for transition descriptions:**
1. **In tables:** State transition tables with From | To columns
   - Extract transition pairs: (from_state, to_state)

2. **In text:** Prose describing transitions
   - Patterns: "from <state-A> to <state-B>", "<state-A> → <state-B>", "transitions to <state-B>"

**Validation:**
For each found transition:
- Look up in `VALID_TRANSITIONS[]` array
- Check if {from: <state-A>, to: <state-B>} exists
- If not found: Flag as invalid transition

**Result structure:**
```
{
  check: "STND-03b: PackML transition validation",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>:line <N>",
      context: "<table or text>",
      found: "<from-state> → <to-state>",
      expected: "Valid transitions from <from-state>: [<list>]",
      remediation: "Transition '<from> → <to>' is not valid per PackML. See STATE-MODEL.md transition table."
    }
  ]
}
```

### STND-03c: Mode Checking

**Objective:** Verify mode references use valid PackML unit modes.

**Scan for mode references:**
1. **In headings:** Section titles mentioning modes
   - Pattern: `## Mode: <mode-name>` or `### <mode-name> Mode`

2. **In text:** Prose mentioning operational modes
   - Patterns: "in <mode-name> mode", "unit operates in <mode-name>"

**Validation:**
For each found mode reference:
- Compare against `VALID_PACKML_MODES[]`
- If PROJECT.md specifies `standards.packml.modes`, validate only against that subset
- If not found: Flag as non-standard mode

**Result structure:**
```
{
  check: "STND-03c: PackML mode validation",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>:line <N>",
      context: "<surrounding text>",
      found: "<non-standard-mode>",
      expected: "Valid modes: [<VALID_PACKML_MODES>]",
      remediation: "Use standard PackML mode from UNIT-MODES.md. Common modes: PRODUCTION, MAINTENANCE, MANUAL."
    }
  ]
}
```

**Store results:** Array of PackML check results for report generation.

---

## Step 5: Run ISA-88 Checks (if enabled)

Execute ISA-88 validation checks ONLY if `standards.isa88.enabled: true`.

### STND-04a: Terminology Enforcement

**Objective:** Verify equipment-related terms use canonical ISA-88 terminology.

**Scan for equipment terminology:**
1. **In headings:** Section titles describing equipment
   - Patterns: `## <term>: <name>`, `### <term> Description`
   - Extract term used (e.g., "Machine", "Unit", "Component")

2. **In text:** Equipment descriptions and hierarchy discussions
   - Patterns: "the <term> consists of", "<term> contains", "this <term>"
   - Extract equipment-level terms

**Validation:**
For each found term:
- Check if term is in `CANONICAL_TERMS[]` (Process Cell, Unit, Equipment Module, Control Module)
- If canonical: PASS
- If not canonical: check `INCORRECT_ALTERNATIVES_MAP`
- If mapping found: Flag with correct term suggestion
- If no mapping: PASS (may be equipment-specific name, not hierarchy term)

**Context-aware filtering:**
- Terms in I/O tables, vendor references, spare parts lists: Allow non-standard usage (engineering context)
- Terms in heading structure, hierarchy diagrams, equipment classification: Enforce ISA-88 (hierarchy context)

**Result structure:**
```
{
  check: "STND-04a: ISA-88 terminology enforcement",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>:line <N>",
      context: "<heading or text>",
      found: "<incorrect-term>",
      expected: "<canonical-ISA-88-term>",
      remediation: "Use ISA-88 canonical term '<canonical>' instead of '<found>'. See TERMINOLOGY.md for standard terms."
    }
  ]
}
```

### STND-04b: Hierarchy Depth Validation

**Objective:** Verify equipment hierarchy does not exceed maximum depth (4 levels).

**Analyze hierarchy structure:**
1. **Parse heading nesting:** Analyze markdown heading levels (##, ###, ####, #####)
2. **Identify hierarchy sections:** Look for sections describing equipment hierarchy
   - Typical patterns: "Equipment Hierarchy", "System Architecture", equipment module sections
3. **Calculate depth:** Count nesting levels from Process Cell to Control Module

**Depth calculation:**
- Level 1 (##): Process Cell
- Level 2 (###): Unit
- Level 3 (####): Equipment Module
- Level 4 (#####): Control Module
- Level 5+ (######+): INVALID (exceeds ISA-88 maximum)

**Validation:**
- If depth ≤ 4: PASS
- If depth > 4: Flag as hierarchy too deep
- Compare against `standards.isa88.hierarchy_depth` from PROJECT.md (if specified)

**Result structure:**
```
{
  check: "STND-04b: ISA-88 hierarchy depth validation",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>, Section '<section-title>'",
      context: "<hierarchy path>",
      found: "<depth> levels (Process Cell > Unit > EM > EM > CM)",
      expected: "Maximum 4 levels per ISA-88",
      remediation: "Flatten hierarchy to 4 levels maximum. See EQUIPMENT-HIERARCHY.md for nesting rules."
    }
  ]
}
```

### STND-04c: Hierarchy Consistency

**Objective:** Verify correct parent-child containment per ISA-88 nesting rules.

**Analyze hierarchy relationships:**
1. **Extract hierarchy tree:** Parse heading structure to build parent-child tree
2. **Identify level types:** Determine which ISA-88 level each heading represents (based on terminology)
3. **Validate containment:** Check each parent-child pair against nesting rules

**Nesting rules validation:**
- Process Cell children: Must be Units only (not EMs or CMs directly)
- Unit children: Can be Equipment Modules or Control Modules
- Equipment Module children: Can be Control Modules only (not other EMs)
- Control Module children: None (leaf level)

**Validation:**
For each parent-child relationship:
- Look up parent level in `VALID_HIERARCHY_LEVELS[]`
- Check if child level is in allowed children for that parent (from nesting rules)
- If not allowed: Flag as incorrect containment

**Result structure:**
```
{
  check: "STND-04c: ISA-88 hierarchy consistency",
  status: "pass" | "fail",
  severity: <from PROJECT.md>,
  findings: [
    {
      location: "<file-path>, Section '<parent-section>'",
      context: "<parent-level> contains <child-level>",
      found: "<parent-term> directly contains <child-term>",
      expected: "<parent-term> can contain: [<allowed-children>]",
      remediation: "Correct hierarchy containment. See EQUIPMENT-HIERARCHY.md 'Valid Nesting Rules' table."
    }
  ]
}
```

**Store results:** Array of ISA-88 check results for report generation.

---

## Step 6: Generate COMPLIANCE.md Report

Create COMPLIANCE.md using compliance-report.md template with all check results.

### 6a. Determine Output Path

**If phase-specific check:**
```
.planning/phases/<NN>-<slug>/COMPLIANCE.md
```

**If all-phases check:**
```
.planning/COMPLIANCE.md
```

### 6b. Calculate Summary Metrics

**Per-standard summary:**
For each enabled standard (PackML, ISA-88):
- Total checks run: Count of STND-03a/b/c or STND-04a/b/c executed
- Passed checks: Count where status = "pass"
- Failed checks: Count where status = "fail"
- Score: (passed / total) × 100%

**Overall result determination:**
- **COMPLIANT:** All checks passed OR all failures are severity "warning"
- **NON-COMPLIANT:** Any check failed with severity "error"
- **PARTIALLY COMPLIANT:** Mix of pass/fail with only warnings

### 6c. Write COMPLIANCE.md

Use template from `gsd-docs-industrial/templates/reports/compliance-report.md`.

**Header:**
```markdown
# Standards Compliance Report

**Date:** <YYYY-MM-DD>
**Scope:** <Phase NN or "All Phases">
**Standards Checked:** <PackML, ISA-88, or both>
**Overall Result:** <COMPLIANT | NON-COMPLIANT | PARTIALLY COMPLIANT>
```

**Summary Table:**
```markdown
## Summary

| Standard | Severity | Checks | Passed | Failed | Score |
|----------|----------|--------|--------|--------|-------|
| PackML   | <error/warning> | <N> | <M> | <K> | <X%> |
| ISA-88   | <error/warning> | <N> | <M> | <K> | <X%> |
```

**Per-Standard Detail Sections:**

For each standard with checks run:

```markdown
## PackML Compliance

### STND-03a: State Name Enforcement

**Status:** <PASS | FAIL (severity)>
**Findings:** <N> issues found

<for each finding>
**Location:** <file>:line <N>
**Context:** <surrounding text>
**Issue:** Uses '<found>' instead of '<expected>'
**Remediation:** <hint from check result>

---
</for each finding>

### STND-03b: Transition Validation
...
```

**Footer:**
```markdown
---

Generated by `/doc:check-standards` on <timestamp>

**Next steps:**
<if NON-COMPLIANT>
- Fix issues marked as 'error' severity before /doc:complete-fds
- Review warnings and address if necessary
</if>

<if COMPLIANT>
- Standards checks passed
- Ready for assembly
</if>
```

**Write file:**
```bash
cat > <output-path> << 'EOF'
<generated report content>
EOF
```

---

## Step 7: Display Summary

Show terminal output with DOC > banner and standards check result.

**Banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > STANDARDS CHECK COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Summary table:**
```
Standards Compliance Summary:

| Standard | Severity | Checks | Passed | Failed | Result    |
|----------|----------|--------|--------|--------|-----------|
| PackML   | warning  | 3      | 2      | 1      | ⚠ Warning |
| ISA-88   | error    | 3      | 3      | 0      | ✓ Pass    |

Overall: PARTIALLY COMPLIANT (warnings present)
```

**Result-specific messages:**

**If NON-COMPLIANT (errors present):**
```
⚠ Standards compliance FAILED

Issues marked as 'error' severity must be fixed before /doc:complete-fds.
Review COMPLIANCE.md for details and remediation hints.

Full report: .planning/COMPLIANCE.md
```

**If COMPLIANT (all passed or only warnings):**
```
✓ Standards compliance PASSED

<if warnings present>
Some warnings found. Review COMPLIANCE.md for recommendations.
</if>

Standards checks complete. Ready for assembly.

Full report: .planning/COMPLIANCE.md
```

**End output.**

---

</workflow>
