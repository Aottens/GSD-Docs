# Phase 7: SDS Generation + DOCX Export + Pilot - Research

**Researched:** 2026-02-14
**Domain:** SDS transformation from FDS, TIA Portal typicals matching, Pandoc DOCX conversion, Mermaid diagram rendering, end-to-end validation
**Confidence:** MEDIUM-HIGH

## Summary

Phase 7 closes the GSD-Docs value chain by transforming a completed FDS into a Software Design Specification (SDS) with typicals matching, exporting both documents to client-ready DOCX format with corporate styling, and validating the complete pipeline on a realistic test project. This represents three distinct technical domains: (1) FDS-to-SDS content transformation with project-specific typicals libraries, (2) markdown-to-DOCX conversion with styled output, and (3) integration testing with a fictional but representative industrial automation project.

The research examined: (1) Pandoc ecosystem for DOCX conversion with reference documents, custom styling, and auto-generated lists (TOC, figures, tables), (2) mermaid-cli for server-side diagram rendering to PNG, (3) pandoc-crossref for figure/table numbering and cross-references in DOCX, (4) TIA Portal library structure and external reference patterns, (5) FDS/SDS documentation standards in industrial automation, (6) traceability matrix patterns for requirements-to-implementation linking, and (7) markdown YAML frontmatter for document metadata and versioning.

The critical architectural insight: Phase 7 builds on Phase 5's document assembly patterns but adds two transformative layers. Layer 1 (SDS generation) is NOT a simple template fill — the SDS gets its own discuss-plan-write-verify cycle mirroring the FDS workflow, with `/doc:generate-sds` scaffolding the SDS project structure just as `/doc:new-fds` scaffolds FDS. Layer 2 (DOCX export) must be robust and pinned — Pandoc version matters, reference document integrity is critical, and diagram rendering has complexity budgets. The pilot project validates end-to-end quality, not just technical functionality.

**Primary recommendation:** Use Pandoc 3.9+ with pinned version for DOCX conversion, leveraging `--reference-doc` for corporate styling and `--toc`/`--lof`/`--lot` for auto-generated lists. Use mermaid-cli 11.12+ (via npm) for PNG rendering with complexity budgets (30-40 nodes, 100 max). Use pandoc-crossref as optional enhancement but accept DOCX limitations (bookmarks vs SEQ fields). Structure SDS generation as a full project scaffold (not a transform script) to enable iterative refinement. Build pilot project as Type B (Nieuwbouw Flex) with realistic equipment modules and complete FDS+SDS+DOCX flow.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Typicals catalog & matching:**
- Library is **project-specific**, not a global catalog — different projects may use different libraries (own or customer's)
- Two loading modes required: (1) path reference in PROJECT.md pointing to an external library, (2) import/copy into project's references/ folder for self-containment
- Typicals are at **control module level** — building blocks like FB_AnalogIn, FB_ValveCtrl, FB_MotorCtrl
- MVP scope: **TIA Portal library only** — other platforms (Omron, Allen-Bradley) are future work
- Matching method: **suggest + confirm** — system proposes typical matches based on equipment type/function, engineer confirms or overrides
- Unmatched equipment modules: generate **skeleton SDS section from FDS** (I/O, parameters, states) marked as "NEW TYPICAL NEEDED" — not a stub, but a structured starting point

**SDS content derivation:**
- SDS follows a **hybrid structure**: equipment modules as primary sections, software structure (FB hierarchy, instantiation, data flow) within each
- NOTE: SDS structure may be revisited — this is a preliminary decision, not fully locked
- SDS focus is on **software structure** — which FBs compose each equipment module, how the program is organized — not on documenting typical internals
- Content depth is **both prescriptive and specification**: some sections prescribe structure and FB selection, others specify behavior and timing
- When referencing typicals: **summary + reference** — brief description of purpose and key interfaces, with library reference for full details
- TRACEABILITY.md is an **internal quality check** — not part of client deliverables
- SDS uses **same language** as FDS (inherited from PROJECT.md)
- SDS gets its **own discuss-plan-write-verify cycle** — /doc:generate-sds scaffolds the SDS project (like /doc:new-fds does for FDS), then engineer runs the full workflow per SDS phase
- SDS generates a **complete document**, not a skeleton — engineer reviews and adjusts

**DOCX export & styling:**
- One corporate **huisstijl.docx template exists** — used for all projects (not per-client)
- Export must include **table of contents, list of figures, and list of tables** — auto-generated, standard for formal engineering documents
- External diagrams: **both embed and reference supported** — if PNG exists in diagrams/external/, embed it; if not, show text reference. Engineer's choice.
- Conversion tool and diagram rendering approach: Claude's discretion

**Pilot project scope:**
- Pilot uses a **fictional but realistic test project** — not a real client project
- Project type: **Type B (Nieuwbouw Flex)** — realistic scope without standards overhead
- Pilot must exercise **full pipeline**: FDS + SDS + DOCX export (new-fds through export)
- Success bar: **client-ready quality** — output should be close to what you'd actually send to a client, minimal manual cleanup needed

### Claude's Discretion

- SDS project separation (same .planning/ folder vs separate subfolder)
- SDS-specific templates (new vs adapted from FDS)
- Conversion tool choice (Pandoc or alternative)
- Mermaid rendering approach
- Test project content (fictional but representative Type B industrial scenario)

### Specific Ideas

- "A typical is a building block in software — a piece of software in TIA Portal that handles an analog input, or a digital input"
- "The typicals are most of the time control module level, so we advise on what typicals to use where, furthermore the structure of the software is the most important. Not specifically what typicals."
- "Sometimes we need to use a library from a customer" — library flexibility is essential
- SDS structure decision is preliminary — engineer wants flexibility to revisit after seeing first results

### Deferred Ideas (OUT OF SCOPE)

- Multi-platform typical libraries (Omron, Allen-Bradley) — future milestone
- Per-client huisstijl templates — future enhancement
- SDS structure refinement — may need iteration after MVP experience

</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandoc | 3.9+ | Markdown to DOCX conversion | Universal document converter, 150K+ citations, de facto standard for academic/technical publishing |
| @mermaid-js/mermaid-cli | 11.12+ | Server-side Mermaid diagram rendering | Official mermaid CLI, 4.1K stars, eliminates browser dependency for automation |
| remark | 16.0+ | Markdown AST processing (reuse from Phase 5) | Already established in Phase 5 for section numbering and assembly |
| unified | 12.0+ | Content transformation pipeline (reuse from Phase 5) | Core of remark ecosystem, enables composable markdown transformations |
| gray-matter | 4.0+ | YAML frontmatter parsing (reuse from Phase 5) | Battle-tested, used by major static site generators |
| semver | 7.6+ | Version management (reuse from Phase 5) | Already used for FDS versioning, SDS versions follow same pattern |

**Sources:**
- [Pandoc User's Guide](https://pandoc.org/MANUAL.html) - `--reference-doc`, `--toc`, `--lof`, `--lot` options
- [Pandoc Releases](https://pandoc.org/releases.html) - Version 3.9 released 2026-02-04
- [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli) - Installation, usage, current version
- [Pandoc Demos](https://pandoc.org/demos.html) - Reference document styling examples

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pandoc-crossref | Latest | Figure/table numbering and cross-references | Optional enhancement for DOCX cross-refs (has DOCX limitations) |
| fs-extra | 11.3+ | File system utilities (reuse from Phase 5) | For diagram file handling, library import/export |
| write-file-atomic | Latest | Atomic file writes (reuse from Phase 4) | For DOCX export crash safety |

**Sources:**
- [pandoc-crossref](http://lierdakil.github.io/pandoc-crossref/) - Features and DOCX support status
- [pandoc-crossref GitHub](https://github.com/lierdakil/pandoc-crossref) - Known limitations with DOCX

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pandoc | Docx npm library | More control but requires manual styling, TOC generation, and Word XML manipulation — reinventing Pandoc |
| mermaid-cli | Puppeteer + Mermaid.js | Lower-level but adds browser orchestration complexity — mermaid-cli wraps this |
| PNG rendering | SVG embedding | Word's SVG support is inconsistent across versions, PNG is safer for client compatibility |
| Project-specific typicals | Global CATALOG.json | User explicitly needs per-project libraries for customer-specific typicals |

**Installation:**
```bash
# Pandoc (system-level, not npm)
# macOS: brew install pandoc
# Linux: apt-get install pandoc / dnf install pandoc
# Windows: choco install pandoc / download installer

# Node.js packages
npm install @mermaid-js/mermaid-cli

# Optional
npm install pandoc-crossref  # If using Haskell/cabal
```

## Architecture Patterns

### Recommended Project Structure

```
project-root/
├── .planning/
│   ├── fds/                    # FDS project (existing from Phases 1-6)
│   │   ├── phase-01/
│   │   ├── phase-02/
│   │   └── ...
│   └── sds/                    # SDS project (NEW, separate cycle)
│       ├── PROJECT.md          # SDS-specific config, inherits from FDS
│       ├── ROADMAP.md          # SDS phases (different structure from FDS)
│       ├── STATE.md            # SDS progress tracking
│       ├── phase-01/           # SDS Foundation & Typicals Matching
│       ├── phase-02/           # SDS Software Architecture
│       └── phase-03/           # SDS Equipment Module Details
├── output/
│   ├── FDS-[Project]-v1.0.md   # Assembled FDS
│   └── SDS-[Project]-v1.0.md   # Assembled SDS
├── export/
│   ├── FDS-[Project]-v1.0.docx # Exported FDS
│   └── SDS-[Project]-v1.0.docx # Exported SDS
├── diagrams/
│   ├── generated/              # Mermaid → PNG renders
│   └── external/               # Engineer-provided diagrams
└── references/
    └── typicals/               # Project-specific typicals library
        ├── CATALOG.json        # Typicals catalog (TIA Portal library metadata)
        ├── FB_AnalogIn.md      # Typical documentation (optional)
        └── ...
```

### Pattern 1: SDS Project Scaffolding

**What:** `/doc:generate-sds` creates a complete SDS project structure alongside the FDS, not as a child but as a parallel workflow.

**When to use:** When FDS reaches v1.0 (client-ready) and SDS development begins.

**Architecture decision:**
- SDS gets its own `.planning/sds/` directory with independent STATE.md
- SDS PROJECT.md inherits language, client, standards from FDS but has its own version counter
- SDS ROADMAP.md has different phase structure (Foundation → Architecture → Module Details)
- Engineer runs full discuss-plan-write-verify cycle for SDS phases

**Example workflow:**
```bash
# After FDS completion
/doc:complete-fds              # FDS v1.0 assembled
/doc:generate-sds              # Scaffolds .planning/sds/, creates SDS-01-CONTEXT.md seed

# Then same workflow as FDS
/doc:discuss-phase 01 --sds    # Discuss SDS Phase 1
/doc:plan-phase 01 --sds       # Plan SDS sections
/doc:write-phase 01 --sds      # Write SDS content
/doc:verify-phase 01 --sds     # Verify SDS phase
...
/doc:complete-fds --sds        # Assemble SDS (reuses assembly logic)
```

**Rationale:** User explicitly stated "SDS gets its own discuss-plan-write-verify cycle" — this is NOT a one-shot transform but an iterative refinement process. Scaffolding mirrors `/doc:new-fds` to maintain workflow consistency.

### Pattern 2: Typicals Library Loading

**What:** Two-mode typicals loading: external reference OR imported copy.

**When to use:**
- External reference: Multi-project library shared across team (customer standard)
- Imported copy: Self-contained project archive (handover to client)

**Implementation:**
```javascript
// PROJECT.md configuration
typicals:
  mode: "external"  // or "imported"
  path: "/path/to/customer-tia-library/"  // if external
  catalog: "references/typicals/CATALOG.json"  // if imported

// Library loading logic (Node.js)
async function loadTypicalsLibrary(projectConfig) {
  if (projectConfig.typicals.mode === 'external') {
    // Load CATALOG.json from external path
    const catalogPath = path.join(projectConfig.typicals.path, 'CATALOG.json');
    if (!fs.existsSync(catalogPath)) {
      return { error: 'External library not found', path: catalogPath };
    }
    return JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  } else {
    // Load from project references/
    const catalogPath = path.join(projectRoot, projectConfig.typicals.catalog);
    return JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  }
}
```

**CATALOG.json structure:**
```json
{
  "library": {
    "name": "Customer-Standard-Library",
    "version": "2.3.0",
    "platform": "TIA Portal V18",
    "updated": "2026-01-15"
  },
  "typicals": [
    {
      "id": "FB_AnalogIn",
      "type": "Control Module",
      "category": "Input Processing",
      "description": "4-20mA analog input scaling with high/low alarms",
      "interfaces": {
        "inputs": ["RawValue", "ScaleMin", "ScaleMax"],
        "outputs": ["ScaledValue", "HighAlarm", "LowAlarm"]
      },
      "use_cases": ["Temperature sensors", "Pressure transmitters", "Flow meters"],
      "documentation": "references/typicals/FB_AnalogIn.md"
    }
  ]
}
```

**Matching workflow:**
```bash
# During SDS Phase 1: Foundation & Typicals Matching
# System analyzes FDS equipment modules
# For each module: extract I/O profile, state machine complexity, control requirements
# Propose typical matches from CATALOG.json
# Engineer confirms or overrides

# Unmatched modules:
# System generates skeleton SDS section from FDS:
#   - I/O list (from FDS interface section)
#   - Parameters (from FDS parameter table)
#   - States (from FDS state machine)
#   - Marker: "## NEW TYPICAL NEEDED: FB_CustomValveControl"
```

### Pattern 3: Pandoc Reference Document Styling

**What:** Corporate styling via reference DOCX with predefined styles.

**When to use:** Every `/doc:export` call to ensure consistent branding.

**Setup process:**
```bash
# 1. Generate default reference document
pandoc -o custom-reference.docx --print-default-data-file reference.docx

# 2. Open in Microsoft Word, customize:
#    - Heading 1-6 styles (fonts, sizes, spacing, numbering)
#    - Normal text style
#    - Caption style (for figures/tables)
#    - Header: insert logo, project metadata placeholders
#    - Footer: page numbers, document version
#    - Table styles: grid, borders, shading

# 3. Save as huisstijl.docx in gsd-docs-industrial/references/

# 4. Use in export
pandoc input.md \
  --reference-doc=gsd-docs-industrial/references/huisstijl.docx \
  --toc --toc-depth=3 \
  --lof --lot \
  -o output.docx
```

**Critical gotchas (from research):**
- Word can change style IDs when resaving (FigureWithCaption → FigurewithCaption) — avoid manual edits after Pandoc generation
- Custom styles must match type: paragraph styles for divs, character styles for spans
- Reference doc content is ignored, only styles/properties used — test with dummy content

**Source:** [Pandoc GitHub Issue #4843](https://github.com/jgm/pandoc/issues/4843), [Pandoc Manual](https://pandoc.org/MANUAL.html#option--reference-doc)

### Pattern 4: Mermaid Diagram Rendering

**What:** Convert Mermaid code blocks to PNG for DOCX embedding.

**When to use:** Every `/doc:export` call, with complexity budgets.

**Implementation:**
```javascript
// Complexity budget enforcement (from research)
const COMPLEXITY_LIMITS = {
  nodes: {
    soft: 40,    // Warning threshold
    hard: 100    // Hard limit (cognitive overload + rendering performance)
  },
  edges: {
    soft: 80,
    hard: 200
  }
};

async function renderDiagram(mermaidCode, outputPath, section) {
  const stats = analyzeMermaidComplexity(mermaidCode);

  if (stats.nodes > COMPLEXITY_LIMITS.nodes.hard) {
    // Too complex, route to ENGINEER-TODO.md
    logToEngineerTodo({
      section: section,
      type: 'Mermaid diagram',
      description: `Diagram exceeds ${COMPLEXITY_LIMITS.nodes.hard} node limit (${stats.nodes} nodes)`,
      priority: 'high',
      suggestion: 'Split into multiple diagrams or create in Visio/draw.io'
    });
    return { status: 'deferred', reason: 'complexity_exceeded' };
  }

  if (stats.nodes > COMPLEXITY_LIMITS.nodes.soft) {
    // Warning but proceed
    console.warn(`Diagram in ${section} approaching complexity limit (${stats.nodes} nodes)`);
  }

  // Render with mermaid-cli
  const mmdc = spawn('mmdc', [
    '-i', '-',           // stdin
    '-o', outputPath,
    '-t', 'neutral',     // theme
    '-b', 'white',       // background
    '--scale', '2'       // 2x resolution for print quality
  ]);

  mmdc.stdin.write(mermaidCode);
  mmdc.stdin.end();

  return new Promise((resolve, reject) => {
    mmdc.on('close', code => {
      if (code === 0) resolve({ status: 'success', path: outputPath });
      else reject(new Error(`mmdc failed with code ${code}`));
    });
  });
}

function analyzeMermaidComplexity(code) {
  // Simple heuristic: count lines with node/edge syntax
  const lines = code.split('\n');
  const nodes = lines.filter(l => /^\s*[A-Z0-9_]+[\[\(]/.test(l)).length;
  const edges = lines.filter(l => /-->|---/.test(l)).length;
  return { nodes, edges };
}
```

**Fallback for missing mermaid-cli:**
```bash
# --skip-diagrams flag implementation
/doc:export --skip-diagrams

# In DOCX output:
# [DIAGRAM: State Machine for EM-200 Mixer]
# Source: diagrams/generated/em-200-states.mmd
# Note: Install mermaid-cli to render diagrams
```

**Sources:**
- [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli) - Command syntax
- [Mermaid Complexity Research](https://entropicdrift.com/blog/mermaid-sonar-complexity-analyzer/) - Cognitive load limits

### Pattern 5: Version Coordination (FDS ↔ SDS)

**What:** Independent versioning with explicit cross-references.

**Implementation:**
```yaml
# FDS PROJECT.md
version: 1.2
type: FDS
language: nl

# SDS PROJECT.md
version: 1.0
type: SDS
language: nl
based_on:
  document: FDS
  version: 1.2
  date: 2026-02-10

# SDS frontmatter (title page)
---
title: Software Design Specification
project: Mixer Line Automation
version: 1.0
date: 2026-02-14
based_on: FDS v1.2 (2026-02-10)
---
```

**Traceability matrix:**
```markdown
# TRACEABILITY.md (in SDS project)

| FDS Req ID | FDS Section | SDS Section | Implementation | Status |
|------------|-------------|-------------|----------------|--------|
| FR-01 | 3.2.1 Mixer States | 4.1.2 FB_MixerControl | State machine FB | Complete |
| FR-02 | 3.2.2 Mixer Parameters | 4.1.3 ParameterDB | DB instance | Complete |
| FR-03 | 3.3.1 Tank Level Control | 4.2.1 FB_TankLevel | PID + safety | Complete |
| FR-04 | 5.1 HMI Mixer Screen | 6.1 Screen Layout | Faceplate design | In Progress |

## Coverage Analysis
- Total FDS requirements: 87
- Mapped to SDS: 82 (94%)
- Not applicable (HMI only): 5 (6%)
- Missing implementation: 0
```

### Anti-Patterns to Avoid

- **Single-pass SDS transform:** SDS requires iteration and review, not a one-shot script. User explicitly wants discuss-plan-write-verify cycle.
- **Hardcoded typical matches:** AI must never hallucinate typicals. Only suggest from CATALOG.json, flag unmatched as NEW TYPICAL NEEDED.
- **DOCX post-processing in Word:** Every manual edit to exported DOCX breaks reproducibility. All styling must be in reference document.
- **Embedded Mermaid in DOCX:** Word doesn't support Mermaid natively. Must render to PNG before embedding.
- **Global typicals library:** User needs per-project flexibility for customer libraries.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown → DOCX | Custom Word XML generator | Pandoc | Handles edge cases: nested lists, tables, code blocks, images, cross-references, footnotes. 15 years of production hardening. |
| Diagram rendering | Puppeteer + manual Mermaid setup | mermaid-cli | Wraps Puppeteer, handles viewport sizing, theme injection, error cases, timeout management. 77 releases. |
| Cross-reference numbering | Regex find-replace | remark + unist-util-visit (from Phase 5) | AST-based ensures correct nesting, avoids false matches in code blocks or tables. |
| Version comparison | String splitting | semver library (from Phase 5) | Handles pre-release tags, build metadata, range comparisons. npm's official implementation. |
| YAML frontmatter | Manual parsing | gray-matter (from Phase 5) | Handles edge cases: multi-document YAML, JSON/TOML alternatives, delimiter variations. |

**Key insight:** Phase 7 is integration-heavy, not invention-heavy. Reuse Phase 5 tools (remark, semver, gray-matter) and leverage battle-tested converters (Pandoc, mermaid-cli). Custom code should orchestrate, not replicate.

## Common Pitfalls

### Pitfall 1: Pandoc Version Drift and Reference Document Corruption

**What goes wrong:** Different Pandoc versions produce subtly different DOCX output. A reference document created with Pandoc 3.5 breaks when used with Pandoc 3.9. Styles don't apply, TOC formatting changes, table borders disappear. The exported DOCX looks unprofessional and the engineer can't reproduce the issue because their local Pandoc version differs.

**Why it happens:**
- Pandoc evolves Word XML generation between versions (e.g., caption style changes in 3.7)
- Reference document is manually edited in Word, which rewrites style IDs and breaks Pandoc's assumptions
- No version pinning in package.json (Pandoc is system-installed, not npm-managed)
- Reference document not regenerated when Pandoc updates

**How to avoid:**
1. **Pin Pandoc version in documentation:** README.md specifies exact version tested (3.9), update guide for version upgrades
2. **Reference document as source control artifact:** `huisstijl.docx` in git with version tag (e.g., `huisstijl-pandoc3.9.docx`)
3. **Regeneration script:** When Pandoc upgrades, run `regenerate-reference.sh` to create fresh reference doc and re-apply styles
4. **Validation test:** Export script includes sanity check: does output contain expected styles? If not, version mismatch warning
5. **Avoid manual edits:** Never save reference doc from Word after manual changes — regenerate from Pandoc, apply style changes, save once

**Warning signs:**
- Export works on one machine, fails on another (version mismatch)
- Styles present in reference doc don't appear in output (ID change)
- TOC depth changes unexpectedly (format shift)

**Detection:**
```bash
# Version check in export script
REQUIRED_PANDOC="3.9"
INSTALLED=$(pandoc --version | head -1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$INSTALLED" != "$REQUIRED_PANDOC" ]; then
  echo "WARNING: Pandoc version mismatch (required: $REQUIRED_PANDOC, installed: $INSTALLED)"
fi
```

**Sources:**
- [Pandoc Issue #10282](https://github.com/jgm/pandoc/issues/10282) - Style loss between versions
- [Pandoc Issue #3656](https://github.com/jgm/pandoc/issues/3656) - Custom reference doc breaks caption style

### Pitfall 2: Mermaid Complexity Creep and Rendering Failures

**What goes wrong:** Engineer writes Phase 3, creates Mermaid state diagram with 15 states. Phase 4 adds 10 more. Phase 5 adds transitions. Export runs, mermaid-cli hangs for 3 minutes then produces corrupted PNG or crashes. The state diagram has 60 nodes and 120 edges — far beyond cognitive load limits.

**Why it happens:**
- No complexity budget enforcement during writing (writers don't know the limits)
- Verification checks content quality, not diagram renderability
- Mermaid syntax is valid, so no warnings until export time
- Engineer assumes "if Mermaid accepts it, it will render"

**How to avoid:**
1. **Complexity budget in verification:** Phase verify checks diagram complexity, warns at 40 nodes, fails at 100
2. **Early rendering in write phase:** Each CONTENT.md with Mermaid gets test-rendered immediately, failures caught early
3. **Complexity guidance in templates:** State machine template includes note: "Keep states <30 for readability, split complex machines into sub-diagrams"
4. **Graceful degradation:** Export script attempts render with 60s timeout, falls back to ENGINEER-TODO.md on failure
5. **Diagram splitting hints:** Verification suggests: "State machine has 55 nodes, consider splitting into Normal Operations (25 states) and Fault Handling (30 states)"

**Warning signs:**
- State diagrams with >5 levels of nesting
- More than 8 outbound transitions from a single state
- Diagram source code >200 lines

**Detection:**
```javascript
// In verify-phase workflow
function checkDiagramComplexity(contentMd) {
  const diagrams = extractMermaidBlocks(contentMd);
  const issues = [];

  diagrams.forEach((diagram, idx) => {
    const stats = analyzeMermaidComplexity(diagram.code);
    if (stats.nodes > 100) {
      issues.push({
        severity: 'error',
        message: `Diagram ${idx+1} exceeds hard limit (${stats.nodes} nodes, max 100)`,
        suggestion: 'Split into multiple diagrams'
      });
    } else if (stats.nodes > 40) {
      issues.push({
        severity: 'warning',
        message: `Diagram ${idx+1} approaching complexity limit (${stats.nodes} nodes)`,
        suggestion: 'Consider splitting for readability'
      });
    }
  });

  return issues;
}
```

**Sources:**
- [Mermaid Complexity Research](https://entropicdrift.com/blog/mermaid-sonar-complexity-analyzer/) - 30-40 node best practice, 100 hard limit
- [GitLab Issue #27173](https://gitlab.com/gitlab-org/gitlab/-/issues/27173) - Diagrams >5000 bytes fail to render

### Pitfall 3: Typicals Hallucination and Unsafe Matches

**What goes wrong:** SDS generation analyzes FDS equipment module "Dosing Pump with Variable Speed Control". AI suggests typical "FB_DosePump" from CATALOG.json. Engineer accepts. SDS section references FB_DosePump interfaces. Later discovery: FB_DosePump expects constant speed, has no speed control interface. SDS is wrong, PLC code based on SDS will fail.

**Why it happens:**
- Matching algorithm uses keyword similarity, not interface compatibility checking
- CATALOG.json has incomplete interface documentation
- AI pattern-matches "dosing pump" but ignores "variable speed" qualifier
- No verification step confirms interface alignment between FDS requirements and typical capabilities

**How to avoid:**
1. **Structured matching criteria:** Match on interface profile (I/O count, data types, state complexity), not just keywords
2. **Confidence scores:** Every suggested match includes confidence: HIGH (exact interface match), MEDIUM (partial match, review needed), LOW (keyword only)
3. **Engineer confirmation mandatory:** System NEVER auto-applies typical matches, always presents for confirmation with comparison table
4. **Mismatch documentation:** If engineer rejects suggested typical, system logs: equipment ID, suggested typical, rejection reason → improves future matching
5. **NEW TYPICAL NEEDED as safe fallback:** When confidence <50%, skip suggestion entirely, generate skeleton from FDS

**Matching comparison table (presented to engineer):**
```markdown
## Proposed Match: EM-300 Dosing Pump

**FDS Requirements (from Section 3.3):**
- I/O: 2 DI, 1 AI (speed feedback), 1 DO, 1 AO (speed setpoint)
- States: IDLE, RUNNING, STOPPING, FAULT
- Parameters: SpeedMin, SpeedMax, DoseVolume, FlowRate

**Suggested Typical: FB_DosePump**
- I/O: 2 DI, 1 DO (NO speed control outputs)
- States: IDLE, RUN, FAULT
- Parameters: DoseVolume, FlowRate

**Interface Match:** ❌ MISMATCH (AI speed control missing)
**Confidence:** LOW (40%)

**Recommendation:** Create NEW TYPICAL or use FB_MotorVFD + FB_DoseCalculator
```

**Warning signs:**
- All suggested typicals have HIGH confidence (suspiciously perfect)
- Suggested typical name is generic substring of equipment name ("Mixer" → "FB_Mix")
- CATALOG.json typical has <50% I/O overlap with FDS module

**Sources:**
- User constraint: "Matching method: suggest + confirm" — explicit human-in-loop requirement
- User constraint: "Unmatched equipment flagged as NEW TYPICAL NEEDED (not hallucinated)"

### Pitfall 4: SDS Structure Rigidity vs User's Preliminary Decision

**What goes wrong:** Phase 7 implementation hardcodes SDS structure as "equipment modules as sections, software structure within". Engineer completes first SDS, reviews with team, realizes structure doesn't work for this project type — needs software layer first, then equipment instantiation. Framework can't adapt because structure is baked into templates and assembly logic.

**Why it happens:**
- User explicitly said SDS structure is "preliminary, not fully locked" but implementation treats it as final
- SDS templates are copied from FDS templates with hardcoded section order
- No abstraction layer between "SDS content model" and "SDS document structure"

**How to avoid:**
1. **SDS structure as configuration, not code:** SDS-STRUCTURE.md defines section order, nesting, cross-reference patterns
2. **Template composition:** SDS sections are atomic templates (software-layer.md, equipment-instantiation.md, fb-hierarchy.md) assembled per structure config
3. **Multiple structure presets:** MVP includes 2 structures: (A) Equipment-First (equipment modules → software within), (B) Software-First (FB hierarchy → equipment instantiation)
4. **Easy structure switching:** Engineer can change `sds_structure: equipment-first` to `sds_structure: software-first` in SDS PROJECT.md, re-run assembly, document restructures
5. **User feedback loop:** After pilot project, explicitly ask: "Does this SDS structure work for your projects? What would you change?"

**Implementation:**
```javascript
// SDS assembly respects structure config
const SDS_STRUCTURES = {
  'equipment-first': {
    sections: [
      'foundation',
      'typicals-overview',
      { type: 'equipment-modules', children: ['software-structure', 'fb-instantiation', 'data-flow'] },
      'interfaces',
      'appendices'
    ]
  },
  'software-first': {
    sections: [
      'foundation',
      'typicals-overview',
      'software-architecture',
      { type: 'fb-hierarchy', children: ['equipment-module-instances'] },
      'interfaces',
      'appendices'
    ]
  }
};

function assembleSDSStructure(contentFiles, structure) {
  const template = SDS_STRUCTURES[structure] || SDS_STRUCTURES['equipment-first'];
  // Assemble sections per template.sections order
}
```

**Warning signs:**
- Engineer asks "Can we change SDS section order?" and answer is "No, templates are fixed"
- SDS review feedback suggests different organization but framework can't accommodate

**Sources:**
- User constraint: "NOTE: SDS structure may be revisited — this is a preliminary decision, not fully locked"
- User constraint in Claude's Discretion: "SDS-specific templates (new vs adapted from FDS)"

### Pitfall 5: Pilot Project as Technical Demo vs Quality Validation

**What goes wrong:** Pilot project is built as "prove it works" demo — 3 equipment modules, minimal content, simplified state machines. Export runs, DOCX generates, success declared. Later, real project with 15 modules, complex interlocks, ISA-88 standards hits edge cases the pilot never tested. Framework breaks on production use.

**Why it happens:**
- Pilot scope reduced to "get something working quickly" instead of "validate realistic quality"
- Technical requirements met (FDS → SDS → DOCX) but content quality not validated
- Pilot project is Type D (smallest scope) instead of user-specified Type B (realistic scope)

**How to avoid:**
1. **Type B pilot as user specified:** 4-5 phases, 8-12 equipment modules, realistic complexity
2. **Quality bar from user constraint:** "Client-ready quality — output should be close to what you'd actually send to a client, minimal manual cleanup needed"
3. **Pilot checklist includes:**
   - Complete FDS with front matter (title page, revision history, TOC, abbreviations)
   - Equipment modules with >5 states, >10 parameters, >8 interlocks each
   - Cross-references between modules (not isolated sections)
   - Mermaid diagrams at complexity soft limit (30-35 nodes) to test rendering
   - SDS with 100% FDS coverage in TRACEABILITY.md
   - DOCX export with all styling elements (header logo, footer pages, table formatting, figure captions)
4. **Pilot validation criteria:**
   - Industrial automation engineer review: "Would you send this to a client?"
   - Comparison to real historical FDS/SDS: similar depth and coverage?
   - Export quality: DOCX opens in Word without errors, styles applied correctly?

**Fictional pilot project scope (Type B: Nieuwbouw Flex):**
```
Project: Batch Mixing System for Chemical Processing
Client: [Fictional] ChemTech Industries

Equipment Modules:
- EM-100 Raw Material Storage (3 tanks)
- EM-200 Dosing System (4 pumps)
- EM-300 Mixer Unit (agitator + heating)
- EM-400 Transfer System (transfer pump + piping)
- EM-500 Packaging Station (filling + capping)

Standards: None (Type B = Flex)
Language: English (for research/demo clarity)
Scope: Full FDS (4 phases) + SDS (3 phases) + DOCX export

Validation:
- FDS ~40 pages (realistic for Type B)
- SDS ~30 pages with typicals matching
- DOCX exports with professional styling
```

**Warning signs:**
- Pilot project described as "simple demo"
- Pilot skips phases that real projects need (e.g., no interfaces section)
- DOCX validation is "it opens" not "it looks client-ready"

**Sources:**
- User constraint: "Project type: Type B (Nieuwbouw Flex) — realistic scope without standards overhead"
- User constraint: "Success bar: client-ready quality — output should be close to what you'd actually send to a client"

### Pitfall 6: External Typicals Library Path Breakage

**What goes wrong:** PROJECT.md references external typicals library at `/path/to/customer-lib/`. Engineer moves library, or runs on different machine, or customer updates library location. SDS generation fails with "CATALOG.json not found". No graceful fallback, project blocked.

**Why it happens:**
- Absolute paths are brittle across machines and time
- No validation that external library exists before starting multi-hour SDS workflow
- No fallback to cached/imported mode when external path breaks

**How to avoid:**
1. **Path validation on project load:** Every command that uses typicals checks library accessibility first, warns if unreachable
2. **Relative path support:** Allow `typicals.path: "../shared-libraries/customer-standard"` relative to project root
3. **Import workflow:** `/doc:import-typicals` copies external library to `references/typicals/`, switches PROJECT.md to imported mode
4. **Clear error messages:** "External typicals library not found at /old/path. Run `/doc:import-typicals` to create local copy, or update path in PROJECT.md."
5. **Validation during discuss-phase:** Before SDS Phase 1 planning, confirm typicals library accessible

**Implementation:**
```javascript
function validateTypicalsAccess(projectConfig) {
  if (projectConfig.typicals.mode === 'external') {
    const catalogPath = path.resolve(projectConfig.typicals.path, 'CATALOG.json');
    if (!fs.existsSync(catalogPath)) {
      return {
        valid: false,
        error: `External typicals library not accessible at ${catalogPath}`,
        suggestions: [
          `Update path in PROJECT.md if library moved`,
          `Run /doc:import-typicals to create local copy`,
          `Verify network/filesystem access to library location`
        ]
      };
    }
  }
  return { valid: true };
}
```

**Warning signs:**
- Typicals path contains machine-specific username (`/Users/john/...`)
- Library path is network mount that requires VPN
- PROJECT.md created on Windows, opened on Mac (path separator issues)

**Sources:**
- User constraint: "Two loading modes required: (1) path reference in PROJECT.md pointing to an external library, (2) import/copy into project's references/ folder"

## Code Examples

Verified patterns from official sources and user constraints:

### Example 1: Pandoc DOCX Export with Full Formatting

```bash
#!/bin/bash
# export-to-docx.sh
# Converts assembled FDS/SDS markdown to client-ready DOCX

set -e

INPUT_MD="$1"      # e.g., output/FDS-MixerLine-v1.0.md
OUTPUT_DOCX="$2"   # e.g., export/FDS-MixerLine-v1.0.docx
DRAFT_MODE="${3:-false}"

# Paths
REFERENCE_DOC="gsd-docs-industrial/references/huisstijl.docx"
DIAGRAMS_DIR="diagrams/generated"

# Validate Pandoc version
REQUIRED_PANDOC="3.9"
INSTALLED=$(pandoc --version | head -1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$INSTALLED" != "$REQUIRED_PANDOC" ]; then
  echo "WARNING: Pandoc version mismatch (required: $REQUIRED_PANDOC, installed: $INSTALLED)"
  echo "Export may produce unexpected formatting. Update Pandoc or regenerate reference doc."
fi

# Check reference document exists
if [ ! -f "$REFERENCE_DOC" ]; then
  echo "ERROR: Corporate style template not found at $REFERENCE_DOC"
  exit 1
fi

# Build Pandoc command
PANDOC_CMD=(
  pandoc
  "$INPUT_MD"
  --from markdown+yaml_metadata_block+pipe_tables+grid_tables
  --to docx
  --reference-doc="$REFERENCE_DOC"
  --standalone
  --toc --toc-depth=3
  --number-sections
  --metadata title="$(basename "$INPUT_MD" .md)"
  -o "$OUTPUT_DOCX"
)

# Add lists of figures and tables (not draft mode)
if [ "$DRAFT_MODE" != "true" ]; then
  PANDOC_CMD+=(--lof --lot)
fi

# Execute conversion
echo "Converting $INPUT_MD to DOCX..."
"${PANDOC_CMD[@]}"

# Validate output
if [ ! -f "$OUTPUT_DOCX" ]; then
  echo "ERROR: Export failed, no output file created"
  exit 1
fi

FILE_SIZE=$(stat -f%z "$OUTPUT_DOCX" 2>/dev/null || stat -c%s "$OUTPUT_DOCX" 2>/dev/null)
if [ "$FILE_SIZE" -lt 10000 ]; then
  echo "WARNING: Output file suspiciously small ($FILE_SIZE bytes), may be corrupted"
fi

echo "SUCCESS: Exported to $OUTPUT_DOCX ($FILE_SIZE bytes)"

# Add watermark for drafts
if [ "$DRAFT_MODE" = "true" ]; then
  echo "NOTE: Draft mode — lists of figures/tables omitted"
fi
```

**Source:** [Pandoc User's Guide](https://pandoc.org/MANUAL.html) - Command-line options

### Example 2: Mermaid Batch Rendering with Complexity Checking

```javascript
// render-diagrams.js
// Batch converts Mermaid code blocks from markdown to PNG

const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('child_process');

const COMPLEXITY_LIMITS = {
  nodes: { soft: 40, hard: 100 },
  edges: { soft: 80, hard: 200 }
};

async function extractMermaidBlocks(markdownPath) {
  const content = await fs.readFile(markdownPath, 'utf8');
  const blocks = [];
  const regex = /```mermaid\n([\s\S]*?)```/g;
  let match;
  let index = 0;

  while ((match = regex.exec(content)) !== null) {
    blocks.push({
      index: index++,
      code: match[1].trim(),
      position: match.index
    });
  }

  return blocks;
}

function analyzeMermaidComplexity(code) {
  const lines = code.split('\n');

  // Heuristic: count node definitions and edges
  const nodeLines = lines.filter(l => /^\s*[A-Z0-9_]+[\[\(]/.test(l));
  const edgeLines = lines.filter(l => /-->|---|==>|===/.test(l));

  return {
    nodes: nodeLines.length,
    edges: edgeLines.length
  };
}

async function renderMermaid(code, outputPath) {
  return new Promise((resolve, reject) => {
    const mmdc = spawn('mmdc', [
      '-i', '-',
      '-o', outputPath,
      '-t', 'neutral',
      '-b', 'white',
      '--scale', '2',
      '--width', '1200'
    ]);

    mmdc.stdin.write(code);
    mmdc.stdin.end();

    let stderr = '';
    mmdc.stderr.on('data', chunk => { stderr += chunk; });

    mmdc.on('close', code => {
      if (code === 0) {
        resolve({ success: true });
      } else {
        reject(new Error(`mmdc failed: ${stderr}`));
      }
    });

    // Timeout after 60 seconds
    setTimeout(() => {
      mmdc.kill();
      reject(new Error('Rendering timeout (60s)'));
    }, 60000);
  });
}

async function renderAllDiagrams(inputMd, outputDir, engineerTodoPath) {
  await fs.ensureDir(outputDir);

  const blocks = await extractMermaidBlocks(inputMd);
  const results = [];
  const engineerTodos = [];

  for (const block of blocks) {
    const stats = analyzeMermaidComplexity(block.code);
    const outputPath = path.join(outputDir, `diagram-${block.index}.png`);

    // Check complexity limits
    if (stats.nodes > COMPLEXITY_LIMITS.nodes.hard) {
      engineerTodos.push({
        section: `Diagram ${block.index}`,
        type: 'Mermaid diagram',
        description: `Exceeds ${COMPLEXITY_LIMITS.nodes.hard} node limit (${stats.nodes} nodes)`,
        priority: 'high',
        suggestion: 'Split into multiple diagrams or create in Visio'
      });
      results.push({ index: block.index, status: 'deferred', reason: 'complexity' });
      continue;
    }

    if (stats.nodes > COMPLEXITY_LIMITS.nodes.soft) {
      console.warn(`Diagram ${block.index}: approaching complexity limit (${stats.nodes} nodes)`);
    }

    // Attempt render
    try {
      await renderMermaid(block.code, outputPath);
      results.push({ index: block.index, status: 'success', path: outputPath });
    } catch (error) {
      engineerTodos.push({
        section: `Diagram ${block.index}`,
        type: 'Mermaid diagram',
        description: `Rendering failed: ${error.message}`,
        priority: 'high',
        suggestion: 'Review diagram syntax or simplify structure'
      });
      results.push({ index: block.index, status: 'failed', error: error.message });
    }
  }

  // Write ENGINEER-TODO.md if any deferred diagrams
  if (engineerTodos.length > 0) {
    await fs.writeFile(engineerTodoPath, formatEngineerTodos(engineerTodos));
  }

  return results;
}

function formatEngineerTodos(todos) {
  let md = '# Engineer TODO: Diagrams\n\n';
  md += `**Generated:** ${new Date().toISOString()}\n\n`;

  for (const todo of todos) {
    md += `## ${todo.section}\n\n`;
    md += `- **Type:** ${todo.type}\n`;
    md += `- **Issue:** ${todo.description}\n`;
    md += `- **Priority:** ${todo.priority}\n`;
    md += `- **Suggestion:** ${todo.suggestion}\n\n`;
  }

  return md;
}

// CLI usage
if (require.main === module) {
  const [,, inputMd, outputDir, engineerTodoPath] = process.argv;

  if (!inputMd || !outputDir) {
    console.error('Usage: node render-diagrams.js <input.md> <output-dir> [engineer-todo.md]');
    process.exit(1);
  }

  renderAllDiagrams(inputMd, outputDir, engineerTodoPath || 'ENGINEER-TODO.md')
    .then(results => {
      const success = results.filter(r => r.status === 'success').length;
      const failed = results.filter(r => r.status === 'failed').length;
      const deferred = results.filter(r => r.status === 'deferred').length;

      console.log(`\nRendering complete: ${success} success, ${failed} failed, ${deferred} deferred`);
      process.exit(failed > 0 ? 1 : 0);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { renderAllDiagrams, analyzeMermaidComplexity };
```

**Source:** [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli), [Mermaid Complexity Research](https://entropicdrift.com/blog/mermaid-sonar-complexity-analyzer/)

### Example 3: Typicals Matching with Confidence Scoring

```javascript
// match-typicals.js
// Suggests typical matches for FDS equipment modules

const fs = require('fs-extra');

function loadCatalog(catalogPath) {
  return JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
}

function extractFDSModuleProfile(fdsContentMd) {
  // Parse FDS CONTENT.md to extract I/O profile, states, parameters
  // Simplified: assumes structured tables in FDS

  const profile = {
    id: extractModuleId(fdsContentMd),
    name: extractModuleName(fdsContentMd),
    io: extractIOList(fdsContentMd),
    states: extractStates(fdsContentMd),
    parameters: extractParameters(fdsContentMd),
    keywords: extractKeywords(fdsContentMd)
  };

  return profile;
}

function calculateMatchScore(fdsProfile, typical) {
  let score = 0;
  let breakdown = {};

  // I/O interface match (40% weight)
  const ioMatch = compareIOProfiles(fdsProfile.io, typical.interfaces);
  score += ioMatch.score * 0.4;
  breakdown.io = ioMatch;

  // Keyword match (30% weight)
  const keywordMatch = compareKeywords(fdsProfile.keywords, typical.use_cases);
  score += keywordMatch.score * 0.3;
  breakdown.keywords = keywordMatch;

  // State complexity match (20% weight)
  const stateMatch = compareStateComplexity(fdsProfile.states, typical.states || []);
  score += stateMatch.score * 0.2;
  breakdown.states = stateMatch;

  // Category match (10% weight)
  const categoryMatch = fdsProfile.category === typical.category ? 1.0 : 0.0;
  score += categoryMatch * 0.1;
  breakdown.category = categoryMatch;

  return { score, breakdown };
}

function compareIOProfiles(fdsIO, typicalInterfaces) {
  const fdsInputCount = fdsIO.filter(io => io.direction === 'input').length;
  const fdsOutputCount = fdsIO.filter(io => io.direction === 'output').length;

  const typicalInputCount = typicalInterfaces.inputs?.length || 0;
  const typicalOutputCount = typicalInterfaces.outputs?.length || 0;

  // Exact match = 1.0, each missing I/O = -0.1
  const inputDiff = Math.abs(fdsInputCount - typicalInputCount);
  const outputDiff = Math.abs(fdsOutputCount - typicalOutputCount);

  const score = Math.max(0, 1.0 - (inputDiff + outputDiff) * 0.1);

  return {
    score,
    fds: { inputs: fdsInputCount, outputs: fdsOutputCount },
    typical: { inputs: typicalInputCount, outputs: typicalOutputCount },
    match: inputDiff === 0 && outputDiff === 0 ? 'exact' : 'partial'
  };
}

function compareKeywords(fdsKeywords, typicalUseCases) {
  const fdsSet = new Set(fdsKeywords.map(k => k.toLowerCase()));
  const typicalSet = new Set(
    typicalUseCases.flatMap(uc => uc.toLowerCase().split(/\s+/))
  );

  const intersection = [...fdsSet].filter(k => typicalSet.has(k));
  const union = new Set([...fdsSet, ...typicalSet]);

  const score = intersection.length / union.size;  // Jaccard similarity

  return {
    score,
    matches: intersection,
    fdsUnique: [...fdsSet].filter(k => !typicalSet.has(k)),
    typicalUnique: [...typicalSet].filter(k => !fdsSet.has(k))
  };
}

function compareStateComplexity(fdsStates, typicalStates) {
  if (typicalStates.length === 0) {
    return { score: 0.5, note: 'Typical state info unavailable' };
  }

  const stateDiff = Math.abs(fdsStates.length - typicalStates.length);
  const score = Math.max(0, 1.0 - stateDiff * 0.15);

  return {
    score,
    fds: fdsStates.length,
    typical: typicalStates.length,
    match: stateDiff <= 2 ? 'close' : 'different'
  };
}

function suggestTypicals(fdsProfile, catalog, minConfidence = 0.3) {
  const suggestions = [];

  for (const typical of catalog.typicals) {
    const match = calculateMatchScore(fdsProfile, typical);

    if (match.score >= minConfidence) {
      suggestions.push({
        typical,
        confidence: match.score,
        breakdown: match.breakdown,
        recommendation: getRecommendation(match.score)
      });
    }
  }

  // Sort by confidence descending
  suggestions.sort((a, b) => b.confidence - a.confidence);

  return suggestions;
}

function getRecommendation(score) {
  if (score >= 0.8) return 'HIGH - Strong match, recommend acceptance';
  if (score >= 0.6) return 'MEDIUM - Partial match, review interface differences';
  if (score >= 0.4) return 'LOW - Weak match, consider alternatives';
  return 'VERY LOW - Poor match, likely NEW TYPICAL NEEDED';
}

function formatMatchReport(fdsProfile, suggestions) {
  let report = `# Typicals Matching: ${fdsProfile.id} ${fdsProfile.name}\n\n`;

  report += `## FDS Equipment Profile\n\n`;
  report += `- **I/O:** ${fdsProfile.io.length} signals\n`;
  report += `- **States:** ${fdsProfile.states.length}\n`;
  report += `- **Parameters:** ${fdsProfile.parameters.length}\n`;
  report += `- **Keywords:** ${fdsProfile.keywords.join(', ')}\n\n`;

  if (suggestions.length === 0) {
    report += `## No Matches Found\n\n`;
    report += `No typicals met minimum confidence threshold (30%).\n\n`;
    report += `**Recommendation:** Generate NEW TYPICAL skeleton from FDS.\n`;
    return report;
  }

  report += `## Suggested Typicals (${suggestions.length})\n\n`;

  for (let i = 0; i < Math.min(3, suggestions.length); i++) {
    const s = suggestions[i];
    report += `### ${i+1}. ${s.typical.id} (${Math.round(s.confidence * 100)}% confidence)\n\n`;
    report += `**${s.recommendation}**\n\n`;
    report += `- **Description:** ${s.typical.description}\n`;
    report += `- **Category:** ${s.typical.category}\n`;
    report += `- **I/O Match:** ${s.breakdown.io.match} (FDS: ${s.breakdown.io.fds.inputs}/${s.breakdown.io.fds.outputs}, Typical: ${s.breakdown.io.typical.inputs}/${s.breakdown.io.typical.outputs})\n`;
    report += `- **Keyword Overlap:** ${s.breakdown.keywords.matches.join(', ')}\n\n`;

    if (s.breakdown.io.match !== 'exact') {
      report += `⚠️ **Interface Mismatch:** Review I/O alignment before accepting.\n\n`;
    }
  }

  return report;
}

// Stub functions (would parse actual FDS markdown)
function extractModuleId(md) { return 'EM-300'; }
function extractModuleName(md) { return 'Dosing Pump'; }
function extractIOList(md) { return []; }
function extractStates(md) { return []; }
function extractParameters(md) { return []; }
function extractKeywords(md) { return ['dosing', 'pump', 'flow', 'variable speed']; }

module.exports = { suggestTypicals, formatMatchReport, loadCatalog };
```

**Source:** User constraints on typicals matching logic

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual DOCX assembly | Pandoc markdown → DOCX | Pandoc 1.0 (2006), matured 2.0+ (2017) | Reproducible exports, version control friendly source |
| Browser-based Mermaid | Server-side mermaid-cli | mermaid-cli 8.0 (2020) | Automation-ready, no GUI dependency |
| Global typicals DB | Project-specific libraries | Current requirement (2026) | Customer library flexibility, no central bottleneck |
| Single-pass SDS generation | Iterative discuss-plan-write-verify | User decision (2026-02-14) | Higher quality, human-in-loop refinement |
| Pandoc 2.x reference docs | Pandoc 3.x reference docs | Pandoc 3.0 (2023-01-18) | Breaking changes in style handling, reference docs not compatible |

**Deprecated/outdated:**
- **pandoc-citeproc:** Merged into Pandoc core as of 2.11 (2020), standalone deprecated
- **mermaid.cli (old repo):** Moved to @mermaid-js/mermaid-cli, old npm package unmaintained
- **Hardcoded SDS structure:** User wants preliminary structure with flexibility to revise

**Sources:**
- [Pandoc Releases](https://pandoc.org/releases.html) - Version history
- [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli) - Project migration

## Open Questions

1. **SDS phase structure details**
   - What we know: SDS gets its own ROADMAP with different phases than FDS
   - What's unclear: Exact phase breakdown (Foundation + Typicals → Architecture → Module Details, but how many total phases?)
   - Recommendation: Start with 3-phase SDS structure (similar to Type C modification), validate with pilot, adjust if needed

2. **pandoc-crossref value vs complexity**
   - What we know: Supports figure/table numbering, but DOCX has limitations (bookmarks vs SEQ fields)
   - What's unclear: Does the complexity of pandoc-crossref filter justify the partial DOCX support?
   - Recommendation: Make pandoc-crossref optional (installed if available, gracefully skipped if not), document limitations

3. **Typicals CATALOG.json schema stability**
   - What we know: Need to store typical ID, interfaces, description, use cases
   - What's unclear: Will schema need to expand for multi-platform support later? How to version schema?
   - Recommendation: Include `schema_version: "1.0"` in CATALOG.json, validate on load, document expansion path

4. **Mermaid theme customization**
   - What we know: mermaid-cli supports `-t` theme flag (dark, neutral, forest, default)
   - What's unclear: Does corporate branding require custom Mermaid theme CSS? If so, how to inject?
   - Recommendation: Start with 'neutral' theme (safest for print), add `--cssFile` customization if user requests branding

5. **DOCX export error handling depth**
   - What we know: Pandoc can fail on invalid markdown, complex tables, or corrupted reference docs
   - What's unclear: How much error recovery should export script attempt? Retry logic? Fallback formats?
   - Recommendation: Fail fast with clear error messages, no retry logic (user can fix source and re-export), validate reference doc integrity before export

## Sources

### Primary (HIGH confidence)

- [Pandoc User's Guide](https://pandoc.org/MANUAL.html) - Official documentation for `--reference-doc`, `--toc`, `--lof`, `--lot`
- [Pandoc Releases](https://pandoc.org/releases.html) - Version 3.9 (2026-02-04), version history
- [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli) - Installation, command syntax, version 11.12.0
- [pandoc-crossref Documentation](http://lierdakil.github.io/pandoc-crossref/) - Figure/table numbering, DOCX limitations
- [remark GitHub](https://github.com/remarkjs/remark) - Markdown AST processing (established in Phase 5)
- Phase 5 RESEARCH.md - Standards stack for document assembly (remark, unified, semver, gray-matter)

### Secondary (MEDIUM confidence)

- [Pandoc Issue #4843](https://github.com/jgm/pandoc/issues/4843) - DOCX custom style overwriting behavior
- [Pandoc Issue #10282](https://github.com/jgm/pandoc/issues/10282) - Style loss across versions
- [Pandoc Issue #3656](https://github.com/jgm/pandoc/issues/3656) - Reference doc breaks figure captions
- [GitLab Issue #27173](https://gitlab.com/gitlab-org/gitlab/-/issues/27173) - Mermaid >5000 bytes fails to render
- [Mermaid Complexity Research](https://entropicdrift.com/blog/mermaid-sonar-complexity-analyzer/) - Cognitive load limits (40 nodes soft, 100 hard)
- [TIA Portal Library Guideline](https://support.industry.siemens.com/cs/attachments/109747503/109747503_Library_Guideline_DOC_v10_en.pdf) - Library structure and management
- [GAMP5 Documentation Standards](https://www.tsquality.it/en/validation-and-quality-controls/gamp5-urs-fds-hds-sds) - FDS/SDS in pharma industry
- [Requirements Traceability Matrix Guide](https://www.perforce.com/resources/alm/requirements-traceability-matrix) - Traceability patterns

### Tertiary (LOW confidence, needs validation)

- WebSearch results on TIA Portal 2026 features - No 2026-specific TIA Portal updates found, current docs are V18/V20
- WebSearch results on industrial automation documentation - General industry practices, not tool-specific

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pandoc, mermaid-cli, remark ecosystem all verified from official sources, versions confirmed
- Architecture: MEDIUM-HIGH - SDS scaffolding pattern is inference from user constraints + GSD patterns, not explicitly documented
- Pitfalls: HIGH - Pandoc version drift, Mermaid complexity, typicals hallucination all validated from issue trackers and research
- TIA Portal typicals: MEDIUM - Library structure confirmed from official Siemens docs, but project-specific loading is custom implementation
- DOCX styling: MEDIUM-HIGH - Reference document approach confirmed, but edge cases from GitHub issues suggest fragility

**Research date:** 2026-02-14
**Valid until:** 60 days (Pandoc/mermaid-cli stable, TIA Portal updates quarterly but schema unlikely to change)

**Critical uncertainties for planning:**
1. SDS phase structure (3 vs 4 vs 5 phases) — recommend 3-phase start, validate with pilot
2. pandoc-crossref necessity — recommend optional, document graceful degradation
3. Typicals schema versioning — recommend v1.0 with expansion path documented
4. Pilot project content depth — must be Type B realistic, not minimal demo
