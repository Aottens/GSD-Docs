<workflow>

# Status Workflow: Project Progress Display

This workflow renders comprehensive project status from three authoritative sources: STATE.md (operation state), ROADMAP.md (phase structure), and filesystem (actual file existence as proof of work). Status is read-only and never modifies any files.

**Core principle:** Use filesystem for proof of work, never trust STATE.md alone. SUMMARY.md existence is the ONLY completion proof for plans.

---

## Step 1: Load Project State

Read three data sources to build complete project picture.

**Check for .planning/ directory:**
```bash
if [ ! -d ".planning" ]; then
  # Display error and stop
fi
```

**Error display if no project found:**
```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

No project found. Run /doc:new-fds to create a project.
```

**Read STATE.md:**
Extract from `.planning/STATE.md`:
- Current Position section: phase number, plan number, status, last activity
- Current Operation section (8 fields): command, phase, wave, wave_total, plans_done, plans_pending, status, started
- Decisions section: list of key decisions
- Blockers section: any blocking issues
- Session Continuity section: last session, stopped at, resume file

**Read ROADMAP.md:**
Parse all phase entries from `.planning/ROADMAP.md`:
- Phase number (from heading `## Phase N:`)
- Phase name (from heading text)
- Phase goal (from "Goal:" line)
- Requirements count (from "Requirements:" line if present)
- Dependencies (from "Dependencies:" line)
- Status (from "Status:" line if present, but verify against filesystem)

**Read PROJECT.md:**
Extract from `.planning/PROJECT.md`:
- Project name (from heading or metadata)
- Project type (Type A/B/C/D)
- Language (Dutch/English)

---

## Step 2: Calculate Progress from Filesystem

For EACH phase listed in ROADMAP.md, calculate actual progress using file existence.

**Find phase directory:**
```bash
PHASE_DIR=$(find .planning/phases -type d -name "${PHASE_NUM}-*" | head -1)
```

**Count plans in phase:**
```bash
# Total plans
PLAN_FILES=$(find ${PHASE_DIR} -name "${PHASE_NUM}-[0-9][0-9]-PLAN.md" 2>/dev/null | wc -l)

# Completed plans (SUMMARY.md is completion proof)
SUMMARY_FILES=$(find ${PHASE_DIR} -name "${PHASE_NUM}-[0-9][0-9]-SUMMARY.md" 2>/dev/null | wc -l)
```

**Check for verification:**
```bash
# Check for VERIFICATION.md
if [ -f "${PHASE_DIR}/${PHASE_NUM}-VERIFICATION.md" ] || [ -f "${PHASE_DIR}/VERIFICATION.md" ]; then
  # Read status from VERIFICATION.md
  VERIFICATION_STATUS=$(grep "^Status:" ${VERIFICATION_FILE} | cut -d: -f2 | tr -d ' ')
fi
```

**Detect partial writes using 4-heuristic cascade:**

For each CONTENT.md file in the phase directory:

1. **Missing SUMMARY.md (HIGH confidence):**
   ```bash
   CONTENT_FILE="${PHASE_DIR}/${PLAN_ID}-CONTENT.md"
   SUMMARY_FILE="${PHASE_DIR}/${PLAN_ID}-SUMMARY.md"
   if [ -f "${CONTENT_FILE}" ] && [ ! -f "${SUMMARY_FILE}" ]; then
     PARTIAL_REASON="missing_summary"
     CONFIDENCE="HIGH"
   fi
   ```

2. **Content too short (HIGH confidence):**
   ```bash
   CONTENT_SIZE=$(wc -c < "${CONTENT_FILE}")
   if [ ${CONTENT_SIZE} -lt 200 ]; then
     PARTIAL_REASON="content_too_short"
     CONFIDENCE="HIGH"
   fi
   ```

3. **Completion marker (HIGH confidence):**
   ```bash
   if grep -q "\[TO BE COMPLETED\]" "${CONTENT_FILE}"; then
     PARTIAL_REASON="completion_marker"
     CONFIDENCE="HIGH"
   fi
   ```

4. **Abrupt ending (MEDIUM confidence):**
   Check if last non-empty line looks incomplete (no period, ends mid-sentence, etc.)
   ```bash
   LAST_LINE=$(tail -5 "${CONTENT_FILE}" | grep -v "^$" | tail -1)
   # Heuristic check for abrupt ending
   if [[ ! "${LAST_LINE}" =~ \.$|^#|^-|^\* ]]; then
     PARTIAL_REASON="abrupt_ending"
     CONFIDENCE="MEDIUM"
   fi
   ```

**Derive phase status:**

Use this priority order to determine status:
1. `Verified` — VERIFICATION.md exists with `Status: PASS`
2. `Gaps Found` — VERIFICATION.md exists with `Status: GAPS_FOUND`
3. `Blocked` — STATE.md shows phase as BLOCKED (check Blockers section)
4. `Written` — All plans have SUMMARY.md but no VERIFICATION.md yet (100% completion)
5. `In Progress` — Some plans have SUMMARY.md (partial completion) OR Current Operation targets this phase
6. `Planned` — PLAN.md files exist but no SUMMARY.md files yet (0% completion but plans ready)
7. `Pending` — No PLAN.md files in phase directory (or directory doesn't exist)

**Calculate overall completion percentage:**
```
completed_plans = sum(SUMMARY.md counts across all phases)
total_plans = sum(PLAN.md counts across all phases)
percentage = (completed_plans / total_plans) * 100
```

**Note:** Only count phases that HAVE plans. Pending phases with 0 plans are excluded from both numerator and denominator.

---

## Step 3: Display Progress

Display the DOC > PROJECT STATUS banner following ui-brand.md pattern.

**Display banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PROJECT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Display project info:**
```
Project: {project_name}
Type: {type} | Language: {language}
```

**Display overall progress bar:**
```
Progress: ████████████████░░░░░░░░░░░░░░ 53%
```

**Progress bar rendering:**
- Total bar width: 30 characters
- Use `█` for filled portions
- Use `░` for empty portions
- Calculate filled characters: `round(percentage / 100 * 30)`
- Display percentage to nearest whole number

Example calculations:
- 0% → `░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%`
- 53% → `████████████████░░░░░░░░░░░░░░ 53%`
- 100% → `██████████████████████████████ 100%`

---

## Step 4: Display Phase Table

Display per-phase status table showing all phases from ROADMAP.md.

**Table format:**
```
| Phase | Name                              | Plans  | Status       |
|-------|-----------------------------------|--------|--------------|
| 1     | Framework Foundation              | 4/4    | ✓ Verified   |
| 2     | Discuss + Plan Commands           | 4/4    | ✓ Verified   |
| 3     | Write + Verify (Core Value)       | 3/5    | ⚙ In Progress|
| 4     | State Management + Recovery       | -/-    | ○ Pending    |
| 5     | Complete-FDS + Standards          | -/-    | ○ Pending    |
```

**Column definitions:**
- **Phase:** Phase number from ROADMAP.md
- **Name:** Phase name (truncate to 35 chars if needed)
- **Plans:** `{completed}/{total}` or `-/-` for phases with 0 plans
- **Status:** Status indicator + text

**Status indicators (from ui-brand.md):**
- `✓ Verified` — Phase has VERIFICATION.md with Status: PASS
- `✓ Written` — All plans complete (100% SUMMARY.md), no verification yet
- `⚙ In Progress` — Some plans complete but not all
- `⚙ Gaps Found` — VERIFICATION.md with Status: GAPS_FOUND
- `○ Planned` — Plans exist but no SUMMARY.md files
- `○ Pending` — No plans in phase directory
- `✗ Blocked` — Blocker exists in STATE.md for this phase

**Alternative single-symbol indicators for compact display:**
- `✓` for verified/written
- `⚙` for in progress/gaps/planned
- `○` for pending
- `✗` for blocked

---

## Step 5: Display Active Phase Detail

Find the active phase (first phase that is not Verified and not Pending) and show detailed artifact information.

**Active phase determination:**

Active phase is the FIRST phase in this order:
1. Phase with status = Blocked (highest priority)
2. Phase with status = Gaps Found
3. Phase with status = In Progress
4. Phase with status = Written (not verified yet)
5. Phase with status = Planned (has plans, nothing written)

**If active phase found, display:**
```
Active Phase: {N} — {Phase Name}

| Plan    | CONTENT.md | SUMMARY.md | Status    |
|---------|------------|------------|-----------|
| {NN}-01 | ✓ 2.3KB   | ✓ 142w    | Complete  |
| {NN}-02 | ✓ 1.8KB   | ✗ missing  | Partial   |
| {NN}-03 | ✗ missing  | ✗ missing  | Pending   |

VERIFICATION.md: {status}
```

**Column definitions for plan table:**
- **Plan:** Plan ID ({NN}-{MM})
- **CONTENT.md:** `✓ {size}` if exists, `✗ missing` if not. Size in KB (e.g., "2.3KB")
- **SUMMARY.md:** `✓ {words}w` if exists, `✗ missing` if not. Word count (e.g., "142w")
- **Status:**
  - `Complete` — Both CONTENT.md and SUMMARY.md exist
  - `Partial` — CONTENT.md exists but SUMMARY.md missing
  - `Pending` — Neither file exists

**VERIFICATION.md status line:**
- `Yes (PASS)` — Verification complete and passed
- `Yes (GAPS_FOUND, cycle 1/2)` — Gaps found, show cycle count
- `No` — Not yet verified

**If no active phase found:**
Don't display this section (all phases either verified or pending).

---

## Step 6: Display Partial Write Warnings

If any partial writes detected in the active phase, display warning section.

**Check for partials:**
Review the partial detection results from Step 2 for the active phase.

**If partials exist, display:**
```
⚠ Partial Writes Detected:

- {plan-id}: {reason} — Run /doc:resume or /doc:write-phase {N}
- {plan-id}: {reason} — Run /doc:resume or /doc:write-phase {N}
```

**Reason text mapping:**
- `missing_summary` → "CONTENT.md exists but no SUMMARY.md"
- `content_too_short` → "CONTENT.md < 200 bytes"
- `completion_marker` → "Contains [TO BE COMPLETED] marker"
- `abrupt_ending` → "Possible abrupt ending (MEDIUM confidence)"

**If no partials:**
Don't display this section.

---

## Step 7: Display Current Operation (if active)

If STATE.md Current Operation section shows status = IN_PROGRESS, display operation info.

**Check operation status:**
```bash
OPERATION_STATUS=$(grep "^- Status:" .planning/STATE.md | grep "Current Operation" -A 8 | grep "Status:" | cut -d: -f2 | tr -d ' ')
```

**If status is IN_PROGRESS, display:**
```
Current Operation: {command} phase {phase}
  Wave: {wave}/{wave_total}
  Plans done: {plans_done}
  Plans pending: {plans_pending}
  Started: {started}
```

**Field extraction from Current Operation section:**
- command: e.g., "write-phase"
- phase: e.g., "3"
- wave: current wave number
- wave_total: total waves in phase
- plans_done: comma-separated list of completed plan IDs
- plans_pending: comma-separated list of pending plan IDs
- status: IN_PROGRESS
- started: ISO 8601 timestamp

**If status is not IN_PROGRESS or section doesn't exist:**
Don't display this section.

---

## Step 8: Derive and Display Next Action

Determine recommended next action based on project state and display it prominently.

**Next action logic (checked in this order):**

1. **If Current Operation status is IN_PROGRESS:**
   - Action: "Resume interrupted operation"
   - Context: `{command} phase {phase}, wave {wave}/{wave_total}`
   - Command: `/doc:resume`

2. **If any phase has partial writes (HIGH confidence only):**
   - Action: "Complete partial writes"
   - Context: `{N} partial plans in Phase {phase}`
   - Command: `/doc:resume` or `/doc:write-phase {phase}`

3. **If any phase has status Blocked:**
   - Action: "Resolve blocked phase"
   - Context: `Phase {phase} blocked`
   - Command: `See .planning/ENGINEER-TODO.md`

4. **If any phase has status Gaps Found:**
   - Action: "Close gaps in phase {N}"
   - Context: `{gap_count} gaps found, cycle {cycle}/2`
   - Command: `/doc:plan-phase {phase} --gaps`

5. **If any phase has status Written (not verified):**
   - Action: "Verify phase {N}"
   - Context: `{plan_count} plans ready for verification`
   - Command: `/doc:verify-phase {phase}`

6. **If any phase has status Planned (has plans, nothing written):**
   - Action: "Write phase {N}"
   - Context: `{plan_count} plans ready, 0 written`
   - Command: `/doc:write-phase {phase}`

7. **If any phase has CONTEXT.md but no plans:**
   - Action: "Plan phase {N}"
   - Context: `Discussion complete, ready for planning`
   - Command: `/doc:plan-phase {phase}`

8. **If next unstarted phase exists (no CONTEXT.md):**
   - Action: "Discuss phase {N}"
   - Context: `Next phase in roadmap`
   - Command: `/doc:discuss-phase {phase}`

9. **If all phases verified:**
   - Action: "Assemble FDS"
   - Context: `All {total_phases} phases complete`
   - Command: `/doc:complete-fds`

**Display format:**
```
───────────────────────────────────────────────────────────────

Next: {action description} ({context})

  {command}

───────────────────────────────────────────────────────────────
```

**Example displays:**
```
───────────────────────────────────────────────────────────────

Next: Resume interrupted operation (write-phase phase 3, wave 2/3)

  /doc:resume

───────────────────────────────────────────────────────────────
```

```
───────────────────────────────────────────────────────────────

Next: Write phase 3 (5 plans ready, 0 written)

  /doc:write-phase 3

───────────────────────────────────────────────────────────────
```

```
───────────────────────────────────────────────────────────────

Next: Verify phase 3 (5 plans ready for verification)

  /doc:verify-phase 3

───────────────────────────────────────────────────────────────
```

---

## Workflow Rules

**File system as source of truth:**
- SUMMARY.md existence is the ONLY completion proof for plan completion
- Never trust STATE.md status alone — always verify against filesystem
- Progress calculation uses file counts, not STATE.md status field
- STATE.md Current Operation is hint only, verify actual file state

**Read-only operation:**
- Status command NEVER modifies any file
- No writes to STATE.md, no creating files, no updating timestamps
- Pure display operation only

**User-facing text:**
- All text matches project language from PROJECT.md (Dutch or English)
- Use DOC > prefix on all banners (never GSD >)
- Follow ui-brand.md patterns for all visual elements
- Status symbols: ✓ ✗ ⚙ ○ (from ui-brand.md)

**Error handling:**
- If .planning/ doesn't exist: show error box and stop
- If STATE.md or ROADMAP.md missing: show error with file name and stop
- If phase directory doesn't exist: treat as Pending (0 plans)
- If CONTENT.md or SUMMARY.md unreadable: show file size as "error"

**Partial detection confidence:**
- HIGH confidence: missing SUMMARY.md, content < 200 bytes, [TO BE COMPLETED] marker
- MEDIUM confidence: abrupt ending detection (heuristic-based, can have false positives)
- Only HIGH confidence partials affect next action recommendation

</workflow>
