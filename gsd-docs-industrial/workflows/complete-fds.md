<workflow>

# Complete-FDS Workflow: Assembly Pipeline

This workflow orchestrates the full FDS document assembly process, transforming all verified phase outputs into a single, numbered, versioned document with resolved cross-references, standards compliance checks, orphan detection, and source archiving.

**Core innovation:** Template-driven section ordering, not ROADMAP phase order. Phase content is reordered to match canonical FDS structure, with dynamic equipment module expansion and type-conditional sections.

**Target:** ~700-900 lines (most complex workflow in the project)
**Pattern:** Pre-flight verification → content discovery → reordering → numbering → cross-reference resolution → standards checks → front matter generation → assembly → reporting → archiving

---

## Step 1: Pre-flight Verification

Verify all phases have PASS status before assembly proceeds. Block if any phase lacks verification.

**Parse arguments:**
```bash
FORCE_MODE=false
if [[ "$ARGUMENTS" == *"--force"* ]]; then
  FORCE_MODE=true
fi
```

**Display banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > FDS ASSEMBLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Read STATE.md and ROADMAP.md:**
```bash
cat .planning/STATE.md
cat .planning/ROADMAP.md
```

**Extract all phases from ROADMAP.md:**
Parse lines starting with `## Phase N:` to build list of all phases in the project.

**For each phase, check verification status:**
```bash
PHASE_DIR=$(find .planning/phases -type d -name "${PHASE}-*" | head -1)
VERIFICATION_FILE="${PHASE_DIR}/${PHASE}-VERIFICATION.md"
```

Check if VERIFICATION.md exists and contains `Status: PASS`.

**If any phase does NOT have PASS status:**

Without --force flag:
```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Cannot assemble FDS: the following phases are not verified:

- Phase 2: Discuss + Plan Commands
- Phase 5: Complete-FDS + Standards

**To fix:** Run /doc:verify-phase N for each unverified phase.

Alternatively, use --force flag to generate a DRAFT version with
unverified content (not recommended for client delivery).
```

Exit with error (assembly blocked).

With --force flag:
Display warning but continue:
```
⚠ WARNING: Assembling FDS with unverified phases

The following phases have not passed verification:
- Phase 2
- Phase 5

Generated document will be marked as DRAFT.
```

**Command conflict check (same pattern as verify-phase Step 1a):**

Read STATE.md Current Operation section:
- If `status: IN_PROGRESS` and `command:` is NOT `complete-fds`
- Display warning: "Another command ({command}) is currently in progress. Continue with assembly?"
- Ask for confirmation (Y/n)
- If no: exit cleanly

**ASBL-01 compliance:** ✓ Verifies all phases PASS before assembly proceeds (or --force overrides)

---

## Step 2: Load Project Configuration

Read project metadata, FDS structure template, front matter templates, and version information.

**Read PROJECT.md:**
```bash
cat .planning/PROJECT.md
```

**Extract configuration:**
- `project_name:` (string)
- `client:` (string)
- `language:` (en or nl)
- `type:` (A, B, C, or D)
- `standards.packml.enabled:` (boolean, default false)
- `standards.isa88.enabled:` (boolean, default false)

**Read fds-structure.json:**
```bash
cat ~/.claude/gsd-docs-industrial/templates/fds-structure.json
```

Parse JSON to extract:
- Canonical section ordering (sections array with hierarchical IDs)
- Section titles (bilingual: en/nl)
- Source type mappings (how ROADMAP phases map to FDS sections)
- Dynamic expansion rules (equipment modules)
- Type-conditional sections (baseline for Type C/D)

Store as structured data for Step 4 ordering logic.

**Read front matter templates:**
```bash
cat ~/.claude/gsd-docs-industrial/templates/frontmatter/title-page.md
cat ~/.claude/gsd-docs-industrial/templates/frontmatter/revision-history.md
cat ~/.claude/gsd-docs-industrial/templates/frontmatter/abbreviations.md
```

Store template content for Step 9 front matter generation.

**Determine output version from STATE.md:**

Read STATE.md Versions section (or similar version tracking):
```yaml
## Versions

FDS: v0.1
SDS: v0.1
```

Extract FDS version string: `VERSION="0.1"`

If Versions section missing: default to `VERSION="0.1"`

**Store configuration:**
- PROJECT_NAME
- CLIENT
- LANGUAGE
- PROJECT_TYPE
- VERSION
- STANDARDS_PACKML_ENABLED
- STANDARDS_ISA88_ENABLED
- FDS_STRUCTURE (parsed JSON)
- FRONTMATTER_TEMPLATES

---

## Step 3: Discover and Collect All CONTENT.md Files

Scan all phase directories for CONTENT.md files, CROSS-REFS.md files, and COMPLIANCE.md files.

**Discover phase directories:**
```bash
PHASE_DIRS=$(find .planning/phases -mindepth 1 -maxdepth 1 -type d | sort)
```

**For each phase directory:**

1. **Find all CONTENT.md files:**
```bash
CONTENT_FILES=$(find ${PHASE_DIR} -name "*-CONTENT.md" | sort)
```

2. **For each CONTENT.md file, extract metadata:**

**Read file:**
```bash
CONTENT=$(cat ${CONTENT_FILE})
```

**Parse frontmatter (YAML between --- markers):**
- `phase:` (number)
- `plan:` (number)
- `section_type:` (e.g., "equipment-module", "system-overview", "functional-requirements")
- `title:` (section title)

**Extract heading structure:**
Scan content for markdown headings (# ## ### ####) to understand depth hierarchy.

**Store in memory:**
```
COLLECTED_CONTENT[] = {
  file_path: string,
  phase: number,
  plan: number,
  section_type: string,
  title: string,
  headings: array of {depth, text},
  content: string (full markdown)
}
```

3. **Collect CROSS-REFS.md from phase directory:**
```bash
CROSS_REFS_FILE="${PHASE_DIR}/${PHASE}-CROSS-REFS.md"
if [ -f "$CROSS_REFS_FILE" ]; then
  cat $CROSS_REFS_FILE
fi
```

Parse cross-references:
- Source section ID
- Target section ID (symbolic, like "03-02" or "EM-200")
- Reference type (depends-on, related-to, see-also)
- Context (brief description)
- Status (resolved, pending, broken)

Store as array: `CROSS_REFS[]`

4. **Collect COMPLIANCE.md files (if they exist):**
```bash
COMPLIANCE_FILE="${PHASE_DIR}/${PHASE}-COMPLIANCE.md"
if [ -f "$COMPLIANCE_FILE" ]; then
  cat $COMPLIANCE_FILE
fi
```

Store compliance results for aggregation in Step 12.

**Track collection stats:**
- Total CONTENT.md files collected
- Total phases scanned
- Total cross-references found
- Total compliance reports found

**Display progress:**
```
Discovered content:
  ○ 12 CONTENT.md files
  ○ 8 phases scanned
  ○ 34 cross-references
  ○ 2 compliance reports
```

---

## Step 4: Apply FDS Structure Template Ordering

Reorder collected content to match canonical FDS structure from fds-structure.json, NOT ROADMAP phase order.

**Core principle:** FDS structure is predefined and locked. Phase content is MAPPED and REORDERED to fit the template, not assembled in ROADMAP order.

**Per locked decision:** "Section ordering follows a predefined FDS structure template, not ROADMAP phase order"

**Mapping algorithm:**

1. **Walk through fds-structure.json sections hierarchy:**

For each section in `FDS_STRUCTURE.sections[]`:

**Match by source_type:**
Look for collected CONTENT.md with matching `section_type` field:
- `"system-overview"` → matches CONTENT.md with `section_type: "system-overview"`
- `"equipment-module"` → matches CONTENT.md with `section_type: "equipment-module"`
- `"functional-requirements"` → matches CONTENT.md with `section_type: "functional-requirements"`
- `"auto-generated"` → no CONTENT.md needed, generated in Step 9

**Match by equipment module name (for dynamic section 4.x):**

Special case: Section 4 (Equipment Modules) in fds-structure.json is DYNAMIC.

Read ROADMAP.md to discover all equipment module phases:
```bash
grep -E "^###.*EM-[0-9]+" .planning/ROADMAP.md
```

For each equipment module discovered (e.g., "EM-100 Waterbad", "EM-200 Bovenloopkraan"):
- Create a new section 4.x in the FDS structure
- Title: equipment module name
- Source: corresponding CONTENT.md for that equipment module plan
- Subsections: 5 required + 4 optional (per equipment module template pattern)

**Handle type-conditional sections:**

If `section.conditional` is present in fds-structure.json:
- Check PROJECT_TYPE
- If section.conditional == "type_c_or_d" AND PROJECT_TYPE in ["C", "D"]: include section
- Otherwise: skip section

Example: Section 1.4 "Baseline" only for Type C/D projects.

**Create placeholder stubs for unwritten sections:**

**Per locked decision:** "Unwritten sections appear as placeholder stubs with [TO BE COMPLETED] markers"

For each required section in fds-structure.json with NO matching CONTENT.md:
```markdown
## {Section Title}

[TO BE COMPLETED]

{Brief description of what this section should contain, derived from fds-structure.json}
```

2. **Build reordered content array:**

```
ORDERED_SECTIONS[] = [
  {
    fds_id: "1",
    title: "Introduction",
    content: (from matched CONTENT.md or placeholder stub),
    source_file: (if matched),
    is_placeholder: boolean
  },
  {
    fds_id: "1.1",
    title: "Purpose and Scope",
    content: ...,
    source_file: ...,
    is_placeholder: false
  },
  ...
]
```

**Ordering guarantee:** ORDERED_SECTIONS[] follows fds-structure.json hierarchy exactly, NOT ROADMAP phase order.

**Pitfall 1 mitigation:** Ordering happens HERE, BEFORE numbering in Step 5. Never number then reorder.

**Display ordering result:**
```
Section ordering applied:
  ○ 7 top-level sections
  ○ 23 subsections (including 4 equipment modules)
  ○ 5 placeholder stubs for unwritten content
  ○ 1 type-conditional section included (Type C project)
```

---

## Step 5: Apply Hierarchical Section Numbering

Walk through ordered sections and apply IEC-style numbering based on heading depth.

**Per locked decision:** "Hierarchical (IEC-style) section numbering: 1.1, 1.2, 2.1.1, etc."

**Numbering algorithm:**

Initialize counters:
```
LEVEL_1 = 0
LEVEL_2 = 0
LEVEL_3 = 0
LEVEL_4 = 0
```

**For each section in ORDERED_SECTIONS[]:**

1. **Determine heading depth from markdown:**
   - `#` heading = depth 1 (top level)
   - `##` heading = depth 2 (subsection)
   - `###` heading = depth 3 (sub-subsection)
   - `####` heading = depth 4 (sub-sub-subsection)

2. **Increment appropriate counter and reset deeper levels:**

   If depth == 1:
   ```
   LEVEL_1++
   LEVEL_2 = 0
   LEVEL_3 = 0
   LEVEL_4 = 0
   SECTION_NUMBER = "${LEVEL_1}"
   ```

   If depth == 2:
   ```
   LEVEL_2++
   LEVEL_3 = 0
   LEVEL_4 = 0
   SECTION_NUMBER = "${LEVEL_1}.${LEVEL_2}"
   ```

   If depth == 3:
   ```
   LEVEL_3++
   LEVEL_4 = 0
   SECTION_NUMBER = "${LEVEL_1}.${LEVEL_2}.${LEVEL_3}"
   ```

   If depth == 4:
   ```
   LEVEL_4++
   SECTION_NUMBER = "${LEVEL_1}.${LEVEL_2}.${LEVEL_3}.${LEVEL_4}"
   ```

3. **Prepend section number to heading text:**

   Original: `## Function Description`
   Numbered: `## 4.1.1 Function Description`

   **Pattern:** `{heading_prefix} {section_number} {original_heading_text}`

4. **Store section number mapping for cross-reference resolution:**

   Build symbol table:
   ```
   SYMBOL_TABLE = {
     "03-02": "4.1",        // Plan ID → section number
     "EM-200": "4.2",       // Equipment module name → section number
     "system-overview": "2" // Section type → section number
   }
   ```

   **Multiple mapping keys per section:**
   - Plan ID (from CONTENT.md frontmatter: phase-plan like "03-02")
   - Equipment module name (if applicable, like "EM-200")
   - Section type (generic fallback)
   - Section title (for fuzzy matching)

5. **Update ORDERED_SECTIONS[] with numbered content:**

   ```
   ORDERED_SECTIONS[i].section_number = SECTION_NUMBER
   ORDERED_SECTIONS[i].content = (updated with numbered headings)
   ```

**Pitfall 2 mitigation:** Symbol table is built AFTER numbering is finalized (Step 5 complete), before cross-reference resolution (Step 6).

**Display numbering result:**
```
Section numbering applied:
  ○ 7 top-level sections (1-7)
  ○ 23 second-level sections (e.g., 1.1, 2.1, 4.1)
  ○ 12 third-level sections (e.g., 4.1.1, 4.2.3)
  ○ 4 fourth-level sections (e.g., 4.1.2.1)
  ○ Symbol table built with 45 mappings
```

---

## Step 6: Resolve Cross-References

Scan assembled content for symbolic cross-references and resolve them to final section numbers using the symbol table from Step 5.

**Per locked decision:** "Cross-references render as plain text section numbers, not clickable links"

**Cross-reference patterns to detect:**

English patterns:
- `see NN-MM` (plan ID reference, e.g., "see 03-02")
- `see phase-N/NN-MM` (explicit phase/plan reference)
- `see Section NN-MM` (already partially formatted)
- `see EM-NNN` (equipment module reference, e.g., "see EM-200")

Dutch patterns:
- `zie NN-MM`
- `zie §NN-MM`
- `zie paragraaf NN-MM`
- `zie EM-NNN`

**Resolution algorithm:**

**For each section in ORDERED_SECTIONS[]:**

1. **Scan content for cross-reference patterns:**

Use regex to find patterns:
```regex
(see|zie)\s+(§|Section|paragraaf)?\s*([A-Z0-9-]+)
```

Extract symbolic ID: `$3` (e.g., "03-02", "EM-200")

2. **Look up in symbol table:**

```
TARGET_SECTION_NUMBER = SYMBOL_TABLE[SYMBOLIC_ID]
```

3. **If found (resolved reference):**

Replace with formatted section reference:
- English: `see Section X.Y.Z`
- Dutch: `zie Paragraaf X.Y.Z`

Example:
- Original: "see 03-02 for detailed state machine"
- Resolved: "see Section 4.1 for detailed state machine"

**Track as resolved:**
```
RESOLVED_REFS[] = {
  source_section: "2.3",
  target_section: "4.1",
  symbolic_id: "03-02",
  context: "detailed state machine",
  status: "resolved"
}
```

4. **If NOT found (broken reference):**

**Without --force flag:**
Track as broken, will block assembly in Step 7:
```
BROKEN_REFS[] = {
  source_section: "2.3",
  symbolic_id: "05-07",
  context: "advanced diagnostics",
  status: "broken",
  reason: "Target section not found in symbol table"
}
```

**With --force flag:**
Replace with [BROKEN REF] placeholder:
- Original: "see 05-07 for advanced diagnostics"
- With placeholder: "see 05-07 [BROKEN REF] for advanced diagnostics"

**Track as broken:**
Same as above, but assembly will continue with placeholder.

**Update ORDERED_SECTIONS[] with resolved content:**
```
ORDERED_SECTIONS[i].content = (updated with resolved cross-references)
```

**Detect orphan sections:**

**Per locked decision:** "Orphan handling: Claude's discretion on severity based on section type"

**Definition:** Orphan section = section that exists in the document but is NEVER referenced by any other section.

**Algorithm:**
1. Build set of ALL section numbers: `ALL_SECTIONS = {1, 1.1, 1.2, 2, 2.1, 4.1, 4.2, ...}`
2. Build set of REFERENCED section numbers from RESOLVED_REFS: `REFERENCED_SECTIONS = {4.1, 4.2, 3.2, ...}`
3. Compute orphans: `ORPHAN_SECTIONS = ALL_SECTIONS - REFERENCED_SECTIONS`

**Severity classification (Claude's discretion per CONTEXT.md):**

For each orphan section, determine severity based on section type:

- **HIGH severity:**
  - Equipment modules (section 4.x) — should always be referenced from System Overview (section 2.3)
  - Functional requirements without incoming references — likely integration issue

- **MEDIUM severity:**
  - Introduction/Safety sections — typically self-contained but should be referenced from overview
  - Control philosophy sections — may be standalone but better if integrated

- **LOW severity:**
  - Appendices (section 6.x, 7.x) — standalone by nature (signal lists, parameter tables)
  - References/Abbreviations sections — support material, not narrative content

**Store orphan data:**
```
ORPHAN_SECTIONS[] = {
  section_number: "4.3",
  section_title: "EM-300 Vulunit",
  severity: "HIGH",
  reason: "Equipment module never referenced from System Overview",
  suggested_fix: "Add reference from Section 2.3 Equipment Overview"
}
```

**Display cross-reference resolution result:**
```
Cross-reference resolution:
  ✓ 28 references resolved
  ✗ 3 broken references
  ⚠ 2 orphan sections detected (1 HIGH, 1 LOW severity)
```

---

## Step 7: Cross-reference Validation

Count broken references and orphan sections, decide whether to block assembly or continue.

**Count broken references:**
```
BROKEN_COUNT=${#BROKEN_REFS[@]}
```

**ASBL-04: Without --force flag:**

If `BROKEN_COUNT > 0`:
```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Cannot assemble FDS: 3 broken cross-references detected.

Broken references:
  • Section 2.3 → 05-07 (advanced diagnostics) - Target not found
  • Section 4.1 → EM-500 (mixing unit) - Equipment module not documented
  • Section 3.2 → 04-03 (HMI screens) - Plan not written

**To fix:**
1. Run /doc:verify-phase N to identify missing content
2. Write missing sections with /doc:write-phase N
3. Re-run /doc:complete-fds after all references are resolvable

Alternatively, use --force flag to generate DRAFT version with
[BROKEN REF] placeholders (not recommended for client delivery).
```

Exit with error (assembly blocked).

**ASBL-06: With --force flag:**

If `BROKEN_COUNT > 0`:
```
⚠ WARNING: 3 broken cross-references found

Assembly will continue with [BROKEN REF] placeholders.
Output file will be marked as DRAFT.

See XREF-REPORT.md for details after assembly completes.
```

Continue assembly, set flag: `IS_DRAFT=true`

**ASBL-05: Report orphan sections:**

Orphan sections are ALWAYS reported (informational), never block assembly.

```
⚠ INFO: 2 orphan sections detected

These sections exist but are never referenced:
  • Section 4.3 (EM-300 Vulunit) - HIGH severity
  • Section 7.2 (Historical Changes) - LOW severity

See XREF-REPORT.md for details and suggested fixes.
```

---

## Step 8: Run Standards Compliance Checks (if enabled)

If standards are enabled in PROJECT.md, invoke the standards validation logic from check-standards workflow.

**Check if standards are enabled:**
```bash
if [ "$STANDARDS_PACKML_ENABLED" = true ] || [ "$STANDARDS_ISA88_ENABLED" = true ]; then
  # Run standards checks
fi
```

**If NO standards enabled:**
Skip this step entirely (standards are opt-in, never pushed).

**If standards ARE enabled:**

**Invoke check-standards workflow logic (Steps 2-5 from Plan 01's workflow):**

Reuse the exact validation logic from `~/.claude/gsd-docs-industrial/workflows/check-standards.md`:

1. **Load enabled reference data** (Step 2)
   - PackML STATE-MODEL.md and UNIT-MODES.md (if packml.enabled)
   - ISA-88 EQUIPMENT-HIERARCHY.md and TERMINOLOGY.md (if isa88.enabled)

2. **Discover target CONTENT.md files** (Step 3)
   - Use ORDERED_SECTIONS[] from Step 4 (already have all content)

3. **Run PackML checks** (Step 4, if enabled)
   - STND-03a: State names
   - STND-03b: Transitions
   - STND-03c: Modes

4. **Run ISA-88 checks** (Step 5, if enabled)
   - STND-04a: Terminology
   - STND-04b: Hierarchy depth
   - STND-04c: Hierarchy consistency

**Collect validation results:**
```
STANDARDS_RESULTS[] = {
  check_id: "STND-03a",
  standard: "PackML",
  description: "State names match ISA-TR88.00.02",
  status: "FAIL",
  severity: "error",
  violations: [
    {
      section: "4.1",
      found: "Running",
      expected: "EXECUTE",
      line: 47
    }
  ],
  remediation: "Use EXECUTE instead of Running (common synonym)"
}
```

**Evaluate severity and decide action:**

Count errors vs warnings based on `severity` field and configured `standards.{standard}.severity` from PROJECT.md:

```
ERROR_COUNT = (violations with severity: "error")
WARNING_COUNT = (violations with severity: "warning")
```

**Without --force flag:**

If `ERROR_COUNT > 0`:
```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

Cannot assemble FDS: 4 standards compliance errors detected.

PackML violations:
  • Section 4.1 line 47: "Running" should be "EXECUTE"
  • Section 4.2 line 23: Invalid transition Idle→Execute

ISA-88 violations:
  • Section 2.3: "Module" should be "Equipment Module"
  • Section 4.1: Hierarchy depth exceeds 4 levels

**To fix:**
Run /doc:check-standards for full compliance report with remediation hints.

Alternatively, use --force flag to generate DRAFT version with
standards violations (not recommended for client delivery).
```

Exit with error (assembly blocked).

**With --force flag:**

If `ERROR_COUNT > 0`:
```
⚠ WARNING: 4 standards compliance errors found

Assembly will continue with standards violations.
Output file will be marked as DRAFT.

See COMPLIANCE.md for details after assembly completes.
```

Continue assembly, set flag: `IS_DRAFT=true`

**If only warnings (no errors):**
Display info message, continue normally:
```
⚠ INFO: 2 standards compliance warnings

See COMPLIANCE.md for details. These are non-blocking.
```

**Store standards results for Step 12 COMPLIANCE.md generation.**

---

## Step 9: Generate Front Matter

Generate professional document header sections: title page, table of contents, revision history, abbreviations list.

**Per locked decision:** "Full auto-generated front matter: title page, revision history, table of contents, abbreviations list"

### 9a. Generate Title Page

**Read template:**
```bash
TITLE_TEMPLATE=$(cat ~/.claude/gsd-docs-industrial/templates/frontmatter/title-page.md)
```

**Select language variant:**
Based on `LANGUAGE` from PROJECT.md (en or nl), extract the appropriate language block:

Template has dual blocks with `lang='en'` and `lang='nl'` attributes. Select matching block.

**Fill placeholders:**
Replace `{PLACEHOLDER}` markers with actual values from PROJECT.md and STATE.md:
- `{PROJECT_NAME}` → from PROJECT.md
- `{CLIENT}` → from PROJECT.md
- `{VERSION}` → from STATE.md Versions section
- `{DATE}` → current date in format YYYY-MM-DD
- `{LANGUAGE}` → "English" or "Nederlands"

**Result:**
```markdown
# Functional Design Specification

**Project:** Packaging Line Automation
**Client:** ACME Manufacturing
**Document Version:** v0.1
**Date:** 2026-02-14
**Language:** English
```

Store as: `FRONTMATTER_TITLE_PAGE`

### 9b. Generate Table of Contents

Walk through ORDERED_SECTIONS[] and create hierarchical TOC with section numbers and titles.

**Algorithm:**
For each section in ORDERED_SECTIONS[]:
- Extract section_number (e.g., "4.1.1")
- Extract section title (without number, e.g., "Function Description")
- Determine indentation level based on depth (depth 1 = no indent, depth 2 = 2 spaces, depth 3 = 4 spaces, depth 4 = 6 spaces)

**Format:**
```markdown
## Table of Contents

1 Introduction
  1.1 Purpose and Scope
  1.2 Document Conventions
  1.3 References
  1.4 Abbreviations
2 System Overview
  2.1 System Description
  2.2 System Architecture
  2.3 Equipment Overview
3 Functional Requirements
  3.1 Operating Modes
  3.2 State Machine
4 Equipment Modules
  4.1 EM-100 Waterbad
    4.1.1 Function Description
    4.1.2 Operating Principle
  4.2 EM-200 Bovenloopkraan
```

Store as: `FRONTMATTER_TOC`

### 9c. Generate Revision History

**Per locked decision:** "Revision history hybrid approach: auto-generated from git as draft, engineer edits before release"

**Read template:**
```bash
REVISION_TEMPLATE=$(cat ~/.claude/gsd-docs-industrial/templates/frontmatter/revision-history.md)
```

**Auto-generate from git log:**
```bash
git log --oneline --date=short --pretty=format:"%ad | %h | %s" -10
```

**Parse git log into revision table:**

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| v0.1 | 2026-02-14 | AI Draft | Initial FDS assembly from verified phases |
| - | 2026-02-13 | - | Phase 4 verified complete |
| - | 2026-02-10 | - | Phase 3 content written |

**Add placeholder for engineer edits:**
```markdown
## Revision History

<!-- AUTO-GENERATED DRAFT - Review and edit before client release -->

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| v0.1 | 2026-02-14 | [Engineer Name] | Initial release |

<!-- Detailed change log from git:
  * 2026-02-14 82ae1db docs(05): create phase plan
  * 2026-02-13 546f4e4 wip: phase 4 complete
  ...
-->
```

Store as: `FRONTMATTER_REVISION_HISTORY`

### 9d. Generate Abbreviations List

**Per locked decision:** "Abbreviations auto-extraction from document content plus manual additions"

**Read template:**
```bash
ABBREV_TEMPLATE=$(cat ~/.claude/gsd-docs-industrial/templates/frontmatter/abbreviations.md)
```

**Extract abbreviations from assembled content:**

Scan all ORDERED_SECTIONS[].content for abbreviation patterns:
- 2+ uppercase letters (e.g., PLC, SCADA, HMI)
- Common patterns: acronyms in parentheses like "Programmable Logic Controller (PLC)"

**Algorithm:**
1. Find all uppercase 2+ letter words
2. Deduplicate
3. Look up in pre-populated abbreviation dictionary from template (22 common terms)
4. For matches: use dictionary definition
5. For unknowns: mark as `[DEFINITION NEEDED]` for engineer review

**Merge with manual additions from PROJECT.md:**
If PROJECT.md has an `abbreviations:` section, include those definitions (engineer-defined abbreviations take precedence).

**Format:**
```markdown
## Abbreviations

| Abbreviation | Definition |
|--------------|------------|
| FDS | Functional Design Specification |
| HMI | Human-Machine Interface |
| ISA-88 | International Standard for Batch Control (ANSI/ISA-88) |
| PackML | Packaging Machine Language (ISA-TR88.00.02) |
| PLC | Programmable Logic Controller |
| SCADA | Supervisory Control and Data Acquisition |
| SDS | Software Design Specification |
| TWN | Technical Work Notice |
| EM-100 | [DEFINITION NEEDED] |
```

Store as: `FRONTMATTER_ABBREVIATIONS`

**Display front matter generation result:**
```
Front matter generated:
  ✓ Title page (Project: Packaging Line Automation, v0.1)
  ✓ Table of contents (45 entries, 4 levels deep)
  ✓ Revision history (auto-generated draft from git log)
  ✓ Abbreviations (12 terms: 8 from dictionary, 4 extracted)
```

---

## Step 10: Assemble Final Document

Concatenate all components in correct order with page breaks between major sections.

**Assembly order:**
1. Title page
2. Page break (`\n\n---\n\n`)
3. Table of contents
4. Page break
5. Revision history
6. Page break
7. Abbreviations list
8. Page break
9. All numbered sections (from ORDERED_SECTIONS[])
   - Insert page break between top-level sections (depth 1, `#` headings)
   - No page break between subsections

**Concatenation:**
```bash
FINAL_CONTENT="${FRONTMATTER_TITLE_PAGE}"
FINAL_CONTENT+="\n\n---\n\n"
FINAL_CONTENT+="${FRONTMATTER_TOC}"
FINAL_CONTENT+="\n\n---\n\n"
FINAL_CONTENT+="${FRONTMATTER_REVISION_HISTORY}"
FINAL_CONTENT+="\n\n---\n\n"
FINAL_CONTENT+="${FRONTMATTER_ABBREVIATIONS}"
FINAL_CONTENT+="\n\n---\n\n"

PREV_DEPTH=0
for section in ORDERED_SECTIONS[]:
  if section.depth == 1 && PREV_DEPTH == 1:
    FINAL_CONTENT+="\n\n---\n\n"  # Page break before new top-level section
  FINAL_CONTENT+="${section.content}"
  FINAL_CONTENT+="\n\n"
  PREV_DEPTH=section.depth
done
```

**Determine output filename:**

Base filename: `FDS-${PROJECT_NAME}-v${VERSION}.md`

**If IS_DRAFT flag is set (broken refs or standards violations with --force):**
Append DRAFT suffix: `FDS-${PROJECT_NAME}-v${VERSION}-DRAFT.md`

**Write to project root:**
```bash
OUTPUT_FILE="${PROJECT_ROOT}/FDS-${PROJECT_NAME}-v${VERSION}.md"
echo "$FINAL_CONTENT" > "$OUTPUT_FILE"
```

**Calculate file size:**
```bash
FILE_SIZE=$(wc -c < "$OUTPUT_FILE" | numfmt --to=iec)
```

**Display assembly result:**
```
Final document assembled:
  ✓ File: FDS-Packaging-Line-v0.1.md
  ✓ Size: 127K
  ✓ Sections: 45 (7 top-level, 38 subsections)
  ✓ Front matter: 4 sections
```

---

## Step 11: Generate ENGINEER-TODO.md for Complex Diagrams

Scan assembled content for Mermaid diagram blocks and flag diagrams that exceed Mermaid complexity limits.

**ASBL-07 + KNOW-04:** "ENGINEER-TODO.md lists diagrams too complex for Mermaid with section reference, type, description, priority"

**Scan for Mermaid diagrams:**

For each section in ORDERED_SECTIONS[]:
  Search content for Mermaid code blocks:
  ````markdown
  ```mermaid
  ...
  ```
  ````

**Extract diagram content between triple backticks.**

**Apply complexity heuristic:**

A diagram is considered "too complex for Mermaid" if ANY of these conditions are met:
1. **Node count > 20:** Count distinct node identifiers
2. **Nesting depth > 4:** Count levels of indentation or subgraph depth
3. **Line count > 50:** Count lines in the diagram block

**Complexity detection algorithm:**

For each diagram:
```
node_count = (count unique node IDs in diagram)
nesting_depth = (max indentation level or subgraph depth)
line_count = (count lines)

if node_count > 20 OR nesting_depth > 4 OR line_count > 50:
  exceeds_complexity = true
```

**For diagrams exceeding complexity:**

Record:
- Section reference (section number + section title)
- Diagram type (state, flowchart, sequence — parse from `stateDiagram`, `flowchart`, `sequenceDiagram` keywords)
- Description (first comment line in diagram, or brief context from surrounding text)
- Priority (based on diagram type):
  - **High:** State machines (stateDiagram) — critical for control logic
  - **Medium:** Flowcharts (flowchart) — important for process understanding
  - **Low:** Sequence diagrams (sequenceDiagram) — supplementary communication flows

**Store in array:**
```
COMPLEX_DIAGRAMS[] = {
  section: "4.1.3 State Machine",
  type: "stateDiagram",
  description: "PackML state machine with 25 states and transitions",
  priority: "High",
  node_count: 25,
  reason: "Exceeds 20-node limit for Mermaid rendering"
}
```

**Generate ENGINEER-TODO.md:**

Create directory:
```bash
mkdir -p .planning/assembly/v${VERSION}
```

Write ENGINEER-TODO.md:
```bash
cat > .planning/assembly/v${VERSION}/ENGINEER-TODO.md <<EOF
# Engineer TODO: Complex Diagrams

The following diagrams exceed Mermaid complexity limits and require manual creation in a professional diagramming tool (Visio, draw.io, etc.).

Generated: $(date -u +"%Y-%m-%d")
FDS Version: v${VERSION}

---

## High Priority

### Section 4.1.3 State Machine
- **Type:** State diagram
- **Description:** PackML state machine with 25 states and transitions
- **Reason:** Exceeds 20-node limit (found: 25 nodes)
- **Action:** Create in Visio, export as PNG/SVG, embed in final document

---

## Medium Priority

### Section 3.2 Process Flow
- **Type:** Flowchart
- **Description:** Overall process flow with 8 decision points
- **Reason:** Nesting depth exceeds 4 levels (found: 6 levels)
- **Action:** Simplify or create in draw.io

---

## Low Priority

(None)

---

**Next steps:**
1. Create diagrams using professional tool
2. Export as high-resolution PNG or vector SVG
3. Place in project /diagrams/ folder
4. Update FDS markdown to reference image files instead of Mermaid code blocks
5. Re-run /doc:complete-fds to regenerate with embedded images
EOF
```

**Note:** This ENGINEER-TODO.md is assembly-specific (located in `.planning/assembly/v{VERSION}/`), distinct from the gap-closure ENGINEER-TODO.md generated during verify-phase (located in phase directories).

**Display diagram analysis result:**
```
Complex diagrams detected:
  ⚠ 3 diagrams exceed Mermaid limits (2 High, 1 Medium priority)
  ✓ ENGINEER-TODO.md generated at .planning/assembly/v0.1/
```

If no complex diagrams found:
```
✓ All diagrams within Mermaid complexity limits
```

---

## Step 12: Generate Reports

Generate XREF-REPORT.md (always) and COMPLIANCE.md (if standards were checked).

### 12a. Generate XREF-REPORT.md

**Read template:**
```bash
XREF_TEMPLATE=$(cat ~/.claude/gsd-docs-industrial/templates/reports/xref-report.md)
```

**Populate template with data from Steps 6-7:**

**Header:**
- Date: current date
- FDS Version: `v${VERSION}`
- Total References: `${#RESOLVED_REFS[@]} + ${#BROKEN_REFS[@]}`
- Resolved: `${#RESOLVED_REFS[@]}`
- Broken: `${#BROKEN_REFS[@]}`
- Orphan Sections: `${#ORPHAN_SECTIONS[@]}`

**Section 1: Resolution Summary**

| Status | Count | Percentage |
|--------|-------|------------|
| Resolved | 28 | 90% |
| Broken | 3 | 10% |
| **Total** | **31** | **100%** |

**Section 2: Resolved References**

| Source Section | Target Section | Symbolic ID | Final Number | Context |
|----------------|----------------|-------------|--------------|---------|
| 2.3 | 4.1 | 03-02 | Section 4.1 | detailed state machine |
| 3.2 | 4.2 | EM-200 | Section 4.2 | crane control logic |
| ... | ... | ... | ... | ... |

Populate from `RESOLVED_REFS[]`.

**Section 3: Broken References**

| Source Section | Symbolic ID | Reason | Suggested Fix |
|----------------|-------------|--------|---------------|
| 2.3 | 05-07 | Target not found | Write section 05-07 or remove reference |
| 4.1 | EM-500 | Equipment module not documented | Add EM-500 to ROADMAP and write content |
| 3.2 | 04-03 | Plan not written | Run /doc:write-phase 4 to complete HMI sections |

Populate from `BROKEN_REFS[]`.

**If --force was used:** Add note:
```
**Note:** These broken references appear as [BROKEN REF] placeholders in the assembled DRAFT document.
```

**Section 4: Orphan Sections**

| Section Number | Section Title | Severity | Notes |
|----------------|---------------|----------|-------|
| 4.3 | EM-300 Vulunit | HIGH | Equipment module never referenced from System Overview. Add reference in Section 2.3. |
| 7.2 | Historical Changes | LOW | Appendix section, standalone by nature. Consider adding "see Section 7.2" from relevant sections if historical context is important. |

Populate from `ORPHAN_SECTIONS[]`.

**Severity reasoning (Claude's discretion per locked decision):**
- HIGH: Equipment modules (section 4.x) — should always be referenced
- MEDIUM: Introduction/safety — typically self-contained but better if referenced
- LOW: Appendices — standalone by nature

**Section 5: Statistics**

- Total sections in document: `${#ORDERED_SECTIONS[@]}`
- Total cross-references found: `${#RESOLVED_REFS[@]} + ${#BROKEN_REFS[@]}`
- Resolution rate: `(RESOLVED / TOTAL) * 100%`
- Most-referenced section: (section with most incoming references, compute from RESOLVED_REFS)
- Most-referencing section: (section with most outgoing references, compute from RESOLVED_REFS)

**Write report:**
```bash
cat > .planning/assembly/v${VERSION}/XREF-REPORT.md <<EOF
[Populated template content]
EOF
```

### 12b. Generate COMPLIANCE.md (if standards were checked)

**Only execute if standards checks were run in Step 8.**

**Read template:**
```bash
COMPLIANCE_TEMPLATE=$(cat ~/.claude/gsd-docs-industrial/templates/reports/compliance-report.md)
```

**Populate template with data from Step 8:**

**Header:**
- Date: current date
- FDS Version: `v${VERSION}`
- Standards checked: PackML, ISA-88 (list enabled standards)

**Per-standard sections:**

For each enabled standard (PackML, ISA-88):

**Section: PackML Compliance**

Overall status: PASS / FAIL (based on error count)

| Check ID | Description | Status | Violations | Severity |
|----------|-------------|--------|------------|----------|
| STND-03a | State names match ISA-TR88.00.02 | FAIL | 2 | error |
| STND-03b | Transitions are valid | PASS | 0 | - |
| STND-03c | Modes are valid | PASS | 0 | - |

**Violation details:**

For each check with violations:
```markdown
### STND-03a: State names match ISA-TR88.00.02

**Status:** FAIL (2 violations)

| Section | Line | Found | Expected | Remediation |
|---------|------|-------|----------|-------------|
| 4.1 | 47 | Running | EXECUTE | Use EXECUTE instead of Running (common synonym) |
| 4.2 | 23 | Idle | IDLE | Use uppercase IDLE (case-sensitive) |
```

**Repeat for ISA-88 section.**

**Overall compliance summary:**
- Total checks: 6
- Passed: 4
- Failed: 2
- Warnings: 0
- Compliance score: 67%

**Write report:**
```bash
cat > .planning/assembly/v${VERSION}/COMPLIANCE.md <<EOF
[Populated template content]
EOF
```

**Display report generation result:**
```
Reports generated:
  ✓ XREF-REPORT.md (31 references, 3 broken, 2 orphans)
  ✓ COMPLIANCE.md (6 checks: 4 passed, 2 failed)
```

---

## Step 13: Archive Phase Files

Copy phase files to .planning/archive/v{VERSION}/ for version control.

**ASBL-08:** "Phase files archived to .planning/archive/vN.M/ after successful assembly"

**Create archive directory:**
```bash
ARCHIVE_DIR=".planning/archive/v${VERSION}"
mkdir -p "$ARCHIVE_DIR"
```

**Check if archive already exists (pitfall 5 from research):**

If `$ARCHIVE_DIR` already exists from a previous assembly with the same version:
```bash
if [ -d "$ARCHIVE_DIR/phases" ]; then
  # Archive exists, create timestamped backup
  TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
  BACKUP_DIR=".planning/archive/v${VERSION}-backup-${TIMESTAMP}"
  mv "$ARCHIVE_DIR" "$BACKUP_DIR"
  echo "Previous archive backed up to: $BACKUP_DIR"
fi
```

**Copy phase files:**
```bash
cp -r .planning/phases "$ARCHIVE_DIR/phases"
```

**Copy ROADMAP.md:**
```bash
cp .planning/ROADMAP.md "$ARCHIVE_DIR/ROADMAP.md"
```

**Archive is a COPY, not a move:** Original phase files remain in `.planning/phases/` for continued work.

**Write archive metadata:**
```bash
cat > "$ARCHIVE_DIR/ARCHIVE-INFO.md" <<EOF
# Archive v${VERSION}

**Created:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**FDS Version:** v${VERSION}
**Assembly Mode:** $([ "$FORCE_MODE" = true ] && echo "FORCED (DRAFT)" || echo "Normal")

## Contents

- phases/ — All phase directories with CONTENT.md, SUMMARY.md, VERIFICATION.md
- ROADMAP.md — Snapshot of ROADMAP at assembly time

## Verification Status

$(cat .planning/phases/*/\*-VERIFICATION.md | grep "^Status:" | sort | uniq -c)

## Assembly Stats

- Total sections: ${#ORDERED_SECTIONS[@]}
- Cross-references: ${#RESOLVED_REFS[@]} resolved, ${#BROKEN_REFS[@]} broken
- Orphan sections: ${#ORPHAN_SECTIONS[@]}
- Standards checked: $([ "$STANDARDS_PACKML_ENABLED" = true ] && echo "PackML" || echo "")$([ "$STANDARDS_ISA88_ENABLED" = true ] && echo " ISA-88" || echo "")

---

This archive preserves the exact state of all phase files at the time of FDS v${VERSION} assembly.
EOF
```

**Display archive result:**
```
Phase files archived:
  ✓ .planning/archive/v0.1/phases/ (8 phases)
  ✓ .planning/archive/v0.1/ROADMAP.md
  ✓ Archive metadata written
```

---

## Step 14: Update STATE.md

Update STATE.md with assembly completion status and current version.

**Read current STATE.md:**
```bash
cat .planning/STATE.md
```

**Update Current Operation section:**

Replace or add:
```yaml
## Current Operation

- Command: complete-fds
- Status: COMPLETE
- Started: [timestamp from start of this workflow]
- Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
```

**Update Versions section:**

If Versions section exists, update FDS version:
```yaml
## Versions

FDS: v${VERSION}
SDS: v0.1
```

If Versions section doesn't exist, create it:
```yaml
## Versions

FDS: v${VERSION}
SDS: (not generated yet)
```

**Update Current focus:**

Replace current focus text with assembly completion note:
```
**Current focus:** FDS v${VERSION} assembled successfully. $([ "$IS_DRAFT" = true ] && echo "DRAFT version with broken references/standards violations." || echo "Ready for client review.") Next: /doc:release --type internal to bump version or /doc:release --type client for client release.
```

**Write updated STATE.md:**
```bash
echo "$UPDATED_STATE_CONTENT" > .planning/STATE.md
```

**Display STATE.md update:**
```
STATE.md updated:
  ✓ Current Operation: complete-fds COMPLETE
  ✓ FDS Version: v0.1
  ✓ Current focus: Assembly complete, ready for release
```

---

## Step 15: Display Summary

Display final assembly summary with all key metrics and next steps.

**Banner:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > FDS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Assembly result:**
```
FDS Assembly Complete!

**Output File:**
  • FDS-Packaging-Line-v0.1.md (127K)
  $([ "$IS_DRAFT" = true ] && echo "  ⚠ DRAFT version (broken references/standards violations)" || echo "  ✓ Production-ready")

**Document Structure:**
  • 7 top-level sections
  • 45 total sections (38 subsections)
  • 4 front matter sections (title, TOC, revision history, abbreviations)
  • 5 placeholder stubs for unwritten content

**Cross-References:**
  • 28 references resolved (90%)
  • 3 broken references (10%)
  $([ ${#BROKEN_REFS[@]} -gt 0 ] && echo "  ⚠ See XREF-REPORT.md for details" || echo "")

**Orphan Sections:**
  • 2 orphans detected (1 HIGH, 1 LOW severity)
  ⚠ See XREF-REPORT.md for suggested fixes

**Standards Compliance:**
  $(if [ "$STANDARDS_PACKML_ENABLED" = true ] || [ "$STANDARDS_ISA88_ENABLED" = true ]; then
    echo "  • PackML: 4/6 checks passed"
    echo "  • ISA-88: 2/3 checks passed"
    echo "  ⚠ See COMPLIANCE.md for remediation hints"
  else
    echo "  • No standards checks enabled"
  fi)

**Complex Diagrams:**
  $(if [ ${#COMPLEX_DIAGRAMS[@]} -gt 0 ]; then
    echo "  • ${#COMPLEX_DIAGRAMS[@]} diagrams exceed Mermaid limits (2 High, 1 Medium priority)"
    echo "  ⚠ See ENGINEER-TODO.md at .planning/assembly/v${VERSION}/"
  else
    echo "  ✓ All diagrams within Mermaid complexity limits"
  fi)

**Archive:**
  • Phase files archived to .planning/archive/v${VERSION}/

**Reports Generated:**
  • .planning/assembly/v${VERSION}/XREF-REPORT.md
  $([ "$STANDARDS_PACKML_ENABLED" = true ] || [ "$STANDARDS_ISA88_ENABLED" = true ] && echo "  • .planning/assembly/v${VERSION}/COMPLIANCE.md" || echo "")
  $([ ${#COMPLEX_DIAGRAMS[@]} -gt 0 ] && echo "  • .planning/assembly/v${VERSION}/ENGINEER-TODO.md" || echo "")
```

**Next steps:**
```
───────────────────────────────────────────────────────────────

## > Next Up

**Version Management**

If ready for client review:
  /doc:release --type client

For internal version bump:
  /doc:release --type internal

$(if [ "$IS_DRAFT" = true ]; then
  echo "**Fix Draft Issues (recommended before release):**"
  echo ""
  echo "1. Fix broken cross-references:"
  echo "   - Review XREF-REPORT.md for missing sections"
  echo "   - Write missing content with /doc:write-phase N"
  echo "   - Re-run /doc:complete-fds"
  echo ""
  echo "2. Fix standards violations:"
  echo "   - Review COMPLIANCE.md for remediation hints"
  echo "   - Edit CONTENT.md files with corrections"
  echo "   - Re-run /doc:verify-phase N"
  echo "   - Re-run /doc:complete-fds"
fi)

───────────────────────────────────────────────────────────────

**Also available:**
- /doc:generate-sds -- Transform FDS to SDS with typicals matching
- /doc:export -- Export to DOCX with corporate styling
- /doc:review-phase N -- Client/engineer review with REVIEW.md

───────────────────────────────────────────────────────────────
```

**If DRAFT version was generated due to --force flag:**
Add additional reminder:
```
⚠ REMINDER: This is a DRAFT version

The assembled FDS contains broken references and/or standards violations.
It is NOT recommended for client delivery without fixes.

See the reports above for details and remediation steps.
```

**End of workflow.**

</workflow>
