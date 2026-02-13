<workflow>

# ROADMAP Expansion Workflow

**Purpose:** Detect project complexity exceeding initial ROADMAP estimates and propose decimal-numbered phase insertions to break down large scopes into manageable chunks.

**Entry points:**
1. Manual: `/doc:expand-roadmap [after-phase]`
2. Auto-trigger: Called from verify-phase after System Overview PASS with >5 units

**Outputs:**
- ROADMAP.md updated with decimal phases (4.1, 4.2, etc.)
- Phase directories created: `.planning/phases/{NN}.{M}-{slug}/`
- STATE.md updated with expansion decision

---

## Step 1: Detect Units and Determine Insertion Point

### 1a. Determine Entry Mode

Check if this is a manual invocation or auto-trigger:

**Manual invocation:** `/doc:expand-roadmap [after-phase]`
- If `after-phase` argument provided: use that phase number
- If NOT provided: scan ROADMAP.md for the first phase with status "Written" or "Verified" that mentions "System Overview" OR "equipment" OR "unit identification" in its goal

**Auto-trigger:** Called from verify-phase
- Unit list and count provided in context
- Phase number to insert after provided
- Skip directly to Step 2 (unit detection already done)

### 1b. Manual Mode: Extract Phase Number and Directory

If manual invocation without argument:

```bash
# Find System Overview phase in ROADMAP.md
grep -A 5 "^## Phase" .planning/ROADMAP.md | grep -i "system overview\|equipment.*identif"
```

Extract phase number from matched line (e.g., "## Phase 4: System Overview" → 4).

Set `AFTER_PHASE` variable.

### 1c. Locate Phase Directory

```bash
# Find phase directory
ls -d .planning/phases/${AFTER_PHASE}-*/ 2>/dev/null
```

Set `PHASE_DIR` variable.

If directory not found:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > ROADMAP EXPANSION ERROR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase {AFTER_PHASE} directory not found.

Expansion requires a verified System Overview phase with documented units.
```
STOP execution.

### 1d. Extract Units from Phase Content

For manual mode only (auto-trigger skips this):

Read all CONTENT.md and SUMMARY.md files in the phase directory:

```bash
cat ${PHASE_DIR}/*-CONTENT.md 2>/dev/null
cat ${PHASE_DIR}/*-SUMMARY.md 2>/dev/null
```

Parse for equipment module identifiers:
- **Pattern 1:** Equipment Module references: `EM-NNN`, `Equipment Module NNN`
- **Pattern 2:** Unit headings: `## Equipment Unit: [Name]`, `### Unit: [Name]`
- **Pattern 3:** Explicit unit declarations: `Unit ID:`, `Unit Name:`
- **Pattern 4:** Equipment lists in tables or bullet points

Build unit list:
```
units = [
  { id: "EM-001", name: "Mixing Tank MT-101", description: "..." },
  { id: "EM-002", name: "Pump P-201", description: "..." },
  ...
]
```

Count total unique units identified.

### 1e. Threshold Check

If `unit_count <= 5`:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > ROADMAP EXPANSION CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{unit_count} units identified (threshold: >5)

No expansion needed. Current ROADMAP phases can accommodate this scope.
```

STOP execution.

If `unit_count > 5`: proceed to Step 2.

---

## Step 2: Propose Phase Groupings

### 2a. Determine Grouping Strategy

**Available strategies** (Claude's discretion based on unit characteristics):

1. **Process area:** Group units by function (mixing, filling, transport, packaging, CIP, utility)
2. **Dependency:** Group units that reference each other (upstream/downstream relationships)
3. **Complexity:** Balance phases by estimated documentation effort (simple vs complex units)
4. **Mixed:** Combine strategies as appropriate for the project

**Locked constraints:**
- 3-5 units per phase group
- Maximum 7 new phases total
- Each unit must appear in exactly one group

### 2b. Generate Grouping Proposal

Analyze unit list and apply chosen strategy. Generate groups:

```
groups = [
  {
    number: "{AFTER_PHASE}.1",
    name: "Mixing Equipment",
    units: ["EM-001: Mixing Tank MT-101", "EM-002: Agitator AG-101", "EM-003: Dosing Pump DP-101"],
    rationale: "Grouped by process function: mixing operations"
  },
  {
    number: "{AFTER_PHASE}.2",
    name: "Transfer and Storage",
    units: ["EM-004: Transfer Pump P-201", "EM-005: Buffer Tank BT-201", "EM-006: Level Transmitter LT-201"],
    rationale: "Grouped by dependency: transfer system components"
  },
  ...
]
```

Ensure:
- Total groups <= 7
- Each group has 3-5 units
- All units assigned to exactly one group

### 2c. Display Overview

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > ROADMAP EXPANSION PROPOSAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Overview identified {unit_count} units (threshold: 5)
Proposing {group_count} new phases:

  Phase {AFTER_PHASE}.1: {name} ({unit_count} units)
  Phase {AFTER_PHASE}.2: {name} ({unit_count} units)
  Phase {AFTER_PHASE}.3: {name} ({unit_count} units)
  ...

Grouping strategy: {strategy name}
```

---

## Step 3: Interactive Approval Loop

### 3a. Loop Through Groups

For each proposed group (one at a time):

Display:
```
───────────────────────────────────────────────────────────────
Proposed Phase {number}: {name}

  Units ({count}):
  - {unit 1}
  - {unit 2}
  - {unit 3}
  ...

  Rationale: {rationale}

  Options:
  1. Approve (use as-is)
  2. Modify (change name or units)
  3. Skip (merge units into next group)
───────────────────────────────────────────────────────────────
```

**Use AskUserQuestion** for each group.

### 3b. Process User Response

**Option 1: Approve**
- Add group to `approved_groups` list as-is
- Continue to next group

**Option 2: Modify**
- Ask for new name (default: current name):
  ```
  Enter phase name (or press Enter to keep "{current_name}"):
  ```
- Ask for units (default: current units):
  ```
  Enter unit list (comma-separated, or press Enter to keep current):

  Current: {unit_1}, {unit_2}, {unit_3}
  ```
- Parse comma-separated list, trim whitespace
- Add modified group to `approved_groups` list
- Continue to next group

**Option 3: Skip**
- Move this group's units into the NEXT group's unit list
- If this is the LAST group:
  ```
  Warning: These units have no group to merge into.

  Add them to the previous group instead? (Y/n)
  ```
  - If Y: append to last approved group
  - If n: warn "Units orphaned. Please re-run expansion with different grouping."
- Continue to next group

### 3c. Handle Edge Cases

**All groups skipped:**
```
No phases approved for expansion. ROADMAP unchanged.

You can re-run /doc:expand-roadmap with manual grouping later.
```
STOP execution.

**Units orphaned after modifications:**
- Collect all units that were in original groups but not in approved groups
- Display warning:
  ```
  Warning: {count} units not assigned to any group:
  - {unit 1}
  - {unit 2}

  Add to final group? (Y/n)
  ```

### 3d. Re-number Approved Groups

After approval loop completes, renumber groups sequentially:

```
approved_groups[0].number = "{AFTER_PHASE}.1"
approved_groups[1].number = "{AFTER_PHASE}.2"
approved_groups[2].number = "{AFTER_PHASE}.3"
...
```

---

## Step 4: Final Confirmation

Display expansion summary:

```
───────────────────────────────────────────────────────────────
EXPANSION SUMMARY

Phase {AFTER_PHASE}.1: {name} ({unit_count} units)
Phase {AFTER_PHASE}.2: {name} ({unit_count} units)
Phase {AFTER_PHASE}.3: {name} ({unit_count} units)

Total: {total_units} units across {phase_count} phases

Proceed with ROADMAP expansion? (Y/n)
───────────────────────────────────────────────────────────────
```

**If n (rejected):**
```
ROADMAP unchanged. You can re-run /doc:expand-roadmap later.
```
STOP execution.

**If Y (confirmed):** Proceed to Step 5.

---

## Step 5: Update ROADMAP.md

### 5a. Read Current ROADMAP

```bash
cat .planning/ROADMAP.md
```

Parse structure to locate:
- Parent phase section: `## Phase {AFTER_PHASE}: {Name}`
- End of parent phase section (next `## Phase` or `---` separator or end of file)

### 5b. Generate Decimal Phase Sections

For each approved group, generate phase section:

```markdown
## Phase {AFTER_PHASE}.{M}: {Phase Name}

**Goal:** Document equipment modules {unit list} with complete state machines, I/O specifications, and interlock definitions.

**Dependencies:** Phase {AFTER_PHASE} (System Overview must be verified)

**Requirements:** (Inherited from parent phase)

**Plans:** TBD (will be generated by /doc:plan-phase)

**Success Criteria:**

1. All {unit_count} equipment modules in this phase have complete CONTENT.md with substantive documentation
2. All I/O tables, state machines, and interlock definitions are populated (not stubs)
3. Cross-references between units within and across phases are logged in CROSS-REFS.md
4. Verification PASS on all must-have truths derived from phase goal

**Units in this phase:**
- {unit 1}
- {unit 2}
- {unit 3}
```

### 5c. Insert Sections into ROADMAP

Locate insertion point: immediately after parent phase section (before next `## Phase` or `---`).

Insert all decimal phase sections in order (.1, .2, .3, ...).

### 5d. Update Progress Table

Locate Progress table at end of ROADMAP.md:

```markdown
| Phase | Name | Requirements | Status |
|-------|------|:------------:|--------|
```

Insert new rows after parent phase:

```markdown
| {AFTER_PHASE}.1 | {name} | - | Pending |
| {AFTER_PHASE}.2 | {name} | - | Pending |
| {AFTER_PHASE}.3 | {name} | - | Pending |
```

### 5e. Update Phase Count in Header

Locate ROADMAP header: `**Phases:** N`

Increment count by number of new phases: `**Phases:** {N + phase_count}`

### 5f. Write Updated ROADMAP

```bash
# Backup original
cp .planning/ROADMAP.md .planning/ROADMAP.md.bak

# Write updated version
cat > .planning/ROADMAP.md <<'EOF'
{updated_content}
EOF
```

---

## Step 6: Create Phase Directories

For each approved group:

### 6a. Generate Directory Name

Convert phase name to kebab-case slug:
- Lowercase
- Replace spaces with hyphens
- Remove special characters (keep alphanumeric and hyphens)

Example: "Mixing Equipment" → "mixing-equipment"

### 6b. Create Directory

```bash
mkdir -p ".planning/phases/{AFTER_PHASE}.{M}-{slug}/"
```

Example: `.planning/phases/4.1-mixing-equipment/`

### 6c. Verify Creation

```bash
ls -d .planning/phases/{AFTER_PHASE}.*-*/
```

Collect created directories for final display.

---

## Step 7: Update STATE.md

### 7a. Read Current STATE.md

```bash
cat .planning/STATE.md
```

### 7b. Add Expansion Event to Decisions Section

Locate `## Decisions` section.

Append new decision with timestamp:

```markdown
- ROADMAP expanded: {phase_count} decimal phases added after Phase {AFTER_PHASE} ({timestamp})
```

Timestamp format: `YYYY-MM-DD`

Example:
```markdown
- ROADMAP expanded: 3 decimal phases added after Phase 4 (2026-02-13)
```

### 7c. Update Progress Table (if exists)

If STATE.md has a Progress table, add new rows for decimal phases:

```markdown
| {AFTER_PHASE}.1 | {name} | -/- | Pending |
| {AFTER_PHASE}.2 | {name} | -/- | Pending |
| {AFTER_PHASE}.3 | {name} | -/- | Pending |
```

### 7d. Write Updated STATE.md

```bash
cat > .planning/STATE.md <<'EOF'
{updated_content}
EOF
```

---

## Step 8: Completion

### 8a. Display Success Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > ROADMAP EXPANDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{phase_count} phases added to ROADMAP.md

Phase directories created:
- .planning/phases/{AFTER_PHASE}.1-{slug}/
- .planning/phases/{AFTER_PHASE}.2-{slug}/
- .planning/phases/{AFTER_PHASE}.3-{slug}/
...

Total units distributed: {total_units} across {phase_count} phases
```

### 8b. Show Next Steps

```
───────────────────────────────────────────────────────────────

Next: Discuss first expansion phase

  /doc:discuss-phase {AFTER_PHASE}.1

───────────────────────────────────────────────────────────────
```

---

## Workflow Rules

**Decimal numbering:**
- Preserves existing phase numbers (locked decision)
- Format: `{parent_phase}.{sequence}` (e.g., 4.1, 4.2, 4.3)
- Sequential numbering starting at .1

**Grouping constraints:**
- 3-5 units per group (locked)
- Maximum 7 groups total (locked)
- Grouping strategy: Claude's discretion

**Interactive approval:**
- One group at a time (locked decision)
- Options: approve / modify / skip
- Final confirmation before ROADMAP modification

**Phase directory naming:**
- Pattern: `{NN}.{M}-{slug}` (e.g., `4.1-mixing-equipment`)
- Slug is kebab-case of phase name
- Created empty (ready for discuss/plan/write/verify)

**UI branding:**
- All banners use `DOC >` prefix (never `GSD >`)
- Success banners: `━` characters (full width)
- Section separators: `─` characters
- Consistent spacing and alignment

**State management:**
- Expansion event logged in STATE.md Decisions
- Progress tables updated in both ROADMAP.md and STATE.md
- Backup created before ROADMAP modification

**Error handling:**
- Phase directory not found: clear error, suggest prerequisites
- No units detected: threshold check prevents unnecessary expansion
- All groups skipped: preserve original ROADMAP, allow retry
- Units orphaned: prompt to assign to existing groups

</workflow>
