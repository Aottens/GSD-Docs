<workflow>

# Verify Phase Workflow

Comprehensive workflow for goal-backward verification of FDS phase content using a 5-level cascade with gap closure loop management.

---

## Step 1: Parse Arguments and Validate Phase

**Parse phase number from $ARGUMENTS:**
```
Example: /doc:verify-phase 3 → phase = "03"
```

**Read ROADMAP.md:**
```bash
Read .planning/ROADMAP.md
```

**Extract phase information:**
- Phase number (NN format, zero-padded)
- Phase name (kebab-case slug from heading)
- Phase goal statement (the "what this phase delivers" text)
- Success criteria (list of observable outcomes)
- Requirements list (if present)

**Read PROJECT.md:**
```bash
Read .planning/PROJECT.md
```

Extract:
- Project type (A/B/C/D)
- Standards settings (PackML enabled, ISA-88 enabled)
- Language (Dutch/English)
- Project name

**Verify phase has written content:**
```bash
Check for *-CONTENT.md files in .planning/phases/{NN}-{name}/
```

If no CONTENT.md files found:
- Display error box:
  ```
  ╔══════════════════════════════════════════════════════════════╗
  ║  ERROR                                                       ║
  ╚══════════════════════════════════════════════════════════════╝

  Phase {N} has no written content to verify.

  **To fix:** Run /doc:write-phase {N} first
  ```
- STOP execution

**Display banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > VERIFYING PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 1.5: Partial Write Pre-flight Check

Before proceeding to verification, check for partial writes that would invalidate verification results.

**For each plan in the phase:**

Apply the same 4-heuristic cascade used in write-phase Step 4c:

1. **Missing SUMMARY.md** (confidence: HIGH)
   - Check: CONTENT.md exists but SUMMARY.md does not
   - Reason: Writer crashed before completing

2. **Content too short** (confidence: HIGH)
   - Check: CONTENT.md exists and file size < 200 bytes
   - Reason: Content is a stub or crash artifact

3. **[TO BE COMPLETED] marker** (confidence: HIGH)
   - Check: CONTENT.md contains literal string `[TO BE COMPLETED]`
   - Reason: Writer explicitly signaled incompleteness

4. **Abrupt ending** (confidence: MEDIUM)
   - Check: Last non-empty line does not end with `.`, `!`, `?`, `|`, or `-->`
   - AND: Not a markdown heading (starts with `#`)
   - AND: Not a list marker (starts with `-`, `*`, or digit+`.`)
   - Reason: Content may have been truncated mid-sentence

**If HIGH-confidence partials detected:**

Display error box and STOP execution:

```
╔══════════════════════════════════════════════════════════════╗
║  PARTIAL WRITES DETECTED                                     ║
╚══════════════════════════════════════════════════════════════╝

{count} partial write(s) found in phase {N}:

- {plan-id}: {reason} (HIGH confidence)
- {plan-id}: {reason} (HIGH confidence)

Verification cannot proceed with incomplete content.

**To fix:**
- Run /doc:resume to complete interrupted writing
- Or run /doc:write-phase {N} to retry all incomplete plans
```

STOP execution — do not proceed to Step 2.

**If only MEDIUM-confidence partials (abrupt ending):**

Display WARNING but proceed with verification:

```
WARNING: {count} plan(s) have potential abrupt endings (MEDIUM confidence)

- {plan-id}: Last line may be truncated
- {plan-id}: Last line may be truncated

Proceeding with verification. Manual review recommended.
```

Add note to VERIFICATION.md header when generated: `Warning: {count} plans have potential abrupt endings (medium confidence). Manual review recommended.`

**If no partials detected:**

Proceed silently to Step 2.

---

## Step 2: Determine Verification Cycle

**Check for existing VERIFICATION.md:**
```bash
Check .planning/phases/{NN}-{name}/VERIFICATION.md
```

**If VERIFICATION.md exists:**
- Read the file
- Parse header for cycle count: `Cycle: {N} of 2`
- Parse status: `Status: PASS` or `Status: GAPS_FOUND` or `Status: GAPS_FOUND (ESCALATED)`

**If status is GAPS_FOUND:**
- Extract current cycle number
- Increment: this is cycle {previous + 1}
- Check if new cycle > 2:
  - If yes: jump to Step 7 (Max Iterations Escalation)
  - If no: proceed with cycle {previous + 1}
- Display:
  ```
  DOC > Verification Cycle {N} of 2
  ```

**If status is PASS or GAPS_FOUND (ESCALATED):**
- This is a re-run after manual fixes (cycle reset to 1)
- Display:
  ```
  DOC > Re-verification after manual intervention
  ```

**If no VERIFICATION.md or status is PASS:**
- This is cycle 1 (initial verification)
- Display:
  ```
  DOC > Initial Verification
  ```

**Set cycle variable:**
```
current_cycle = {N}
max_cycles = 2
```

---

## Step 3: Derive Must-Have Truths (Goal-Backward)

**Goal-backward methodology:** Verify that GOALS are achieved, not just that tasks are completed.

**Read the phase goal statement from ROADMAP.md.**

Example phase goal:
```
Phase 3: Equipment Modules
Document all equipment modules with complete state machines,
I/O specifications, and interlock definitions
```

**Ask: "What must be TRUE for this goal to be achieved?"**

Derive 3-7 observable truths stated from the USER's perspective (what the engineer sees when reading the documentation).

**Truth derivation rules:**
1. **Observable** - Can be checked by reading content
2. **Specific** - Not vague (use counts, explicit requirements)
3. **User-perspective** - What the engineer sees, not what files exist

**Example truths for equipment modules phase:**
```
1. All {N} equipment modules identified in CONTEXT.md are fully documented
2. All equipment modules have complete I/O tables with tag, description, type, signal range, engineering unit, PLC address, fail-safe state, alarm limits, and scaling columns
3. All equipment modules have state machine descriptions with Mermaid diagrams and transition tables including entry/exit conditions
4. All equipment modules have parameter tables with name, description, data type, range, default, and access level columns
5. All interlocks are documented with condition, action, priority, and reset condition
6. Cross-references between equipment modules are consistent and resolvable
7. All terminology follows PackML/ISA-88 standards (if enabled)
```

**Truth count guidance by project type:**
- Type A (Greenfield + Standards): 6-7 truths (more rigor)
- Type B (Greenfield Flex): 4-6 truths
- Type C (Modification Large): 4-5 truths (focus on delta)
- Type D (Modification Small): 3-4 truths (minimal scope)

**Display derived truths to engineer:**
```
Must-Have Truths for Phase {N}:

1. {Truth 1}
2. {Truth 2}
3. {Truth 3}
...

These truths will be verified at 5 levels:
  • Level 1: Exists (content is present)
  • Level 2: Substantive (content is not placeholder)
  • Level 3: Complete (all required elements present)
  • Level 4: Consistent (aligns with CONTEXT.md decisions)
  • Level 5: Standards-compliant (follows PackML/ISA-88 if enabled)
```

---

## Step 4: Spawn Verifier Subagent

**Prepare context file list:**
```
Context files to load:
- .planning/ROADMAP.md (phase goals)
- .planning/PROJECT.md (project config, standards settings, language)
- .planning/phases/{NN}-{name}/{NN}-CONTEXT.md (phase decisions)
- .planning/phases/{NN}-{name}/*-CONTENT.md (all content files)
- .planning/phases/{NN}-{name}/*-SUMMARY.md (all summary files)
- .planning/phases/{NN}-{name}/{NN}-CROSS-REFS.md (if exists)
```

**Add standards files if enabled:**
```
If PROJECT.md has standards.packml.enabled = true:
  - ~/.claude/gsd-docs-industrial/references/standards/packml/states.md
  - ~/.claude/gsd-docs-industrial/references/standards/packml/modes.md

If PROJECT.md has standards.isa88.enabled = true:
  - ~/.claude/gsd-docs-industrial/references/standards/isa-88/hierarchy.md
  - ~/.claude/gsd-docs-industrial/references/standards/isa-88/terminology.md
```

**Prepare verification scope:**

If this is cycle 2+ (re-verification):
- Check previous VERIFICATION.md for which sections had gaps
- Read previous fix plans (NN-MM-PLAN.md files from gap closure)
- Determine if cross-references were touched:
  - If PLAN.md mentions "cross-reference" or "reference to": FULL PHASE re-verification
  - If PLAN.md is isolated content fixes: RE-VERIFY ONLY FIXED SECTIONS

**Document scope decision:**
```
Re-verification scope: {full phase | sections NN-MM, NN-MM}
(Reason: {cross-references modified | isolated content fixes})
```

**Spawn doc-verifier subagent using Task tool:**

```markdown
Verify phase {N} content against these must-have truths:

1. {Truth 1}
2. {Truth 2}
3. {Truth 3}
...

For each truth, run the 5-level verification cascade:
  • Level 1: Exists (content is present)
  • Level 2: Substantive (content is not placeholder)
  • Level 3: Complete (all required elements present)
  • Level 4: Consistent (aligns with CONTEXT.md decisions)
  • Level 5: Standards-compliant (follows standards if enabled)

STOP at first failure level. Higher levels marked as "Not Checked" if lower level fails.

**Verification scope:** {full phase | sections NN-MM, NN-MM}

**Cross-reference handling:**
- References to written sections: verify consistency
- References to unwritten sections: warn-only (your discretion on whether to warn or defer as gap)
- Document reasoning in VERIFICATION.md

**Gap descriptions:**
- Describe what is missing or wrong (factual, descriptive language)
- Do NOT suggest fixes (no imperatives like "add X" or "change to Y")
- Use format: "uses X instead of Y" NOT "change X to Y"

**Output:**
Produce VERIFICATION.md in .planning/phases/{NN}-{name}/ following the template at ~/.claude/gsd-docs-industrial/templates/verification.md

Include:
- Header with cycle count ({current_cycle} of 2)
- Summary pass/gap table at top for quick scan
- Detailed findings per truth with 5-level cascade evidence
- Status: PASS or GAPS_FOUND

@~/.claude/gsd-docs-industrial/agents/doc-verifier.md
@~/.claude/gsd-docs-industrial/templates/verification.md
```

**Wait for subagent completion.**

Display:
```
◆ Spawning verifier...
```

When complete:
```
✓ Verifier complete: VERIFICATION.md written
```

---

## Step 5: Process Verification Results

**Read VERIFICATION.md:**
```bash
Read .planning/phases/{NN}-{name}/VERIFICATION.md
```

**Parse key fields:**
- Status: `PASS` or `GAPS_FOUND`
- Cycle count: `{N} of 2`
- Total truths count
- Passed truths count
- Gap truths count (total - passed)

**Extract gap details (if GAPS_FOUND):**
```
For each truth with status GAP:
  - Truth number and description
  - Which level failed (Exists, Substantive, Complete, Consistent, Standards)
  - Gap description
  - Evidence (what was found vs what was expected)
```

---

## Step 6A: Handle PASS Result

**If status is PASS:**

Display banner:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PHASE {N} VERIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Show pass summary:**
```
═══════════════════════════════════════════════════════════════
RESULT: PASS
═══════════════════════════════════════════════════════════════

All {total_truths} must-have truths verified at 5 levels:

✓ {Truth 1}
✓ {Truth 2}
✓ {Truth 3}
...

Phase {N} content is complete and ready.
```

**Update STATE.md:**
```bash
# Update phase status to VERIFIED
# Command: Update .planning/STATE.md
# Set phase {N} status to "✓ Verified"
```

**Show Next Up:**
```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase {N+1}: {Next Phase Name}** -- {next phase goal summary}

`/doc:discuss-phase {N+1}`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:review-phase {N}` -- optional client/engineer review
- `/doc:status` -- view overall progress

───────────────────────────────────────────────────────────────
```

**STOP - verification complete.**

---

## Step 6B: Handle GAPS_FOUND Result

**If status is GAPS_FOUND:**

Display banner:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > GAPS FOUND IN PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Show summary table from VERIFICATION.md:**
```
═══════════════════════════════════════════════════════════════
RESULT: GAPS_FOUND
═══════════════════════════════════════════════════════════════

Cycle: {current_cycle} of 2

| Truth | Status | Failed Level |
|-------|--------|--------------|
| 1     | ✓ PASS | -            |
| 2     | ✗ GAP  | Complete     |
| 3     | ✓ PASS | -            |
| 4     | ✗ GAP  | Consistent   |
...

{passed_count}/{total_truths} truths verified
```

**Display each gap with evidence:**
```
Gap 1: {Truth description}
  Failed at: Level {N} ({level name})
  Description: {gap description from VERIFICATION.md}
  Evidence: {what was found vs expected}

Gap 2: {Truth description}
  Failed at: Level {N} ({level name})
  Description: {gap description}
  Evidence: {evidence}

...
```

**Update STATE.md:**
```bash
# Update .planning/STATE.md:
# - Set phase {N} status to "GAPS_FOUND"
# - Set gap_closure_cycle to {current_cycle}
```

**Proceed to Step 6C (Gap Routing).**

---

## Step 6C: Gap Routing (GAPS_FOUND Flow)

**Display gap preview (per user decision):**
```
───────────────────────────────────────────────────────────────

## Gaps to Address

{gap_count} gaps identified:

1. {Gap 1 summary - truth description + failed level}
2. {Gap 2 summary - truth description + failed level}
3. {Gap 3 summary - truth description + failed level}
...

These gaps will be addressed by /doc:plan-phase {N} --gaps

───────────────────────────────────────────────────────────────
```

**Show cycle tracking:**
```
Gap closure cycle: {current_cycle} of 2
```

**Show Next Up:**
```
───────────────────────────────────────────────────────────────

## > Next Up

**Fix gaps:** Run /doc:plan-phase {N} --gaps to generate targeted fix plans

Then: /doc:write-phase {N} to execute fixes
Then: /doc:verify-phase {N} to re-verify

───────────────────────────────────────────────────────────────
```

**STOP - engineer will run plan-phase --gaps.**

---

## Step 7: Max Iterations Escalation

**Triggered when:** current_cycle > 2 (checked in Step 2)

Display banner:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > MAX GAP CLOSURE CYCLES REACHED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Read remaining gaps from VERIFICATION.md:**
```bash
Read .planning/phases/{NN}-{name}/VERIFICATION.md
Parse all truths with status GAP
```

**Create ENGINEER-TODO.md:**

```markdown
# Phase {N}: {Phase Name} - Manual Intervention Required

**Date:** {current date YYYY-MM-DD}
**Reason:** Gap closure loop terminated after max 2 cycles

The automated verification and gap closure process has reached its limit. The following gaps require manual resolution by the engineer.

---

## Remaining Gaps

### Gap 1: {Truth description}
**Severity:** {High/Medium/Low based on failed level}
  - Level 1-2 failures: High
  - Level 3-4 failures: Medium
  - Level 5 failures: Low

**Description:** {Full gap description from VERIFICATION.md}

**Context:** {Evidence from VERIFICATION.md showing what was found vs expected}

**Attempts:** 2 automated fix cycles attempted

**Next steps:**
1. {Suggested manual action based on gap type}
   - For Exists/Substantive: Add missing content to {section-file}
   - For Complete: Fill in missing elements (see evidence above)
   - For Consistent: Review CONTEXT.md and align content
   - For Standards: Review standard requirements and update terminology
2. Re-run /doc:verify-phase {N} after manual fix

---

### Gap 2: {Truth description}
...

---

## Resolution Process

After manually addressing the gaps above:

1. Run `/doc:verify-phase {N}` to re-verify
2. If verification passes: proceed to next phase
3. If new gaps appear: investigate and fix manually (automated loop disabled)

**Note:** The gap closure cycle counter has been reset. Manual fixes bypass the automated loop.
```

**Write ENGINEER-TODO.md:**
```bash
Write to: .planning/ENGINEER-TODO.md
```

**Update STATE.md:**
```bash
Update .planning/STATE.md:
  - Set phase {N} status to "BLOCKED"
  - Set blocked_reason to "Gap closure failed after 2 iterations - see ENGINEER-TODO.md"
```

**Update VERIFICATION.md status:**
```bash
Read current VERIFICATION.md
Change status line from "Status: GAPS_FOUND" to "Status: GAPS_FOUND (ESCALATED)"
Write back to VERIFICATION.md
```

**Display escalation message:**
```
═══════════════════════════════════════════════════════════════
PHASE {N} BLOCKED
═══════════════════════════════════════════════════════════════

Remaining gaps require manual resolution.

See: .planning/ENGINEER-TODO.md

{gap_count} gaps documented with resolution guidance.

After manual fixes: /doc:verify-phase {N}
```

**STOP - engineer must manually fix gaps.**

---

## Step 8: Re-Verification Scope Decision

**When this step runs:** Only during cycle 2+ (re-verification after gap closure)

This step was already integrated into Step 4 (Spawn Verifier Subagent) as the scope determination logic.

**Scope determination rules:**

1. **Read previous fix plans:**
   ```bash
   Check .planning/phases/{NN}-{name}/ for PLAN.md files created during gap closure
   Read each PLAN.md that was generated by /doc:plan-phase {N} --gaps
   ```

2. **Check for cross-reference impact:**
   ```
   If any PLAN.md contains keywords:
     - "cross-reference"
     - "reference to"
     - "CROSS-REFS.md"
     - "dependency"
     - "related section"

   Then: FULL PHASE re-verification (cross-references may have cascading effects)
   ```

3. **Check for isolated content fixes:**
   ```
   If PLAN.md files only mention:
     - Specific section numbers (NN-MM)
     - Content additions within one section
     - No cross-reference mentions

   Then: RE-VERIFY ONLY FIXED SECTIONS (efficient, no cascading effects)
   ```

4. **Document scope decision:**
   Add to VERIFICATION.md header:
   ```markdown
   Re-verification scope: {full phase | sections NN-MM, NN-MM}
   (Reason: {rationale - e.g., "cross-references modified in 03-02 PLAN.md" or "isolated content fixes to sections 03-02, 03-04"})
   ```

5. **Pass scope filter to verifier:**
   When spawning doc-verifier in Step 4, include scope information so the verifier knows which sections to focus on.

**Claude's discretion:**
- If uncertain whether a fix affects cross-references: default to FULL PHASE re-verification (safer)
- Document reasoning in VERIFICATION.md

---

## WORKFLOW RULES

**User-facing text:**
- All banners and messages use the project language (from PROJECT.md: Dutch or English)
- Use DOC > prefix on all banners (never GSD >)
- Use status symbols: ✓ (pass), ✗ (gap), ◆ (in progress), ○ (pending)

**Gap handling:**
- Gap descriptions only -- never suggest fixes in VERIFICATION.md (locked user decision)
- Gap format: "uses X instead of Y" NOT "change X to Y"
- Descriptive language only, no imperatives

**Verification cascade:**
- All 5 levels always run (locked user decision)
- STOP at first failure level per truth
- Higher levels marked as "Not Checked" if lower level fails

**Cross-reference handling:**
- References to unwritten sections: Claude's discretion (warn or defer as gap)
- Document reasoning in VERIFICATION.md
- Example: "Reference to section 04-02 (not yet written) - deferred for assembly-time validation"

**Cycle tracking:**
- Max 2 cycles (locked user decision)
- Cycle count in VERIFICATION.md header and STATE.md
- Exceeding max cycles: create ENGINEER-TODO.md AND set phase status to BLOCKED (both tracking and blocking)

**State management:**
- Update STATE.md after verification result
- Phase status values: "In Progress", "GAPS_FOUND", "✓ Verified", "BLOCKED"
- Track gap_closure_cycle in STATE.md

**Next Up blocks:**
- Always show Next Up after PASS or GAPS_FOUND
- Include copy-paste command
- Include alternatives (review-phase, status)

**Error handling:**
- No content to verify: clear error box with fix instruction
- Missing ROADMAP.md or PROJECT.md: clear error with path to fix
- Verifier subagent failure: display error and suggest retry

</workflow>
