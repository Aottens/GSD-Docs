<workflow>

# /doc:plan-phase Workflow

Complete execution logic for phase planning and section plan generation. The command file (`~/.claude/commands/doc/plan-phase.md`) delegates here. Follow each step in order.

**Purpose:** Transform CONTEXT.md decisions into actionable writing plans. Each generated PLAN.md tells a writer subagent (spawned by `/doc:write-phase`) exactly what to write, what context to load, which template to use, which standards apply, and how to verify quality. Wave assignments enable parallel writing of independent sections.

**Downstream consumer:** `/doc:write-phase` reads PLAN.md files to spawn writer subagents per wave. Each writer receives exactly one PLAN.md plus its referenced context -- no other PLAN.md or CONTENT.md files.

**Key distinction:** This workflow generates DOC PLAN.md files (## Goal, ## Sections, ## Context, ## Template, ## Standards, ## Writing Rules, ## Verification). NOT GSD-format plans with `<task type="auto">` XML.

**Non-interactive:** Reads CONTEXT.md and ROADMAP.md, generates plans autonomously. No AskUserQuestion calls.

---

## Step 1: Parse Arguments and Validate Phase

Parse `$ARGUMENTS` to get the phase number and detect the --gaps flag.

```bash
# Parse arguments
ARGS=$ARGUMENTS
PHASE=$(echo "$ARGS" | grep -oE '[0-9]+' | head -1)
GAPS_FLAG=$(echo "$ARGS" | grep -o '\-\-gaps')
PADDED_PHASE=$(printf "%02d" ${PHASE})
```

**If phase number missing:** Show error box: "Phase number is required. Usage: `/doc:plan-phase <phase> [--gaps]`" and abort.

**If --gaps flag detected:** Jump to Step 8 (Gap Closure Mode). Skip Steps 2-7.

### 1.1 Read ROADMAP.md

Read `.planning/ROADMAP.md` to find the phase entry.

Extract: phase name, phase goal/description, dependencies, requirements/deliverables.

**If phase not found:** Show error box: "Phase {N} not found in ROADMAP.md. Use `/doc:status` to see available phases." Stop execution.

### 1.2 Check Dependencies

For each dependency listed in the phase entry, verify completion by checking for SUMMARY.md files in the dependent phase directories. SUMMARY.md existence is the completion proof -- not STATE.md status.

```bash
# Example: if phase 3 depends on phase 2
ls .planning/phases/02-*/SUMMARY.md 2>/dev/null
ls .planning/phases/02-*/*-SUMMARY.md 2>/dev/null
```

**If dependencies unmet:** Show error box: "Phase {N} depends on Phase {D} which is not yet complete. No SUMMARY.md found. Complete Phase {D} first." Stop execution.

### 1.3 Find Phase Directory

```bash
PHASE_DIR=$(ls -d .planning/phases/${PADDED_PHASE}-* 2>/dev/null | head -1)
PHASE_NAME=$(basename "$PHASE_DIR" | sed "s/^${PADDED_PHASE}-//")
```

**If phase directory not found:** Show error box: "Phase directory not found. Run `/doc:discuss-phase {N}` first." Stop execution.

### 1.4 Display Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PLANNING PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} PLANNEN`

---

## Step 2: Load Phase Context

### 2.1 Read Project Configuration

Read `.planning/PROJECT.md` for:
- Project type (A, B, C, or D)
- Language setting (nl or en)
- Standards configuration (PackML enabled, ISA-88 enabled)

Store as `PROJECT_TYPE`, `LANGUAGE`, `PACKML_ENABLED`, `ISA88_ENABLED`.

### 2.2 Read CONTEXT.md

Read `${PHASE_DIR}/${PADDED_PHASE}-CONTEXT.md` for phase decisions.

**If CONTEXT.md not found:** Show error box: "No CONTEXT.md for Phase {N}. Run `/doc:discuss-phase {N}` first to capture decisions." Stop execution.

### 2.3 Parse CONTEXT.md Sections

Extract from CONTEXT.md:
- `<domain>` section: phase boundary, scope definition
- `<decisions>` section: implementation decisions organized by topic
- `<specifics>` section: exact technical values, preferred approaches
- `<deferred>` section: ideas for other phases (informational only)

Identify "Claude's Discretion" items from the `<decisions>` section. These inform plan generation without requiring further input.

### 2.4 Type C/D: Load Baseline

**Only if `PROJECT_TYPE` is C or D:**

Read `.planning/BASELINE.md` to understand the existing system scope. Extract:
- Which equipment exists and is UNCHANGED
- Which equipment is MODIFIED
- What is NEW

Plans for Type C/D focus on the delta -- new or modified content only.

---

## Step 3: Analyze Sections

Based on phase goal, CONTEXT.md, and ROADMAP.md, determine what sections need plans. Each plan covers one logical documentation section (or a small group of closely related sections).

### 3.1 Content Type Detection

Analyze the phase goal text from ROADMAP.md to determine content types:

| Keywords in phase goal | Content type |
|---|---|
| "equipment", "module", "EM-", "unit", "functional unit" | Equipment Modules |
| "architecture", "system overview", "hierarchy", "overview" | System Architecture |
| "interface", "communication", "protocol", "bus", "network" | Interfaces |
| "HMI", "visualization", "screen", "display", "operator" | HMI |
| "safety", "interlock", "SIL", "E-stop", "emergency" | Safety |
| "foundation", "scope", "terminology", "introduction", "definitions" | Foundation |
| "appendix", "signal list", "parameter list", "index" | Appendices |
| "control", "philosophy", "operating mode", "mode" | Control Philosophy |
| "state", "state machine", "PackML" | State Machines |

A phase can match multiple types. Equipment Module phases typically include both Equipment Modules AND State Machines content.

### 3.2 Section Identification

**For Equipment Module phases:**
- Identify each equipment module from CONTEXT.md decisions or ROADMAP phase description
- Each EM gets one plan (one PLAN.md per equipment module)
- Determine which subsections apply per EM using the configurable subsection list:
  - **Required always:** description, operating-states, parameters, interlocks, io-table
  - **Include manual-controls if:** CONTEXT.md mentions manual operation for this EM
  - **Include alarm-list if:** CONTEXT.md mentions alarms for this EM
  - **Include maintenance-mode if:** CONTEXT.md mentions maintenance procedures for this EM
  - **Include startup-shutdown if:** CONTEXT.md mentions complex startup/shutdown sequences for this EM
- If an EM has a state machine: the state machine is part of the EM plan (not a separate plan). The EM plan references both the equipment module template AND the state machine template.
- If the phase has an overview/summary section: create a separate plan for it

**For Interface phases:**
- One plan per interface (or per interface group if closely related)
- Template: section-interface.md

**For Foundation/Architecture/HMI/Safety/Appendix phases:**
- One plan per logical section group
- Template varies by content type (or no specific FDS template -- plan describes structure directly in ## Sections)

### 3.3 Granularity Rules (Claude's Discretion)

Adapt granularity to phase complexity:
- If a phase has 1-3 sections: one plan per section
- If a phase has 4-8 sections: one plan per section or per small group
- If a phase has 8+ sections: group related sections (e.g., similar equipment types)

Never create a single plan covering 10+ equipment modules. Never create 30 plans for a 3-section phase.

---

## Step 4: Build Dependency Graph

For each identified section/plan from Step 3:

### 4.1 Record Cross-References

1. What does this section cross-reference? (other EMs, interfaces, shared interlocks)
2. What references this section? (other EMs that depend on this EM's interlock definitions)
3. Does this section reference content from OTHER phases? (flag for review, do not block)

### 4.2 Identify Dependency Chains

Build a directed graph of dependencies:
- Node: each planned section
- Edge: section A depends on section B (A references B's content)

Common dependency patterns:
- EM with cross-EM interlocks depends on the referenced EM
- Overview/summary sections depend on all sections they summarize
- Interface sections may depend on the EMs they connect
- Safety sections may depend on EMs they protect

### 4.3 Cross-Phase References

When a section references content from a DIFFERENT phase:
- Do NOT create a dependency edge (cross-phase dependencies are not wave-blocking)
- Add a flag to the plan's ## Context: "Cross-ref: verify against Phase {X} when available"
- The writer will use symbolic references that can be validated later by `/doc:verify-phase`

---

## Step 5: Assign Waves

Apply dependency-based wave assignment using the graph from Step 4.

### 5.1 Wave Assignment Algorithm

1. **Wave 1:** All sections with no incoming dependency edges (independent sections)
2. **Wave 2:** Sections whose dependencies are ALL in Wave 1
3. **Wave 3+:** Sections whose dependencies are ALL in Wave 2 or earlier (cascading)
4. **Last wave:** Overview/summary sections that reference multiple sections

### 5.2 Wave Assignment Rules

- If no dependencies exist between sections: put ALL in Wave 1
- Sections within the same EM are NEVER split across plans (one plan per EM, always)
- Cross-references to sections in OTHER phases are flagged for review, not blocked
- Minimize wave count -- do not create unnecessary waves
- If only 1-2 sections would be in a later wave with minimal dependencies: consider moving them to the earlier wave with a cross-reference note

### 5.3 Wave Validation

After assignment, verify:
- No plan depends on a plan in the same or later wave
- No circular dependencies exist (follow depends_on chains -- they must terminate)
- Every plan has a wave assignment

---

## Step 6: Generate PLAN.md Files

For each identified section, generate a PLAN.md file in the phase directory.

### 6.1 File Naming

Format: `{NN}-{MM}-PLAN.md` where:
- `NN` = zero-padded phase number (01, 02, 03...)
- `MM` = zero-padded plan number within the phase (01, 02, 03...)

Plan numbers are assigned sequentially: 01 for the first plan, 02 for the second, etc. Order by wave first, then by section name within each wave.

### 6.2 PLAN.md Format

Each generated plan follows this format (doc PLAN format, NOT GSD format):

```markdown
---
phase: {N}
plan: {MM}
name: {Section Name}
type: {equipment-module | state-machine | interface | overview | appendix | foundation | architecture | hmi | safety | control-philosophy}
wave: {W}
depends_on: [{list of NN-MM plan IDs this plan depends on}]
autonomous: true
---

# {Section Name}

## Goal
{What this documentation section must achieve -- derived from ROADMAP phase goal
and CONTEXT.md decisions. Specific to THIS section, not the whole phase.
Write a clear, actionable goal that the writer can verify against.}

## Sections
{Numbered list of subsections to write. For equipment modules, this is the
selected subsections from the configurable list.}
1. {Subsection 1}
2. {Subsection 2}
...

## Context
{Relevant decisions extracted from CONTEXT.md for THIS section ONLY.
Do not dump the entire CONTEXT.md -- extract only what the writer needs.}
- {Decision 1 relevant to this section}
- {Decision 2 relevant to this section}

## Template
@~/.claude/gsd-docs-industrial/templates/fds/{template-file}.md

## Standards
{Only if standards are enabled in PROJECT.md. Reference by name, not inline.}
- PackML: @~/.claude/gsd-docs-industrial/references/standards/packml/
- ISA-88: @~/.claude/gsd-docs-industrial/references/standards/isa-88/

## Writing Rules
@~/.claude/gsd-docs-industrial/references/writing-guidelines.md

## Verification
- [ ] {Content completeness check}
- [ ] {Consistency check with CONTEXT.md decisions}
- [ ] {Table completeness check (all required columns filled)}
- [ ] {Standards compliance check if applicable}
- [ ] {Cross-reference accuracy check}
- [ ] {Language correctness check}
```

### 6.3 Verification Checklist Generation

Generate verification checklists at FULL FDS quality level, tailored to the section type. Every checklist MUST include these universal checks plus type-specific checks:

**Universal checks (all plan types):**
- [ ] All subsections in ## Sections present with substantive content
- [ ] CONTEXT.md decisions reflected (not contradicted)
- [ ] Language: configured language for descriptive text, English for technical terms
- [ ] Cross-references use symbolic format (not hardcoded section numbers)

**Equipment Module additions:** description covers function/purpose/position; operating states have entry/exit conditions and actions; all parameters have range, unit, default; all interlocks have condition, action, priority; I/O table has all 9 columns filled (Tag, Description, Type, Signal Range, Eng. Unit, PLC Address, Fail-safe State, Alarm Limits, Scaling); signal tags follow PROJECT.md naming; standards compliance if enabled (PackML state names exact, ISA-88 terminology correct).

**Interface additions:** overview table complete (type, direction, counterpart, update rate); signal list with type/direction/range; protocol details cover connection, data exchange, error handling; timeout and recovery specified.

**State Machine additions (part of EM plan):** Mermaid stateDiagram-v2 present; all states described with actions; transition table complete (from, to, trigger, condition, action); PackML names correct if enabled.

**Overview/Summary additions:** all phase sections referenced; no contradictions with individual content.

### 6.4 Context Extraction Rules

For each plan's ## Context section:
- Extract ONLY decisions from CONTEXT.md that are relevant to THIS specific section
- Include specific technical values (temperatures, capacities, timing) that apply to this section
- Include Claude's Discretion items that affect this section
- Include cross-phase reference flags if this section references other phases
- Do NOT include decisions about other equipment modules or other sections
- Keep ## Context concise: 5-15 bullet points maximum

### 6.5 Template Reference Rules

- Equipment Module sections: `@~/.claude/gsd-docs-industrial/templates/fds/section-equipment-module.md`
- State Machine sections (standalone): `@~/.claude/gsd-docs-industrial/templates/fds/section-state-machine.md`
- Interface sections: `@~/.claude/gsd-docs-industrial/templates/fds/section-interface.md`
- EM with state machine: reference BOTH equipment module template AND state machine template
- Foundation/Architecture/HMI/Safety/Appendix: no specific template (## Sections describes structure directly)

### 6.6 Standards Reference Rules

**Only include ## Standards section if standards are enabled in PROJECT.md.**

- If PackML enabled: `- PackML: @~/.claude/gsd-docs-industrial/references/standards/packml/`
- If ISA-88 enabled: `- ISA-88: @~/.claude/gsd-docs-industrial/references/standards/isa-88/`
- If no standards enabled: omit the ## Standards section entirely

Standards are ALWAYS referenced by name/path. Never embed PackML state lists, ISA-88 hierarchy definitions, or other standards content directly in the plan.

### 6.7 Write Plan Files

Write each plan file to the phase directory:

```bash
PLAN_FILE="${PHASE_DIR}/${PADDED_PHASE}-$(printf "%02d" ${PLAN_NUM})-PLAN.md"
```

Track all generated plan files for the completion summary.

---

## Step 7: Self-Verify Plans

Before completing, run inline verification checks on ALL generated plans. Do not present broken plans to the engineer.

### 7.1 Run Verification Checks

**Check 1 -- Structure:** Every plan has all required sections (Goal, Sections, Context, Template or structure description, Verification). Writing Rules section present.

**Check 2 -- Wave consistency:** No plan depends on a plan in the same or later wave. For each plan, follow its `depends_on` list and verify all dependencies are in earlier waves.

**Check 3 -- No circular dependencies:** Follow `depends_on` chains from each plan. Every chain must terminate (reach a plan with empty depends_on). If a cycle is detected: fix it by breaking the weakest dependency.

**Check 4 -- CONTEXT.md coverage:** Every decision in CONTEXT.md `<decisions>` section is reflected in at least one plan's ## Context section. No decisions should be orphaned (captured but never used in any plan).

**Check 5 -- Template references valid:** Every ## Template path points to an existing template file. Verify using Glob:

```bash
# Example check
ls ~/.claude/gsd-docs-industrial/templates/fds/section-equipment-module.md
```

**Check 6 -- Standards conditional:** ## Standards section is only present in plans if PROJECT.md has the corresponding standard enabled. Plans must NOT include ## Standards if no standards are enabled.

**Check 7 -- Naming convention:** All generated files follow `NN-MM-PLAN.md` naming where NN is the zero-padded phase number and MM is the zero-padded plan number.

### 7.2 Fix Issues

If any check fails:
1. Fix the issue in the affected plan file(s)
2. Re-run the failed check
3. Continue until all checks pass

### 7.3 Display Verification Results

```
Self-Verification:
[PASS] Structure: all plans have required sections
[PASS] Waves: no dependency violations
[PASS] No circular dependencies
[PASS] Coverage: all CONTEXT.md decisions mapped
[PASS] Templates: all references valid
[PASS] Standards: conditional on PROJECT.md settings
[PASS] Naming: all files follow NN-MM-PLAN.md format
```

If a check was initially failed and fixed:
```
[FIXED] {Check name}: {what was wrong} -> {what was fixed}
```

---

## Step 8: Gap Closure Mode (--gaps flag)

This step runs ONLY if --gaps flag was detected in Step 1. Skip Steps 2-7 for gap closure.

### 8.1 Load VERIFICATION.md

Look for the phase verification file:

```bash
VERIFICATION_FILE="${PHASE_DIR}/${PADDED_PHASE}-VERIFICATION.md"
if [ ! -f "$VERIFICATION_FILE ]; then
  VERIFICATION_FILE="${PHASE_DIR}/VERIFICATION.md"
fi
```

**If VERIFICATION.md not found:** Show error box: "No VERIFICATION.md found. Run `/doc:verify-phase {N}` first." Stop execution.

Read VERIFICATION.md and parse:

**8.1a Parse Status:**
- Extract from header: `Status: {PASS | GAPS_FOUND}`
- **If status is PASS:** Show message: "No gaps to fix. Phase already verified." Stop execution.
- **If status is GAPS_FOUND:** Proceed with gap closure

**8.1b Parse Cycle Count:**
- Extract from header: `Cycle: {N} of 2`
- Store as `CURRENT_CYCLE` for tracking

**8.1c Parse Summary Table:**
Read the Summary table (## Summary section) to identify all truths and their verification status:
- Column headers: Truth | Exists | Substantive | Complete | Consistent | Standards | Status
- For each row: extract truth description and final status (PASS or GAP)
- Extract failure level (the first column with ⚠ symbol) for each GAP
- Store list of failed truths with their failure levels

**8.1d Parse Detailed Findings:**
For each truth with status GAP from the summary table:
- Find the corresponding "### Truth {N}: {description}" section in Detailed Findings
- Extract:
  - Truth number and full description
  - Failure level name (Exists, Substantive, Complete, Consistent, or Standards)
  - Gap description paragraph (descriptive text below "**Gap description:**")
  - Evidence section (File paths, Context references, Details)
- Store complete gap information for plan generation

### 8.2 Extract and Group Gaps

Process all identified gaps to determine fix plan grouping:

**8.2a Analyze Gap Relationships:**
For each gap:
- Identify affected file(s) from Evidence section
- Identify affected section/artifact (extract from file path)
- Note failure level (determines fix complexity)
- Check if gap mentions cross-references

**8.2b Gap Grouping Rules:**
- **Same artifact + related levels:** If multiple truths fail for the same CONTENT.md file at related levels (e.g., Complete + Consistent), group into ONE fix plan
- **Same artifact + unrelated levels:** If failure levels indicate different root causes (e.g., Exists + Standards), create SEPARATE fix plans
- **Different artifacts:** Always separate fix plans
- **Cross-reference gaps:** Separate fix plan (affects multiple sections)

**8.2c Create Gap Groups:**
Generate a list of gap groups where each group contains:
- Gap group ID (sequential)
- List of truths in this group (by number)
- Primary affected file
- Failure level(s)
- Combined gap description

### 8.3 Gap Preview

Display the extracted gaps to the engineer (informational preview per user decision):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > GAP CLOSURE FOR PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cycle {CURRENT_CYCLE} of 2

Gaps to address ({count}):

1. Truth {N}: {Truth description}
   Level: {failure level name}
   File: {affected file}

2. Truth {M}: {Truth description}
   Level: {failure level name}
   File: {affected file}

...

Fix plans to generate: {gap_group_count}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > GAT HERSTEL VOOR FASE {N}`, translate "Cycle" to "Cyclus", "Gaps to address" to "Gaten om te verhelpen", "Fix plans to generate" to "Herstelplannen om te genereren".

**Note:** The preview is informational only. In non-interactive mode, display the preview and proceed. Engineers can delete unwanted generated fix plans before running write-phase.

### 8.4 Determine Next Plan Number

Find existing plan files in the phase directory to determine the next available plan number:

```bash
LAST_PLAN=$(ls ${PHASE_DIR}/${PADDED_PHASE}-*-PLAN.md 2>/dev/null | sort | tail -1)
LAST_PLAN_NUM=$(echo "$LAST_PLAN" | grep -oE '[0-9]+-[0-9]+' | cut -d'-' -f2)
NEXT_PLAN_NUM=$((LAST_PLAN_NUM + 1))
```

Start generating fix plans from `${NEXT_PLAN_NUM}`.

### 8.5 Generate Fix Plans

For each gap group identified in Step 8.2, generate a targeted fix PLAN.md file.

**Fix Plan Frontmatter:**
```yaml
---
phase: {N}
plan: {MM}
name: Fix: {brief gap description}
type: {same type as original section -- equipment-module, interface, etc.}
wave: 1
depends_on: []
autonomous: true
gap_closure: true
original_plan: {NN-MM of original plan that produced the content}
---
```

**Fix Plan Body:**
```markdown
# Fix: {Gap Description}

## Goal
Close the verification gap: {truth that failed}.

Original content in {file} failed verification at Level {N} ({level name}).

{Additional context about what this fix achieves}

## Gap Description

{Full gap description from VERIFICATION.md -- copied verbatim from "Gap description:" section}

## Evidence

{Evidence from VERIFICATION.md -- copied verbatim from "Evidence:" section}
- File: {path}
- Context: {CONTEXT.md reference or standards reference}
- Details: {specific values, quotes from files}

## Context

{Extract relevant decisions from phase CONTEXT.md that apply to this fix}
- {Decision that was violated or not fully implemented}
- {Technical value or requirement that needs to be met}

{If failure level is Consistent: include the specific CONTEXT.md section that was contradicted}
{If failure level is Standards: include the specific standard requirement}

## Template

@~/.claude/gsd-docs-industrial/templates/fds/{original template reference}

{Use the same template as the original plan that created the content being fixed}

## Writing Rules

@~/.claude/gsd-docs-industrial/references/writing-guidelines.md

## Verification

- [ ] Truth {N} ({truth description}) now passes Level {failure level} verification
- [ ] {Specific check that the gap is closed -- based on gap description}
- [ ] Content still passes all previously passing verification levels
- [ ] CONTEXT.md decisions reflected correctly
- [ ] Cross-references remain valid (if applicable)
- [ ] {Standards compliance if failure level was Standards}
```

**Fix Plan Generation Rules:**
- **wave:** All gap closure plans get wave: 1 (they are independent targeted fixes)
- **type:** Use the same type as the original section (equipment-module, interface, overview, etc.)
- **gap_closure:** Set to `true` to mark this as a gap closure plan
- **original_plan:** Include the plan ID (NN-MM) that originally created the content being fixed (extract from CONTENT.md filename or SUMMARY.md tracking)
- **name:** Keep concise (under 60 chars): "Fix: {brief description}" not "Gap Fix: {long description}"
- **Goal:** State the truth being fixed and the failure level
- **Gap Description:** Copy verbatim from VERIFICATION.md (do not paraphrase or rewrite)
- **Evidence:** Copy verbatim from VERIFICATION.md
- **Context:** Extract ONLY the relevant decisions from CONTEXT.md that apply to THIS specific gap (not all phase decisions)
- **Verification:** Include the specific truth number and tailored checks for the failure level

**Failure Level-Specific Verification:**
- **Level 1 (Exists):** "Content file exists with non-zero size", "All required sections present"
- **Level 2 (Substantive):** "No placeholder markers ([TODO], [TBD], [PLACEHOLDER])", "Content has substantive detail (not stubs)"
- **Level 3 (Complete):** "All required template sections present", "All table columns filled", "All parameters/interlocks documented"
- **Level 4 (Consistent):** "CONTEXT.md decision {X} reflected correctly", "Technical values match CONTEXT.md", "No contradictions with phase decisions"
- **Level 5 (Standards):** "PackML state names use exact canonical names", "ISA-88 terminology correct", "Standards references accurate"

### 8.6 Write Fix Plan Files

Write each generated fix plan to the phase directory:

```bash
PLAN_NUM=${NEXT_PLAN_NUM}
for each gap_group:
  PLAN_FILE="${PHASE_DIR}/${PADDED_PHASE}-$(printf "%02d" ${PLAN_NUM})-PLAN.md"
  # Write plan content to file
  PLAN_NUM=$((PLAN_NUM + 1))
done
```

Track all generated plan files for the completion summary.

### 8.7 Self-Verify Fix Plans

Before completing, run inline verification checks on ALL generated fix plans (same checks as Step 7). Do not present broken plans to the engineer.

**Run Checks 1-7 from Step 7:**
- Structure: all required sections present
- Wave consistency: all are Wave 1 (no dependencies)
- No circular dependencies: all have empty depends_on
- Template references valid
- Standards conditional on PROJECT.md settings
- Naming convention: NN-MM-PLAN.md format
- Special: gap_closure: true flag present in frontmatter

**Fix issues if any check fails, then re-run until all pass.**

### 8.8 Display Verification Results

```
Self-Verification:
[PASS] Structure: all fix plans have required sections
[PASS] Waves: all fix plans in Wave 1
[PASS] Templates: all references valid
[PASS] Gap closure flags: all plans marked with gap_closure: true
[PASS] Naming: all files follow NN-MM-PLAN.md format
```

---

## Step 9: Completion

### 9.1 Git Commit

**For normal planning mode (Steps 2-7):**

Stage and commit all generated plan files:

```bash
git add ${PHASE_DIR}/${PADDED_PHASE}-*-PLAN.md
git commit -m "docs(${PADDED_PHASE}): generate section plans for phase ${PHASE}

Phase ${PHASE}: ${PHASE_NAME}
- ${PLAN_COUNT} plans in ${WAVE_COUNT} waves
- Wave assignments based on dependency analysis
- Self-verified: all 7 checks passed
- Ready for /doc:write-phase ${PHASE}"
```

**For gap closure mode (Step 8):**

Stage and commit gap closure fix plans:

```bash
git add ${PHASE_DIR}/${PADDED_PHASE}-*-PLAN.md
git commit -m "docs(${PADDED_PHASE}): generate gap closure plans for phase ${PHASE}

Phase ${PHASE}: ${PHASE_NAME} (Gap Closure - Cycle ${CURRENT_CYCLE})
- ${FIX_PLAN_COUNT} fix plans generated (all Wave 1)
- Targets ${GAP_COUNT} gaps from VERIFICATION.md
- Self-verified: all checks passed
- Ready for /doc:write-phase ${PHASE}"
```

### 9.2 Display Completion Banner

**For normal planning mode:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PHASE {N} PLANNED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} GEPLAND`

**For gap closure mode:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > GAP FIX PLANS GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > GAT HERSTELPLANNEN GEGENEREERD`

### 9.3 Display Summary

**For normal planning mode:**

Show a wave summary table so the engineer understands the parallel execution structure:

```
Wave Structure:
| Wave | Plans | Sections |
|------|-------|----------|
| 1    | 01, 02, 03 | {Section names for wave 1} |
| 2    | 04 | {Section names for wave 2} |
| 3    | 05 | {Section names for wave 3} |

Plans: {total} in {wave count} waves
Parallel: Wave 1 ({count} plans){, Wave 2 ({count} plans)}
Sequential: {Last wave description}
```

**For gap closure mode:**

```
Fix Plans: {count}
Wave: 1 (all parallel)
Files: {list of generated PLAN.md files}

Gap Coverage:
| Plan | Truth | Failure Level | Target File |
|------|-------|---------------|-------------|
| {MM} | {Truth N}: {brief description} | {Level name} | {filename} |
| {MM} | {Truth N}: {brief description} | {Level name} | {filename} |
...

Plans: {count} gap closure plans (all Wave 1)
```

### 9.4 Next Up Block

**For normal planning mode:**

```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase {N}: {Phase Name}** -- Write sections using generated plans

`/doc:write-phase {N}`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:status` -- view project progress
- Review/edit PLAN.md files before continuing

───────────────────────────────────────────────────────────────
```

Dutch (if `LANGUAGE = "nl"`): translate "Next Up" to "Volgende Stap", "Also available" to "Ook beschikbaar".

**For gap closure mode:**

```
───────────────────────────────────────────────────────────────

## > Next Up

**Fix gaps:** Execute generated fix plans

`/doc:write-phase {N}`

Then: `/doc:verify-phase {N}` to re-verify

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:status` -- view project progress
- Review/edit fix PLAN.md files before continuing
- Delete unwanted fix plans if needed

───────────────────────────────────────────────────────────────
```

Dutch (if `LANGUAGE = "nl"`): translate "Fix gaps" to "Verhelp gaten", "Then" to "Daarna", "to re-verify" to "om opnieuw te verifiëren".

---

## Workflow Rules

1. **Non-interactive:** No AskUserQuestion calls. Reads inputs, generates outputs.
2. **Language consistency:** User-facing text matches PROJECT.md language. Internal variables remain English.
3. **DOC > prefix:** All banners use `DOC >`. Never use GSD namespace.
4. **Doc PLAN.md format:** ## Goal, ## Sections, ## Context, ## Template, ## Standards, ## Writing Rules, ## Verification. Never `<task type="auto">` XML.
5. **CONTEXT.md is source of truth:** Do not invent decisions or ask the engineer.
6. **Standards by reference only:** Name/path in ## Standards. Never inline content.
7. **SUMMARY.md = completion proof:** Dependency checks use SUMMARY.md, not STATE.md.
8. **Configurable subsections:** Select applicable subsections per EM from CONTEXT.md. Not all 9 every time.
9. **Wave assignment:** Minimize waves. Independent to Wave 1. Dependent to earliest valid. Overview/summary last.
10. **Self-verify before completing:** All 7 checks must pass. Fix issues. Never output broken plans.
11. **One plan per EM:** Never split EM across plans. State machines are part of EM plan.
12. **Cross-phase references:** Flag for review, do not block. Symbolic references validated by `/doc:verify-phase`.
13. **Type C/D delta focus:** New or changed content only. Reference BASELINE.md for unchanged.
14. **Error handling:** Error box and stop on missing ROADMAP, phase, CONTEXT, or unmet dependencies.
15. **No emoji:** Only status symbols from ui-brand.md.
16. **Full FDS quality verification:** Content, CONTEXT.md consistency, tables, standards, naming, cross-refs, language.

</workflow>
