<workflow>

# /doc:review-phase Workflow

Complete execution logic for interactive section-by-section phase review with structured feedback capture. The command file (`~/.claude/commands/doc/review-phase.md`) delegates here. Follow each step in order.

**Purpose:** Enable structured documentation handover where completed phase content is presented systematically with full context (SUMMARY.md facts, cross-references, CONTENT.md), and reviewer feedback is captured in a format that can optionally feed into the gap closure pipeline.

**Downstream consumers:**
- Engineers reviewing completed work (handover to colleague taking over project)
- Clients reviewing FDS content (section-by-section walkthrough)
- Internal reviewers performing quality checks
- `/doc:plan-phase N --gaps --source review` for automatic gap closure (if --route-gaps flag used)

**Philosophy:** Review is supplementary to verify-phase. Verification checks completeness and standards compliance (automated checks). Review captures human judgment on clarity, correctness, and suitability. Review does not change verification status -- both can exist independently.

---

## Step 1: Parse Arguments and Validate Phase

Parse `$ARGUMENTS` to get the phase number and flags. Phase number is required -- abort if missing.

```bash
# Parse arguments
PHASE=$(echo "$ARGUMENTS" | sed 's/--route-gaps//g' | sed 's/--resume//g' | xargs)
PADDED_PHASE=$(printf "%02d" ${PHASE})

# Parse flags
ROUTE_GAPS=false
RESUME=false
if echo "$ARGUMENTS" | grep -q -- "--route-gaps"; then
  ROUTE_GAPS=true
fi
if echo "$ARGUMENTS" | grep -q -- "--resume"; then
  RESUME=true
fi
```

### 1.1 Read ROADMAP.md

Read `.planning/ROADMAP.md` to find the phase entry.

Extract:
- Phase number and name
- Phase goal / description

**If phase not found in ROADMAP.md:**

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Phase {N} not found in ROADMAP.md.

**To fix:** Use `/doc:status` to see available phases,
or check .planning/ROADMAP.md for the phase list.
```

Stop execution. Do not continue.

### 1.2 Read PROJECT.md

Read `.planning/PROJECT.md` for language setting.

```bash
LANGUAGE=$(grep "^Language:" .planning/PROJECT.md | awk '{print $2}' | tr -d '"')
if [ -z "$LANGUAGE" ]; then
  LANGUAGE="en"  # Default to English if not set
fi
```

### 1.3 Check Phase Has Content

Look for CONTENT.md files in the phase directory:

```bash
PHASE_DIR=$(ls -d .planning/phases/${PADDED_PHASE}-* 2>/dev/null | head -1)
if [ -z "$PHASE_DIR" ]; then
  echo "ERROR: Phase ${PHASE} directory not found."
  exit 1
fi

CONTENT_COUNT=$(find "$PHASE_DIR" -name "*-CONTENT.md" 2>/dev/null | wc -l)
if [ "$CONTENT_COUNT" -eq 0 ]; then
  echo "ERROR: Phase ${PHASE} has no content to review (no *-CONTENT.md files found)."
  echo ""
  echo "To fix: Run /doc:write-phase ${PHASE} to generate content first."
  exit 1
fi
```

**Optional verification check (warn-only):**

Check for VERIFICATION.md with PASS status:

```bash
VERIFICATION_FILE="${PHASE_DIR}/VERIFICATION.md"
if [ -f "$VERIFICATION_FILE" ]; then
  VERIFICATION_STATUS=$(grep "^Status:" "$VERIFICATION_FILE" | awk '{print $2}')
  if [ "$VERIFICATION_STATUS" != "PASS" ]; then
    echo "⚠️  Warning: Phase ${PHASE} verification status is ${VERIFICATION_STATUS}"
    echo "   Review can proceed, but content has not passed verification checks."
    echo ""
  fi
else
  echo "⚠️  Warning: Phase ${PHASE} has not been verified."
  echo "   Review can proceed, but consider running /doc:verify-phase ${PHASE} first."
  echo ""
fi
```

### 1.4 Display Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > REVIEWING PHASE {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} BEOORDELEN`

---

## Step 2: Load Phase Content

### 2.1 Discover CONTENT.md and SUMMARY.md Files

Build a list of all sections in the phase directory:

```bash
# Find all CONTENT.md files, sorted by plan number
CONTENT_FILES=$(find "$PHASE_DIR" -name "*-CONTENT.md" | sort)

# Initialize arrays
declare -a SECTION_IDS
declare -a SECTION_NAMES
declare -a CONTENT_PATHS
declare -a SUMMARY_PATHS
declare -a CONTENT_SIZES

SECTION_INDEX=0
for CONTENT_FILE in $CONTENT_FILES; do
  # Extract section ID (e.g., "03-01" from "03-01-CONTENT.md")
  BASENAME=$(basename "$CONTENT_FILE")
  SECTION_ID=$(echo "$BASENAME" | sed 's/-CONTENT.md$//')

  # Find corresponding SUMMARY.md
  SUMMARY_FILE=$(echo "$CONTENT_FILE" | sed 's/-CONTENT.md$/-SUMMARY.md/')

  # Extract section name from SUMMARY.md title (if exists)
  if [ -f "$SUMMARY_FILE" ]; then
    SECTION_NAME=$(grep "^# " "$SUMMARY_FILE" | head -1 | sed 's/^# //')
  else
    SECTION_NAME="(No summary)"
  fi

  # Get content file size (line count)
  CONTENT_SIZE=$(wc -l < "$CONTENT_FILE")

  # Store in arrays
  SECTION_IDS[$SECTION_INDEX]="$SECTION_ID"
  SECTION_NAMES[$SECTION_INDEX]="$SECTION_NAME"
  CONTENT_PATHS[$SECTION_INDEX]="$CONTENT_FILE"
  SUMMARY_PATHS[$SECTION_INDEX]="$SUMMARY_FILE"
  CONTENT_SIZES[$SECTION_INDEX]="$CONTENT_SIZE"

  SECTION_INDEX=$((SECTION_INDEX + 1))
done

TOTAL_SECTIONS=${#SECTION_IDS[@]}
```

### 2.2 Load Cross-References

If `CROSS-REFS.md` exists, load cross-references for each section:

```bash
CROSS_REFS_FILE="${PHASE_DIR}/CROSS-REFS.md"
if [ -f "$CROSS_REFS_FILE" ]; then
  CROSS_REFS_AVAILABLE=true
else
  CROSS_REFS_AVAILABLE=false
fi
```

### 2.3 Display Overview

```
Review: {section_count} sections in Phase {N}: {Phase Name}
Type: Engineer handover / Client walkthrough
```

Example:
```
Review: 5 sections in Phase 3: Equipment Modules
Type: Engineer handover
```

---

## Step 3: Check for Resume State

### 3.1 Check for Existing REVIEW.md

```bash
REVIEW_FILE="${PHASE_DIR}/REVIEW.md"
REVIEW_EXISTS=false
if [ -f "$REVIEW_FILE" ]; then
  REVIEW_EXISTS=true
fi
```

### 3.2 Resume Logic

**If --resume flag provided OR REVIEW.md exists without --resume flag:**

**Case A: --resume flag provided**
```bash
if [ "$RESUME" = true ]; then
  if [ "$REVIEW_EXISTS" = true ]; then
    # Parse Review Progress section to find last reviewed section
    LAST_REVIEWED=$(grep "^Next section:" "$REVIEW_FILE" | sed 's/Next section: //' | awk '{print $1}')

    if [ -n "$LAST_REVIEWED" ]; then
      # Find index of next section to review
      for i in "${!SECTION_IDS[@]}"; do
        if [ "${SECTION_IDS[$i]}" = "$LAST_REVIEWED" ]; then
          START_INDEX=$i
          break
        fi
      done

      # Count how many already reviewed
      REVIEWED_COUNT=$START_INDEX

      echo "Resuming review from section ${LAST_REVIEWED} (${REVIEWED_COUNT}/${TOTAL_SECTIONS} already reviewed)"
      echo ""
    else
      echo "⚠️  Warning: Could not parse resume position from REVIEW.md. Starting from beginning."
      START_INDEX=0
      REVIEWED_COUNT=0
    fi
  else
    echo "⚠️  Warning: --resume flag provided but no REVIEW.md found. Starting from beginning."
    START_INDEX=0
    REVIEWED_COUNT=0
  fi
fi
```

**Case B: REVIEW.md exists but no --resume flag**

Use AskUserQuestion:
- header: "Previous Review Found"
- question: "Phase {N} already has a REVIEW.md. What do you want to do?"
- options:
  - "Resume from last position" -- continue where you left off
  - "Start fresh" -- clear existing review and start over
  - "View existing" -- show current review content, then choose

If "Resume": same logic as Case A
If "Start fresh": initialize new REVIEW.md from template
If "View existing": display REVIEW.md, then offer resume/fresh choice

**Case C: No REVIEW.md**

Initialize from template:

```bash
cp ~/.claude/gsd-docs-industrial/templates/review.md "$REVIEW_FILE"

# Replace placeholders
sed -i "s/{N}/${PHASE}/g" "$REVIEW_FILE"
sed -i "s/{Phase Name}/${PHASE_NAME}/g" "$REVIEW_FILE"
sed -i "s/{YYYY-MM-DD}/$(date +%Y-%m-%d)/g" "$REVIEW_FILE"
# {Name or role} and {Type} will be asked or set to defaults

START_INDEX=0
REVIEWED_COUNT=0
```

If no existing review: set `START_INDEX=0` and `REVIEWED_COUNT=0`.

---

## Step 4: Interactive Section-by-Section Review

For each section (starting from `START_INDEX`):

### 4.1 Display Section Header

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Section {current}/{total}: {section_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Example:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Section 3/5: EM-300 Vulunit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 Display SUMMARY.md Content

Read and display the SUMMARY.md for this section. Show all 4 mandatory sections:
- Facts
- Key Decisions
- Dependencies
- Cross-refs

```
## SUMMARY

{Full SUMMARY.md content displayed here}
```

### 4.3 Display Cross-References

If CROSS-REFS.md exists, extract cross-references where this section is source or target:

```bash
SECTION_ID="${SECTION_IDS[$CURRENT_INDEX]}"

if [ "$CROSS_REFS_AVAILABLE" = true ]; then
  # Extract cross-refs for this section
  DEPENDS_ON=$(grep "^| ${SECTION_ID} |" "$CROSS_REFS_FILE" | grep "depends-on" | awk -F'|' '{print $3}' | xargs)
  REFERENCED_BY=$(grep "| ${SECTION_ID}$" "$CROSS_REFS_FILE" | awk -F'|' '{print $2}' | xargs)
  RELATED_TO=$(grep "^| ${SECTION_ID} |" "$CROSS_REFS_FILE" | grep "related-to" | awk -F'|' '{print $3}' | xargs)

  if [ -n "$DEPENDS_ON" ] || [ -n "$REFERENCED_BY" ] || [ -n "$RELATED_TO" ]; then
    echo ""
    echo "## CROSS-REFERENCES"
    echo ""
    [ -n "$DEPENDS_ON" ] && echo "Depends on: ${DEPENDS_ON}"
    [ -n "$REFERENCED_BY" ] && echo "Referenced by: ${REFERENCED_BY}"
    [ -n "$RELATED_TO" ] && echo "Related to: ${RELATED_TO}"
    echo ""
  fi
fi
```

### 4.4 Display CONTENT.md (Paginated)

Read the CONTENT.md file size:

```bash
CONTENT_SIZE="${CONTENT_SIZES[$CURRENT_INDEX]}"

if [ "$CONTENT_SIZE" -lt 60 ]; then
  # Show full content
  echo "## CONTENT"
  echo ""
  cat "${CONTENT_PATHS[$CURRENT_INDEX]}"
  echo ""
  FULL_CONTENT_SHOWN=true
else
  # Show first 40 lines + truncation notice
  echo "## CONTENT (first 40 lines of ${CONTENT_SIZE} total)"
  echo ""
  head -40 "${CONTENT_PATHS[$CURRENT_INDEX]}"
  echo ""
  echo "... (${CONTENT_SIZE} lines total)"
  echo ""
  FULL_CONTENT_SHOWN=false
fi
```

### 4.5 Collect Feedback via AskUserQuestion

Use AskUserQuestion:
- header: "Section {current}/{total}: {section_name}"
- question: "Review status?"
- options:
  - "Approved (no issues)"
  - "Comment (minor note)"
  - "Flag (needs revision)"
  - "View full content" (only if `FULL_CONTENT_SHOWN=false`)
  - "Skip to next"

### 4.6 Handle Response

**Response: "Approved"**

Record in REVIEW.md feedback table:
```markdown
| {section_id} | Approved | - | - |
```

Update summary counts (increment approved_count).

Display: "✓ Section approved"

Continue to next section (4.8).

---

**Response: "Comment"**

Follow up with inline conversation to collect comment text:

```
Please enter your comment for section {section_name}:
(Minor note, observation, or suggestion that doesn't require revision)
```

Capture comment text from user.

Record in REVIEW.md feedback table:
```markdown
| {section_id} | Comment | {comment_text} | - |
```

Update summary counts (increment comment_count).

Display: "📝 Comment logged"

Continue to next section (4.8).

---

**Response: "Flag"**

Follow up with structured collection:

**1. Issue description (inline conversation):**
```
Please describe the issue with section {section_name}:
(What needs revision? What is incorrect, unclear, or missing?)
```

Capture issue description.

**2. Severity selection (AskUserQuestion):**
- header: "Issue Severity"
- question: "How critical is this issue?"
- options:
  - "High (blocks approval)" -- Must be fixed before client delivery
  - "Medium (should fix)" -- Should be addressed but not blocking
  - "Low (nice to have)" -- Minor improvement, optional

Capture severity level.

**3. Suggested action (inline conversation, optional):**
```
Suggested action to resolve this issue? (optional)
(Leave blank if unclear, or provide specific fix recommendation)
```

Capture suggested action (may be empty).

**4. Record in REVIEW.md:**

Feedback table entry:
```markdown
| {section_id} | Flag | {issue_brief} | {suggested_action or "-"} |
```

Detailed flagged issues section:
```markdown
### {section_id} {section_name}: {issue_title}
**Severity:** {High/Medium/Low}
**Finding:** {issue_description}
**Context:** Section {section_id} in {CONTENT_filename}
**Suggested Action:** {suggested_action or "None provided"}
**Routed to gaps:** No
```

Update summary counts (increment flag_count).

Display: "🚩 Issue flagged ({severity})"

Continue to next section (4.8).

---

**Response: "View full content"**

Display full CONTENT.md:

```bash
echo "## FULL CONTENT"
echo ""
cat "${CONTENT_PATHS[$CURRENT_INDEX]}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
```

Return to feedback selection (re-present AskUserQuestion from 4.5, but without "View full content" option this time).

---

**Response: "Skip to next"**

Do not record anything in REVIEW.md for this section.

Display: "⏭️  Skipped"

Continue to next section (4.8).

---

### 4.7 Review Fatigue Check

After every 10 sections reviewed, if more sections remain:

```bash
CURRENT_SECTION_NUMBER=$((CURRENT_INDEX + 1))
if [ $((CURRENT_SECTION_NUMBER % 10)) -eq 0 ] && [ $CURRENT_SECTION_NUMBER -lt $TOTAL_SECTIONS ]; then
  # Fatigue check
  Use AskUserQuestion:
    header: "Review Progress"
    question: "You have reviewed ${CURRENT_SECTION_NUMBER} of ${TOTAL_SECTIONS} sections. Continue?"
    options:
      - "Continue reviewing"
      - "Save progress and stop"
fi
```

**If "Save progress and stop":**

Update REVIEW.md "Review Progress" section:
```markdown
**Sections reviewed:** {current} of {total}
**Next section:** {next_section_id} {next_section_name}
**Status:** In Progress

To resume: /doc:review-phase {N} --resume
```

Write REVIEW.md to disk.

Display:
```
Review paused at section {current}/{total}.
Progress saved to REVIEW.md.

To resume: /doc:review-phase {N} --resume
```

Exit workflow (go to Step 6 with partial results).

---

### 4.8 Update REVIEW.md After Each Section

After processing each section, update the REVIEW.md file:

1. Update summary counts table (increment approved/comment/flag counts)
2. Append feedback table row (if not skipped)
3. Append detailed flagged issue section (if flagged)
4. Update "Review Progress" section:
   ```markdown
   **Sections reviewed:** {current} of {total}
   **Next section:** {next_section_id} {next_section_name}
   **Status:** {In Progress / Complete}
   ```

Write updated REVIEW.md to disk.

Increment `CURRENT_INDEX` and continue to next section.

---

## Step 5: Route to Gap Closure (Optional)

After all sections reviewed (or partial review stopped):

### 5.1 Count Flagged Issues

```bash
FLAG_COUNT=$(grep "| .* | Flag |" "$REVIEW_FILE" | wc -l)
```

### 5.2 If --route-gaps Flag AND Flagged Issues Exist

**5.2.1 Display preview of all flagged issues:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 REVIEW COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{flag_count} issues flagged.

Flagged issues:
```

Extract and display each flagged issue:

```bash
# Parse flagged issues from "Flagged Issues (Detail)" section
# Format: {number}. [{severity}] {section}: {brief description}

FLAGGED_SECTIONS=$(grep "^### " "$REVIEW_FILE" | grep -v "^### {" | sed 's/^### //')

ISSUE_NUMBER=1
for FLAGGED in $FLAGGED_SECTIONS; do
  # Extract section ID and name
  SECTION_ID=$(echo "$FLAGGED" | awk '{print $1}')
  ISSUE_TITLE=$(echo "$FLAGGED" | cut -d':' -f2-)

  # Extract severity from detailed section
  SEVERITY=$(grep -A1 "^### ${FLAGGED}" "$REVIEW_FILE" | grep "Severity:" | awk '{print $2}')

  echo "${ISSUE_NUMBER}. [${SEVERITY}] ${SECTION_ID}:${ISSUE_TITLE}"
  ISSUE_NUMBER=$((ISSUE_NUMBER + 1))
done
echo ""
```

**5.2.2 Ask confirmation via AskUserQuestion:**

Use AskUserQuestion:
- header: "Route to Gap Closure"
- question: "Generate fix plans for these issues?"
- options:
  - "All flagged issues" -- Route all issues to gap closure pipeline
  - "Select specific issues" -- Choose which issues to route
  - "Skip -- resolve manually" -- No automatic routing, manual resolution

**5.2.3 Handle routing selection:**

**If "All flagged issues":**

Display:
```
Routing all {flag_count} flagged issues to gap closure pipeline...

Next steps:
1. /doc:plan-phase {N} --gaps --source review
   (Generates fix plans for flagged issues)

2. /doc:write-phase {N}
   (Executes fix plans)

3. /doc:verify-phase {N}
   (Re-verifies fixed content)
```

Update REVIEW.md flagged issues: set "Routed to gaps: Yes" for all flagged entries.

**If "Select specific issues":**

Present numbered list via AskUserQuestion (multiSelect: true):
- header: "Select Issues to Route"
- question: "Which issues should be routed to gap closure?"
- options: List of flagged issues (numbered), each formatted as:
  - "[{severity}] {section}: {brief description}"

Capture selected issues.

Display:
```
Routing {selected_count} of {flag_count} flagged issues to gap closure pipeline...

Next steps:
1. /doc:plan-phase {N} --gaps --source review
   (Generates fix plans for selected issues)

2. /doc:write-phase {N}
   (Executes fix plans)

3. /doc:verify-phase {N}
   (Re-verifies fixed content)
```

Update REVIEW.md: set "Routed to gaps: Yes" only for selected issues.

**If "Skip -- resolve manually":**

Display:
```
{flag_count} issues flagged for manual resolution.
Review feedback captured in REVIEW.md.

Engineer should address flagged issues and update sections as needed.
```

No routing action taken.

---

### 5.3 If No --route-gaps Flag AND Flagged Issues Exist

Display:
```
{flag_count} issues flagged.

Resolve manually or re-run with --route-gaps to generate fix plans:

  /doc:review-phase {N} --route-gaps

Review feedback: {REVIEW.md path}
```

---

### 5.4 If No Flagged Issues

Display:
```
All sections approved or have minor comments only.
No issues flagged for revision.
```

---

## Step 6: Review Summary and Completion

### 6.1 Display Completion Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PHASE {N} REVIEWED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Dutch (if `LANGUAGE = "nl"`): `DOC > FASE {N} BEOORDEELD`

### 6.2 Display Summary

Read final counts from REVIEW.md summary table:

```bash
APPROVED_COUNT=$(grep "| Approved |" "$REVIEW_FILE" | wc -l)
COMMENT_COUNT=$(grep "| Comment |" "$REVIEW_FILE" | wc -l)
FLAG_COUNT=$(grep "| Flag |" "$REVIEW_FILE" | wc -l)
REVIEWED_COUNT=$((APPROVED_COUNT + COMMENT_COUNT + FLAG_COUNT))
SKIPPED_COUNT=$((TOTAL_SECTIONS - REVIEWED_COUNT))
```

Display:
```
Sections reviewed: {reviewed_count}
  Approved: {approved_count}
  Comments: {comment_count}
  Flagged: {flag_count}
  Skipped: {skipped_count}

Feedback: {REVIEW.md relative path}
```

### 6.3 If Partial Review (Stopped Early)

```
Review Progress: {reviewed}/{total} sections
Resume: /doc:review-phase {N} --resume
```

### 6.4 Git Commit

Commit the REVIEW.md file:

```bash
git add "$REVIEW_FILE"
git commit -m "docs(${PADDED_PHASE}): phase ${PHASE} review feedback

Sections reviewed: ${REVIEWED_COUNT}/${TOTAL_SECTIONS}
- Approved: ${APPROVED_COUNT}
- Comments: ${COMMENT_COUNT}
- Flagged: ${FLAG_COUNT}
"
```

### 6.5 Next Up Block

Read ROADMAP.md to find next phase:

```bash
NEXT_PHASE=$((PHASE + 1))
NEXT_PHASE_PADDED=$(printf "%02d" ${NEXT_PHASE})
NEXT_PHASE_ENTRY=$(grep "^## Phase ${NEXT_PHASE}:" .planning/ROADMAP.md | head -1)
if [ -n "$NEXT_PHASE_ENTRY" ]; then
  NEXT_PHASE_NAME=$(echo "$NEXT_PHASE_ENTRY" | sed 's/^## Phase [0-9]*: //')
  NEXT_PHASE_GOAL=$(grep -A1 "^## Phase ${NEXT_PHASE}:" .planning/ROADMAP.md | tail -1)
fi
```

Display:
```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase {N+1}: {Next Phase Name}** -- {goal}

`/doc:discuss-phase {N+1}`

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:verify-phase {N} --perspective engineer` -- Fresh Eyes review
- `/doc:review-phase {N} --resume` -- continue review (if partial)
- `/doc:status` -- view overall progress

───────────────────────────────────────────────────────────────
```

If no next phase exists (final phase):
```
───────────────────────────────────────────────────────────────

## > Next Up

**Final phase complete!**

Run `/doc:status` to view project completion status.

───────────────────────────────────────────────────────────────
```

---

## Workflow Rules

1. **Language consistency:** All user-facing text matches project language (from PROJECT.md). Internal variable names remain English.

2. **DOC > prefix:** All banners use the `DOC >` namespace prefix.

3. **Interactive mode:** AskUserQuestion for selections (topic selection, confirmation, severity levels). Inline conversation for free-text feedback (issue descriptions, comments, suggested actions).

4. **REVIEW.md is per-phase:** In phase directory (`.planning/phases/{NN}-{name}/REVIEW.md`), not project-wide.

5. **Review does not change verification status:** Review is supplementary to verify-phase. Both can exist independently. Review captures human judgment, verify-phase performs automated checks.

6. **Partial review support:** Engineer can stop and resume at any point. "Review Progress" section tracks position. `--resume` flag continues from last section.

7. **Fatigue check:** After every 10 sections, offer pause option to avoid review fatigue (Pitfall 4 mitigation).

8. **Gap closure routing:** Optional via `--route-gaps` flag. Always preview flagged issues before routing (Pitfall 5 mitigation). Engineer can select which issues to route or skip routing entirely.

9. **Unverified content allowed:** Review can happen before or after verify-phase. Warn if content is unverified but allow review to proceed.

10. **Section presentation order:** Sorted by plan number (natural order). All sections presented sequentially.

11. **Paginated content:** If CONTENT.md > 60 lines, show first 40 lines with "View full content" option.

12. **SUMMARY.md context:** Always shown before CONTENT.md to provide context (Facts, Key Decisions, Dependencies, Cross-refs).

13. **Cross-references:** Extracted from CROSS-REFS.md where section is source or target. Shows depends-on, referenced-by, related-to relationships.

14. **Skip option:** Engineer can skip sections without recording feedback. Useful for sections already reviewed in a previous session or not relevant to current review focus.

15. **Feedback structure:** Feedback table for quick scan (section, status, brief finding, suggested action). Detailed flagged issues section for full context (severity, finding, context, suggested action, routing status).

16. **Multi-session consistency:** REVIEW.md updated incrementally after each section. Engineer can exit and resume without losing progress.

17. **No emoji in text:** Only use status symbols defined in ui-brand.md (✓, 📝, 🚩, ⏭️, ⚠️).

18. **Error handling:** Show error box and stop if ROADMAP.md missing, phase not found, or no content files exist.

</workflow>
