<workflow>

# /doc:generate-sds Workflow

Complete execution logic for SDS project scaffolding from a completed FDS. The command file delegates here. Follow each step in order.

**Bridge pattern:** This workflow creates the SDS project infrastructure and seeds initial content from the FDS, enabling the engineer to then run the full SDS workflow (discuss, plan, write, verify) independently. This is NOT a single-pass transform — SDS gets its own discuss-plan-write-verify cycle.

**Typicals matching strategy:** Suggest + confirm — system proposes typical matches based on equipment module I/O, states, and keywords, engineer confirms or overrides during SDS Phase 1 discuss. Matching is NEVER auto-applied.

**Unmatched modules:** Generate structured skeleton from FDS (I/O, parameters, states) marked as "NEW TYPICAL NEEDED" — not a stub, but a complete starting point for custom FB development.

---

## Step 1: Validate FDS Prerequisites

**Objective:** Verify an assembled FDS document exists, extract its version and metadata, and validate it has substantial content.

### 1.1 Check for Assembled FDS

Scan the `output/` directory for assembled FDS documents:

```bash
ls -t output/FDS-*.md 2>/dev/null | head -1
```

**If no FDS files found**, display error and abort:

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR: No FDS Found                                         ║
╚══════════════════════════════════════════════════════════════╝

No assembled FDS document found in output/ directory.

**To fix:**
1. Run /doc:complete-fds to assemble the FDS document
2. Verify output/FDS-*.md exists
3. Re-run /doc:generate-sds

**Cannot scaffold SDS without a completed FDS.**
```

Stop execution. Do not continue.

**If multiple FDS files found**, use the most recent by modification time. Display:

```
DOC > Found multiple FDS versions, using most recent: {filename}
```

Store the FDS file path as `FDS_PATH`.

### 1.2 Extract FDS Metadata

Read the FDS YAML frontmatter from `FDS_PATH`:

```bash
head -50 ${FDS_PATH} | grep -A 20 "^---$" | head -20
```

Extract these fields:
- `project_name` (store as `FDS_PROJECT_NAME`)
- `version` (store as `FDS_VERSION`)
- `date` (store as `FDS_DATE`)
- `language` (store as `FDS_LANGUAGE` — "en" or "nl")
- `type` (store as `FDS_TYPE` — "A", "B", "C", or "D")

**If frontmatter is missing or incomplete**, display warning:

```
⚠ WARNING: FDS frontmatter incomplete
Using fallback extraction from STATE.md
```

Fall back to reading `.planning/STATE.md`:
- Extract version from `## Versions` section
- Extract project name from `PROJECT.md` reference
- Read `.planning/PROJECT.md` for language and type

### 1.3 Verify FDS Content

Check that the FDS file has substantial content (not just frontmatter):

```bash
FILE_SIZE=$(wc -c < "${FDS_PATH}")
if [ "$FILE_SIZE" -lt 1024 ]; then
    echo "ERROR: FDS file too small (${FILE_SIZE} bytes)"
fi
```

**If file size < 1KB**, display error and abort:

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR: FDS Appears Empty                                    ║
╚══════════════════════════════════════════════════════════════╝

FDS file exists but appears to be empty or incomplete.
File: {FDS_PATH}
Size: {FILE_SIZE} bytes

**To fix:**
1. Verify FDS was assembled successfully
2. Check that phases were written (not just planned)
3. Re-run /doc:complete-fds if needed
```

Stop execution. Do not continue.

### 1.4 Read STATE.md for Project Configuration

Read `.planning/STATE.md` to extract:
- Current FDS version (from `## Versions` section)
- Project configuration (from `## Project Reference`)

### 1.5 Display FDS Analysis Banner

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > SDS GENERATION: READING FDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project:  {FDS_PROJECT_NAME}
FDS:      v{FDS_VERSION} ({FDS_DATE})
Type:     {FDS_TYPE}
Language: {FDS_LANGUAGE}
File:     {FDS_PATH}
```

(Adapt to Dutch if `FDS_LANGUAGE = "nl"`)

**Verification:**
- [ ] Assembled FDS found in output/
- [ ] FDS metadata extracted from frontmatter or STATE.md
- [ ] FDS file has substantial content (>= 1KB)
- [ ] Project configuration read from STATE.md

---

## Step 2: Load Typicals Library

**Objective:** Load project-specific typicals library in one of three modes: external reference, imported copy, or no typicals (skeleton mode).

### 2.1 Determine Typicals Mode

Check for typicals configuration in this priority order:

1. **Command argument:** If `--typicals [path]` flag provided, use that path
2. **PROJECT.md configuration:** Read `.planning/PROJECT.md`, look for `typicals.path` field
3. **No configuration:** If neither found, proceed in skeleton mode (no typicals matching)

Store the mode as `TYPICALS_MODE`:
- `external` — path provided, no --import flag
- `imported` — path provided, --import flag present
- `none` — no path configured

### 2.2 Load Typicals Catalog (External or Imported Mode)

**If `TYPICALS_MODE = "external"` or `TYPICALS_MODE = "imported"`:**

1. **Resolve typicals path:**
   - If path is absolute: use directly
   - If path is relative: resolve relative to project root
   - Store resolved path as `TYPICALS_PATH`

2. **Verify CATALOG.json exists:**
   ```bash
   if [ -f "${TYPICALS_PATH}/CATALOG.json" ]; then
       echo "CATALOG_FOUND"
   else
       echo "CATALOG_NOT_FOUND"
   fi
   ```

   **If CATALOG.json not found**, display error and abort:

   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║  ERROR: Typicals Catalog Not Found                          ║
   ╚══════════════════════════════════════════════════════════════╝

   Typicals library path configured but CATALOG.json not found.
   Path: {TYPICALS_PATH}

   **To fix:**
   1. Verify the path points to a valid typicals library
   2. Ensure CATALOG.json exists in that directory
   3. Or run without --typicals for skeleton mode
   ```

   Stop execution. Do not continue.

3. **Read CATALOG.json:**
   - Parse JSON file
   - Extract `library` object: name, version, platform, updated date
   - Extract `typicals` array: all typical definitions
   - Store as `CATALOG` object

4. **Validate against CATALOG-SCHEMA.json:**
   - Read `~/.claude/gsd-docs-industrial/references/typicals/CATALOG-SCHEMA.json`
   - Validate CATALOG structure: has `schema_version`, `library`, `typicals` array
   - Check each typical has required fields: `id`, `type`, `category`, `description`, `interfaces`

   **If validation fails**, display warning (non-blocking):

   ```
   ⚠ WARNING: Typicals catalog validation issues found:
   - {issue 1}
   - {issue 2}

   Proceeding with matching, but results may be incomplete.
   ```

5. **If `TYPICALS_MODE = "imported"` (--import flag present):**
   - Copy `CATALOG.json` to `references/typicals/CATALOG.json`
   - If library has documentation files (*.md), copy those too
   - Display: `DOC > Typicals: Imported catalog to references/typicals/`

### 2.3 Display Typicals Loading Result

**For external or imported mode:**

```
DOC > Typicals: Loaded {N} typicals from {library_name} v{library_version} ({mode})
DOC >   Platform: {platform}
DOC >   Last updated: {updated_date}
DOC >   Path: {path}
```

**For skeleton mode (`TYPICALS_MODE = "none"`):**

```
DOC > Typicals: No library configured — skeleton mode
DOC >   All equipment modules will be flagged as NEW TYPICAL NEEDED
DOC >   Engineer will design custom FBs based on FDS requirements
```

Store typicals count as `TYPICALS_COUNT` (0 if skeleton mode).

**Verification:**
- [ ] Typicals mode determined (external/imported/none)
- [ ] CATALOG.json loaded and validated (if mode is external/imported)
- [ ] Library metadata extracted
- [ ] Imported copy created if --import flag used
- [ ] Skeleton mode fallback if no typicals configured

---

## Step 3: Extract FDS Equipment Modules

**Objective:** Parse the assembled FDS document to extract equipment module profiles with I/O, states, parameters, and keywords for matching.

### 3.1 Identify Equipment Module Sections

Read the FDS document and identify all section 4.x entries (equipment modules):

```bash
grep -n "^## 4\." ${FDS_PATH}
```

Expected pattern: `## 4.1 Module Name`, `## 4.2 Another Module`, etc.

Extract:
- Section number (e.g., "4.1")
- Module name (e.g., "Dosing System")

Store as array of module entries: `MODULES[]`

**If no equipment modules found**, display warning:

```
⚠ WARNING: No equipment modules found in FDS
Expected section 4.x entries but found none.

This is unusual for an FDS. Proceeding with empty SDS equipment section.
```

Set `MODULES_COUNT = 0` and skip to Step 7 (no matching needed).

### 3.2 Extract Equipment Module Profiles

For each module in `MODULES[]`, extract detailed profile:

**Module ID:**
- Look for "Module ID:" or "Equipment ID:" in section 4.x content
- Pattern: `EM-XXX` or similar
- If not found: derive from section number (e.g., "EM-4.1")

**I/O Interface:**
- Find I/O table in subsection 4.x.1 (Process Interfaces)
- Count by type: DI (digital inputs), DO (digital outputs), AI (analog inputs), AO (analog outputs)
- Store as: `{ DI: count, DO: count, AI: count, AO: count }`
- Extract data types (BOOL, INT, REAL) from Signal Type column

**Operating States:**
- Find state table in subsection 4.x.2 (Operating States and Modes)
- Extract state names (e.g., "Idle", "Running", "Stopped")
- Count total states
- Store as: `{ states: [names], count: N }`

**Parameters:**
- Find parameter table in subsection 4.x.3 (Parameters and Setpoints)
- Extract parameter names, ranges, units
- Store as: `{ parameters: [{ name, range, unit }], count: N }`

**Interlocks (if present):**
- Find interlock table in subsection 4.x.4 (Interlocks and Safety) if it exists
- Count interlock types (permissive, inhibit)
- Store as: `{ count: N, types: [...] }`

**Keywords for Matching:**
- Extract from module description (first paragraph of section 4.x)
- Derive from module name (tokenize: "Dosing System" → ["dosing", "system"])
- Include category if mentioned (e.g., "pump", "valve", "motor", "analog input")
- Store as: `{ keywords: [...] }`

Store each module profile as:

```json
{
  "section": "4.1",
  "module_id": "EM-200",
  "module_name": "Dosing System",
  "io": { "DI": 3, "DO": 2, "AI": 1, "AO": 1 },
  "states": { "names": ["Idle", "Running", "Stopped"], "count": 3 },
  "parameters": { "count": 5, "list": [...] },
  "interlocks": { "count": 2, "types": ["permissive", "inhibit"] },
  "keywords": ["dosing", "system", "pump", "flow"]
}
```

**If extraction fails for a module**, display warning and use partial profile:

```
⚠ WARNING: Incomplete data for module {module_name}
Missing: {missing_fields}
Using partial profile for matching.
```

### 3.3 Display Extraction Summary

```
DOC > FDS Analysis: Found {N} equipment modules
```

For each module, display brief summary:
```
DOC >   {section} {module_name} ({module_id})
DOC >     I/O: {DI}DI + {DO}DO + {AI}AI + {AO}AO
DOC >     States: {state_count}
DOC >     Parameters: {param_count}
```

Store total as `MODULES_COUNT`.

**Verification:**
- [ ] Equipment module sections identified from FDS section 4.x
- [ ] Module profiles extracted with I/O, states, parameters, keywords
- [ ] Partial profiles used if extraction incomplete
- [ ] Module count stored

---

## Step 4: Match Equipment Modules Against Typicals

**Objective:** For each FDS equipment module, calculate confidence-scored matches against loaded typicals catalog, producing a matching report for engineer review.

**This step is skipped if `TYPICALS_MODE = "none"` (no catalog loaded).**

### 4.1 Matching Algorithm

For each module profile in `MODULES[]`:

1. **Initialize match candidates array:** `matches = []`

2. **For each typical in `CATALOG.typicals`:**

   **Calculate I/O interface match score (40% weight):**
   - Compare input counts: exact match = 10, within ±1 = 7, within ±2 = 5, else 0
   - Compare output counts: same scoring
   - Compare data types: BOOL vs INT vs REAL alignment
   - Score range: 0-40

   **Calculate keyword/use-case match score (30% weight):**
   - Use Jaccard similarity: `intersection(module_keywords, typical_use_cases) / union(module_keywords, typical_use_cases)`
   - Score range: 0-30

   **Calculate state complexity match score (20% weight):**
   - Compare state count similarity: exact = 20, ±1 = 15, ±2 = 10, else 5
   - Score range: 0-20

   **Calculate category match score (10% weight):**
   - Exact category match (e.g., module keyword "pump" matches typical category "pump"): 10
   - Else: 0
   - Score range: 0-10

   **Total confidence score:** Sum all components (range 0-100)

3. **Filter matches with confidence >= 30%**

4. **Rank by confidence descending, take top 3 suggestions per module**

5. **Classify confidence level:**
   - HIGH: >= 80%
   - MEDIUM: 60-79%
   - LOW: 40-59%
   - VERY LOW: 30-39% (shown but not recommended)

6. **If no matches >= 30%:** Mark module as "NEW TYPICAL NEEDED" immediately

### 4.2 Generate Comparison Table for Each Module

For each equipment module, create a matching analysis table:

```markdown
### Module: {module_name} ({module_id})

**FDS Requirements Summary:**
- I/O: {DI} DI, {DO} DO, {AI} AI, {AO} AO
- States: {state_count} ({state_names})
- Parameters: {param_count}
- Keywords: {keywords}

**Top Suggested Typical:**

| Typical ID | Confidence | I/O Match | State Match | Category | Status |
|------------|------------|-----------|-------------|----------|--------|
| {typical_id} | {score}% ({level}) | {io_analysis} | {state_analysis} | {category} | {status} |

**Interface Match Analysis:**
- Inputs: {analysis of DI/AI alignment}
- Outputs: {analysis of DO/AO alignment}
- Data types: {BOOL/INT/REAL compatibility}

**Recommendation:**
- {HIGH confidence: "ACCEPT MATCH — high confidence, proceed with this typical"}
- {MEDIUM confidence: "REVIEW INTERFACES — moderate confidence, verify I/O alignment"}
- {LOW confidence: "MANUAL DECISION — low confidence, engineer discretion required"}
- {No match: "NEW TYPICAL NEEDED — custom FB development required"}
```

### 4.3 Store Matching Results

For each module, store the best match:

```json
{
  "module_id": "EM-200",
  "module_name": "Dosing System",
  "suggested_typical": "FB_PumpCtrl",
  "confidence": 85,
  "confidence_level": "HIGH",
  "status": "Matched",
  "io_match": "Exact inputs, 1 extra output in typical",
  "state_match": "3 states align with PackML subset",
  "category_match": "pump",
  "alternatives": ["FB_MotorCtrl (62%)", "FB_ValveCtrl (45%)"]
}
```

**For unmatched modules:**

```json
{
  "module_id": "EM-300",
  "module_name": "Complex Reactor",
  "suggested_typical": null,
  "confidence": 0,
  "confidence_level": "NONE",
  "status": "NEW TYPICAL NEEDED",
  "reason": "No catalog typical matches this equipment (complex state machine, 15 I/O signals)"
}
```

### 4.4 Display Matching Summary

```
DOC > Matching: {matched} matched, {unmatched} unmatched, {review} need review
DOC >   HIGH confidence: {high_count} modules
DOC >   MEDIUM confidence: {medium_count} modules
DOC >   LOW confidence: {low_count} modules
DOC >   NEW TYPICAL NEEDED: {new_count} modules
```

**Verification:**
- [ ] Matching algorithm run for all modules (if catalog loaded)
- [ ] Confidence scores calculated with I/O (40%), keywords (30%), states (20%), category (10%) weights
- [ ] Matches filtered >= 30%, ranked by confidence
- [ ] Unmatched modules flagged as NEW TYPICAL NEEDED
- [ ] Matching results stored for report generation

---

## Step 5: Generate SDS Equipment Module Seeds

**Objective:** For each equipment module, create initial SDS section content as a starting point for the engineer's SDS write-phase cycle.

### 5.1 For Matched Modules (any confidence level)

For modules with `status = "Matched"`:

1. **Use section-equipment-software.md template** from `~/.claude/gsd-docs-industrial/templates/sds/`

2. **Pre-fill content:**

   **Subsection 1: Typical Assignment**
   - Table row: Equipment Module ID, Matched Typical, Confidence, Status, Library Reference
   - Example: `| EM-200 | FB_PumpCtrl | 85% (HIGH) | Matched | See CATALOG v1.2, FB_PumpCtrl.md |`
   - Add typical summary: "FB_PumpCtrl is a standard pump control function block providing start/stop control, flow monitoring, and fault detection. Inputs: Start command, Flow sensor (AI). Outputs: Motor contactor (DO), Flow alarm (DO)."

   **Subsection 2: FB Composition**
   - Infer from typical's interfaces: "This module instantiates FB_PumpCtrl with associated data blocks."
   - FB hierarchy placeholder: "Main FB calls FB_PumpCtrl → FB_AnalogIn (for flow sensor) → FB_AlarmHandler"
   - Mark as: "(Derived from typical structure — engineer to refine during SDS Phase 2)"

   **Subsection 3: Instantiation**
   - Placeholder: Instance name derived from module ID (e.g., "DB_DosingSys")
   - DB number: "[TO BE ASSIGNED]"
   - PLC/CPU mapping: "[TO BE ASSIGNED]"

   **Subsection 4: Parameter Configuration**
   - Merge FDS parameters with typical defaults:
     - FDS param: "Flow setpoint: 10-50 L/min (from FDS section 4.1.3)"
     - Typical default: "Alarm delay: 5s (from FB_PumpCtrl default)"
   - Source tracking column: "FDS" or "Typical Default" or "Engineer Override"

   **Subsection 5: Data Flow**
   - List I/O signals from FDS: "Flow sensor (AI) → FB_PumpCtrl.FlowIn"
   - Destination: "[TO BE DESIGNED — map to HMI tags]"
   - Mermaid flowchart placeholder

   **Subsection 6: State Machine Implementation**
   - Map FDS states to typical states where names align:
     - FDS state "Running" → FB state "Running" (exact match)
     - FDS state "Idle" → FB state "Idle" (exact match)
     - FDS state "Stopped" → FB state "Stopped" (exact match)
   - Mark as: "(Preliminary mapping — engineer to verify transitions during SDS Phase 2)"

3. **Mark section as "NEEDS ENGINEER REVIEW":**
   - Add note at top: "<!-- This section was auto-generated from FDS and typical matching. Review and refine during SDS Phase 2. -->"

4. **Save to:** `.planning/sds/phases/sds-02-equipment/{section}-{module-id}-seed.md`

### 5.2 For Unmatched Modules (NEW TYPICAL NEEDED)

For modules with `status = "NEW TYPICAL NEEDED"`:

1. **Use section-equipment-software.md template** (same template)

2. **Generate structured skeleton from FDS:**

   **Subsection 1: Typical Assignment**
   - Table row: Equipment Module ID, Matched Typical, Confidence, Status, Library Reference
   - Example: `| EM-300 | FB_ComplexReactor | 0% (NONE) | NEW TYPICAL NEEDED | Custom FB required |`
   - Add NEW TYPICAL specification:
     ```markdown
     ## NEW TYPICAL NEEDED: FB_ComplexReactor

     **Reason:** No catalog typical matches this equipment module. Custom FB development required.

     **I/O Profile from FDS:**
     - Inputs: {list all DI and AI from FDS section 4.x.1}
     - Outputs: {list all DO and AO from FDS section 4.x.1}

     **State Machine from FDS:**
     - States: {list all states from FDS section 4.x.2}
     - Transitions: {extract state transitions if documented in FDS}

     **Parameters from FDS:**
     - {list all parameters from FDS section 4.x.3 with ranges and units}

     **Design Notes:**
     - This FB will be designed during SDS Phase 1 (Foundation).
     - Once designed, it becomes a candidate for the project typicals library.
     ```

   **Subsection 2: FB Composition**
   - Empty template with module I/O as requirements:
     ```markdown
     ## FB Composition

     **Requirements from FDS:**
     - Must handle {DI_count} digital inputs, {AI_count} analog inputs
     - Must provide {DO_count} digital outputs, {AO_count} analog outputs
     - Must implement {state_count} operating states

     **FB Structure:** [TO BE DESIGNED]

     **FB Hierarchy:** [TO BE DESIGNED]
     ```

   **Subsection 3: Instantiation**
   - Same placeholder as matched modules

   **Subsection 4: Parameter Configuration**
   - All FDS parameters listed with "Source: FDS" and no typical defaults:
     ```markdown
     | Parameter | Value/Range | Unit | Source | Notes |
     |-----------|-------------|------|--------|-------|
     | {param1_name} | {param1_range} | {unit} | FDS | From FDS section 4.x.3 |
     | {param2_name} | {param2_range} | {unit} | FDS | From FDS section 4.x.3 |
     ```

   **Subsection 5: Data Flow**
   - All FDS I/O signals listed with "Destination: [TO BE DESIGNED]":
     ```markdown
     | Signal | Type | Direction | Destination | Notes |
     |--------|------|-----------|-------------|-------|
     | {signal1} | AI | Input | [TO BE DESIGNED] | From FDS I/O table |
     | {signal2} | DO | Output | [TO BE DESIGNED] | From FDS I/O table |
     ```

   **Subsection 6: State Machine Implementation**
   - All FDS states listed with "FB State: [TO BE DESIGNED]":
     ```markdown
     | FDS State | FB State Variable | Transitions | Notes |
     |-----------|-------------------|-------------|-------|
     | {state1} | [TO BE DESIGNED] | [TO BE DESIGNED] | From FDS section 4.x.2 |
     | {state2} | [TO BE DESIGNED] | [TO BE DESIGNED] | From FDS section 4.x.2 |
     ```

3. **Mark section as "NEW TYPICAL NEEDED":**
   - Add note at top: "<!-- NEW TYPICAL NEEDED: This equipment module requires custom FB development. Design FB during SDS Phase 1, then complete this section during SDS Phase 2. -->"

4. **Save to:** `.planning/sds/phases/sds-02-equipment/{section}-{module-id}-seed.md`

### 5.3 Display Seed Generation Summary

```
DOC > Seeds: Generated {total} SDS equipment module seeds
DOC >   Matched with typical: {matched_count}
DOC >   Custom FB needed: {new_count}
```

**Verification:**
- [ ] SDS section seeds generated for all equipment modules
- [ ] Matched modules use typical structure and defaults
- [ ] Unmatched modules have structured skeleton from FDS
- [ ] All seeds marked as NEEDS REVIEW or NEW TYPICAL NEEDED
- [ ] Seeds saved to .planning/sds/phases/sds-02-equipment/

---

## Step 6: Generate TRACEABILITY.md

**Objective:** Create FDS-to-SDS requirement traceability matrix with coverage analysis.

### 6.1 Parse FDS for Requirements

Read FDS document to extract functional requirements:

**Option A: Dedicated REQUIREMENTS.md exists**
- Read `.planning/REQUIREMENTS.md`
- Parse requirement IDs and descriptions

**Option B: Inline requirements in FDS sections**
- Scan FDS for requirement markers: "**REQ-xxx:**" or "Requirement: " patterns
- Extract from equipment module sections (4.x), system overview (2.x), interfaces (5.x)

**If no requirements found**, display warning:

```
⚠ WARNING: No explicit requirements found in FDS
TRACEABILITY.md will be generated with placeholder structure.
Engineer should populate requirements during SDS Phase 1.
```

Create minimal traceability structure with placeholder rows.

### 6.2 Map Requirements to SDS Sections

For each FDS requirement, determine SDS implementation section:

**Mapping logic:**
- Equipment module requirements (from section 4.x) → SDS section 4.x (same equipment module)
- System-level requirements (from section 2.x) → SDS section 2 (Software Architecture Overview)
- Interface requirements (from section 5.x) → SDS section 5 (Interfaces)
- Safety requirements → Multiple SDS sections (note in Status field)

**For each requirement, create traceability row:**

```markdown
| FDS-REQ-001 | 4.1.2 Operating States | 4.1.6 State Machine Implementation | FB_PumpCtrl state variables | Pending |
```

Fields:
- FDS Req ID: Requirement identifier from FDS
- FDS Section: Section number where requirement originates (with section title for clarity)
- SDS Section: Target SDS section number (with section title)
- Implementation: FB/DB reference or description (initially placeholder "[TO BE IMPLEMENTED]")
- Status: Pending (all requirements start as Pending during scaffolding)

### 6.3 Generate Coverage Analysis

Calculate traceability coverage metrics:

- **Total FDS requirements:** Count all extracted requirements
- **Mapped to SDS:** Count requirements with assigned SDS sections
- **Not Applicable:** 0 (none determined during scaffolding — engineer marks N/A during SDS Phase 3)
- **Missing Implementation:** Total - Mapped (initially all are missing implementation)

**Coverage Status:** FAIL (expected during scaffolding — will become PASS when engineer completes SDS)

### 6.4 Write TRACEABILITY.md

Use template from `~/.claude/gsd-docs-industrial/templates/reports/traceability.md`:

```markdown
---
type: traceability-report
purpose: internal-quality-check
deliverable: false
generated: {date}
fds_version: {FDS_VERSION}
sds_version: 0.1 (scaffolded)
---

# FDS-to-SDS Traceability Matrix

**Project:** {FDS_PROJECT_NAME}
**FDS Version:** v{FDS_VERSION} ({FDS_DATE})
**SDS Version:** v0.1 (scaffolded — not yet complete)
**Generated:** {current_date}

---

## Requirements Traceability

| FDS Req ID | FDS Section | SDS Section | Implementation | Status |
|------------|-------------|-------------|----------------|--------|
{traceability_rows}

---

## Coverage Analysis

**Total FDS Requirements:** {total_count}
**Mapped to SDS:** {mapped_count} ({mapped_percentage}%)
**Not Applicable:** 0
**Missing Implementation:** {missing_count}

**Coverage Status:** FAIL (SDS not yet implemented)

**Note:** This traceability matrix was auto-generated during SDS scaffolding. Requirements are mapped to target SDS sections but implementations are pending. Engineer will update during SDS Phase 2 (Equipment Details) and verify 100% coverage during SDS Phase 3 (Integration).

---

## Missing Implementations

{list_of_all_pending_requirements}

**Action Required:** Complete SDS sections during write-phase to implement these requirements.

---

## Release Gate

**Conditions for SDS Release:**
- [ ] All FDS requirements have Status = Complete, Partial, or N/A
- [ ] Coverage >= 100% ((Complete + Partial + N/A) / Total)
- [ ] No requirements with Status = Pending or Missing

**Current Status:** NOT READY (SDS in scaffolding phase)

**Override:** `--force` flag available during /doc:release --type client --sds
**Justification required if override used.**

---

## Engineer Sign-Off

**Reviewed by:** [TO BE COMPLETED]
**Review date:** [TO BE COMPLETED]
**Approval status:** Pending
**Comments:** [TO BE COMPLETED during SDS Phase 3]

---

*Auto-generated by /doc:generate-sds workflow*
*All traceability links must be verified during SDS verification phase*
```

Save to: `.planning/sds/TRACEABILITY.md`

### 6.5 Display Traceability Summary

```
DOC > Traceability: {N} FDS requirements mapped to SDS sections
DOC >   Equipment module requirements: {equipment_count}
DOC >   System-level requirements: {system_count}
DOC >   Interface requirements: {interface_count}
DOC >   Coverage: {mapped_percentage}% mapped (100% required for release)
```

**Verification:**
- [ ] FDS requirements extracted from REQUIREMENTS.md or inline markers
- [ ] Requirements mapped to target SDS sections
- [ ] Traceability table generated with Pending status
- [ ] Coverage analysis calculated
- [ ] TRACEABILITY.md saved to .planning/sds/

---

## Step 7: Scaffold SDS Project Structure

**Objective:** Create the complete SDS project directory structure with PROJECT.md, ROADMAP.md, STATE.md, and phase directories.

### 7.1 Create SDS Directory Structure

Create these directories:

```bash
mkdir -p .planning/sds
mkdir -p .planning/sds/phases
mkdir -p .planning/sds/phases/sds-01-foundation
mkdir -p .planning/sds/phases/sds-02-equipment
mkdir -p .planning/sds/phases/sds-03-integration
```

### 7.2 Create SDS PROJECT.md

Copy language, client, project name from FDS `.planning/PROJECT.md`. Add SDS-specific fields:

```yaml
---
type: SDS
version: 0.1
status: scaffolded
language: {FDS_LANGUAGE}
---

# Project: {FDS_PROJECT_NAME} — Software Design Specification

## Overview

This is the Software Design Specification (SDS) for {FDS_PROJECT_NAME}.

**Based on:**
- Document: FDS (Functional Design Specification)
- Version: v{FDS_VERSION}
- Date: {FDS_DATE}

**Client:** {CLIENT}
**Location:** {LOCATION}
**Project Type:** Type {FDS_TYPE}

## SDS Configuration

**Version:** v0.1 (scaffolded — not yet complete)
**Structure Preset:** {structure_preset} (equipment-first or software-first)
**Language:** {FDS_LANGUAGE} (inherited from FDS)

## Typicals Library

**Mode:** {TYPICALS_MODE} (external | imported | none)
{if external or imported:}
**Library Name:** {library_name}
**Library Version:** v{library_version}
**Platform:** {platform}
**Path:** {typicals_path}
{if none:}
**Mode:** Skeleton mode — custom FBs required for all equipment modules

## Standards

**Software:** TIA Portal V18+, IEC 61131-3
{if FDS has PackML:}
**PackML:** States mapped from FDS equipment module states
{if FDS has ISA-88:}
**ISA-88:** Hierarchy maintained from FDS

## Workflow Status

**Current Phase:** SDS Phase 1 (Foundation)
**Next Step:** Run `/doc:discuss-phase 1 --sds` to discuss SDS foundation

---

*SDS project scaffolded: {current_date}*
*Source FDS: v{FDS_VERSION}*
```

Save to: `.planning/sds/PROJECT.md`

### 7.3 Create SDS ROADMAP.md

Define 3-phase SDS structure:

```markdown
# SDS Roadmap — {FDS_PROJECT_NAME}

**Based on FDS:** v{FDS_VERSION}
**SDS Structure:** {structure_preset}

---

## Phase Overview

| Phase | Name | Focus | Status |
|-------|------|-------|--------|
| SDS-01 | Foundation + Typicals Matching | Software architecture overview, confirm/override typical matches, library setup | Pending |
| SDS-02 | Equipment Module Details | Write SDS sections per equipment module using seeds from scaffolding | Pending |
| SDS-03 | Integration + Assembly | Interfaces, HMI, final SDS assembly, TRACEABILITY verification | Pending |

---

## SDS-01: Foundation + Typicals Matching Confirmation

**Goal:** Establish software architecture foundation and finalize typical assignments.

**Sections:**
- 2.1 Program Structure (TIA Portal project organization: OBs, FCs, FBs, DBs)
- 2.2 FB Hierarchy Overview (high-level FB composition and calling relationships)
- 2.3 Communication Architecture (network topology, protocols, PLC-to-PLC, SCADA)
- 3.1 Library Metadata (typicals library configuration)
- 3.2 Typicals Summary (all typicals used in project with descriptions and interfaces)
{if unmatched modules exist:}
- 3.3 Unmatched Equipment Modules (NEW TYPICAL NEEDED list with design requirements)

**Engineer Tasks:**
- Review MATCHING-REPORT.md: confirm HIGH confidence matches, review MEDIUM/LOW matches, override if needed
- Design custom FBs for NEW TYPICAL NEEDED modules (add to project typicals library)
- Define overall program structure (CPU allocation, OB organization)
- Create FB hierarchy diagram showing equipment module relationships

**Outcome:** Software architecture established, all typical assignments finalized.

---

## SDS-02: Equipment Module Details

**Goal:** Complete SDS sections for each equipment module using seeds from scaffolding.

**Sections:**
- 4.1 {Equipment Module 1 Name} (6 subsections: Typical Assignment, FB Composition, Instantiation, Parameter Configuration, Data Flow, State Machine Implementation)
- 4.2 {Equipment Module 2 Name}
- ... (one section per FDS equipment module)

**Engineer Tasks:**
- For matched modules: Review auto-filled content, refine FB composition, assign DB numbers, map parameters, verify state machine
- For NEW TYPICAL modules: Implement custom FB, document FB composition, configure parameters
- Create Mermaid diagrams for FB hierarchy and data flow per module
- Map FDS states to FB state variables with transition logic

**Outcome:** All equipment modules have complete SDS sections with FB details.

---

## SDS-03: Integration + Assembly

**Goal:** Complete interface sections, HMI integration, assemble final SDS, verify traceability.

**Sections:**
- 5.1 Internal Interfaces (PLC-to-PLC communication, data exchange)
- 5.2 External Interfaces (SCADA, MES, field devices)
- 6.1 HMI Tag Mapping (equipment module tags to SCADA)
- 6.2 Alarm Configuration (alarm classes, priorities, HMI display)
- 7.x Appendices (I/O summary, abbreviations, revision history)

**Engineer Tasks:**
- Document interface protocols and data structures
- Map all equipment module tags to HMI SCADA tags
- Configure alarm handling and display
- Update TRACEABILITY.md with implementation details (FB/DB references)
- Verify 100% FDS-to-SDS requirement coverage
- Run /doc:complete-fds --sds to assemble final SDS document

**Outcome:** Complete, verified SDS ready for client delivery.

---

*SDS Roadmap created: {current_date}*
*3 phases: Foundation → Equipment Details → Integration*
```

Save to: `.planning/sds/ROADMAP.md`

### 7.4 Create SDS STATE.md

Initialize SDS state tracking:

```markdown
# STATE.md — SDS Project

## Project Reference

See: .planning/sds/PROJECT.md (scaffolded {current_date})

**Core value:** Transform completed FDS into detailed Software Design Specification through typicals matching and structured discuss-plan-write-verify workflow
**Current focus:** SDS Phase 1 (Foundation + Typicals Matching Confirmation)

## Current Position

- Phase: 1 of 3 (Foundation)
- Plan: 0 of 0 (no plans yet — run /doc:plan-phase 01 --sds)
- Status: Pending
- Last activity: {current_date} - SDS project scaffolded from FDS v{FDS_VERSION}
- Next: Run /doc:discuss-phase 1 --sds to discuss foundation

## Progress

Progress: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ~0%

| Phase | Name | Plans | Status |
|-------|------|-------|--------|
| SDS-01 | Foundation + Typicals Matching | 0/0 | Pending |
| SDS-02 | Equipment Module Details | 0/0 | Pending |
| SDS-03 | Integration + Assembly | 0/0 | Pending |

## Decisions

- SDS scaffolded from FDS v{FDS_VERSION} ({current_date})
- Typicals mode: {TYPICALS_MODE} ({library_name} v{library_version} or "none")
- Structure preset: {structure_preset}
{if matched modules:}
- Typical matches: {matched_count} modules matched, {new_count} need custom FB
{if all new:}
- No typicals library — all {total_modules} modules need custom FB development

## Blockers

(None)

## Session Continuity

Last session: {current_date}
Stopped at: SDS project scaffolded — ready for Phase 1 discuss
Resume file: N/A

---
*Last updated: {current_date}*
```

Save to: `.planning/sds/STATE.md`

### 7.5 Create SDS REQUIREMENTS.md

Derive SDS requirements from FDS:

```markdown
# SDS Requirements — {FDS_PROJECT_NAME}

**Derived from:** FDS v{FDS_VERSION}
**Focus:** Software implementation requirements

---

## Software Architecture Requirements

{Extract system-level requirements from FDS section 2.x, rephrased for software focus}

**Example:**
- REQ-SDS-001: TIA Portal project must support CPU 1515-2 PN with distributed I/O
- REQ-SDS-002: Program structure must separate safety FBs from standard FBs
- REQ-SDS-003: Communication must use PROFINET IRT for time-critical I/O

## Equipment Module Software Requirements

{Extract equipment module requirements from FDS section 4.x, focused on software behavior}

**Example (per module):**
### EM-200: Dosing System
- REQ-SDS-101: Dosing system must implement PackML states (Idle, Running, Stopped)
- REQ-SDS-102: Flow control must use PI control loop with configurable setpoint
- REQ-SDS-103: Alarm delay must be configurable (range: 1-30 seconds)

## Interface Requirements

{Extract interface requirements from FDS section 5.x}

**Example:**
- REQ-SDS-201: SCADA interface must expose all equipment module states and alarms
- REQ-SDS-202: PLC-to-PLC communication must use IEC 104 protocol

---

*Derived from FDS v{FDS_VERSION}*
*Engineer may add software-specific requirements during SDS Phase 1*
```

Save to: `.planning/sds/REQUIREMENTS.md`

**Note:** If FDS has a dedicated REQUIREMENTS.md, parse and transform those. Otherwise, derive from inline requirements in FDS sections.

### 7.6 Display Scaffolding Summary

```
DOC > SDS Project Structure Created:
DOC >   .planning/sds/PROJECT.md
DOC >   .planning/sds/ROADMAP.md (3 phases)
DOC >   .planning/sds/STATE.md
DOC >   .planning/sds/REQUIREMENTS.md
DOC >   .planning/sds/TRACEABILITY.md
DOC >   .planning/sds/phases/sds-01-foundation/
DOC >   .planning/sds/phases/sds-02-equipment/ ({module_count} seeds)
DOC >   .planning/sds/phases/sds-03-integration/
```

**Verification:**
- [ ] .planning/sds/ directory created
- [ ] PROJECT.md created with SDS version 0.1, based_on FDS version
- [ ] ROADMAP.md created with 3-phase structure
- [ ] STATE.md initialized at Phase 1, Pending
- [ ] REQUIREMENTS.md derived from FDS
- [ ] Phase directories created
- [ ] Equipment module seeds saved to sds-02-equipment/

---

## Step 8: Generate Typicals Matching Report

**Objective:** Create human-readable matching report for engineer review during SDS Phase 1 discuss.

### 8.1 Create MATCHING-REPORT.md

```markdown
# Typicals Matching Report — {FDS_PROJECT_NAME}

**Generated:** {current_date}
**FDS Version:** v{FDS_VERSION}
**Typicals Library:** {library_name} v{library_version} ({TYPICALS_MODE})
{or if skeleton mode:}
**Typicals Library:** None — skeleton mode (custom FBs required)

---

## Summary

| Equipment Module | Module Name | Suggested Typical | Confidence | Status |
|------------------|-------------|-------------------|------------|--------|
{for each module:}
| {module_id} | {module_name} | {typical_id or "None"} | {score}% ({level}) | {Matched or NEW TYPICAL NEEDED} |

**Statistics:**
- Total modules: {total}
- Matched (HIGH): {high_count}
- Matched (MEDIUM): {medium_count}
- Matched (LOW): {low_count}
- NEW TYPICAL NEEDED: {new_count}

---

## Detailed Comparison

{for each module:}

### {module_id}: {module_name}

**FDS Requirements Summary:**
- **I/O:** {DI} DI, {DO} DO, {AI} AI, {AO} AO
- **States:** {state_count} ({state_names})
- **Parameters:** {param_count}
- **Keywords:** {keywords}

{if matched:}

**Suggested Typical: {typical_id}**

| Aspect | FDS Requirement | Typical Provides | Match Score | Analysis |
|--------|-----------------|------------------|-------------|----------|
| Inputs | {FDS_inputs} | {typical_inputs} | {input_score}/40 | {exact / partial / mismatch} |
| Outputs | {FDS_outputs} | {typical_outputs} | {output_score}/40 | {exact / partial / mismatch} |
| States | {FDS_states} | {typical_states} | {state_score}/20 | {aligned / similar / different} |
| Keywords | {FDS_keywords} | {typical_use_cases} | {keyword_score}/30 | {strong / moderate / weak} |
| Category | {FDS_category} | {typical_category} | {category_score}/10 | {match / no match} |
| **Total** | - | - | **{total_score}/100** | **{confidence_level}** |

**Interface Match Analysis:**
- **Inputs:** {detailed analysis of DI/AI alignment, e.g., "Exact match on 2 DI, 1 AI. Typical has 1 extra enable input (can be hardwired)."}
- **Outputs:** {detailed analysis of DO/AO alignment, e.g., "FDS requires 2 DO (motor + alarm), typical provides 3 DO (motor + alarm + fault). Extra output unused."}
- **Data Types:** {BOOL/INT/REAL compatibility, e.g., "All BOOL signals compatible. AI is REAL, matches typical."}

**Recommendation:**
- **{HIGH}:** ACCEPT MATCH — High confidence match. Proceed with {typical_id} for this module.
- **{MEDIUM}:** REVIEW INTERFACES — Moderate confidence. Verify I/O alignment and parameter compatibility before proceeding.
- **{LOW}:** MANUAL DECISION — Low confidence match. Engineer discretion required. Consider alternatives: {alt1}, {alt2}.

{else if NEW TYPICAL NEEDED:}

**Status: NEW TYPICAL NEEDED**

**Reason:** No catalog typical matches this equipment module (confidence < 30% for all typicals).

**Requirements for Custom FB:**

**I/O Profile:**
- **Inputs:** {list all DI with names}, {list all AI with names}
- **Outputs:** {list all DO with names}, {list all AO with names}

**State Machine:**
- **States:** {list all state names from FDS}
- **Transitions:** {extract state transitions if documented in FDS, else "See FDS section {section} for state transition logic"}

**Parameters:**
{table of parameters with ranges and units from FDS}

| Parameter | Range | Unit | Source |
|-----------|-------|------|--------|
| {param1} | {range1} | {unit1} | FDS section {section} |
| {param2} | {range2} | {unit2} | FDS section {section} |

**Design Notes:**
- Custom FB design required during SDS Phase 1 (Foundation).
- Once designed, add to project typicals library for reuse.
- Consider reusability: if similar equipment exists in future projects, document as a new typical.

**Priority:** {HIGH if many instances / MEDIUM if single instance}

{end if}

---

{end for each module}

---

## Instructions for Engineer

**Review this report during `/doc:discuss-phase 1 --sds` (SDS Foundation phase).**

**For HIGH confidence matches:**
- Accept and proceed — these are strong matches.

**For MEDIUM/LOW confidence matches:**
- Review interface details carefully.
- Check if extra inputs/outputs in typical can be left unused or hardwired.
- Verify parameter compatibility.
- Override to different typical if needed (or mark as NEW TYPICAL).

**For NEW TYPICAL NEEDED modules:**
- Design custom FB during SDS Phase 1.
- Document FB in project typicals library.
- Once designed, complete SDS section during Phase 2.

**Override mechanism:**
- During discuss-phase, you can change any typical assignment.
- Update `.planning/sds/phases/sds-02-equipment/{module}-seed.md` manually.
- Matching suggestions are NOT auto-applied — always engineer-confirmed.

---

*Auto-generated by /doc:generate-sds workflow*
*All suggestions require engineer confirmation*
```

Save to: `.planning/sds/MATCHING-REPORT.md`

### 8.2 Display Matching Report Summary

```
DOC > Matching Report: MATCHING-REPORT.md created
DOC >   Review during /doc:discuss-phase 1 --sds
DOC >   Confirm or override typical assignments before Phase 2
```

**Verification:**
- [ ] MATCHING-REPORT.md created with summary table
- [ ] Detailed comparison for each module with confidence scoring
- [ ] NEW TYPICAL NEEDED modules have design requirements listed
- [ ] Engineer instructions included
- [ ] Report saved to .planning/sds/

---

## Step 9: Update PROJECT.md with SDS Configuration

**Objective:** Add SDS section to the main FDS PROJECT.md so other commands can detect SDS project existence.

### 9.1 Read Main PROJECT.md

Read `.planning/PROJECT.md` (FDS project configuration).

### 9.2 Add SDS Section

Append SDS configuration to PROJECT.md:

```yaml

## SDS Configuration

**SDS Version:** v0.1 (scaffolded)
**Based on FDS:** v{FDS_VERSION} ({FDS_DATE})
**Structure Preset:** {structure_preset}
**Typicals:**
  - Mode: {TYPICALS_MODE}
{if external or imported:}
  - Library: {library_name} v{library_version}
  - Path: {typicals_path}
{if imported:}
  - Imported to: references/typicals/
{if none:}
  - Library: None (skeleton mode — custom FBs required)

**SDS Workflow:**
- Current Phase: SDS Phase 1 (Foundation)
- Status: Pending
- Next Step: /doc:discuss-phase 1 --sds
```

**If SDS section already exists**, update version and status instead of appending.

### 9.3 Display Update Confirmation

```
DOC > Updated PROJECT.md with SDS configuration
```

**Verification:**
- [ ] Main PROJECT.md updated with SDS section
- [ ] SDS version, based_on FDS version, typicals mode documented
- [ ] Other commands (/doc:status, /doc:export) can now detect SDS project

---

## Step 10: Update STATE.md

**Objective:** Update main FDS STATE.md to reflect SDS generation activity.

### 10.1 Read Main STATE.md

Read `.planning/STATE.md` (FDS state tracking).

### 10.2 Add SDS Version Tracking

If `## Versions` section exists, add SDS version:

```markdown
## Versions

- FDS: v{FDS_VERSION} (released {FDS_DATE})
- SDS: v0.1 (scaffolded {current_date})
```

If section doesn't exist, create it.

### 10.3 Update Session Continuity

Update `## Session Continuity`:

```markdown
## Session Continuity

Last session: {current_date}
Stopped at: SDS project scaffolded from FDS v{FDS_VERSION}
Next: Run /doc:discuss-phase 1 --sds to begin SDS Foundation phase
Resume file: N/A
```

### 10.4 Add Decision (optional)

If significant typicals decision made (e.g., external vs imported, skeleton mode), add to `## Decisions`:

```markdown
- SDS scaffolded from FDS v{FDS_VERSION} with {TYPICALS_MODE} typicals mode ({current_date})
```

### 10.5 Display Update Confirmation

```
DOC > Updated STATE.md with SDS scaffolding activity
```

**Verification:**
- [ ] STATE.md updated with SDS version v0.1
- [ ] Session continuity reflects SDS scaffolding
- [ ] Decision added if applicable

---

## Step 11: Git Commit

**Objective:** Commit all SDS project files with structured commit message.

### 11.1 Stage SDS Files

```bash
git add .planning/sds/
git add .planning/PROJECT.md
git add .planning/STATE.md
{if imported typicals:}
git add references/typicals/
```

### 11.2 Commit with Structured Message

```bash
git commit -m "$(cat <<'EOF'
feat(sds): scaffold SDS project from FDS v{FDS_VERSION}

- SDS project structure created in .planning/sds/
- PROJECT.md, ROADMAP.md, STATE.md, REQUIREMENTS.md initialized
- Typicals mode: {TYPICALS_MODE} ({library_name} v{library_version} or "none")
- Equipment modules: {total} ({matched} matched, {new} need custom FB)
- TRACEABILITY.md generated with {req_count} FDS requirements
- MATCHING-REPORT.md created with confidence-scored suggestions
- Equipment module seeds generated in sds-02-equipment/
- Ready for /doc:discuss-phase 1 --sds
EOF
)"
```

### 11.3 Display Commit Confirmation

```
DOC > Committed SDS project files to git
```

**Verification:**
- [ ] All SDS files staged
- [ ] Commit message structured with summary and details
- [ ] Git commit successful

---

## Step 12: Display Summary

**Objective:** Show comprehensive summary of SDS generation with next steps.

### 12.1 Display Success Banner

```
╔══════════════════════════════════════════════════════════════╗
║  SDS PROJECT SCAFFOLDED                                      ║
╚══════════════════════════════════════════════════════════════╝

DOC > ════════════════════════════════════════
DOC > SDS Project Scaffolded
DOC > ════════════════════════════════════════
DOC > Based on:   FDS v{FDS_VERSION} ({FDS_DATE})
{if typicals loaded:}
DOC > Typicals:   {typicals_count} loaded from {library_name} v{library_version} ({TYPICALS_MODE})
{else:}
DOC > Typicals:   None — skeleton mode (custom FBs required)
DOC > Modules:    {total} equipment modules analyzed
{if typicals loaded:}
DOC >   Matched:  {matched} ({high} HIGH, {medium} MEDIUM, {low} LOW)
DOC >   New:      {unmatched} modules need NEW TYPICAL
{else:}
DOC >   New:      {total} modules need custom FB development
DOC > Structure:  {structure_preset}
DOC > SDS Version: v0.1 (scaffolded)
DOC > ════════════════════════════════════════
DOC >
DOC > Created Files:
DOC >   .planning/sds/PROJECT.md
DOC >   .planning/sds/ROADMAP.md (3 phases)
DOC >   .planning/sds/STATE.md
DOC >   .planning/sds/REQUIREMENTS.md
DOC >   .planning/sds/TRACEABILITY.md ({req_count} requirements)
DOC >   .planning/sds/MATCHING-REPORT.md
DOC >   .planning/sds/phases/sds-02-equipment/ ({module_count} module seeds)
DOC >
DOC > Next Steps:
DOC > ════════════════════════════════════════
DOC > 1. Review MATCHING-REPORT.md in .planning/sds/
{if typicals loaded:}
DOC >    - Confirm HIGH confidence matches
DOC >    - Review MEDIUM/LOW confidence matches
DOC >    - Override assignments if needed
{if unmatched > 0:}
DOC > 2. Design custom FBs for {unmatched} NEW TYPICAL NEEDED modules
{else:}
DOC > 2. Design custom FBs for all {total} equipment modules
DOC > 3. Run /doc:discuss-phase 1 --sds to discuss SDS Phase 1 (Foundation)
DOC > 4. Run full discuss → plan → write → verify cycle for each SDS phase
DOC > 5. Run /doc:complete-fds --sds to assemble final SDS document
DOC >
DOC > SDS Workflow:
DOC >   Phase 1: Foundation + Typicals Matching Confirmation
DOC >   Phase 2: Equipment Module Details (write SDS sections)
DOC >   Phase 3: Integration + Assembly (interfaces, HMI, verify)
```

(Adapt to Dutch if `FDS_LANGUAGE = "nl"`)

### 12.2 Return Success

Return control to the command caller. The SDS project is now scaffolded and ready for the discuss-plan-write-verify workflow.

**Verification:**
- [ ] Success banner displayed with comprehensive summary
- [ ] Next steps clearly communicated
- [ ] Engineer knows to review MATCHING-REPORT.md and run /doc:discuss-phase 1 --sds

---

</workflow>

## Workflow Verification

**Complete workflow checklist:**

- [ ] Step 1: FDS prerequisites validated (assembled FDS exists, metadata extracted, content verified)
- [ ] Step 2: Typicals library loaded (external/imported/none mode, CATALOG.json validated)
- [ ] Step 3: Equipment modules extracted from FDS (I/O, states, parameters, keywords)
- [ ] Step 4: Matching algorithm run with confidence scoring (I/O 40%, keywords 30%, states 20%, category 10%)
- [ ] Step 5: SDS equipment module seeds generated (matched with typical reference, unmatched with structured skeleton)
- [ ] Step 6: TRACEABILITY.md generated (FDS-to-SDS requirement mapping, coverage analysis)
- [ ] Step 7: SDS project structure scaffolded (PROJECT.md, ROADMAP.md, STATE.md, REQUIREMENTS.md, phase directories)
- [ ] Step 8: MATCHING-REPORT.md generated (human-readable matching analysis for engineer review)
- [ ] Step 9: Main PROJECT.md updated with SDS configuration
- [ ] Step 10: Main STATE.md updated with SDS scaffolding activity
- [ ] Step 11: Git commit with structured message
- [ ] Step 12: Comprehensive summary displayed with next steps

**Pattern adherence:**

- Lean command file (62 lines) + detailed workflow file (this file, ~1600 lines) separation maintained
- DOC > prefix used for all stage banners
- Typicals matching uses suggest + confirm pattern (never auto-applied)
- Unmatched modules get structured skeleton from FDS (not stubs)
- SDS gets independent versioning with based_on FDS cross-reference
- SDS project ready for full discuss-plan-write-verify cycle

---

*Workflow version: 1.0*
*Created: 2026-02-14*
*Pattern: SDS scaffolding from completed FDS with typicals matching and project setup*
