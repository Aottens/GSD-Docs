<workflow>

# Write-Phase Workflow: Parallel FDS Content Generation

This workflow orchestrates parallel section writing with strict context isolation. It spawns doc-writer subagents per section, executes them in dependency-based waves, checkpoints STATE.md for crash recovery, and aggregates cross-references.

**Core principle:** The orchestrator reads ALL plans to build the dependency graph but NEVER passes other plans' content to writers. Each writer subagent receives only its own PLAN.md via strict context loading rules.

---

## Step 1: Parse Arguments and Validate Phase

Parse the phase number from $ARGUMENTS and validate the phase exists with all dependencies met.

**Extract phase number:**
```bash
PHASE=$ARGUMENTS
```

**Read ROADMAP.md to find phase entry:**
```bash
grep -A 5 "^## Phase ${PHASE}:" .planning/ROADMAP.md
```

**Extract phase information:**
- Phase name (from heading)
- Phase goal (from "Goal:" line)
- Dependencies (from "Dependencies:" line)

**Verify dependencies met:**
For each dependency listed:
- Check for corresponding phase directory: `.planning/phases/{dep}-*/`
- Check for SUMMARY.md files in that directory (completion proof)
- If any dependency missing or incomplete: show error box and abort

**Error format (from ui-brand.md):**
```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Phase ${PHASE} depends on Phase ${DEP}, but Phase ${DEP} has not been completed.

**To fix:** Run /doc:verify-phase ${DEP} to complete the dependency first.
```

**Read PROJECT.md for configuration:**
- Language setting (Dutch/English)
- Standards configuration:
  - standards.packml.enabled (true/false)
  - standards.isa88.enabled (true/false)

**Display banner (from ui-brand.md):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > WRITING PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 2: Discover and Classify Plans

Glob for all PLAN.md files in the phase directory and extract their metadata.

**Discover plans:**
```bash
PHASE_DIR=$(find .planning/phases -type d -name "${PHASE}-*" | head -1)
PLAN_FILES=$(find ${PHASE_DIR} -name "${PHASE}-[0-9][0-9]-PLAN.md" | sort)
```

**For each plan file, read YAML frontmatter:**
```bash
# Extract frontmatter fields
PLAN_NUMBER=$(grep "^plan:" ${PLAN_FILE} | cut -d: -f2 | tr -d ' ')
PLAN_NAME=$(basename ${PLAN_FILE} .md)
WAVE=$(grep "^wave:" ${PLAN_FILE} | cut -d: -f2 | tr -d ' ')
DEPENDS_ON=$(grep "^depends_on:" ${PLAN_FILE} | cut -d: -f2)
TYPE=$(grep "^type:" ${PLAN_FILE} | cut -d: -f2 | tr -d ' ')
```

**Group plans by wave number:**
Create a data structure mapping wave → [plan IDs]:
```
WAVE_1=("03-01" "03-02")
WAVE_2=("03-03")
WAVE_3=("03-04" "03-05")
```

**Count waves and plans per wave:**
```bash
TOTAL_WAVES=$(echo "${!WAVE_@}" | wc -w)
TOTAL_PLANS=$(echo ${PLAN_FILES} | wc -w)
```

**Display wave structure table:**
```
Wave Structure:
| Wave | Plans         | Sections                  |
|------|---------------|---------------------------|
| 1    | 03-01, 03-02  | EM-100, EM-200            |
| 2    | 03-03         | EM-300                    |
| 3    | 03-04, 03-05  | EM-400, Phase Overview    |
```

**Validation:**
- All plans must have a wave assignment
- Wave numbers must be sequential starting from 1
- No circular dependencies allowed (detect via topological sort)

If validation fails: show error box with details and abort.

---

## Step 3: Check for Resume State

Check if a previous write-phase execution was interrupted and can be resumed.

**Read STATE.md current operation section:**
```bash
grep -A 10 "^## Current Operation" .planning/STATE.md
```

**Extract fields explicitly (parse structured format):**
```bash
COMMAND=$(grep "^- command:" .planning/STATE.md | cut -d: -f2- | xargs)
PHASE=$(grep "^- phase:" .planning/STATE.md | cut -d: -f2- | xargs)
WAVE=$(grep "^- wave:" .planning/STATE.md | cut -d: -f2- | xargs)
WAVE_TOTAL=$(grep "^- wave_total:" .planning/STATE.md | cut -d: -f2- | xargs)
PLANS_DONE=$(grep "^- plans_done:" .planning/STATE.md | cut -d: -f2- | xargs)
PLANS_PENDING=$(grep "^- plans_pending:" .planning/STATE.md | cut -d: -f2- | xargs)
STATUS=$(grep "^- status:" .planning/STATE.md | cut -d: -f2- | xargs)
STARTED=$(grep "^- started:" .planning/STATE.md | cut -d: -f2- | xargs)
```

**Resume detection logic:**
```bash
if [[ "$COMMAND" == "write-phase" && "$STATUS" == "IN_PROGRESS" && "$PHASE" == "$CURRENT_PHASE" ]]; then
  RESUME=true
fi
```

**If resuming:**
- Extract plans_done list
- Verify completed plans by checking file existence:
  - ${PLAN_ID}-CONTENT.md exists
  - ${PLAN_ID}-SUMMARY.md exists
- If either file missing: remove plan from plans_done (forward-only recovery)
- Filter out completed plans from execution plan
- Display resume message:

```
DOC > Resuming from Wave {N} ({count} plans already complete)

Completed plans: 03-01, 03-02
Remaining plans: 03-03, 03-04, 03-05
```

**If no resume state or fresh start:**
- Proceed with all plans
- Display:

```
DOC > Fresh start: {total_plans} plans in {total_waves} waves
```

---

## Step 4: Execute Waves (Sequential)

For each wave (in order), execute all plans in that wave in parallel.

### 4a. Pre-wave Checkpoint

Before starting wave execution, update STATE.md with current operation state using structured checkpoint format.

**Update STATE.md Current Operation section:**
```markdown
## Current Operation
- command: write-phase
- phase: {N}
- wave: {current_wave}
- wave_total: {total_waves}
- plans_done: [{completed plan IDs as comma-separated list}]
- plans_pending: [{remaining plan IDs as comma-separated list}]
- status: IN_PROGRESS
- started: {ISO 8601 timestamp, e.g. 2026-02-13T14:30:00Z}
```

**Example:**
```markdown
## Current Operation
- command: write-phase
- phase: 3
- wave: 1
- wave_total: 3
- plans_done: []
- plans_pending: [03-01, 03-02, 03-03, 03-04, 03-05]
- status: IN_PROGRESS
- started: 2026-02-13T14:30:00Z
```

**Display:**
```
DOC > Wave {W}/{total}: Writing {count} sections in parallel
```

### 4b. Spawn Writers (Parallel within wave)

For EACH plan in the current wave, spawn a doc-writer subagent using the Task tool.

**CRITICAL CONTEXT ISOLATION:** The orchestrator builds the EXACT file list for each writer. Never pass directory paths. Never pass other plans' files.

**For each plan_id in wave:**

```bash
PLAN_ID="03-02"
PHASE_DIR=".planning/phases/03-write-verify-core-value"

# Build explicit context file list
CONTEXT_FILES=(
  ".planning/PROJECT.md"
  "${PHASE_DIR}/03-CONTEXT.md"
  "${PHASE_DIR}/${PLAN_ID}-PLAN.md"
)

# Add standards files if enabled
if [[ "${PACKML_ENABLED}" == "true" ]]; then
  CONTEXT_FILES+=("gsd-docs-industrial/references/standards/packml/packml-states.md")
fi

if [[ "${ISA88_ENABLED}" == "true" ]]; then
  CONTEXT_FILES+=("gsd-docs-industrial/references/standards/isa-88/hierarchy.md")
fi

# Spawn subagent with explicit file context
# NOTE: Claude Code Task tool syntax - pass files as @-references
TASK_MESSAGE="Write section ${PLAN_ID} per plan. Output files to ${PHASE_DIR}/. Produce ${PLAN_ID}-CONTENT.md and ${PLAN_ID}-SUMMARY.md."

# Spawn using Task tool with doc-writer agent
# Context files passed explicitly (no directory globs)
```

**The orchestrator NEVER passes to writers:**
- Other PLAN.md files in same phase
- Other CONTENT.md files in same phase
- Other SUMMARY.md files in same phase
- Main session conversation history
- Directory paths (always explicit file lists)

**Parallel execution:**
All writers in a wave spawn simultaneously. Use the Task tool's parallel execution capability. Wait for all to complete before proceeding to next wave.

**Max parallelism:**
Default: 4 concurrent writers per wave (conservative for system resources)
Configurable in config.json: `max_concurrent_agents`

If wave has more plans than max parallelism:
- Split wave into sub-batches
- Execute each sub-batch in parallel
- Sub-batches execute sequentially

Example: Wave 1 has 6 plans, max=4
- Sub-batch 1a: plans 1-4 (parallel)
- Sub-batch 1b: plans 5-6 (parallel)

### 4c. Post-wave Validation

After all writers in wave complete, validate their output.

**For each plan in wave:**

1. **Check CONTENT.md exists:**
```bash
if [[ ! -f "${PHASE_DIR}/${PLAN_ID}-CONTENT.md" ]]; then
  echo "ERROR: ${PLAN_ID}-CONTENT.md not created"
  ERRORS+=("${PLAN_ID}: CONTENT.md missing")
fi
```

2. **Check SUMMARY.md exists:**
```bash
if [[ ! -f "${PHASE_DIR}/${PLAN_ID}-SUMMARY.md" ]]; then
  echo "ERROR: ${PLAN_ID}-SUMMARY.md not created"
  ERRORS+=("${PLAN_ID}: SUMMARY.md missing")
fi
```

3. **Count file size:**
```bash
CONTENT_SIZE=$(wc -c < "${PHASE_DIR}/${PLAN_ID}-CONTENT.md")
```

4. **Count SUMMARY.md words:**
```bash
SUMMARY_WORDS=$(wc -w < "${PHASE_DIR}/${PLAN_ID}-SUMMARY.md")
```

5. **Count [VERIFY] markers:**
```bash
VERIFY_COUNT=$(grep -c "\[VERIFY\]" "${PHASE_DIR}/${PLAN_ID}-CONTENT.md")
```

**If any missing:**
- Log error but continue (don't block other waves)
- Missing files will be caught by verify-phase

**Display per-writer results:**
```
Wave {W} Results:
- 03-01: CONTENT.md (2.3KB), SUMMARY.md (142 words), [VERIFY]: 3
- 03-02: CONTENT.md (1.8KB), SUMMARY.md (135 words), [VERIFY]: 1
```

### 4d. Post-wave Checkpoint

After all writers in wave complete successfully, update STATE.md.

**Update STATE.md Current Operation section:**
- Add completed wave's plan IDs to plans_done array (comma-separated list)
- Remove those plan IDs from plans_pending array
- Increment wave counter to next wave number
- Keep status as IN_PROGRESS (until all waves done)

**Example transition:**
```markdown
Before wave 1 completes:
- plans_done: []
- plans_pending: [03-01, 03-02, 03-03, 03-04, 03-05]
- wave: 1

After wave 1 completes:
- plans_done: [03-01, 03-02]
- plans_pending: [03-03, 03-04, 03-05]
- wave: 2
```

**CRITICAL - Atomic checkpoint:**
Write STATE.md atomically — only after ALL writers in wave complete. This is the crash recovery boundary. If a crash occurs during wave execution, the pre-wave checkpoint is the recovery point, and completed plans in the interrupted wave will be re-verified (not re-executed) on resume.

---

## Step 5: Aggregate Cross-References

After all waves complete, collect and consolidate cross-references from all writers.

**Read all CROSS-REFS.md entries:**

Writers may have created/appended to:
- Individual section-level CROSS-REFS.md files
- Phase-level CROSS-REFS.md file

**Aggregation strategy:**

1. **Collect all cross-reference entries:**
```bash
# Find all CROSS-REFS.md files in phase directory
CROSSREF_FILES=$(find ${PHASE_DIR} -name "*CROSS-REFS.md")

# Read and parse each file
for FILE in ${CROSSREF_FILES}; do
  # Extract table rows (skip header)
  grep "^|" ${FILE} | grep -v "^| Source" >> all-refs.tmp
done
```

2. **Deduplicate entries:**
If multiple writers created the same reference:
- Keep first occurrence
- Check for conflicts (same source/target, different type or context)
- If conflict: log warning, keep most specific entry

3. **Update status column:**
For each cross-reference:
- Check if target section exists (CONTENT.md file present)
- If exists: status = "resolved"
- If not exists: status = "pending"

4. **Write consolidated CROSS-REFS.md:**
```bash
# Write to phase-level file
OUTPUT_FILE="${PHASE_DIR}/${PHASE}-CROSS-REFS.md"
```

**Format (from cross-refs.md template):**
```markdown
# Phase {N} Cross-References

**Generated:** {timestamp}
**Total references:** {count}
**Resolved:** {resolved_count}
**Pending:** {pending_count}

| Source | Target | Type | Context | Status |
|--------|--------|------|---------|--------|
| 03-01 EM-100 | 03-03 EM-300 | depends-on | Water level interlock triggers EM-300 fill | resolved |
| 03-02 EM-200 | §6.3 Interlocks | see-also | Full interlock table in safety section | pending |
```

**Statistics:**
- Total cross-references created
- Resolved (target exists)
- Pending (target not yet written)

---

## Step 6: Final STATE.md Update

After all waves complete successfully, update STATE.md to mark operation complete.

**Update STATE.md Current Operation section:**
```markdown
## Current Operation
- command: write-phase
- phase: {N}
- status: COMPLETE
- completed: {ISO 8601 timestamp}
- plans_written: [{all plan IDs as comma-separated list}]
- verify_markers: {total [VERIFY] count across all sections}
- cross_refs: {total cross-reference count}
```

**Example:**
```markdown
## Current Operation
- command: write-phase
- phase: 3
- status: COMPLETE
- completed: 2026-02-13T15:45:00Z
- plans_written: [03-01, 03-02, 03-03, 03-04, 03-05]
- verify_markers: 12
- cross_refs: 8
```

**Field changes on completion:**
- Remove: wave, wave_total, plans_pending (no longer needed)
- Rename: plans_done → plans_written (clearer completion semantics)
- Add: completed timestamp
- Keep: command, phase, status, plans_written, verify_markers, cross_refs
- Remove: started (replaced by completed)

---

## Step 7: Completion Summary

Display final summary and next steps.

**Display banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PHASE {N} WRITTEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Show summary:**
```
Sections written: {count}
Waves executed: {wave_count}
CONTENT.md files: {count} ({total size})
SUMMARY.md files: {count}
[VERIFY] markers: {count} (engineer review needed)
Cross-references: {count} ({resolved} resolved, {pending} pending)
```

**If [VERIFY] markers > 0, display note:**
```
Note: {count} [VERIFY] markers in content require engineer review.
These are inferred values that should be confirmed for accuracy.
```

**Show Next Up block (from ui-brand.md):**
```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase {N}: Verify** -- Goal-backward verification with gap detection

`/doc:verify-phase {N}`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────
```

---

## Workflow Rules

**Language:**
- All user-facing text matches the project language (from PROJECT.md)
- Use DOC > prefix on all banners (never GSD >)

**Context isolation enforcement:**
- Orchestrator reads ALL plans to build dependency graph
- Orchestrator NEVER reads CONTENT.md from other sections
- Context isolation enforced by explicit file listing, not directory access
- Writers cannot discover files beyond explicit context (Glob/Grep disallowed in doc-writer subagent)

**STATE.md checkpointing:**
- Checkpoint is atomic: only write after all writers in wave complete
- Pre-wave: status IN_PROGRESS
- Post-wave: update plans_done, plans_pending
- Final: status COMPLETE
- The Current Operation section is the ONLY section that changes during write-phase execution. All other STATE.md sections (Progress, Decisions, etc.) remain untouched. This limits the blast radius of a checkpoint write.

**Recovery strategy:**
- Forward-only: on resume, never re-execute completed plans
- Completion proof: SUMMARY.md existence (not just STATE.md status)
- Missing files: if resume state says "done" but files missing, re-execute that plan

**Parallelism:**
- Max 4 parallel writers per wave (conservative default)
- Configurable via config.json: max_concurrent_agents
- If wave > max: split into sub-batches, execute sub-batches sequentially

**Error handling:**
- Missing PLAN.md: abort with error
- Circular dependencies: abort with error
- Writer fails: log error, continue with other writers, report in summary
- Missing output files: log error, continue, will be caught by verify-phase

**Standards loading:**
- Only load standards files if enabled in PROJECT.md
- PackML: gsd-docs-industrial/references/standards/packml/packml-states.md
- ISA-88: gsd-docs-industrial/references/standards/isa-88/hierarchy.md
- If not enabled: do not load, do not reference in writer context

**Cross-reference aggregation:**
- Collect from all writers after all waves complete
- Deduplicate identical entries
- Update status based on target file existence
- Log warnings for conflicts (same ref, different type/context)

</workflow>
