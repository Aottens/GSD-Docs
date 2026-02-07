<workflow>

# /doc:new-fds Workflow

Complete execution logic for project initialization. The command file (`~/.claude/commands/doc/new-fds.md`) delegates here. Follow each step in order.

**Template composition rule:** This workflow READS templates from `~/.claude/gsd-docs-industrial/templates/` and FILLS placeholders with gathered metadata. Templates are structure references -- never copy them verbatim. Produce populated, project-specific content.

**Completion proof pattern:** SUMMARY.md existence (not STATE.md status) is the authoritative proof that a section or phase is complete. Downstream commands (`/doc:discuss-phase`, `/doc:verify-phase`) check for SUMMARY.md files to determine what is done. STATE.md is a convenience tracker that may become stale. This pattern is established here at project creation and used throughout the workflow.

---

## Step 1: Prerequisites Check

**Execute these checks before any user interaction.**

### 1.1 Git Repository

```bash
if [ -d .git ] || [ -f .git ]; then
    echo "Git repo exists"
else
    git init
    echo "Initialized new git repo"
fi
```

### 1.2 Existing Project Check

```bash
if [ -d .planning ]; then
    echo "EXISTING_PROJECT"
else
    echo "CLEAN"
fi
```

**If `.planning/` exists**, display error box and abort:

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

A project is already initialized in this directory.
The .planning/ directory already exists.

**To fix:** Use `/doc:status` to check project progress,
or remove .planning/ to start fresh.
```

Stop execution. Do not continue.

### 1.3 Optional Tools Check

```bash
pandoc --version 2>/dev/null && echo "PANDOC_OK" || echo "PANDOC_MISSING"
mmdc --version 2>/dev/null && echo "MMDC_OK" || echo "MMDC_MISSING"
```

If either tool is missing, show info (not error):

```
Note: Optional tools not found:
- pandoc: needed for /doc:export (DOCX generation)
- mmdc (mermaid-cli): needed for /doc:export (diagram rendering)

These are not required now. Install before running /doc:export.
```

Continue regardless.

---

## Step 2: Language Selection

**ALWAYS ask language FIRST.** No default is assumed.

Use AskUserQuestion:
- header: "Language / Taal"
- question: "In which language should the FDS documentation be written? / In welke taal moet de FDS documentatie geschreven worden?"
- options:
  - "Nederlands (Dutch)" -- FDS output and all prompts in Dutch
  - "English" -- FDS output and all prompts in English

Store the choice as `LANGUAGE` ("nl" or "en").

**Bilingual instruction:** From this point forward, ALL user-facing text must match the chosen language:
- If `LANGUAGE = "nl"`: Use Dutch for AskUserQuestion prompts, banners, summary text, and output files
- If `LANGUAGE = "en"`: Use English for all user-facing text

The examples below show English. When language is Dutch, translate all user-facing strings.

---

## Step 3: Classification -- Stage 1 (Type Determination)

Display stage banner:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > CLASSIFYING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

(Dutch: `DOC > CLASSIFICEREN`)

### 3.1 Primary Split

Use AskUserQuestion:
- header: "Project Type / Projecttype"
- question: "New system or modification of existing? / Nieuw systeem of modificatie van bestaand?"
- options:
  - "New system / Nieuw systeem"
  - "Modification of existing / Modificatie van bestaand"

### 3.2 Secondary Classification

**If NEW SYSTEM selected:**

Use AskUserQuestion:
- header: "Standards / Standaarden"
- question: "Are formal standards required (PackML, ISA-88)? / Zijn formele standaarden vereist (PackML, ISA-88)?"
- options:
  - "Yes, formal standards / Ja, formele standaarden" -- suggests Type A
  - "No, flexible approach / Nee, flexibele aanpak" -- suggests Type B

**If MODIFICATION selected:**

Use AskUserQuestion:
- header: "Modification Scope / Omvang Modificatie"
- question: "What is the scope of the modification? / Wat is de omvang van de modificatie?"
- options:
  - "Substantial (multiple EMs, new functionality) / Substantieel (meerdere EMs, nieuwe functionaliteit)" -- suggests Type C
  - "Limited (single change, TWN) / Beperkt (enkele wijziging, TWN)" -- suggests Type D

### 3.3 Confirm or Override

Based on the answers, determine the SUGGESTED_TYPE (A, B, C, or D).

Type descriptions (English / Dutch):
- **Type A**: Greenfield + Standards -- New installation with formal PackML/ISA-88 compliance, 6 phases / Nieuwbouw + Standaarden -- Nieuwe installatie met formele PackML/ISA-88 naleving, 6 fasen
- **Type B**: Greenfield Flex -- New installation with pragmatic standards, 4-5 phases / Nieuwbouw Flex -- Nieuwe installatie met pragmatische standaarden, 4-5 fasen
- **Type C**: Modification Large -- Substantial modification with baseline, 3-4 phases / Modificatie Groot -- Substantiele modificatie met baseline, 3-4 fasen
- **Type D**: Modification Small (TWN) -- Limited change, technical change notification, 2 phases / Modificatie Klein (TWN) -- Beperkte wijziging, technische wijzigingsnotitie, 2 fasen

Use AskUserQuestion:
- header: "Project Classification / Projectclassificatie"
- question: "Based on your answers, this is a **Type {SUGGESTED_TYPE}** project: {description}. Confirm or select a different type. / Op basis van uw antwoorden is dit een **Type {SUGGESTED_TYPE}** project: {description}. Bevestig of selecteer een ander type."
- options:
  - "Type A -- {description_a}"
  - "Type B -- {description_b}"
  - "Type C -- {description_c}"
  - "Type D -- {description_d}"

The suggested type should be visually indicated (e.g., appended with "(suggested)" or "(aanbevolen)").

### 3.4 Override Warning

If the user selects a type that DIFFERS from the suggested type, show a warning:

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: Warning                                         ║
╚══════════════════════════════════════════════════════════════╝

Your answers suggest Type {SUGGESTED} but you selected Type {SELECTED}.

Type {SUGGESTED}: {consequence_of_mismatch}
Type {SELECTED}: {what_they_chose}

Proceeding with Type {SELECTED}.
```

Consequences to mention:
- Selecting a simpler type than suggested: "You may miss important sections (e.g., safety, interfaces, appendices) that your project scope warrants."
- Selecting a more complex type than suggested: "You may have unnecessary phases and overhead for your project scope."

Continue with the user's selected type. Store as `PROJECT_TYPE`.

---

## Step 4: Classification -- Stage 2 (Metadata Gathering)

### 4.1 Core Metadata

Ask these questions inline (freeform, not AskUserQuestion):

1. **Project name:** "What is the project name? / Wat is de projectnaam?"
   - Store as `PROJECT_NAME`

2. **Client name:** "Who is the client? / Wie is de opdrachtgever?"
   - Store as `CLIENT`

3. **Location/site:** "What is the location or site? (optional) / Wat is de locatie? (optioneel)"
   - Store as `LOCATION` (empty string if skipped)

4. **Estimated equipment modules:** "How many equipment modules (EMs) do you estimate? (approximate is fine) / Hoeveel equipment modules (EMs) schat u in? (een schatting is voldoende)"
   - Store as `EM_COUNT`
   - This calibrates scope and informs future dynamic ROADMAP evolution (>5 EMs may trigger phase expansion after System Overview)

### 4.2 Standards Configuration (Type A only)

**Only ask if `PROJECT_TYPE = A`:**

Use AskUserQuestion:
- header: "Standards Configuration / Standaarden Configuratie"
- question: "Which standards apply to this project? Both are enabled by default for Type A. / Welke standaarden zijn van toepassing? Beide zijn standaard ingeschakeld voor Type A."
- multiSelect: true
- options:
  - "PackML (state model, operating modes) / PackML (toestandsmodel, bedrijfsmodi)" -- enabled by default
  - "ISA-88 (equipment hierarchy, terminology) / ISA-88 (equipment hierarchie, terminologie)" -- enabled by default

Store as `PACKML_ENABLED` and `ISA88_ENABLED` (both default true for Type A).

**For Type B:** `PACKML_ENABLED = false`, `ISA88_ENABLED = false` (standards are pragmatic, not enforced).
**For Type C/D:** `PACKML_ENABLED = false`, `ISA88_ENABLED = false` (standards come from existing system, not configured here).

### 4.3 Existing System Information (Type C/D only)

**Only ask if `PROJECT_TYPE = C or D`:**

1. **Existing system name:** "What is the name/version of the existing system? / Wat is de naam/versie van het bestaande systeem?"
   - Store as `EXISTING_SYSTEM`

2. Use AskUserQuestion:
   - header: "Existing Documentation / Bestaande Documentatie"
   - question: "Do existing documents (FDS, P&ID, specifications) exist for the current system? / Bestaan er bestaande documenten (FDS, P&ID, specificaties) voor het huidige systeem?"
   - options:
     - "Yes, I have existing documentation / Ja, ik heb bestaande documentatie"
     - "No, we'll describe from scratch / Nee, we beschrijven vanaf nul"

   - **If yes:** Show instruction:
     ```
     Please place existing documents in the intake/ folder.
     They will be referenced when building the baseline.

     Plaats bestaande documenten in de intake/ map.
     Ze worden gebruikt als referentie voor de baseline.
     ```
     Store `HAS_EXISTING_DOCS = true`

   - **If no:** Store `HAS_EXISTING_DOCS = false`
     Proceed -- BASELINE.md will be populated through structured description during scaffolding.

---

## Step 5: Scaffold Workspace

Display stage banner:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > SCAFFOLDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

(Dutch: `DOC > OPZETTEN PROJECTSTRUCTUUR`)

### 5.1 Create Directory Structure

```bash
mkdir -p .planning/phases
mkdir -p intake
mkdir -p output
mkdir -p diagrams/mermaid diagrams/rendered
mkdir -p export
```

### 5.2 Generate PROJECT.md

Read the template from `@~/.claude/gsd-docs-industrial/templates/project.md`.

Replace ALL placeholders with gathered metadata:

- `{PROJECT_NAME}` -> `PROJECT_NAME`
- `{TYPE}` -> `PROJECT_TYPE` (A, B, C, or D)
- `{CLIENT}` -> `CLIENT`
- `{LOCATION}` -> `LOCATION`
- `{DATE}` -> current date (YYYY-MM-DD)
- `{IS_MODIFICATION}` -> `true` for Type C/D, `false` for A/B
- `{BASELINE_SYSTEM}` -> `EXISTING_SYSTEM` (or empty for A/B)
- `{BASELINE_VERSION}` -> from metadata or empty
- `{PACKML_ENABLED}` -> `PACKML_ENABLED`
- `{ISA88_ENABLED}` -> `ISA88_ENABLED`
- `{LANGUAGE}` -> `LANGUAGE` ("nl" or "en")

Synthesize the descriptive sections from gathered context:
- **What This Is:** Combine project name, type, and purpose into a clear description
- **Core Value:** Describe the primary engineering value this documentation delivers
- **Scope In:** Derive from project type (new system deliverables vs modification delta)
- **Scope Out:** Derive from project type (what is explicitly NOT covered)
- **Constraints:** Fill standards, timeline, and technical constraints from classification
- **Key Decisions:** Include type classification decision and language selection

Write to `.planning/PROJECT.md`.

### 5.3 Generate ROADMAP.md

Load the correct roadmap template based on project type:
- Type A: `@~/.claude/gsd-docs-industrial/templates/roadmap/type-a-nieuwbouw-standaard.md`
- Type B: `@~/.claude/gsd-docs-industrial/templates/roadmap/type-b-nieuwbouw-flex.md`
- Type C: `@~/.claude/gsd-docs-industrial/templates/roadmap/type-c-modificatie.md`
- Type D: `@~/.claude/gsd-docs-industrial/templates/roadmap/type-d-twn.md`

Replace ALL placeholders:
- `{PROJECT_NAME}` -> `PROJECT_NAME`
- `{CLIENT}` -> `CLIENT`
- `{DATE}` -> current date
- `{LANGUAGE}` -> `LANGUAGE`

The roadmap template already contains the correct phase structure, success criteria, and dependency chain for the type. Fill the placeholders and ensure the content is project-specific.

Write to `.planning/ROADMAP.md`.

### 5.4 Generate REQUIREMENTS.md

Read the template from `@~/.claude/gsd-docs-industrial/templates/requirements.md`.

Create the category structure based on project type:

**Type A categories:**
1. Foundation (FNDN)
2. System Architecture (ARCH)
3. Equipment Modules (EQPM)
4. Control & HMI (CTRL)
5. Interfaces & Safety (INTF)
6. Appendices (APPX)

**Type B categories:**
1. Foundation (FNDN)
2. System Overview (SYSV)
3. Functional Units (FUNC)
4. HMI & Interfaces (HMII)
5. Appendices (APPX)

**Type C categories:**
1. Scope & Baseline (SCOP)
2. Delta Functional (DFNC)
3. Delta HMI (DHMI)
4. Verification (VERF)

**Type D categories:**
1. Change (CHNG)
2. Implementation (IMPL)

Each category gets a placeholder requirement: "Requirements to be identified during /doc:discuss-phase" / "Eisen worden geidentificeerd tijdens /doc:discuss-phase"

Create a traceability table linking categories to ROADMAP phases.

Write to `.planning/REQUIREMENTS.md`.

### 5.5 Generate STATE.md

Read the template from `@~/.claude/gsd-docs-industrial/templates/state.md`.

Fill with:
- `{PROJECT_NAME}` -> `PROJECT_NAME`
- `{DATE}` -> current date
- `{CORE_VALUE}` -> synthesized core value
- `{PHASE_COUNT}` -> number of phases from ROADMAP
- `{PHASE_1_NAME}` -> first phase name from ROADMAP
- `{PROGRESS_BAR}` -> all empty blocks (0%)
- `{PHASE_TABLE}` -> table rows from ROADMAP, all "Pending"

Include the classification decision in Decisions section:
- "Project classified as Type {TYPE}: {description}" with date

Write to `.planning/STATE.md`.

### 5.6 Generate config.json

Create `.planning/config.json`:

```json
{
  "project_type": "{PROJECT_TYPE}",
  "language": "{LANGUAGE}",
  "git_integration": true,
  "standards": {
    "packml": {PACKML_ENABLED},
    "isa88": {ISA88_ENABLED}
  }
}
```

Replace placeholders with actual values. Boolean values must be `true` or `false` (not strings).

Write to `.planning/config.json`.

### 5.7 Generate BASELINE.md (Type C/D only)

**Only create if `PROJECT_TYPE = C or D`.**

Read the template from `@~/.claude/gsd-docs-industrial/templates/baseline.md`.

Fill with:
- `{EXISTING_SYSTEM_DESCRIPTION}` -> `EXISTING_SYSTEM` name/version from metadata
- `{DATE}` -> current date

**If `HAS_EXISTING_DOCS = true`:**
- Add note in Source Documents section: "Documents placed in intake/ -- to be processed for baseline extraction"
- Leave equipment and scope sections with clear placeholder markers for extraction

**If `HAS_EXISTING_DOCS = false`:**
- Populate with whatever existing system information was gathered in Step 4
- Leave detailed sections with structured placeholder markers: "{TO BE DESCRIBED during /doc:discuss-phase 1}"

The INSTRUCTIE block is ALWAYS present (bilingual Dutch + English) regardless of project language.

Write to `.planning/BASELINE.md`.

---

## Step 6: Auto-Commit

Stage and commit all scaffolded files:

```bash
git add .planning/ intake/ output/ diagrams/ export/
git commit -m "docs: initialize {PROJECT_NAME} (Type {PROJECT_TYPE})

Project type: Type {PROJECT_TYPE} - {type_description}
Language: {LANGUAGE_DISPLAY}
Phases: {PHASE_COUNT}
Standards: {standards_summary}

Artifacts: PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, config.json{, BASELINE.md if C/D}"
```

Replace all placeholders in the commit message with actual values.

`{type_description}`:
- A: "Greenfield + Standards (PackML, ISA-88)" / "Nieuwbouw + Standaarden"
- B: "Greenfield Flex" / "Nieuwbouw Flex"
- C: "Modification Large" / "Modificatie Groot"
- D: "Modification Small (TWN)" / "Modificatie Klein (TWN)"

`{LANGUAGE_DISPLAY}`: "Nederlands (Dutch)" or "English"

`{standards_summary}`:
- Type A with both: "PackML + ISA-88"
- Type A with one: "PackML" or "ISA-88"
- Type B/C/D: "None (pragmatic)" or "None (from existing system)"

---

## Step 7: Completion Summary

Display banner:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > PROJECT INITIALIZED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

(Dutch: `DOC > PROJECT GEINITIALISEERD`)

### 7.1 Project Summary

Display project overview (in the chosen language):

```
**{PROJECT_NAME}**

| Property      | Value                        |
|---------------|------------------------------|
| Type          | {PROJECT_TYPE} - {type_desc} |
| Client        | {CLIENT}                     |
| Location      | {LOCATION}                   |
| Language      | {LANGUAGE_DISPLAY}           |
| Phases        | {PHASE_COUNT}                |
| Standards     | {standards_summary}          |
```

### 7.2 Artifacts Table

```
| Artifact       | Location                    |
|----------------|-----------------------------|
| Project        | `.planning/PROJECT.md`      |
| Requirements   | `.planning/REQUIREMENTS.md` |
| Roadmap        | `.planning/ROADMAP.md`      |
| State          | `.planning/STATE.md`        |
| Config         | `.planning/config.json`     |
| Baseline       | `.planning/BASELINE.md`     |  <-- only for Type C/D
```

### 7.3 Phase Overview

Show the phase table from ROADMAP.md:

```
| Phase | Name              | Status  |
|-------|-------------------|---------|
| 1     | {phase_1_name}    | Pending |
| 2     | {phase_2_name}    | Pending |
| ...   | ...               | ...     |
```

### 7.4 File Tree

Display the .planning/ directory tree:

```bash
find .planning -type f | sort
```

### 7.5 Next Up Block

```
───────────────────────────────────────────────────────────────

## > Next Up

**Phase 1: {Phase 1 Name}** -- {Goal from ROADMAP}

`/doc:discuss-phase 1`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:status` -- view project progress

───────────────────────────────────────────────────────────────
```

(Dutch: translate "Next Up" to "Volgende Stap", "Also available" to "Ook beschikbaar", etc.)

---

## Workflow Rules

1. **Language consistency:** After Step 2, every user-facing string matches the chosen language. Internal variable names and template placeholders remain English.
2. **Template composition:** Read templates, fill placeholders, synthesize descriptions. Never copy templates verbatim.
3. **SUMMARY.md = completion proof:** Downstream commands check SUMMARY.md existence to determine section completion, not STATE.md status. This pattern is established here and used throughout all subsequent commands.
4. **Error handling:** If any scaffold step fails, show the error box pattern and stop. Do not continue with partial scaffolding.
5. **DOC > prefix:** All banners use `DOC >` (never `GSD >`). This is the namespace separator.
6. **No emoji in text:** Only use status symbols defined in ui-brand.md.

</workflow>
