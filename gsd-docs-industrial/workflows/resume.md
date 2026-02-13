<workflow>

# Resume Workflow: Crash Recovery with Forward-Only Execution

This workflow detects interrupted operations, verifies completion proofs against the filesystem, displays context, applies smart defaults for resume decisions, and re-executes incomplete work using forward-only recovery.

**Core principle:** SUMMARY.md existence is the ONLY definitive completion proof. STATE.md status is a hint only. If filesystem and STATE.md disagree, trust the filesystem.

---

## Step 1: Detect Interrupted Operations

Read `.planning/STATE.md` and extract the Current Operation section to detect interrupted work.

**Parse Current Operation fields:**
```bash
# Extract structured fields from STATE.md
COMMAND=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Command:" | cut -d':' -f2- | xargs)
PHASE=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Phase:" | cut -d':' -f2- | xargs)
WAVE=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Wave:" | cut -d':' -f2- | cut -d'/' -f1 | xargs)
WAVE_TOTAL=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Wave:" | cut -d':' -f2- | cut -d'/' -f2 | xargs)
PLANS_DONE=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Plans done:" | cut -d':' -f2- | xargs)
PLANS_PENDING=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Plans pending:" | cut -d':' -f2- | xargs)
STATUS=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Status:" | cut -d':' -f2- | xargs)
STARTED=$(grep -A 8 "^## Current Operation" .planning/STATE.md | grep "^- Started:" | cut -d':' -f2- | xargs)
```

**Check if interrupted operation exists:**
- If `STATUS` is not `IN_PROGRESS`: no interrupted operation
- Display:
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DOC > RESUME
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No interrupted operation found.

  To start work, use /doc:status to see your project state.
  ```
- STOP execution

If `STATUS` is `IN_PROGRESS`, proceed to Step 2.

---

## Step 2: Verify Completion Proofs

For each plan in the interrupted operation, verify completion against the filesystem. STATE.md may be stale or corrupted — trust file existence only.

**Find phase directory:**
```bash
# Use glob to find phase directory (handles decimal numbering)
PHASE_DIR=$(find .planning/phases -type d -name "${PHASE}-*" | head -n 1)
```

**Split comma-separated plan lists:**
```bash
# Convert "01-01, 01-02" to array
IFS=',' read -ra DONE_ARRAY <<< "$PLANS_DONE"
IFS=',' read -ra PENDING_ARRAY <<< "$PLANS_PENDING"
```

**Verify plans_done (belt-and-suspenders check):**
```bash
VERIFIED_COMPLETE=()
INCOMPLETE=()

for plan_id in "${DONE_ARRAY[@]}"; do
  plan_id=$(echo "$plan_id" | xargs)  # Trim whitespace

  # Completion proof: BOTH files exist
  if [[ -f "${PHASE_DIR}/${plan_id}-CONTENT.md" ]] && [[ -f "${PHASE_DIR}/${plan_id}-SUMMARY.md" ]]; then
    VERIFIED_COMPLETE+=("$plan_id")
  else
    # STATE.md lied — crash corrupted checkpoint
    INCOMPLETE+=("$plan_id")
  fi
done
```

**Check plans_pending for unexpected completions:**
```bash
for plan_id in "${PENDING_ARRAY[@]}"; do
  plan_id=$(echo "$plan_id" | xargs)

  # Check if actually complete (STATE.md didn't record it)
  if [[ -f "${PHASE_DIR}/${plan_id}-CONTENT.md" ]] && [[ -f "${PHASE_DIR}/${plan_id}-SUMMARY.md" ]]; then
    VERIFIED_COMPLETE+=("$plan_id")
  else
    INCOMPLETE+=("$plan_id")
  fi
done
```

**Detect partial writes (from 04-01 heuristics):**
```bash
PARTIAL=()

for plan_id in "${INCOMPLETE[@]}"; do
  CONTENT_PATH="${PHASE_DIR}/${plan_id}-CONTENT.md"
  SUMMARY_PATH="${PHASE_DIR}/${plan_id}-SUMMARY.md"

  # Heuristic 1: Missing SUMMARY.md (definitive)
  if [[ ! -f "$SUMMARY_PATH" ]] && [[ -f "$CONTENT_PATH" ]]; then
    PARTIAL+=("${plan_id}: missing SUMMARY.md")
    continue
  fi

  # Heuristic 2: Content too short
  if [[ -f "$CONTENT_PATH" ]]; then
    SIZE=$(wc -c < "$CONTENT_PATH")
    if [[ $SIZE -lt 200 ]]; then
      PARTIAL+=("${plan_id}: content too short ($SIZE bytes)")
    fi
  fi
done
```

---

## Step 3: Display Context Summary

Show what was interrupted and current state with completion proof verification.

**Build lists:**
```bash
VERIFIED_COUNT=${#VERIFIED_COMPLETE[@]}
INCOMPLETE_COUNT=${#INCOMPLETE[@]}
PARTIAL_COUNT=${#PARTIAL[@]}
```

**Display summary:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Interrupted operation: /doc:${COMMAND} ${PHASE}
  Started: ${STARTED}
  Wave: ${WAVE}/${WAVE_TOTAL}

Completed: ${VERIFIED_COUNT} plans
  ${VERIFIED_COMPLETE[@]}

Remaining: ${INCOMPLETE_COUNT} plans
  ${INCOMPLETE[@]}

${If PARTIAL_COUNT > 0:}
Partial writes detected:
  ${PARTIAL[@]}
```

---

## Step 4: Smart Default Decision

Apply the locked user decision: "Smart default: auto-resume if only one thing was interrupted; show choices if multiple things are incomplete."

**Single incomplete operation (smart default):**

If all incomplete plans are from the same interrupted operation and there's only one operation interrupted:

```bash
# Ask confirmation with smart default
echo ""
read -p "Resume /doc:${COMMAND} ${PHASE} from wave ${WAVE}? (Y/n): " CONFIRM
CONFIRM=${CONFIRM:-Y}  # Default: Y

if [[ "$CONFIRM" =~ ^[Yy] ]]; then
  # Proceed to Step 5
else
  echo ""
  echo "Resume cancelled. Run /doc:status to see project state."
  exit 0
fi
```

**Multiple options needed (rare — e.g., phase has both partial writes AND a different command was interrupted):**

If there are multiple distinct incomplete operations or complex state:

```bash
echo ""
echo "Resume options:"
echo "1. Resume /doc:${COMMAND} ${PHASE} (complete ${INCOMPLETE_COUNT} plans)"
echo "2. View detailed status (/doc:status)"
echo "3. Start different operation (keeps completed work)"
echo ""
read -p "Selection (1-3): " CHOICE

case $CHOICE in
  1)
    # Proceed to Step 5
    ;;
  2)
    echo ""
    echo "Run /doc:status for full project state."
    exit 0
    ;;
  3)
    # Abandon interrupted operation (preserve completed work)
    echo ""
    echo "Updating STATE.md to clear interrupted operation..."

    # Update STATE.md: set status to ABANDONED, preserve plans_done
    # (This allows engineer to run a different command)

    echo "Run your desired command. Completed work is preserved."
    exit 0
    ;;
  *)
    echo "Invalid selection. Cancelled."
    exit 1
    ;;
esac
```

---

## Step 5: Execute Resume

Re-execute the interrupted operation using forward-only recovery. Completed work (verified SUMMARY.md + CONTENT.md pairs) is NEVER re-executed.

**If command was `write-phase`:**

Determine which wave to resume from:
```bash
# Find the lowest wave number among incomplete plans
MIN_WAVE=${WAVE_TOTAL}

for plan_id in "${INCOMPLETE[@]}"; do
  # Extract wave from plan frontmatter
  PLAN_WAVE=$(grep -m 1 "^wave:" "${PHASE_DIR}/${plan_id}-PLAN.md" | cut -d':' -f2 | xargs)

  if [[ $PLAN_WAVE -lt $MIN_WAVE ]]; then
    MIN_WAVE=$PLAN_WAVE
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " DOC > RESUMING WRITE-PHASE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Resuming from wave ${MIN_WAVE}"
echo "Completed plans will be skipped (forward-only recovery)"
echo ""
```

Re-run write-phase execution from that wave forward:
- Follow write-phase workflow Steps 4-7 (wave execution through completion)
- Spawn doc-writer subagents for INCOMPLETE plans only
- Skip plans in VERIFIED_COMPLETE array (NEVER re-execute verified plans)
- Checkpoint STATE.md per wave (same pattern as normal execution)
- Update Current Operation after each wave with new plans_done

**Example delegation to write-phase:**
```bash
# Export verified plans to skip
export SKIP_PLANS="${VERIFIED_COMPLETE[@]}"

# Call write-phase workflow Steps 4-7 with resume flag
# (The write-phase workflow already has wave execution logic)

# Pseudo-code (actual implementation delegates to write-phase.md):
# - Read all PLAN.md files in phase
# - Group by wave (starting from MIN_WAVE)
# - For each wave:
#   - Filter out plans in SKIP_PLANS
#   - Spawn doc-writer for remaining plans
#   - Wait for completion
#   - Checkpoint STATE.md
```

**If command was `verify-phase`:**

Re-spawn doc-verifier subagent:
```bash
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " DOC > RESUMING VERIFY-PHASE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Re-running verification for phase ${PHASE}"
echo ""

# Follow verify-phase workflow from Step 3 onwards
# (Verification is idempotent — re-running produces a new VERIFICATION.md)
```

**If command was anything else:**

Display the command that was interrupted and suggest re-running it:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To resume, run: /doc:${COMMAND} ${PHASE}

The command will auto-detect the interrupted state.
```

---

## Step 6: Completion

After successful resume, update STATE.md and display completion summary.

**Update STATE.md: status → COMPLETE**
```bash
# Use write-phase or verify-phase completion logic to update STATE.md
# Set Current Operation status to COMPLETE
# Transition fields: plans_done → plans_written, remove wave/wave_total/plans_pending
```

**Display completion summary:**

Delegate to the command's normal completion flow:
- For write-phase: show completion table with all CONTENT.md + SUMMARY.md files
- For verify-phase: show verification result summary

---

## Workflow Rules

**Forward-only recovery:**
- NEVER re-execute plans with verified SUMMARY.md + CONTENT.md
- SUMMARY.md existence is the ONLY completion proof
- If both files exist, plan is complete regardless of STATE.md status

**Filesystem as source of truth:**
- STATE.md is a hint — always verify against filesystem
- If filesystem and STATE.md disagree: trust the filesystem
- Completion proof check runs BEFORE resume execution

**Smart defaults:**
- Single incomplete operation: auto-resume with Y/n confirmation (default: Y)
- Multiple operations or complex state: present choices
- Always preserve completed work (forward-only)

**Banner style:**
- Use `DOC >` prefix for all banners (never `GSD >`)
- Match ui-brand.md patterns for consistency

</workflow>
