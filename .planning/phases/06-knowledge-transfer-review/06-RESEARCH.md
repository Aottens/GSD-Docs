# Phase 6: Knowledge Transfer + Review - Research

**Researched:** 2026-02-14
**Domain:** Incremental knowledge capture in FDS workflows + multi-perspective fresh eyes review + structured document review
**Confidence:** HIGH

## Summary

Phase 6 enhances the existing FDS workflow with knowledge transfer artifacts that preserve the "why" behind decisions and capture edge cases as they emerge, plus two review mechanisms: Fresh Eyes (simulated new reader) and review-phase (structured engineer/client handover). The core challenge is **incremental capture** — RATIONALE.md updates during discuss-phase, EDGE-CASES.md during write-phase, Fresh Eyes after verify-phase PASS — rather than generating all knowledge artifacts at the end when context is lost.

The research examined: (1) the existing workflow integration points (discuss-phase, write-phase, verify-phase) where knowledge capture must occur, (2) patterns for updating shared files (RATIONALE.md) without coordination overhead in parallel workflows, (3) multi-perspective review simulation (engineer/customer/operator lenses), (4) structured section-by-section review workflows with feedback capture, and (5) routing review findings to the gap closure pipeline.

The critical architectural insight: Phase 6 does NOT create new standalone commands for knowledge capture. Instead, it **enhances existing workflows** (discuss-phase workflow gains RATIONALE capture step, write-phase workflow gains EDGE-CASES capture step, verify-phase workflow gains Fresh Eyes offer). The only new command is `/doc:review-phase` for structured engineer handover.

**Primary recommendation:** Follow the established pattern: modify existing workflow files to add knowledge capture steps at the exact trigger points, create one new command (review-phase.md) + workflow for structured review, and introduce templates for RATIONALE.md, EDGE-CASES.md, FRESH-EYES.md, and REVIEW.md format specification. Fresh Eyes uses a fresh subagent with configurable perspective (engineer/customer/operator) to simulate different reader types. Review-phase uses interactive section presentation with AskUserQuestion for per-section feedback.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Rationale capture
- Every decision from discuss-phase is logged — completeness over curation
- Full context per entry: decision, reasoning, alternatives considered, and what was ruled out (4-6 sentences)
- Single project-wide RATIONALE.md in .planning/ (not per phase)
- Entries organized by FDS section — a new engineer can find all decisions about a specific section in one place
- discuss-phase workflow updates RATIONALE.md automatically after each discussion area completes

#### Edge case documentation
- Capture everything notable — failure modes, unusual sequences, boundary conditions, and minor quirks
- Entry format: situation, system behavior, recovery steps, AND design reason (why the system behaves this way)
- Per-phase EDGE-CASES.md in the phase directory — edge cases stay close to the content that surfaced them
- 3 severity levels: CRITICAL (safety/equipment), WARNING (operational impact), INFO (notable quirk)
- After write-phase completes, show summary: "N edge cases captured in EDGE-CASES.md"
- Edge cases referencing equipment from other phases add entries to CROSS-REFS.md automatically

#### Fresh Eyes review
- Checks both comprehension gaps (undefined terms, assumed knowledge) AND completeness gaps (missing context, logical jumps)
- Three perspectives via --perspective flag: engineer (technical clarity), customer (jargon/scope/commitments), operator (procedures/recovery/daily use)
- Offered after verify-phase PASS — engineer can accept or skip
- Output goes to standalone FRESH-EYES.md per phase — distinct from formal verification
- Customer perspective is strict on jargon — flag all internal jargon, unexplained abbreviations, overly technical language
- Operator perspective checks both procedural clarity AND operational completeness (states, alarms, sequences)
- 3 severity levels: MUST-FIX (genuinely confusing), SHOULD-FIX (improvement), CONSIDER (nice-to-have)
- Separate sections per perspective in FRESH-EYES.md (Engineer / Customer / Operator)
- Default informational only — --actionable flag routes findings to gap closure pipeline (plan-phase --gaps)

#### Review workflow (/doc:review-phase)
- Primary audience: engineer handover — present for a colleague taking over the project
- Interactive section-by-section flow — show one section at a time, collect feedback, then next
- Each section presentation includes: content, SUMMARY.md key facts, and cross-references
- Per-section status: Approved (no issues), Comment (minor note), Flag (needs revision)
- Feedback captured in REVIEW.md per phase — structured with section, finding, severity, suggested action
- Resolution configurable: default manual, --route-gaps flag sends findings to gap closure pipeline

### Claude's Discretion
- Severity classification calibration for Fresh Eyes (stricter for safety-critical sections, lighter for overview)
- How to present sections during review (formatting, context level)
- RATIONALE.md entry boundaries (when one discussion answer produces multiple entries vs. one)
- Gap closure integration details when --actionable or --route-gaps flags are used

### Specific Implementation Ideas
- RATIONALE.md serves as the "design decisions log" — a new engineer should be able to read it and understand not just "what" but "why" for every FDS section
- Edge cases with CRITICAL severity should stand out visually (not just a label) so they're impossible to miss
- Fresh Eyes customer perspective simulates a customer reading the FDS for the first time and flagging anything that would make them ask "what does this mean?"
- Operator perspective simulates someone who runs the system daily and needs to follow procedures during normal operation and fault recovery

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope

</user_constraints>

## Standard Stack

Phase 6 enhances existing workflow files and creates one new command. The "stack" is the established patterns from Phases 1-5 plus new knowledge transfer templates.

### Core

| Component | Location | Purpose | Why Standard |
|-----------|----------|---------|--------------|
| discuss-phase.md (enhanced) | `workflows/discuss-phase.md` | Add RATIONALE.md capture step after each discussion area | Existing workflow, enhanced with knowledge capture |
| write-phase.md (enhanced) | `workflows/write-phase.md` | Add EDGE-CASES.md aggregation after each wave | Existing workflow, enhanced with edge case capture |
| verify-phase.md (enhanced) | `workflows/verify-phase.md` | Add Fresh Eyes offer after PASS result | Existing workflow, enhanced with review trigger |
| review-phase.md (NEW) | `commands/doc/review-phase.md` | Structured section-by-section review orchestrator | New command following Phase 1 lean command pattern |
| review-phase workflow (NEW) | `workflows/review-phase.md` | Interactive review presentation logic | New workflow following Phase 1 detailed workflow pattern |
| fresh-eyes subagent (NEW) | `agents/fresh-eyes.md` | Simulated reader with configurable perspective | New subagent definition following doc-writer pattern |

### Supporting

| Component | Location | Purpose | When Used |
|-----------|----------|---------|-----------|
| RATIONALE.md template | `templates/rationale.md` | Format for decision logging | Referenced by enhanced discuss-phase workflow |
| EDGE-CASES.md template | `templates/edge-cases.md` | Format for edge case documentation | Referenced by enhanced write-phase workflow |
| FRESH-EYES.md template | `templates/fresh-eyes.md` | Format for Fresh Eyes findings | Referenced by enhanced verify-phase workflow |
| REVIEW.md template | `templates/review.md` | Format for review feedback capture | Referenced by review-phase workflow |
| gsd-tools.js | `~/.claude/get-shit-done/bin/gsd-tools.js` | Phase operations helper | Already exists; used for file operations |

### File Modification Pattern

Phase 6 differs from prior phases: instead of creating entirely new files, it **enhances existing workflows** with knowledge capture steps:

```
Enhanced files (modify existing):
  gsd-docs-industrial/workflows/discuss-phase.md     (add Step X: Update RATIONALE.md)
  gsd-docs-industrial/workflows/write-phase.md       (add edge case aggregation after wave)
  gsd-docs-industrial/workflows/verify-phase.md      (add Fresh Eyes offer after PASS)
  gsd-docs-industrial/agents/doc-writer.md           (add EDGE-CASES.md output step)

New files (create):
  commands/doc/review-phase.md                       (command file ~60-80 lines)
  gsd-docs-industrial/workflows/review-phase.md      (workflow file ~400-500 lines)
  gsd-docs-industrial/agents/fresh-eyes.md           (subagent ~100-150 lines)
  gsd-docs-industrial/templates/rationale.md         (template ~40 lines)
  gsd-docs-industrial/templates/edge-cases.md        (template ~40 lines)
  gsd-docs-industrial/templates/fresh-eyes.md        (template ~60 lines)
  gsd-docs-industrial/templates/review.md            (template ~50 lines)
```

## Architecture Patterns

### Recommended Project Structure

```
commands/doc/
├── discuss-phase.md          # (existing - no change)
├── write-phase.md            # (existing - no change)
├── verify-phase.md           # (existing - no change)
└── review-phase.md           # NEW command (~60-80 lines)

gsd-docs-industrial/
├── workflows/
│   ├── discuss-phase.md      # MODIFY: add RATIONALE.md step
│   ├── write-phase.md        # MODIFY: add EDGE-CASES.md aggregation
│   ├── verify-phase.md       # MODIFY: add Fresh Eyes offer
│   └── review-phase.md       # NEW workflow (~400-500 lines)
├── agents/
│   ├── doc-writer.md         # MODIFY: add EDGE-CASES.md output
│   ├── doc-verifier.md       # (no change)
│   └── fresh-eyes.md         # NEW subagent (~100-150 lines)
└── templates/
    ├── rationale.md          # NEW template
    ├── edge-cases.md         # NEW template
    ├── fresh-eyes.md         # NEW template
    └── review.md             # NEW template

.planning/
├── RATIONALE.md              # Project-wide decision log (created by discuss-phase)
└── phases/
    └── NN-*/
        ├── EDGE-CASES.md     # Per-phase edge cases (created by write-phase)
        ├── FRESH-EYES.md     # Per-phase Fresh Eyes findings (created by verify-phase)
        └── REVIEW.md         # Per-phase review feedback (created by review-phase)
```

### Pattern 1: Incremental Shared File Update (RATIONALE.md)

**What:** RATIONALE.md is a single project-wide file updated incrementally during discuss-phase. Multiple phases add entries to the same file without coordination overhead.

**When to use:** discuss-phase workflow after each discussion area is completed.

**Challenge:** RATIONALE.md is shared across all phases. Phase 3 discuss adds entries, then Phase 4 discuss adds more entries, etc. The file grows incrementally, organized by FDS section reference.

**Solution pattern:**

```markdown
## Enhanced discuss-phase workflow: Step N (new step after decision capture)

After capturing decisions in CONTEXT.md for a discussion area, update RATIONALE.md:

### N.1 Check if RATIONALE.md exists

```bash
if [ ! -f .planning/RATIONALE.md ]; then
  # First time: create from template
  cp ~/.claude/gsd-docs-industrial/templates/rationale.md .planning/RATIONALE.md
fi
```

### N.2 Extract decision context

For the just-discussed area, extract:
- Decision statement (what was decided)
- Reasoning (why this choice)
- Alternatives considered (what was ruled out and why)
- FDS section reference (where this decision applies)

### N.3 Append entry to RATIONALE.md

Use structured format:
```markdown
### [Section Ref] Decision Title
**Decision:** [What was decided, 1-2 sentences]
**Reasoning:** [Why this choice, 2-3 sentences]
**Alternatives:** [What was considered and ruled out, 1-2 sentences]
**Date:** [YYYY-MM-DD]
**Phase:** [N]
```

### N.4 Show confirmation

Display to engineer:
```
📝 RATIONALE.md updated:
   [Section Ref] Decision Title
   └─ Decision, reasoning, and alternatives logged
```

Continue to next discussion area.
```

**File organization strategy:**

RATIONALE.md entries are organized by FDS section reference, NOT by phase or chronological order. This allows a new engineer to find all decisions about a specific section (e.g., "EM-200") in one place, even if those decisions were made across multiple phases.

**Append-only pattern:**
```markdown
# RATIONALE.md structure

## Introduction
[Purpose of this file]

## Equipment Modules

### §3.2 EM-200 Bovenloopkraan: Collision Detection
**Decision:** No collision detection system installed
**Reasoning:** Client confirmed single-crane operation only, collision physically impossible in this configuration. Adding collision detection would add €5k hardware + commissioning complexity with no safety benefit.
**Alternatives:** Ultrasonic sensor collision detection (ruled out: unnecessary cost), software zone management (ruled out: requires PLC upgrade)
**Date:** 2026-02-10
**Phase:** 3

### §3.2 EM-200 Bovenloopkraan: E-stop Behavior
**Decision:** Controlled stop with position retention
**Reasoning:** E-stop must prevent load drop (safety), but immediate motor cut would cause brake engagement at speed (mechanical stress). Controlled deceleration over 500ms balances safety and equipment protection.
**Alternatives:** Immediate stop (ruled out: brake wear), coast to stop (ruled out: safety), drop to safe zone (ruled out: no designated safe zone exists)
**Date:** 2026-02-10
**Phase:** 3

## Interfaces

### §7.2 SCADA Interface: Protocol Selection
**Decision:** Modbus TCP on existing network
**Reasoning:** Client has existing Modbus TCP infrastructure and trained staff. Migration to Profinet would require switch upgrade (€3k) and staff retraining with no functional benefit for this application.
**Alternatives:** Profinet (ruled out: infrastructure cost), OPC-UA (ruled out: PLC doesn't support it), hardwired (ruled out: 50+ signals, cable cost prohibitive)
**Date:** 2026-02-12
**Phase:** 4

## [More sections as added...]
```

**Source:** User decision in CONTEXT.md specifies single project-wide RATIONALE.md organized by FDS section.

### Pattern 2: Per-Phase Edge Case Capture During Write

**What:** EDGE-CASES.md is created per phase during write-phase, capturing edge cases and failure modes as writers discover them. Each writer appends to the phase-level file.

**When to use:** write-phase workflow after each wave completes, aggregating edge cases from all writers in that wave.

**Challenge:** Multiple doc-writer subagents run in parallel within a wave. Each discovers edge cases independently. These must be aggregated into a single EDGE-CASES.md per phase without coordination during parallel execution.

**Solution pattern:**

```markdown
## Enhanced write-phase workflow: after each wave completes

### Wave Completion: Aggregate Edge Cases

After all writers in wave N complete:

```bash
# Check if any writers produced edge case entries
# Writers append to temporary files: {plan-id}-edge-cases.tmp

PHASE_DIR=.planning/phases/${PADDED_PHASE}-${PHASE_NAME}
EDGE_CASE_FILE="${PHASE_DIR}/${PADDED_PHASE}-EDGE-CASES.md"

# Initialize EDGE-CASES.md if first wave
if [ ! -f "$EDGE_CASE_FILE" ]; then
  cp ~/.claude/gsd-docs-industrial/templates/edge-cases.md "$EDGE_CASE_FILE"
fi

# Aggregate from all writers in this wave
for PLAN_FILE in ${PHASE_DIR}/*-PLAN.md; do
  PLAN_ID=$(basename "$PLAN_FILE" -PLAN.md)
  TMP_FILE="${PHASE_DIR}/${PLAN_ID}-edge-cases.tmp"

  if [ -f "$TMP_FILE" ]; then
    # Append entries to phase EDGE-CASES.md
    cat "$TMP_FILE" >> "$EDGE_CASE_FILE"
    rm "$TMP_FILE"
  fi
done

# Count entries by severity
CRITICAL=$(grep -c "| CRITICAL |" "$EDGE_CASE_FILE" || echo 0)
WARNING=$(grep -c "| WARNING |" "$EDGE_CASE_FILE" || echo 0)
INFO=$(grep -c "| INFO |" "$EDGE_CASE_FILE" || echo 0)

echo ""
echo "📝 Edge cases captured: ${CRITICAL} CRITICAL, ${WARNING} WARNING, ${INFO} INFO"
echo "   See: ${EDGE_CASE_FILE}"
```

### Writer Responsibility: Create Temporary Edge Case Entries

Enhanced doc-writer subagent (modified agent definition):

During writing, when an edge case is identified:
1. Document in CONTENT.md as part of section content
2. Extract to temporary file: {plan-id}-edge-cases.tmp in phase directory
3. Use structured format:
   ```
   | [SEVERITY] | [Situation] | [System Behavior] | [Recovery Steps] | [Design Reason] | [Section] |
   ```
4. Continue writing

The orchestrator aggregates after wave completes.
```

**EDGE-CASES.md format (from template):**

```markdown
# Phase N: [Name] - Edge Cases

**Created:** [date]
**Last Updated:** [date]

## CRITICAL (Safety / Equipment Damage)

| Situation | System Behavior | Recovery Steps | Design Reason | Section |
|-----------|-----------------|----------------|---------------|---------|
| E-stop during crane movement | Controlled deceleration (500ms), position retained, brake engages | Operator: clear fault, manual jog to safe position, reset system | Immediate brake = mechanical stress; controlled stop balances safety + equipment protection | §3.2 EM-200 |

## WARNING (Operational Impact)

| Situation | System Behavior | Recovery Steps | Design Reason | Section |
|-----------|-----------------|----------------|---------------|---------|
| Weighing timeout (>10s unstable) | Batch paused, HMI warning, wait for manual continue | Operator: check for vibration source, manual override if stable enough | Vibration from adjacent equipment can prevent settling; human judgment needed | §3.3 EM-300 |

## INFO (Notable Behavior)

| Situation | System Behavior | Recovery Steps | Design Reason | Section |
|-----------|-----------------|----------------|---------------|---------|
| Double start command | Second command ignored, no feedback | None needed (ignore duplicate) | Prevents state confusion; operator might press twice by habit | §3.2 EM-200 |
```

**Visual distinction for CRITICAL:**
In the assembled FDS, CRITICAL edge cases render with warning box formatting:

```markdown
> ⚠️ **CRITICAL EDGE CASE**
>
> **Situation:** E-stop during crane movement
> **Behavior:** Controlled deceleration (500ms), position retained, brake engages
> **Recovery:** Clear fault → manual jog to safe position → reset system
> **Reason:** Immediate brake = mechanical stress; controlled stop balances safety + equipment protection
```

**Cross-reference handling:**
When an edge case references equipment from another phase, automatically add entry to CROSS-REFS.md:

```bash
# After aggregating edge cases, check for cross-phase references
grep -E "§[0-9]+\.[0-9]+" "$EDGE_CASE_FILE" | while read LINE; do
  # Extract section reference
  SECTION_REF=$(echo "$LINE" | grep -oE "§[0-9]+\.[0-9]+")
  PHASE_NUM=$(echo "$SECTION_REF" | grep -oE "[0-9]+" | head -1)

  if [ "$PHASE_NUM" != "$CURRENT_PHASE" ]; then
    # Cross-phase reference: add to CROSS-REFS.md
    echo "| Edge case | §${SECTION_REF} | depends-on | Edge case handling | pending |" >> CROSS-REFS.md
  fi
done
```

**Source:** User decision in CONTEXT.md specifies per-phase EDGE-CASES.md with 3 severity levels and automatic cross-reference tracking.

### Pattern 3: Fresh Eyes Review After Verify PASS

**What:** After verify-phase returns PASS, offer an optional Fresh Eyes review that simulates a new reader (engineer/customer/operator) reviewing the documentation for comprehension and completeness gaps.

**When to use:** verify-phase workflow after VERIFICATION.md shows PASS status.

**Architecture:**

```markdown
## Enhanced verify-phase workflow: after PASS result

### Step N: Offer Fresh Eyes Review (new step)

If VERIFICATION.md status is PASS:

```bash
echo ""
echo "✓ Phase ${PHASE} verification: PASS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Optional: Fresh Eyes Review"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Simulate a new reader reviewing the documentation."
echo "Checks for: undefined terms, assumed knowledge, missing context, logical jumps"
echo ""
echo "Perspectives available:"
echo "  1. Engineer (technical clarity)"
echo "  2. Customer (jargon, commitments, scope)"
echo "  3. Operator (procedures, recovery, daily use)"
echo "  4. All perspectives"
echo "  5. Skip Fresh Eyes"
echo ""
read -p "Selection (1-5): " FRESH_EYES_CHOICE

case "$FRESH_EYES_CHOICE" in
  1) PERSPECTIVE="engineer" ;;
  2) PERSPECTIVE="customer" ;;
  3) PERSPECTIVE="operator" ;;
  4) PERSPECTIVE="all" ;;
  5)
    echo "Fresh Eyes review skipped."
    exit 0
    ;;
  *)
    echo "Invalid choice. Skipping Fresh Eyes."
    exit 0
    ;;
esac

# Spawn fresh-eyes subagent with selected perspective
claude --agent fresh-eyes \
  --context ".planning/PROJECT.md,.planning/RATIONALE.md,.planning/phases/${PHASE_DIR}/*-CONTENT.md,.planning/phases/${PHASE_DIR}/*-SUMMARY.md,.planning/phases/${PHASE_DIR}/${PHASE}-CONTEXT.md" \
  --message "Perform Fresh Eyes review with perspective: ${PERSPECTIVE}. Produce FRESH-EYES.md with findings organized by perspective."

echo ""
echo "Fresh Eyes review complete. See: ${PHASE_DIR}/${PHASE}-FRESH-EYES.md"

# Check if --actionable flag was used
if [[ "$@" == *"--actionable"* ]]; then
  echo ""
  echo "Routing Fresh Eyes findings to gap closure pipeline..."
  /doc:plan-phase ${PHASE} --gaps --source fresh-eyes
fi
```
```

**Fresh-eyes subagent definition:**

```yaml
---
name: fresh-eyes
description: Simulates a new reader reviewing FDS documentation from a specific perspective. Use for Fresh Eyes review after verify-phase PASS.
tools: Read
disallowedTools: Write, Bash, Glob, Grep
model: sonnet
---

# Role: Fresh Eyes Reviewer

You simulate a reader encountering this FDS documentation for the first time. Your job is to identify comprehension gaps (undefined terms, assumed knowledge) and completeness gaps (missing context, logical jumps) from a specific perspective.

## Context You Receive

When spawned, you have access to:
- PROJECT.md: Project metadata and configuration
- RATIONALE.md: Design decisions and reasoning
- All CONTENT.md files for this phase: Full technical content
- All SUMMARY.md files for this phase: Section summaries
- Phase CONTEXT.md: Decisions made during planning

You do NOT have:
- Engineer's domain knowledge or industry experience
- Context from discuss-phase conversation
- Knowledge of what's "obvious" to the author

## Your Perspective

You are told which perspective to simulate via the spawning message:

**Engineer perspective:**
- You're a new engineer joining the project team
- Check for: technical terms without definition, missing implementation details, ambiguous specifications, inconsistent terminology
- Assume: general industrial automation knowledge, familiarity with PLCs and HMI, understanding of control loops
- Don't assume: project-specific decisions, equipment-specific behavior, client preferences

**Customer perspective:**
- You're the client reading the FDS for the first time
- Check for: jargon without explanation, unexplained abbreviations, overly technical language, unclear scope boundaries, commitments not explicitly stated
- Assume: basic understanding of their own process, what they asked for
- Don't assume: technical background, automation knowledge, industry standards

**Operator perspective:**
- You're an operator who will run this system daily
- Check for: procedural clarity (how to start/stop/recover), alarm response instructions, state transition understanding, manual control procedures, missing operational details
- Assume: familiarity with their own process, HMI operation basics
- Don't assume: internal system logic, PLC behavior, interlock reasoning

## Your Task

1. Read all CONTENT.md files with your assigned perspective
2. Identify findings in two categories:
   - **Comprehension gaps:** Things you can't understand without asking someone
   - **Completeness gaps:** Things that should be there but aren't
3. Classify severity for each finding:
   - MUST-FIX: Genuinely confusing, blocks understanding
   - SHOULD-FIX: Improvement that would help clarity
   - CONSIDER: Nice-to-have, minor enhancement
4. Organize findings by section reference
5. Write FRESH-EYES.md with structured findings

## Output Format

Create {phase}-FRESH-EYES.md:

```markdown
# Phase N: [Name] - Fresh Eyes Review

**Reviewed:** [date]
**Perspective:** [Engineer / Customer / Operator / All]

## Summary

| Category | MUST-FIX | SHOULD-FIX | CONSIDER | Total |
|----------|----------|------------|----------|-------|
| Comprehension Gaps | X | Y | Z | N |
| Completeness Gaps | X | Y | Z | N |
| **Total** | **X** | **Y** | **Z** | **N** |

## [PERSPECTIVE] Findings

### Comprehension Gaps

#### §3.2 EM-200: [SEVERITY] - [Brief Description]
**What's unclear:** [Describe the gap from perspective]
**Context:** [Quote or reference from CONTENT.md]
**Why it matters:** [Impact on reader]

### Completeness Gaps

#### §3.3 EM-300: [SEVERITY] - [Brief Description]
**What's missing:** [Describe what should be added]
**Why it matters:** [Impact on reader]

## [NEXT PERSPECTIVE] Findings
[Repeat structure if multiple perspectives]
```

## Severity Guidelines

**MUST-FIX examples:**
- Engineer: "§3.2 mentions 'settling time' without defining the value or units"
- Customer: "§7.2 uses 'Modbus TCP' without explaining what this means or why it was chosen"
- Operator: "§5.1 alarm AL-300-01 has no response procedure documented"

**SHOULD-FIX examples:**
- Engineer: "§3.3 transition conditions reference CONTEXT.md decisions not summarized in section"
- Customer: "§4.1 says 'standard HMI layout' but doesn't specify which standard"
- Operator: "§3.2 describes automatic sequence but not manual override procedure"

**CONSIDER examples:**
- Engineer: "§3.2 could benefit from Mermaid diagram showing state flow"
- Customer: "§7.2 could clarify expected response time"
- Operator: "§5.1 could add typical duration for each state"
```

**Perspective-specific calibration:**

The fresh-eyes subagent adjusts severity based on section type and perspective:

| Perspective | Stricter On | Lighter On |
|-------------|-------------|------------|
| Engineer | Safety-critical sections, interfaces, interlocks | Overview sections, appendices |
| Customer | Scope boundaries, commitments, cost-impacting decisions | Technical implementation details |
| Operator | Alarm responses, manual procedures, recovery steps | System architecture, design rationale |

**Source:** User decision in CONTEXT.md specifies three perspectives with distinct checking criteria and severity levels.

### Pattern 4: Structured Section-by-Section Review

**What:** `/doc:review-phase N` presents completed phase content section-by-section for engineer or client review, collecting feedback interactively and routing issues to gap closure if requested.

**When to use:** After phase verification PASS, when engineer wants structured handover review with a colleague or client walkthrough.

**Architecture:**

```markdown
## review-phase workflow: interactive section presentation

### Step 1: Load Phase Content

Read all CONTENT.md and SUMMARY.md files in phase directory.
Build section list in order.

### Step 2: Display Review Intro

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > Review Phase ${PHASE}: ${PHASE_NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review mode: Section-by-section presentation
Audience: Engineer handover / Client walkthrough

${SECTION_COUNT} sections to review.
```

### Step 3: For Each Section (Sequential)

```bash
for SECTION in ${SECTIONS[@]}; do
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " Section ${SECTION_NUM} of ${SECTION_COUNT}: ${SECTION_NAME}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  # Show SUMMARY.md first (context)
  echo "SUMMARY:"
  cat "${SECTION_DIR}/${SECTION_ID}-SUMMARY.md"
  echo ""

  # Show cross-references if any
  XREFS=$(grep "${SECTION_ID}" CROSS-REFS.md 2>/dev/null || echo "")
  if [ -n "$XREFS" ]; then
    echo "CROSS-REFERENCES:"
    echo "$XREFS"
    echo ""
  fi

  # Show CONTENT.md (paginated if >50 lines)
  echo "CONTENT:"
  CONTENT="${SECTION_DIR}/${SECTION_ID}-CONTENT.md"
  LINE_COUNT=$(wc -l < "$CONTENT")

  if [ $LINE_COUNT -gt 50 ]; then
    echo "(Content is ${LINE_COUNT} lines - showing first 50, full content available)"
    head -50 "$CONTENT"
    echo ""
    echo "[... ${LINE_COUNT} total lines ...]"
  else
    cat "$CONTENT"
  fi

  echo ""

  # Collect feedback via AskUserQuestion
  # (In actual implementation, use AskUserQuestion tool)
  # For workflow pseudocode:

  read -p "Review status for ${SECTION_NAME} (Approved / Comment / Flag / Skip): " STATUS

  case "$STATUS" in
    Approved|approved)
      echo "✓ Section approved"
      ;;
    Comment|comment)
      read -p "Comment: " COMMENT
      # Log to REVIEW.md
      echo "| ${SECTION_ID} | Comment | ${COMMENT} | - |" >> "${PHASE_DIR}/REVIEW.md"
      echo "✓ Comment logged"
      ;;
    Flag|flag)
      read -p "Issue description: " ISSUE
      read -p "Severity (High / Medium / Low): " SEVERITY
      read -p "Suggested action: " ACTION
      # Log to REVIEW.md
      echo "| ${SECTION_ID} | Flag | ${ISSUE} | ${ACTION} |" >> "${PHASE_DIR}/REVIEW.md"
      echo "⚠ Issue flagged"
      ;;
    Skip|skip)
      echo "Skipped"
      ;;
    *)
      echo "Invalid choice, skipping section"
      ;;
  esac

  echo ""
  read -p "Press Enter to continue to next section..." CONTINUE
done
```

### Step 4: Review Summary

After all sections reviewed:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Review Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sections reviewed: ${SECTION_COUNT}
Approved: ${APPROVED_COUNT}
Comments: ${COMMENT_COUNT}
Flagged: ${FLAG_COUNT}

Feedback captured in: ${PHASE_DIR}/REVIEW.md
```

### Step 5: Route to Gap Closure (Optional)

If --route-gaps flag was provided:

```bash
if [[ "$@" == *"--route-gaps"* ]]; then
  echo ""
  echo "Routing flagged issues to gap closure pipeline..."

  # Convert REVIEW.md flags to gap format for plan-phase --gaps
  /doc:plan-phase ${PHASE} --gaps --source review

  echo "Fix plans generated for flagged issues."
fi
```
```

**REVIEW.md format (from template):**

```markdown
# Phase N: [Name] - Review Feedback

**Reviewed:** [date]
**Reviewer:** [name or role]
**Type:** [Engineer handover / Client walkthrough / Internal review]

## Summary

| Status | Count |
|--------|-------|
| Approved | X |
| Comment | Y |
| Flag | Z |
| **Total Sections** | **N** |

## Feedback

| Section | Status | Finding | Suggested Action |
|---------|--------|---------|------------------|
| 03-01 | Approved | - | - |
| 03-02 | Comment | Add typical settling time for reference | - |
| 03-03 | Flag | I/O table missing DO-300-04 (brake release signal) | Add missing I/O entry |
| 03-04 | Approved | - | - |

## Flagged Issues (Detail)

### 03-03 EM-300: Missing I/O Signal
**Severity:** High
**Finding:** I/O table lists 8 signals but mechanical drawing shows 9. DO-300-04 (brake release) is missing.
**Context:** Section 3.3, I/O table
**Suggested Action:** Verify with mechanical engineer, add missing I/O entry, update signal count in SUMMARY.md
**Routed to gaps:** Yes (if --route-gaps used)
```

**Interactive presentation with AskUserQuestion:**

In the actual implementation, the workflow uses the AskUserQuestion tool for feedback collection:

```markdown
For each section:

Use AskUserQuestion:
- header: "Review Section ${SECTION_NUM}/${SECTION_COUNT}: ${SECTION_NAME}"
- question: "Review status for this section?"
- options:
  - "Approved (no issues)"
  - "Comment (minor note)"
  - "Flag (needs revision)"
  - "View full content"
  - "Skip to next"

If "Comment" or "Flag" selected, follow up with:
- header: "Provide Feedback"
- question: "Enter your feedback for ${SECTION_NAME}:"
- type: text input

If "View full content" selected:
- Display full CONTENT.md
- Return to review status question

If "Flag" selected, additional question:
- header: "Issue Severity"
- question: "How critical is this issue?"
- options: ["High (blocks approval)", "Medium (should fix)", "Low (nice to have)"]
```

**Source:** User decision in CONTEXT.md specifies interactive section-by-section flow with content + SUMMARY + cross-refs presentation.

### Pattern 5: Gap Closure Integration for Review Findings

**What:** When review-phase finds issues, they can be routed to the gap closure pipeline (plan-phase --gaps) using a --route-gaps flag, converting review feedback into fix plans automatically.

**When to use:** When engineer wants automated fix planning for review issues instead of manual resolution.

**Integration approach:**

```markdown
## plan-phase workflow: add --source flag support

Enhanced plan-phase already supports --gaps mode (from Phase 3).
Add --source flag to specify gap source:

```bash
/doc:plan-phase N --gaps                    # Default: read from VERIFICATION.md
/doc:plan-phase N --gaps --source fresh-eyes # Read from FRESH-EYES.md
/doc:plan-phase N --gaps --source review    # Read from REVIEW.md
```

### Gap Source Adaptation

```bash
case "$GAP_SOURCE" in
  verification|"")
    # Default: read VERIFICATION.md
    GAP_FILE="${PHASE_DIR}/${PHASE}-VERIFICATION.md"
    EXTRACT_PATTERN="^## Gap "
    ;;
  fresh-eyes)
    # Read FRESH-EYES.md
    GAP_FILE="${PHASE_DIR}/${PHASE}-FRESH-EYES.md"
    EXTRACT_PATTERN="^#### §"
    # Convert severity: MUST-FIX → High, SHOULD-FIX → Medium, CONSIDER → Low
    ;;
  review)
    # Read REVIEW.md
    GAP_FILE="${PHASE_DIR}/REVIEW.md"
    EXTRACT_PATTERN="^| .* | Flag |"
    # Extract only flagged items (not comments or approved)
    ;;
esac

# Parse gaps from source file
# Generate fix plans as usual
```

### Fix Plan Generation (same as Phase 3)

For each gap/finding:
1. Create targeted fix plan: {section-id}-fix-PLAN.md
2. Include gap description, evidence, target section
3. Assign wave 1 (all fixes parallel)
4. Engineer runs /doc:write-phase N to execute fixes
5. Engineer runs /doc:verify-phase N to re-check

**Default behavior:** Findings are informational only (logged in FRESH-EYES.md or REVIEW.md).

**With --actionable or --route-gaps:** Findings automatically generate fix plans and enter gap closure loop.

**User control:** Engineer always sees gap preview and can cancel before fix generation.

**Source:** User decision in CONTEXT.md specifies configurable gap closure routing with flags.

### Anti-Patterns to Avoid

- **Generating knowledge artifacts at the end:** RATIONALE.md and EDGE-CASES.md must be captured incrementally as decisions and edge cases emerge, not generated post-hoc when context is lost
- **Standalone knowledge capture commands:** Don't create `/doc:add-rationale` or `/doc:add-edge-case` commands — knowledge capture is automatic during existing workflows
- **One-size-fits-all Fresh Eyes:** The three perspectives (engineer/customer/operator) have fundamentally different checking criteria — don't collapse into generic "readability check"
- **Batch review presentation:** Don't dump all sections at once — interactive section-by-section with feedback collection maintains focus
- **Auto-routing all findings to gaps:** Fresh Eyes and review-phase findings are informational by default — only route to gap closure when explicitly requested via flags
- **Shared EDGE-CASES.md across phases:** Edge cases are per-phase (close to content that surfaced them), not project-wide like RATIONALE.md

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown table parsing/updating | Custom regex for table row insertion | Structured append with format validation | Tables have alignment, separators, escaping — hand-rolled parsing breaks on edge cases |
| Multi-perspective simulation | Single prompt with "consider different viewpoints" | Separate subagent spawn per perspective with distinct system prompt | Perspectives have conflicting priorities (customer wants simplicity, engineer wants detail) — can't optimize both in one pass |
| Interactive section navigation | Custom TUI with up/down/select | AskUserQuestion with options + sequential flow | Claude Code's AskUserQuestion handles user input validation, option selection, text entry consistently |
| Severity classification | Rule-based keyword matching | Claude's judgment with clear examples in system prompt | Severity depends on context (missing alarm response = MUST-FIX for operator, CONSIDER for customer) |
| Gap source format conversion | Custom parsers for VERIFICATION.md vs FRESH-EYES.md vs REVIEW.md | Unified gap extraction with source-specific patterns | Different formats need different parsing but same downstream fix planning — extract to common gap schema |

**Key insight:** Phase 6 is about **workflow enhancement, not new infrastructure**. The heavy lifting (subagent orchestration, file management, verification) already exists from Phases 1-5. This phase adds capture steps and templates, not complex systems.

## Common Pitfalls

### Pitfall 1: RATIONALE.md Entry Duplication

**What goes wrong:** Multiple phases add entries for the same FDS section, creating duplicates or inconsistent information.

**Why it happens:** RATIONALE.md is organized by section reference, but decisions about the same section can be made in different phases (Phase 3 discuss, Phase 4 discuss).

**How to avoid:**
- Before appending entry, check if section already has entries
- Group related decisions under the same section heading
- Use sub-headings for different decision aspects:
  ```markdown
  ## §3.2 EM-200 Bovenloopkraan

  ### Collision Detection
  [Decision entry from Phase 3]

  ### E-stop Behavior
  [Decision entry from Phase 3]

  ### SCADA Interface
  [Decision entry from Phase 4 — added later]
  ```
- Don't auto-merge — let entries accumulate chronologically under section heading

**Warning signs:** Section heading appears multiple times in RATIONALE.md. Contradictory decisions for same equipment.

### Pitfall 2: Edge Case Aggregation Race Condition

**What goes wrong:** Two writers in the same wave try to update EDGE-CASES.md simultaneously, corrupting the file.

**Why it happens:** Parallel writers append directly to shared file without coordination.

**How to avoid:**
- Writers create temporary files: `{plan-id}-edge-cases.tmp`
- Orchestrator aggregates after wave completes (all writers finished)
- Serial aggregation in orchestrator prevents race condition
- Temporary files deleted after aggregation

**Warning signs:** EDGE-CASES.md with malformed table rows. Missing edge cases that writers reported.

### Pitfall 3: Fresh Eyes Too Lenient or Too Strict

**What goes wrong:** Fresh Eyes flags trivial issues as MUST-FIX or misses genuinely confusing content.

**Why it happens:** Severity calibration is subjective without clear examples.

**How to avoid:**
- Provide concrete MUST-FIX vs SHOULD-FIX vs CONSIDER examples in fresh-eyes subagent prompt
- Calibrate by section type: stricter on safety-critical, lighter on overview
- Perspective-specific guidelines:
  - Engineer MUST-FIX: undefined technical term blocking implementation
  - Customer MUST-FIX: jargon without explanation, unclear scope commitment
  - Operator MUST-FIX: missing alarm response procedure, unclear recovery steps
- Test on reference sections with known issues, tune severity thresholds

**Warning signs:** Every finding is MUST-FIX (too strict) or everything is CONSIDER (too lenient). Engineer dismisses most findings as irrelevant.

### Pitfall 4: Review Fatigue from Too Many Sections

**What goes wrong:** Engineer starts review enthusiastically but attention drops after 10+ sections, later sections get rubber-stamped "Approved" without real review.

**Why it happens:** Sequential review of 20+ sections in one sitting is cognitively draining.

**How to avoid:**
- Offer pause points: "You've reviewed 10 of 23 sections. Continue or save progress?"
- Save partial review state: track which sections reviewed in REVIEW.md
- Allow resume: `/doc:review-phase N --resume` starts from last reviewed section
- Show progress indicator: "Section 12 of 23" helps pace effort
- Suggest grouping for large phases: "This phase has 23 sections. Review in multiple sessions? (Y/n)"

**Warning signs:** REVIEW.md shows "Approved" for last 15 sections with no comments. Review completed in implausibly short time.

### Pitfall 5: Gap Closure Routing Without Preview

**What goes wrong:** Review-phase with --route-gaps immediately generates fix plans for all flagged issues without showing engineer what will be fixed.

**Why it happens:** Automated routing seems efficient but skips engineer confirmation step.

**How to avoid:**
- Always preview flagged issues before routing to gaps:
  ```
  Review complete. 3 issues flagged.

  Flagged issues:
  1. [High] 03-03: Missing I/O signal DO-300-04
  2. [Medium] 03-05: Unclear alarm response for AL-500-02
  3. [Low] 03-06: State diagram could be clearer

  Generate fix plans for these issues? (Y/n)
  ```
- Let engineer deselect: "Which issues should generate fix plans? (1,2,3 or 'all')"
- Separate informational findings (logged only) from actionable findings (routed to gaps)

**Warning signs:** Fix plans generated for trivial issues. Engineer cancels gap closure loop after seeing plans.

### Pitfall 6: Fresh Eyes Hallucinates Missing Content

**What goes wrong:** Fresh Eyes flags "missing" content that actually exists but wasn't noticed during review.

**Why it happens:** Fresh Eyes subagent has limited context window, might not see all content if phase is large.

**How to avoid:**
- Fresh Eyes loads all CONTENT.md + all SUMMARY.md for phase (token-efficient via SUMMARY)
- For findings, include evidence quote: "What's missing: [description]. Checked: [sections reviewed]"
- Engineer validates findings before routing to gaps
- Fresh Eyes uses SUMMARY.md to locate content before flagging as missing
- Test with reference phase where everything is present, check for false positives

**Warning signs:** Fresh Eyes flags missing content that exists. Engineer rejects most findings. Findings reference sections not included in Fresh Eyes context.

### Pitfall 7: RATIONALE.md Grows Unbounded

**What goes wrong:** RATIONALE.md accumulates hundreds of entries, becoming too large to navigate.

**Why it happens:** "Completeness over curation" leads to documenting every minor decision.

**How to avoid:**
- Focus on decisions that **change implementation** or **resolve ambiguity**
- Skip documenting: template defaults, standard practices, obvious choices
- Guide engineer: "Is this decision non-obvious or might be questioned later? (Y/n)"
- If concern about size, organize with collapsible sections:
  ```markdown
  ## §3 Equipment Modules

  <details>
  <summary>§3.2 EM-200 Bovenloopkraan (3 decisions)</summary>

  ### Collision Detection
  [Decision entry]

  ### E-stop Behavior
  [Decision entry]

  </details>
  ```
- Typical project: 30-60 RATIONALE entries (not 300)

**Warning signs:** RATIONALE.md exceeds 500 lines. Entries document template defaults. Engineer says "this is too much detail."

### Pitfall 8: Edge Cases Without Design Reason

**What goes wrong:** EDGE-CASES.md lists situation + behavior + recovery but omits WHY the system behaves this way.

**Why it happens:** Writer focuses on documenting the edge case but not the reasoning.

**How to avoid:**
- Template includes "Design Reason" column — required field
- Writer guidance: "Why does the system behave this way? (safety / equipment protection / client preference / technical constraint)"
- Example:
  - ❌ Bad: "E-stop → controlled stop → operator reset"
  - ✓ Good: "E-stop → controlled stop (500ms decel) → operator reset | Reason: Immediate brake = mechanical stress; controlled stop balances safety + equipment protection"
- Validation: edge cases without design reason are incomplete

**Warning signs:** "Design Reason" column is empty or says "n/a". Engineer can't explain edge case behavior from documentation alone.

### Pitfall 9: Review-Phase Skips Cross-References

**What goes wrong:** Section is reviewed in isolation without checking if cross-references are valid.

**Why it happens:** Review presentation shows CONTENT.md but not CROSS-REFS.md context.

**How to avoid:**
- Always show cross-references during section presentation:
  ```
  Section 03-03: EM-300 Vulunit

  CROSS-REFERENCES:
  - Depends on: §3.1 EM-100 (waterbad level interlock)
  - Referenced by: §6.3 (general interlocks)
  ```
- Flag missing cross-references: "This section mentions EM-100 but no cross-ref logged"
- Engineer can navigate to referenced sections during review

**Warning signs:** Flagged issues mention "this references X but X doesn't exist" — should have been caught by showing cross-refs.

## Code Examples

Verified patterns for Phase 6 implementation:

### Example 1: discuss-phase Enhancement for RATIONALE.md

```markdown
## Enhanced discuss-phase workflow: Step 7.5 (new step after decision capture)

After capturing decisions for a discussion area in CONTEXT.md, update RATIONALE.md:

### 7.5.1 Check RATIONALE.md Exists

```bash
RATIONALE_FILE=".planning/RATIONALE.md"

if [ ! -f "$RATIONALE_FILE" ]; then
  echo "📝 Creating RATIONALE.md from template..."
  cp ~/.claude/gsd-docs-industrial/templates/rationale.md "$RATIONALE_FILE"
fi
```

### 7.5.2 Extract Decision Context

For the discussion area just completed:
- Decision statement (from CONTEXT.md)
- Reasoning (engineer's explanation)
- Alternatives considered (what was ruled out)
- FDS section reference (where this applies)

Example extraction:
```
Discussion area: EM-200 E-stop behavior
Decision: Controlled stop with position retention
Reasoning: E-stop must prevent load drop (safety), but immediate motor cut would cause brake engagement at speed (mechanical stress). Controlled deceleration over 500ms balances safety and equipment protection.
Alternatives:
  - Immediate stop (ruled out: brake wear)
  - Coast to stop (ruled out: safety)
Section reference: §3.2 EM-200 Bovenloopkraan
```

### 7.5.3 Check for Existing Section Entry

```bash
SECTION_REF="§3.2"  # Extracted from discussion context
SECTION_EXISTS=$(grep -c "^## ${SECTION_REF}" "$RATIONALE_FILE" || echo 0)

if [ "$SECTION_EXISTS" -gt 0 ]; then
  # Section already has entries - append under section heading
  INSERT_MODE="append-to-section"
else
  # New section - create heading + entry
  INSERT_MODE="new-section"
fi
```

### 7.5.4 Append Entry to RATIONALE.md

```bash
# Format entry
ENTRY=$(cat <<EOF

### E-stop Behavior
**Decision:** Controlled stop with position retention
**Reasoning:** E-stop must prevent load drop (safety), but immediate motor cut would cause brake engagement at speed (mechanical stress). Controlled deceleration over 500ms balances safety and equipment protection.
**Alternatives:** Immediate stop (ruled out: brake wear), coast to stop (ruled out: safety), drop to safe zone (ruled out: no designated safe zone exists)
**Date:** $(date +%Y-%m-%d)
**Phase:** ${PHASE}

EOF
)

if [ "$INSERT_MODE" == "new-section" ]; then
  # Add section heading + entry
  cat <<EOF >> "$RATIONALE_FILE"

## ${SECTION_REF} EM-200 Bovenloopkraan

${ENTRY}
EOF
else
  # Append to existing section
  # Find section heading line number, append after last entry in section
  SECTION_LINE=$(grep -n "^## ${SECTION_REF}" "$RATIONALE_FILE" | cut -d: -f1)
  NEXT_SECTION_LINE=$(tail -n +$((SECTION_LINE+1)) "$RATIONALE_FILE" | grep -n "^## " | head -1 | cut -d: -f1)

  if [ -z "$NEXT_SECTION_LINE" ]; then
    # No next section - append at end of file
    echo "$ENTRY" >> "$RATIONALE_FILE"
  else
    # Insert before next section
    INSERT_AT=$((SECTION_LINE + NEXT_SECTION_LINE))
    sed -i "${INSERT_AT}i\\${ENTRY}" "$RATIONALE_FILE"
  fi
fi
```

### 7.5.5 Confirm to Engineer

```
📝 RATIONALE.md updated:
   §3.2 EM-200: E-stop Behavior
   └─ Decision, reasoning, and alternatives logged
```

Continue to next discussion area.
```

**Source:** Adapted from discuss-phase workflow pattern with RATIONALE.md append logic.

### Example 2: doc-writer Enhancement for EDGE-CASES.md

```yaml
---
name: doc-writer
description: Writes FDS section content following a PLAN.md. Use for all /doc:write-phase section writing tasks.
tools: Read, Write, Bash
disallowedTools: Glob, Grep
model: sonnet
---

# Role: FDS Technical Documentation Writer

[... existing context and steps 1-6 ...]

## Step 7: Document Edge Cases (NEW)

During writing, when you identify edge cases or failure modes:

### 7.1 Recognize Edge Cases

Edge cases include:
- Failure modes (sensor failure, power loss, communication timeout)
- Unusual sequences (double start command, stop during transition)
- Boundary conditions (overweight, overtemperature, timeout exceeded)
- Recovery procedures (manual intervention, system reset requirements)

### 7.2 Document in CONTENT.md

Include edge case in the appropriate section of CONTENT.md:
```markdown
#### Failure Modes

**E-stop during crane movement:**
System behavior: Controlled deceleration over 500ms, position retained, brake engages
Recovery: Operator must clear fault, manually jog crane to safe position, reset system via HMI
```

### 7.3 Extract to Temporary Edge Case File

Create temporary file for orchestrator aggregation:

```bash
# Determine severity
# CRITICAL: safety or equipment damage risk
# WARNING: operational impact, manual intervention required
# INFO: notable behavior, no intervention needed

SEVERITY="CRITICAL"  # For E-stop example
SITUATION="E-stop during crane movement"
BEHAVIOR="Controlled deceleration (500ms), position retained, brake engages"
RECOVERY="Operator: clear fault, manual jog to safe position, reset system"
REASON="Immediate brake = mechanical stress; controlled stop balances safety + equipment protection"
SECTION="${PLAN_ID}"

# Append to temporary file
EDGE_CASE_TMP="${PHASE_DIR}/${PLAN_ID}-edge-cases.tmp"

echo "| ${SEVERITY} | ${SITUATION} | ${BEHAVIOR} | ${RECOVERY} | ${REASON} | ${SECTION} |" >> "$EDGE_CASE_TMP"
```

### 7.4 Continue Writing

Edge case extraction is non-blocking. Continue writing remaining sections.

The write-phase orchestrator aggregates all edge cases after the wave completes.

## Step 8: Self-verify (existing, unchanged)

[... existing self-verification steps ...]

## Step 9: Return Completion Message

Enhanced completion message includes edge case count:

```
✓ ${PLAN_ID}-CONTENT.md (${SIZE})
✓ ${PLAN_ID}-SUMMARY.md (${WORD_COUNT} words)
✓ Cross-refs: ${XREF_COUNT} logged
✓ Edge cases: ${EDGE_CASE_COUNT} captured (${CRITICAL} CRITICAL, ${WARNING} WARNING, ${INFO} INFO)
✓ [VERIFY] markers: ${VERIFY_COUNT} (locations listed)
```
```

**Source:** Adapted from doc-writer subagent pattern with edge case capture step.

### Example 3: verify-phase Enhancement for Fresh Eyes Offer

```markdown
## Enhanced verify-phase workflow: Step 8 (new step after PASS result)

After VERIFICATION.md status is PASS:

### 8.1 Display PASS Result

```
✓ Phase ${PHASE} verification: PASS

All truths verified at 5 levels (exists, substantive, complete, consistent, standards-compliant).
```

### 8.2 Offer Fresh Eyes Review

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Optional: Fresh Eyes Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Simulate a new reader reviewing the documentation.

Checks:
- Comprehension gaps (undefined terms, assumed knowledge)
- Completeness gaps (missing context, logical jumps)

Perspectives:
  1. Engineer (technical clarity for new team member)
  2. Customer (jargon, commitments, scope for client review)
  3. Operator (procedures, alarms, recovery for daily use)
  4. All perspectives (comprehensive review)
  5. Skip Fresh Eyes

Selection (1-5):
```

Use AskUserQuestion:
```yaml
header: "Optional: Fresh Eyes Review"
question: "Simulate a new reader. Which perspective?"
options:
  - "Engineer (technical clarity)"
  - "Customer (jargon, commitments)"
  - "Operator (procedures, recovery)"
  - "All perspectives"
  - "Skip Fresh Eyes"
```

### 8.3 Spawn fresh-eyes Subagent

Based on selection:

```bash
case "$SELECTION" in
  "Engineer (technical clarity)")
    PERSPECTIVE="engineer"
    ;;
  "Customer (jargon, commitments)")
    PERSPECTIVE="customer"
    ;;
  "Operator (procedures, recovery)")
    PERSPECTIVE="operator"
    ;;
  "All perspectives")
    PERSPECTIVE="all"
    ;;
  "Skip Fresh Eyes")
    echo "Fresh Eyes review skipped."
    exit 0
    ;;
esac

# Build context file list
CONTEXT_FILES=".planning/PROJECT.md"
CONTEXT_FILES+=",planning/RATIONALE.md"
CONTEXT_FILES+=",.planning/phases/${PHASE_DIR}/${PHASE}-CONTEXT.md"

# Add all CONTENT.md files
for CONTENT in .planning/phases/${PHASE_DIR}/*-CONTENT.md; do
  CONTEXT_FILES+=",${CONTENT}"
done

# Add all SUMMARY.md files
for SUMMARY in .planning/phases/${PHASE_DIR}/*-SUMMARY.md; do
  CONTEXT_FILES+=",${SUMMARY}"
done

# Spawn subagent
echo "Launching Fresh Eyes review (${PERSPECTIVE} perspective)..."
echo ""

claude --agent fresh-eyes \
  --context "${CONTEXT_FILES}" \
  --message "Perform Fresh Eyes review from ${PERSPECTIVE} perspective. Identify comprehension gaps (undefined terms, assumed knowledge) and completeness gaps (missing context, logical jumps). Classify severity: MUST-FIX (genuinely confusing), SHOULD-FIX (improvement), CONSIDER (nice-to-have). Produce ${PHASE}-FRESH-EYES.md with findings organized by perspective."

echo ""
echo "✓ Fresh Eyes review complete"
echo "  See: ${PHASE_DIR}/${PHASE}-FRESH-EYES.md"
```

### 8.4 Check for --actionable Flag

```bash
if [[ "$@" == *"--actionable"* ]]; then
  echo ""
  echo "Routing Fresh Eyes findings to gap closure pipeline..."

  # Count findings by severity
  MUST_FIX=$(grep -c "MUST-FIX" "${PHASE_DIR}/${PHASE}-FRESH-EYES.md" || echo 0)
  SHOULD_FIX=$(grep -c "SHOULD-FIX" "${PHASE_DIR}/${PHASE}-FRESH-EYES.md" || echo 0)

  if [ $MUST_FIX -eq 0 ] && [ $SHOULD_FIX -eq 0 ]; then
    echo "No actionable findings (MUST-FIX or SHOULD-FIX). Gap closure not needed."
  else
    echo "Found ${MUST_FIX} MUST-FIX and ${SHOULD_FIX} SHOULD-FIX findings."
    echo "Generating fix plans..."

    /doc:plan-phase ${PHASE} --gaps --source fresh-eyes

    echo "Fix plans generated. Run /doc:write-phase ${PHASE} to execute fixes."
  fi
fi
```
```

**Source:** Adapted from verify-phase workflow pattern with Fresh Eyes integration.

### Example 4: review-phase Command File

```markdown
---
name: doc:review-phase
description: Present completed phase content section-by-section for engineer or client review with feedback capture
argument-hint: "<phase> [--route-gaps]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>

Present phase N documentation section-by-section for structured engineer or client review.

**Workflow:**
1. Load all sections in phase (CONTENT.md + SUMMARY.md)
2. For each section: show SUMMARY + cross-refs + CONTENT (paginated if long)
3. Collect feedback via interactive prompts: Approved / Comment / Flag
4. Capture all feedback in REVIEW.md
5. Optionally route flagged issues to gap closure pipeline

**Output:** phase-N/REVIEW.md with structured feedback per section

**Use case:** Engineer handover (present to colleague taking over project), client walkthrough (section-by-section FDS review), internal review (structured quality check)

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/review-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

Phase number: $ARGUMENTS (required)
Flags: --route-gaps (optional, routes flagged issues to gap closure)

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in review-phase.md exactly. It contains all steps: phase validation, section loading, interactive presentation with AskUserQuestion, feedback capture in REVIEW.md, and optional gap closure routing.

</process>

<success_criteria>

- [ ] Phase validated and has completed content (VERIFICATION.md PASS)
- [ ] All sections loaded with CONTENT.md + SUMMARY.md + cross-refs
- [ ] Each section presented sequentially with interactive feedback collection
- [ ] Feedback captured in REVIEW.md with section reference, status, finding, suggested action
- [ ] Review summary displayed: N sections reviewed, X approved, Y comments, Z flagged
- [ ] If --route-gaps: flagged issues converted to gap format and routed to plan-phase --gaps
- [ ] Engineer knows next steps (manual resolution or automatic gap closure)

</success_criteria>
```

**Source:** Adapted from existing command pattern (new-fds.md, discuss-phase.md) for review-phase domain.

### Example 5: FRESH-EYES.md Template

```markdown
# Phase {N}: {Name} - Fresh Eyes Review

**Reviewed:** {date}
**Perspective:** {Engineer / Customer / Operator / All}
**Reviewer:** Fresh Eyes (simulated)

## Summary

| Category | MUST-FIX | SHOULD-FIX | CONSIDER | Total |
|----------|----------|------------|----------|-------|
| Comprehension Gaps | 0 | 0 | 0 | 0 |
| Completeness Gaps | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

## Engineer Perspective

*(Present if Engineer or All perspective selected)*

### Comprehension Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's unclear:** {Describe gap from engineer perspective}
**Context:** {Quote or reference from CONTENT.md}
**Why it matters:** {Impact on new engineer joining project}

### Completeness Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's missing:** {Describe what should be added}
**Why it matters:** {Impact on implementation or understanding}

---

## Customer Perspective

*(Present if Customer or All perspective selected)*

### Comprehension Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's unclear:** {Describe gap from customer perspective — jargon, unexplained terms}
**Context:** {Quote from CONTENT.md}
**Why it matters:** {Customer will ask "what does this mean?"}

### Completeness Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's missing:** {Scope boundaries, commitments not stated, cost implications unclear}
**Why it matters:** {Customer needs this to approve/understand deliverable}

---

## Operator Perspective

*(Present if Operator or All perspective selected)*

### Comprehension Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's unclear:** {Procedure steps not clear, alarm response missing, recovery steps ambiguous}
**Context:** {Quote from CONTENT.md}
**Why it matters:** {Operator can't perform task without this information}

### Completeness Gaps

#### §{X.Y} {Section}: {SEVERITY} - {Brief Description}
**What's missing:** {Manual override procedure, state transition diagram, alarm response table}
**Why it matters:** {Operator needs this for daily operation or fault recovery}

---

## Routing to Gap Closure

- **Actionable flag:** {Yes / No}
- **Findings routed:** {N MUST-FIX and M SHOULD-FIX findings sent to plan-phase --gaps}
- **Fix plans generated:** {List of generated fix plan IDs}

---

*Generated by: Fresh Eyes subagent*
*Template version: 1.0*
```

**Source:** Created based on user decision in CONTEXT.md for three perspectives with severity levels.

## State of the Art

| Old Approach | GSD-Docs Approach | When Changed | Impact |
|--------------|-------------------|--------------|--------|
| Knowledge transfer at project end | Incremental capture during workflow (RATIONALE during discuss, EDGE-CASES during write) | Phase 6 implementation | Preserves context when decisions are fresh, prevents knowledge loss |
| Post-hoc decision documentation | Real-time RATIONALE.md updates after each discussion area | discuss-phase enhancement | Engineer documents "why" immediately, not weeks later when context is lost |
| Generic document review | Multi-perspective Fresh Eyes (engineer/customer/operator lenses) | Fresh Eyes implementation | Simulates different reader types with distinct checking criteria |
| Batch document handover | Section-by-section interactive review with structured feedback | review-phase workflow | Maintains focus, captures specific feedback per section |
| Manual review issue tracking | Optional gap closure routing for review findings | plan-phase --source integration | Review findings can automatically generate fix plans |

## Open Questions

1. **RATIONALE.md section organization heuristics**
   - What we know: Entries organized by FDS section reference, multiple entries per section allowed
   - What's unclear: When a discussion spans multiple sections (e.g., system-wide decision), should it duplicate entries or use cross-references?
   - Recommendation: Single entry under most relevant section, add "Also applies to: §X.Y, §Z.W" reference, avoid duplication. Test with multi-section decisions in Phase 6 execution.

2. **Fresh Eyes token budget for large phases**
   - What we know: Fresh Eyes loads all CONTENT.md + all SUMMARY.md for comprehensive review
   - What's unclear: What if phase has 20+ sections and exceeds context window?
   - Recommendation: Use SUMMARY.md as primary input (token-efficient), load full CONTENT.md only for sections flagged during SUMMARY review. Estimate: SUMMARY.md ~150 words × 20 sections = 3k words (fits comfortably). Monitor token usage in Phase 6 verification.

3. **Edge case severity classification consistency**
   - What we know: Three levels (CRITICAL/WARNING/INFO) with examples, but writers judge severity independently
   - What's unclear: Will different writers classify the same edge case consistently?
   - Recommendation: Add severity classification guide to doc-writer system prompt with decision tree: "Does it risk safety or equipment damage? → CRITICAL. Does it require manual intervention? → WARNING. Otherwise → INFO." Validate consistency in Phase 6 verification with multi-writer phases.

4. **Review-phase partial session resume**
   - What we know: Large phases may require review in multiple sessions to avoid fatigue
   - What's unclear: How to persist partial review state (which sections reviewed, which pending)?
   - Recommendation: REVIEW.md includes "Review Progress" section: "Sections reviewed: 1-10 of 23. Next: §3.11." review-phase --resume reads this and skips already-reviewed sections. Implement in Phase 6 if multi-session review is needed.

## Sources

### Primary (HIGH confidence)

- Phase 2 RESEARCH.md - Established command + workflow separation pattern, discuss-phase integration points
- Phase 3 RESEARCH.md - Subagent architecture, context isolation, gap closure loop patterns
- discuss-phase.md (C:/Users/Aotte/.claude/commands/doc/discuss-phase.md) - Existing command structure for enhancement
- discuss-phase workflow (gsd-docs-industrial/workflows/discuss-phase.md) - Existing workflow steps for RATIONALE insertion point
- write-phase workflow (gsd-docs-industrial/workflows/write-phase.md) - Existing wave execution for edge case aggregation
- verify-phase workflow (gsd-docs-industrial/workflows/verify-phase.md) - Existing PASS handling for Fresh Eyes trigger
- doc-writer.md (gsd-docs-industrial/agents/doc-writer.md) - Existing subagent for edge case capture enhancement
- SPECIFICATION.md section 9 (lines 1555-1654) - Knowledge transfer timing and RATIONALE/EDGE-CASES format specifications
- Phase 6 CONTEXT.md - User decisions on RATIONALE format, edge case severity, Fresh Eyes perspectives, review workflow
- REQUIREMENTS.md (KNOW-01, KNOW-02, KNOW-03, REVW-01, REVW-02, REVW-03) - Phase 6 requirements specification

### Secondary (MEDIUM confidence)

- existing templates/cross-refs.md, templates/verification.md - Format patterns for new templates (RATIONALE, EDGE-CASES, FRESH-EYES, REVIEW)
- complete-fds.md workflow - Cross-reference resolution patterns applicable to edge case cross-phase references
- AskUserQuestion usage in discuss-phase - Interactive prompt patterns for review-phase section feedback collection

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Enhancing existing workflows (discuss, write, verify) with well-defined integration points; one new command following established pattern
- Architecture patterns: HIGH - Based on proven Phase 1-5 patterns (subagent orchestration, context isolation, template structure)
- Incremental capture: HIGH - User decisions clearly specify trigger points (RATIONALE during discuss, EDGE-CASES during write)
- Fresh Eyes implementation: MEDIUM-HIGH - Multi-perspective simulation is novel but built on established subagent pattern with clear examples
- Review workflow: HIGH - Interactive section presentation follows AskUserQuestion patterns from discuss-phase
- Pitfalls: MEDIUM-HIGH - Derived from RATIONALE.md organization challenges, edge case aggregation race conditions, Fresh Eyes calibration needs

**Research date:** 2026-02-14
**Valid until:** 2026-03-14 (30 days - stable domain, built on established Phase 1-5 infrastructure)

**Critical verification needs:**
- RATIONALE.md organization with multi-section decisions (open question 1)
- Fresh Eyes token budget for large phases (open question 2)
- Edge case severity consistency across writers (open question 3)
- Review-phase partial session resume (open question 4)
