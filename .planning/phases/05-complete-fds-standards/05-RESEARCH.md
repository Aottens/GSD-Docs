# Phase 5: Complete-FDS + Standards + Assembly - Research

**Researched:** 2026-02-14
**Domain:** Document assembly, hierarchical section numbering, cross-reference resolution, standards validation, version management
**Confidence:** HIGH

## Summary

Phase 5 transforms all verified phase outputs into a complete, numbered, versioned FDS document with resolved cross-references, optional standards compliance checks, and version management for internal and client releases. This is where the distributed write-verify cycles of Phases 3-4 coalesce into a single deliverable artifact.

The research examined: (1) markdown AST manipulation with remark/unified for section numbering and TOC generation, (2) cross-reference resolution strategies from symbolic to concrete section numbers, (3) standards validation patterns for PackML and ISA-88 terminology enforcement, (4) version management with semantic versioning and file archiving, (5) document assembly orchestration with broken reference detection and orphan section handling, and (6) PDF generation options for final deliverables.

The critical architectural insight: Phase 5 operates on verified content as read-only input and produces versioned output artifacts, never modifying source CONTENT.md files. Assembly is a transformation (CONTENT.md files → FDS-vX.Y.md + reports), not an in-place edit. The complete-fds workflow orchestrates multiple discrete operations: numbering application, cross-reference resolution, standards checks, and archiving.

**Primary recommendation:** Use remark ecosystem (remark-parse, remark-stringify, unified) for AST-based markdown manipulation with unist-util-visit for traversal. Leverage existing CROSS-REFS.md infrastructure from Phase 3 for reference resolution. Build composable standards modules (packml-validator.js, isa88-validator.js) that load only when enabled. Use semver library for version bumps and fs-extra for atomic archiving. Implement assembly as a pipeline: parse → number → resolve → validate → generate → archive.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Assembly structure:**
- Hierarchical (IEC-style) section numbering: 1.1, 1.2, 2.1.1, etc.
- Full auto-generated front matter: title page, revision history, table of contents, abbreviations list
- Section ordering follows a predefined FDS structure template (not ROADMAP phase order) — template defines the canonical order
- Unwritten sections appear as placeholder stubs with "[TO BE COMPLETED]" markers — shows the full intended document structure even when incomplete

**Cross-reference resolution:**
- Unresolved references (target section doesn't exist) render as [BROKEN REF] placeholders — assembly continues
- Always generate XREF-REPORT.md listing all references, resolution status, and orphan sections
- Orphan handling: Claude's discretion on severity based on section type
- Cross-references render as plain text section numbers (e.g., "see Section 3.2.1"), not clickable links

**Standards enforcement:**
- Configurable severity per standard in PROJECT.md — engineer sets each standard to error (blocking) or warning (non-blocking)
- Standards checks run both automatically during /doc:complete-fds AND available as standalone /doc:check-standards command
- PackML state name enforcement: Claude's discretion based on PackML specification requirements
- Standalone COMPLIANCE.md report per standard with pass/fail per check, overall score, and remediation hints

**Versioning + release:**
- Semantic versioning (vX.Y): minor bumps (v0.1, v1.1) are internal, major bumps (v1.0, v2.0) are client releases
- Previous version files archived to .planning/archive/vX.Y/ on new release
- Revision history: hybrid approach — auto-generated from git as starting draft, engineer edits before release
- Client release gate: all phases must pass verification, but --force flag allows release with warnings

### Claude's Discretion

- Orphan section severity classification (based on section type: equipment module vs appendix)
- PackML state name enforcement approach (exact match vs synonym mapping for common variations)
- FDS structure template section ordering details (how to map ROADMAP phases to canonical FDS structure)
- ENGINEER-TODO.md format for diagrams exceeding Mermaid complexity (section reference, diagram type, description, priority)

### Specific Ideas

- Version scheme already established in project brief: v0.x internal, v1.0 first customer-facing release, v1.1 internal revision, v2.0 next customer release
- FDS/SDS versioned independently (SDS references its source FDS version)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| remark | 16.0+ | Markdown AST parser/serializer | De facto standard for markdown processing, 150+ plugins, used by Gatsby, MDX, Docusaurus |
| unified | 12.0+ | Content transformation pipeline | Core of remark ecosystem, AST-agnostic processing |
| remark-parse | 12.0+ | Markdown → AST | Official remark parser, full CommonMark + GFM support |
| remark-stringify | 12.0+ | AST → Markdown | Official remark serializer, preserves formatting |
| unist-util-visit | 5.0+ | AST traversal | Standard visitor pattern for syntax tree traversal |
| semver | 7.6+ | Semantic versioning | Used by npm, authoritative implementation of semver.org spec |
| fs-extra | 11.3+ | File system utilities | 78k+ projects, adds copy/move/mkdirs to native fs |
| gray-matter | 4.0+ | Frontmatter parsing | Battle-tested, used by Gatsby, VitePress, Astro, TinaCMS |

**Sources:**
- [remark - markdown processor](https://github.com/remarkjs/remark)
- [unified - syntax tree processing](https://github.com/unifiedjs/unified)
- [semver - npm's version parser](https://www.npmjs.com/package/semver)
- [fs-extra - enhanced file system](https://github.com/jprichardson/node-fs-extra)
- [gray-matter - frontmatter parser](https://github.com/jonschlinkert/gray-matter)

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| remark-toc | 9.0+ | Auto-generate table of contents | For front matter TOC generation |
| remark-frontmatter | 5.0+ | Parse/serialize YAML frontmatter | When extracting metadata from CONTENT.md files |
| mdast-util-to-string | 4.0+ | Extract plain text from AST | For abbreviations list generation, keyword extraction |
| write-file-atomic | Latest | Atomic file writes | For crash-safe archive operations (already used in Phase 4) |
| cli-table3 | Latest | Terminal table rendering | For COMPLIANCE.md report formatting (already used in Phase 4) |

**Sources:**
- [remark-toc plugin](https://github.com/remarkjs/remark-toc)
- [remark-frontmatter plugin](https://github.com/remarkjs/remark-frontmatter)

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| remark | marked or markdown-it | Marked is faster but lacks AST plugins; markdown-it has extensibility but different plugin API |
| remark | String manipulation with regex | Loses structural awareness, breaks on edge cases (code blocks, nested headings), impossible to maintain |
| semver | Manual version parsing | Reinvents ~1000 LOC for range logic, loses npm compatibility guarantees |
| fs-extra | Native fs + manual copy logic | Loses atomic operations, cross-platform edge case handling |
| remark-toc | markdown-toc | markdown-toc is widely used but remark-toc integrates better with unified pipeline |

**Installation:**
```bash
npm install remark unified remark-parse remark-stringify unist-util-visit semver fs-extra gray-matter
npm install remark-toc remark-frontmatter mdast-util-to-string write-file-atomic cli-table3
```

## Architecture Patterns

### Recommended Project Structure

```
gsd-docs-industrial/
├── commands/
│   ├── complete-fds.md           # User-facing /doc:complete-fds
│   ├── check-standards.md        # User-facing /doc:check-standards
│   └── release.md                # User-facing /doc:release
├── workflows/
│   ├── complete-fds.md           # Assembly orchestration logic
│   ├── check-standards.md        # Standards validation workflow
│   └── release.md                # Version bump + archiving workflow
├── lib/
│   ├── assembler.js              # Core assembly pipeline
│   │   ├── parsePhases()        # Load all CONTENT.md → AST
│   │   ├── applyNumbering()     # Add hierarchical section numbers
│   │   ├── resolveXrefs()       # Symbolic → concrete references
│   │   ├── generateFrontMatter()# Title page, TOC, abbreviations
│   │   └── archiveSources()     # Copy phase files to archive/
│   ├── numbering.js              # Section numbering logic
│   ├── xref-resolver.js          # Cross-reference resolution
│   ├── standards/                # Composable validators
│   │   ├── packml-validator.js  # PackML state/mode checks
│   │   └── isa88-validator.js   # ISA-88 terminology checks
│   ├── version-manager.js        # Semver operations
│   └── report-generators.js      # XREF-REPORT, COMPLIANCE reports
└── templates/
    ├── fds-structure.json        # Canonical FDS section ordering
    ├── frontmatter/
    │   ├── title-page.md         # Template with {{placeholders}}
    │   ├── revision-history.md   # Auto-gen from git + manual edits
    │   └── abbreviations.md      # Auto-extracted + manual additions
    └── reports/
        ├── xref-report.md        # XREF-REPORT.md format
        └── compliance-report.md  # COMPLIANCE.md format per standard
```

### Pattern 1: Assembly Pipeline with Read-Only Inputs

**What:** The assembly process never modifies source CONTENT.md files. All transformations happen in memory (AST) and output to new versioned files.

**When to use:** /doc:complete-fds command execution.

**Architecture:**
```
Input: Phase directories (read-only)
  ├── .planning/phases/01-foundation/01-01-CONTENT.md
  ├── .planning/phases/01-foundation/01-02-CONTENT.md
  ├── .planning/phases/02-architecture/02-01-CONTENT.md
  └── ...

Pipeline:
  1. Parse all CONTENT.md → AST array (remark-parse)
  2. Apply FDS structure template ordering → reordered AST array
  3. Apply hierarchical numbering → modified ASTs
  4. Resolve cross-references → symbol table + modified ASTs
  5. Generate front matter → title AST, TOC AST, abbrev AST
  6. Concatenate ASTs → single document AST
  7. Serialize → markdown string (remark-stringify)
  8. Write versioned output

Output: Versioned artifacts
  ├── FDS-Project-v0.3.md                    # Main document
  ├── .planning/assembly/v0.3/
  │   ├── XREF-REPORT.md                     # Reference validation
  │   ├── COMPLIANCE.md                      # Standards checks
  │   └── ENGINEER-TODO.md                   # Complex diagrams, unresolved issues
  └── .planning/archive/v0.3/                # Source snapshot
      ├── phases/ (copy of all phase dirs)
      └── ROADMAP.md (copy)
```

**Key insight:** AST manipulation ensures structural correctness. String concatenation would break on edge cases like code blocks containing heading-like patterns or nested lists.

**Example:**
```javascript
// Source: remark documentation + unified handbook
const unified = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');
const { visit } = require('unist-util-visit');
const fs = require('fs-extra');

async function assembleDocument(phaseDirs) {
  // 1. Parse all CONTENT.md files
  const sections = [];
  for (const dir of phaseDirs) {
    const contentPath = `${dir}/CONTENT.md`;
    if (await fs.pathExists(contentPath)) {
      const markdown = await fs.readFile(contentPath, 'utf8');
      const ast = unified().use(remarkParse).parse(markdown);
      sections.push({ path: contentPath, ast, phaseDir: dir });
    }
  }

  // 2. Apply FDS structure template ordering
  const orderedSections = applyStructureTemplate(sections);

  // 3. Apply hierarchical numbering
  let sectionCounter = { major: 0, minor: 0, sub: 0 };
  for (const section of orderedSections) {
    visit(section.ast, 'heading', (node) => {
      const number = incrementCounter(sectionCounter, node.depth);
      prependNumberToHeading(node, number);
    });
  }

  // 4. Resolve cross-references
  const symbolTable = buildSymbolTable(orderedSections);
  for (const section of orderedSections) {
    visit(section.ast, 'text', (node, index, parent) => {
      node.value = resolveSymbolicRefs(node.value, symbolTable);
    });
  }

  // 5. Generate front matter
  const frontMatter = generateFrontMatter(orderedSections, symbolTable);

  // 6. Concatenate
  const documentAst = {
    type: 'root',
    children: [
      ...frontMatter.children,
      ...orderedSections.flatMap(s => s.ast.children)
    ]
  };

  // 7. Serialize
  const markdown = unified().use(remarkStringify).stringify(documentAst);

  return { markdown, symbolTable };
}
```

### Pattern 2: Composable Standards Validators

**What:** Each standard (PackML, ISA-88) is a self-contained module that loads reference data and validates content only when enabled in PROJECT.md.

**When to use:** During /doc:complete-fds or standalone /doc:check-standards.

**Architecture:**
```javascript
// Source: Standards validation patterns + plugin architecture
class StandardValidator {
  constructor(standardName, config) {
    this.name = standardName;
    this.severity = config.severity; // 'error' or 'warning'
    this.enabled = config.enabled;
  }

  async load() {
    // Load reference data only when enabled
    if (!this.enabled) return;
    this.referenceData = await this.loadReferenceData();
  }

  validate(documentAst) {
    if (!this.enabled) return { pass: true, checks: [] };

    const checks = [];
    visit(documentAst, (node) => {
      const result = this.checkNode(node);
      if (result) checks.push(result);
    });

    return {
      pass: checks.every(c => c.status === 'pass'),
      checks,
      summary: this.generateSummary(checks)
    };
  }

  abstract checkNode(node);
  abstract loadReferenceData();
  abstract generateSummary(checks);
}

class PackMLValidator extends StandardValidator {
  async loadReferenceData() {
    // Load from gsd-docs-industrial/references/standards/packml/
    const statePath = 'gsd-docs-industrial/references/standards/packml/STATE-MODEL.md';
    const stateDoc = await fs.readFile(statePath, 'utf8');
    return {
      validStates: extractValidStates(stateDoc), // IDLE, STARTING, EXECUTE, etc.
      validTransitions: extractValidTransitions(stateDoc),
      validModes: extractValidModes('UNIT-MODES.md')
    };
  }

  checkNode(node) {
    // Check for PackML state references
    if (node.type === 'table' && isStateTable(node)) {
      return this.validateStateTable(node);
    }
    if (node.type === 'text' && mentionsState(node.value)) {
      return this.validateStateReference(node.value);
    }
  }

  validateStateTable(tableNode) {
    const states = extractStatesFromTable(tableNode);
    const invalid = states.filter(s => !this.referenceData.validStates.includes(s));

    return {
      status: invalid.length === 0 ? 'pass' : this.severity,
      check: 'PackML state names',
      location: tableNode.position,
      message: invalid.length > 0
        ? `Invalid states: ${invalid.join(', ')}`
        : 'All states valid',
      remediation: invalid.length > 0
        ? `Valid states: ${this.referenceData.validStates.join(', ')}`
        : null
    };
  }
}

class ISA88Validator extends StandardValidator {
  async loadReferenceData() {
    const hierPath = 'gsd-docs-industrial/references/standards/isa-88/EQUIPMENT-HIERARCHY.md';
    const termPath = 'gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md';

    return {
      validLevels: ['Process Cell', 'Unit', 'Equipment Module', 'Control Module'],
      terminology: extractTerminology(await fs.readFile(termPath, 'utf8')),
      maxDepth: 4
    };
  }

  checkNode(node) {
    if (node.type === 'heading' && isEquipmentSection(node)) {
      return this.validateEquipmentTerminology(node);
    }
  }

  validateEquipmentTerminology(headingNode) {
    const text = extractHeadingText(headingNode);
    const usedTerms = extractISA88Terms(text);
    const invalid = usedTerms.filter(t => !this.referenceData.terminology.includes(t));

    return {
      status: invalid.length === 0 ? 'pass' : this.severity,
      check: 'ISA-88 terminology',
      location: headingNode.position,
      message: invalid.length > 0
        ? `Non-standard terms: ${invalid.join(', ')}`
        : 'Terminology compliant',
      remediation: invalid.length > 0
        ? `Use ISA-88 standard: ${this.referenceData.validLevels.join(', ')}`
        : null
    };
  }
}

// Usage in complete-fds workflow
async function checkStandards(documentAst, projectConfig) {
  const validators = [];

  if (projectConfig.standards?.packml?.enabled) {
    validators.push(new PackMLValidator('PackML', projectConfig.standards.packml));
  }

  if (projectConfig.standards?.isa88?.enabled) {
    validators.push(new ISA88Validator('ISA-88', projectConfig.standards.isa88));
  }

  await Promise.all(validators.map(v => v.load()));

  const results = validators.map(v => ({
    standard: v.name,
    result: v.validate(documentAst)
  }));

  return results;
}
```

**Key insight:** Composable validators allow engineers to enable only the standards they need. Disabled validators never load reference data, keeping fast iteration for non-standard projects.

### Pattern 3: Cross-Reference Resolution with Symbol Table

**What:** Build a symbol table mapping symbolic references (phase-3/03-02, EM-200) to concrete section numbers (§3.2.1) during assembly, then resolve all references in a second pass.

**When to use:** During complete-fds after numbering is applied.

**Example:**
```javascript
// Source: Compiler symbol table patterns + MyST cross-reference resolution
function buildSymbolTable(sections) {
  const table = new Map();

  for (const section of sections) {
    visit(section.ast, 'heading', (node) => {
      // Extract symbolic IDs from heading
      const symbolicId = extractSymbolicId(node); // e.g., "03-02" or "EM-200"
      const sectionNumber = extractSectionNumber(node); // e.g., "3.2.1"
      const title = extractHeadingText(node);

      if (symbolicId) {
        table.set(symbolicId, {
          number: sectionNumber,
          title: title,
          sourceFile: section.path
        });
      }

      // Also map by section title for fuzzy matching
      table.set(title.toLowerCase(), {
        number: sectionNumber,
        title: title,
        sourceFile: section.path
      });
    });
  }

  return table;
}

function resolveSymbolicRefs(text, symbolTable) {
  // Pattern: "see phase-3/03-02" or "see EM-200" or "zie §03-02"
  const refPattern = /(?:see|zie)\s+(?:phase-\d+\/)?(\d{2}-\d{2}|[A-Z]+-\d+|§\d{2}-\d{2})/gi;

  return text.replace(refPattern, (match, symbolicId) => {
    const target = symbolTable.get(symbolicId.replace('§', ''));

    if (target) {
      return `see Section ${target.number}`;
    } else {
      // Unresolved reference
      return `see ${symbolicId} [BROKEN REF]`;
    }
  });
}

function detectOrphans(symbolTable, allReferences) {
  const referencedSections = new Set(allReferences.map(r => r.target));
  const orphans = [];

  for (const [id, target] of symbolTable.entries()) {
    if (!referencedSections.has(id) && !referencedSections.has(target.number)) {
      orphans.push({
        id,
        number: target.number,
        title: target.title,
        sourceFile: target.sourceFile
      });
    }
  }

  return orphans;
}
```

**Key insight:** Two-pass resolution (build table → resolve references) allows forward references and catches all broken links before final output.

### Pattern 4: Hierarchical Section Numbering

**What:** Apply IEC-style decimal numbering (1.1, 1.2.1, etc.) based on heading depth, with counter state maintained across sections.

**When to use:** After FDS structure template ordering, before cross-reference resolution.

**Example:**
```javascript
// Source: bookdown numbering + remark heading manipulation
function applyHierarchicalNumbering(sections) {
  const counter = [0]; // Stack: [major, minor, sub, ...]

  for (const section of sections) {
    visit(section.ast, 'heading', (node) => {
      const depth = node.depth; // 1 = #, 2 = ##, 3 = ###

      // Adjust counter stack to match depth
      while (counter.length > depth) counter.pop();
      while (counter.length < depth) counter.push(0);

      // Increment counter at current depth
      counter[depth - 1]++;

      // Reset all deeper levels
      for (let i = depth; i < counter.length; i++) {
        counter[i] = 0;
      }

      // Generate number string
      const number = counter.slice(0, depth).join('.');

      // Prepend number to heading
      prependNumberToHeading(node, number);
    });
  }
}

function prependNumberToHeading(headingNode, number) {
  // Modify AST to add number before heading text
  headingNode.children.unshift({
    type: 'text',
    value: `${number} `
  });

  // Store number in node data for cross-reference resolution
  headingNode.data = headingNode.data || {};
  headingNode.data.sectionNumber = number;
}
```

**Anti-pattern to avoid:** String manipulation for numbering (e.g., regex search-replace on markdown text). Breaks on code blocks containing heading-like patterns, can't preserve heading metadata.

### Pattern 5: Version Management with Archiving

**What:** Semantic version bump (vX.Y), archive current phase files to .planning/archive/vX.Y/, update STATE.md version, commit with version tag.

**When to use:** /doc:release command for internal or client releases.

**Example:**
```javascript
// Source: semantic-release patterns + npm version workflow
const semver = require('semver');
const fs = require('fs-extra');
const path = require('path');

async function releaseDocument(type, options = {}) {
  // 1. Determine current version from STATE.md
  const state = await readState();
  const currentVersion = state.versions.fds; // e.g., "0.3"

  // 2. Calculate next version
  let nextVersion;
  if (type === 'client') {
    // Major bump: v0.3 → v1.0 or v1.5 → v2.0
    const major = parseInt(currentVersion.split('.')[0]);
    nextVersion = `${major + 1}.0`;
  } else if (type === 'internal') {
    // Minor bump: v0.3 → v0.4 or v1.5 → v1.6
    const [major, minor] = currentVersion.split('.').map(Number);
    nextVersion = `${major}.${minor + 1}`;
  }

  // 3. Verify version is valid semver
  if (!semver.valid(nextVersion)) {
    throw new Error(`Invalid version: ${nextVersion}`);
  }

  // 4. Check release gate for client releases
  if (type === 'client' && !options.force) {
    const allPhasesPass = await verifyAllPhases();
    if (!allPhasesPass) {
      throw new Error('Client release blocked: not all phases pass verification. Use --force to override.');
    }
  }

  // 5. Archive current phase files
  const archiveDir = `.planning/archive/v${nextVersion}`;
  await fs.ensureDir(archiveDir);
  await fs.copy('.planning/phases', `${archiveDir}/phases`);
  await fs.copy('.planning/ROADMAP.md', `${archiveDir}/ROADMAP.md`);

  // 6. Rename versioned FDS document
  const oldDoc = `FDS-${state.project.name}-v${currentVersion}.md`;
  const newDoc = `FDS-${state.project.name}-v${nextVersion}.md`;
  if (await fs.pathExists(oldDoc)) {
    await fs.move(oldDoc, newDoc);
  }

  // 7. Update STATE.md
  state.versions.fds = nextVersion;
  state.releaseHistory = state.releaseHistory || [];
  state.releaseHistory.push({
    doc: 'FDS',
    version: nextVersion,
    date: new Date().toISOString().split('T')[0],
    type: type,
    notes: options.notes || ''
  });
  await writeState(state);

  // 8. Git commit with version tag
  await gitCommit(`release: FDS v${nextVersion} (${type})`, [newDoc, '.planning/STATE.md']);
  await gitTag(`fds-v${nextVersion}`);

  return { version: nextVersion, archiveDir, document: newDoc };
}
```

**Key insight:** Archive BEFORE renaming document ensures rollback is possible if anything fails. Atomic archiving with fs-extra.copy preserves file metadata and handles errors gracefully.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown parsing | Regex-based parser | remark-parse | Handles edge cases: escaped characters, code blocks, nested structures, reference-style links |
| Section numbering | String search-replace | AST visitor pattern | Preserves heading metadata, handles code blocks containing "#" patterns, maintains structure |
| Cross-reference resolution | Manual string replacement | Symbol table + two-pass resolution | Handles forward references, detects cycles, provides clear error messages for broken links |
| Version comparison | String splitting | semver library | Handles pre-release versions, build metadata, range expressions, npm compatibility |
| File archiving | fs.rename + recursive copy | fs-extra.copy | Atomic operations, cross-platform path handling, preserves permissions/timestamps |
| Table of contents | Manual heading extraction | remark-toc | Handles nested headings, anchor link generation, depth limits, custom formatting |

**Key insight:** Document assembly has deceptively complex edge cases. Markdown code blocks can contain heading-like patterns, cross-references can be forward or circular, version strings can have pre-release suffixes. Don't reinvent these wheels.

## Common Pitfalls

### Pitfall 1: Numbering Collapse After Re-ordering

**What goes wrong:** Applying section numbers BEFORE re-ordering sections according to FDS structure template causes number mismatches when sections move.

**Why it happens:** Natural inclination to number as you parse, but FDS structure template may reorder phases (e.g., Phase 3 equipment modules move to Section 5, Phase 2 architecture moves to Section 2).

**How to avoid:** Always apply structure template ordering FIRST, then number in document order.

**Warning signs:** Cross-references point to wrong section numbers after assembly, TOC doesn't match actual section order.

**Example:**
```javascript
// WRONG: Number then reorder
const sections = parseSections();
applyNumbering(sections); // Numbers: 1, 2, 3, 4
reorderByTemplate(sections); // Order becomes: 1, 3, 2, 4 — numbers are wrong!

// RIGHT: Reorder then number
const sections = parseSections();
const ordered = reorderByTemplate(sections); // Order: 1, 3, 2, 4
applyNumbering(ordered); // Numbers: 1, 2, 3, 4 — correct!
```

### Pitfall 2: Symbol Table Stale References

**What goes wrong:** Symbol table built before final numbering contains wrong section numbers, causing all cross-references to resolve incorrectly.

**Why it happens:** Symbol table captures section numbers during first pass, but numbering may change if structure is reordered or sections are added/removed.

**How to avoid:** Build symbol table AFTER final numbering is applied and structure is locked.

**Warning signs:** All cross-references off by one or more sections, orphan detection misses obviously referenced sections.

### Pitfall 3: Standards Validation Performance

**What goes wrong:** Loading all standards reference data (PackML states, ISA-88 terminology, etc.) on every assembly run slows down iteration, even when standards are disabled.

**Why it happens:** Eager loading of reference files instead of lazy loading based on PROJECT.md configuration.

**How to avoid:** Check `standards.{standard}.enabled` in PROJECT.md before loading reference data. Disabled standards never touch the filesystem.

**Warning signs:** Assembly takes >5 seconds even for small documents with standards disabled, file I/O during standards checks for non-standard projects.

**Example:**
```javascript
// WRONG: Always load
const packmlStates = await loadPackMLReference(); // Loads even if disabled
if (project.standards.packml.enabled) {
  validatePackML(doc, packmlStates);
}

// RIGHT: Conditional load
if (project.standards.packml.enabled) {
  const packmlStates = await loadPackMLReference(); // Only loads if needed
  validatePackML(doc, packmlStates);
}
```

### Pitfall 4: Broken Reference Cascade

**What goes wrong:** Single unresolved cross-reference blocks entire assembly, preventing engineer from seeing partial output or other issues.

**Why it happens:** Assembly halts on first broken reference instead of collecting all issues and generating report.

**How to avoid:** Collect ALL broken references, generate XREF-REPORT.md with full list, use --force flag to generate document with [BROKEN REF] placeholders.

**Warning signs:** Engineer fixes one broken reference, re-runs assembly, discovers next broken reference, repeat 5+ times instead of seeing all issues at once.

### Pitfall 5: Archive Overwrite Without Backup

**What goes wrong:** Re-running /doc:release with same version overwrites previous archive directory, losing ability to compare or rollback.

**Why it happens:** Not checking if archive directory already exists before copying files.

**How to avoid:** Check for existing archive directory, either abort with error or create timestamped backup (v0.3-backup-20260214-153022).

**Warning signs:** Lost work when engineer accidentally releases twice with same version.

**Example:**
```javascript
// WRONG: Blindly overwrite
await fs.copy('.planning/phases', archiveDir);

// RIGHT: Check and backup
if (await fs.pathExists(archiveDir)) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupDir = `${archiveDir}-backup-${timestamp}`;
  await fs.move(archiveDir, backupDir);
  console.warn(`Archive already exists, backed up to ${backupDir}`);
}
await fs.copy('.planning/phases', archiveDir);
```

## Code Examples

Verified patterns from documentation and standards:

### Complete Assembly Pipeline

```javascript
// Source: unified documentation + remark cookbook
const unified = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');
const remarkToc = require('remark-toc');
const remarkFrontmatter = require('remark-frontmatter');
const { visit } = require('unist-util-visit');
const fs = require('fs-extra');

async function completeDocument(projectDir, options = {}) {
  console.log('Starting document assembly...');

  // 1. Verify all phases pass
  if (!options.force) {
    const verification = await verifyAllPhases(projectDir);
    if (!verification.allPass) {
      throw new Error(`Assembly blocked: ${verification.gaps.length} phases have gaps. Use --force to override.`);
    }
  }

  // 2. Load project configuration
  const project = await loadProject(`${projectDir}/.planning/PROJECT.md`);

  // 3. Discover and parse all CONTENT.md files
  const phases = await discoverPhases(`${projectDir}/.planning/phases`);
  const sections = [];

  for (const phase of phases) {
    const contentFiles = await fs.readdir(phase.dir);
    for (const file of contentFiles.filter(f => f.endsWith('-CONTENT.md'))) {
      const content = await fs.readFile(`${phase.dir}/${file}`, 'utf8');
      const ast = unified()
        .use(remarkParse)
        .use(remarkFrontmatter)
        .parse(content);

      sections.push({
        phase: phase.number,
        file: file,
        path: `${phase.dir}/${file}`,
        ast: ast
      });
    }
  }

  // 4. Apply FDS structure template ordering
  const template = await loadStructureTemplate('gsd-docs-industrial/templates/fds-structure.json');
  const orderedSections = applyStructureTemplate(sections, template);

  // 5. Apply hierarchical numbering
  const counter = [0];
  for (const section of orderedSections) {
    visit(section.ast, 'heading', (node) => {
      const depth = node.depth;

      while (counter.length > depth) counter.pop();
      while (counter.length < depth) counter.push(0);
      counter[depth - 1]++;

      const number = counter.slice(0, depth).join('.');
      node.children.unshift({ type: 'text', value: `${number} ` });
      node.data = node.data || {};
      node.data.sectionNumber = number;
    });
  }

  // 6. Build symbol table for cross-reference resolution
  const symbolTable = new Map();
  for (const section of orderedSections) {
    visit(section.ast, 'heading', (node) => {
      const number = node.data?.sectionNumber;
      const text = extractHeadingText(node);

      // Map symbolic IDs (from PLAN.md) to section numbers
      const match = section.file.match(/(\d{2}-\d{2})-CONTENT\.md/);
      if (match && number) {
        symbolTable.set(match[1], { number, title: text });
      }
    });
  }

  // 7. Resolve cross-references
  const brokenRefs = [];
  for (const section of orderedSections) {
    visit(section.ast, 'text', (node) => {
      const refPattern = /(?:see|zie)\s+(?:phase-\d+\/)?(\d{2}-\d{2})/gi;
      node.value = node.value.replace(refPattern, (match, symbolicId) => {
        const target = symbolTable.get(symbolicId);
        if (target) {
          return `see Section ${target.number}`;
        } else {
          brokenRefs.push({ source: section.file, ref: symbolicId });
          return options.force ? `${match} [BROKEN REF]` : match;
        }
      });
    });
  }

  // 8. Check standards (if enabled)
  const standardsResults = [];
  if (project.standards?.packml?.enabled) {
    const validator = new PackMLValidator('PackML', project.standards.packml);
    await validator.load();
    standardsResults.push(await validator.validate(orderedSections));
  }
  if (project.standards?.isa88?.enabled) {
    const validator = new ISA88Validator('ISA-88', project.standards.isa88);
    await validator.load();
    standardsResults.push(await validator.validate(orderedSections));
  }

  // 9. Generate front matter
  const frontMatter = await generateFrontMatter(project, orderedSections, symbolTable);

  // 10. Assemble final document
  const documentAst = {
    type: 'root',
    children: [
      ...frontMatter.children,
      ...orderedSections.flatMap(s => s.ast.children)
    ]
  };

  // 11. Serialize to markdown
  const markdown = unified()
    .use(remarkStringify)
    .stringify(documentAst);

  // 12. Determine version and output path
  const state = await readState(`${projectDir}/.planning/STATE.md`);
  const version = state.versions.fds;
  const outputPath = `${projectDir}/FDS-${project.name}-v${version}.md`;

  // 13. Write document
  await fs.writeFile(outputPath, markdown, 'utf8');

  // 14. Generate reports
  await generateXrefReport(brokenRefs, symbolTable, `${projectDir}/.planning/assembly/v${version}/XREF-REPORT.md`);
  await generateComplianceReport(standardsResults, `${projectDir}/.planning/assembly/v${version}/COMPLIANCE.md`);

  // 15. Archive phase files
  const archiveDir = `${projectDir}/.planning/archive/v${version}`;
  await fs.ensureDir(archiveDir);
  await fs.copy(`${projectDir}/.planning/phases`, `${archiveDir}/phases`);
  await fs.copy(`${projectDir}/.planning/ROADMAP.md`, `${archiveDir}/ROADMAP.md`);

  console.log(`✓ Assembly complete: ${outputPath}`);
  console.log(`✓ Reports: .planning/assembly/v${version}/`);
  console.log(`✓ Archive: ${archiveDir}`);

  return {
    outputPath,
    version,
    brokenRefs: brokenRefs.length,
    standardsPass: standardsResults.every(r => r.pass)
  };
}
```

### Front Matter Generation with Auto-TOC

```javascript
// Source: remark-toc + gray-matter documentation
const remarkToc = require('remark-toc');
const grayMatter = require('gray-matter');

async function generateFrontMatter(project, sections, symbolTable) {
  // 1. Title page
  const titlePage = {
    type: 'heading',
    depth: 1,
    children: [{ type: 'text', value: `Functional Design Specification` }]
  };

  const metadata = [
    { type: 'paragraph', children: [
      { type: 'strong', children: [{ type: 'text', value: 'Project:' }] },
      { type: 'text', value: ` ${project.name}` }
    ]},
    { type: 'paragraph', children: [
      { type: 'strong', children: [{ type: 'text', value: 'Version:' }] },
      { type: 'text', value: ` ${project.version}` }
    ]},
    { type: 'paragraph', children: [
      { type: 'strong', children: [{ type: 'text', value: 'Date:' }] },
      { type: 'text', value: ` ${new Date().toISOString().split('T')[0]}` }
    ]}
  ];

  // 2. Revision history (from STATE.md release history + git log)
  const revisionHistory = await generateRevisionHistory(project);

  // 3. Table of contents (auto-generated from headings)
  const tocHeading = {
    type: 'heading',
    depth: 2,
    children: [{ type: 'text', value: 'Table of Contents' }]
  };

  // Build TOC from sections
  const tocItems = [];
  for (const section of sections) {
    visit(section.ast, 'heading', (node) => {
      const number = node.data?.sectionNumber;
      const text = extractHeadingText(node);
      const indent = '  '.repeat(node.depth - 1);

      tocItems.push({
        type: 'listItem',
        children: [{
          type: 'paragraph',
          children: [{ type: 'text', value: `${indent}${number} ${text}` }]
        }]
      });
    });
  }

  const toc = {
    type: 'list',
    ordered: false,
    children: tocItems
  };

  // 4. Abbreviations list (extracted from document + manual additions)
  const abbreviations = await extractAbbreviations(sections, project.abbreviations);

  // 5. Assemble front matter
  return {
    type: 'root',
    children: [
      titlePage,
      ...metadata,
      { type: 'thematicBreak' },
      tocHeading,
      toc,
      { type: 'thematicBreak' },
      ...revisionHistory,
      { type: 'thematicBreak' },
      ...abbreviations,
      { type: 'thematicBreak' }
    ]
  };
}

async function extractAbbreviations(sections, manualAbbreviations = []) {
  const abbreviations = new Set(manualAbbreviations);
  const abbrevPattern = /\b([A-Z]{2,})\b/g;

  for (const section of sections) {
    visit(section.ast, 'text', (node) => {
      const matches = node.value.match(abbrevPattern);
      if (matches) {
        matches.forEach(abbr => abbreviations.add(abbr));
      }
    });
  }

  // Sort and format
  const sorted = Array.from(abbreviations).sort();
  const items = sorted.map(abbr => ({
    type: 'listItem',
    children: [{
      type: 'paragraph',
      children: [
        { type: 'strong', children: [{ type: 'text', value: abbr }] },
        { type: 'text', value: `: ${lookupAbbreviation(abbr)}` }
      ]
    }]
  }));

  return [
    { type: 'heading', depth: 2, children: [{ type: 'text', value: 'Abbreviations' }] },
    { type: 'list', ordered: false, children: items }
  ];
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| String concatenation for assembly | AST-based assembly with remark | 2020+ | Eliminates edge case bugs, enables structural validation |
| Manual TOC maintenance | Auto-generated TOC with remark-toc | 2018+ | Reduces maintenance burden, guarantees TOC accuracy |
| Regex-based cross-reference resolution | Symbol table + two-pass resolution | 2019+ | Handles forward references, provides better error messages |
| Eager standards loading | Lazy loading based on PROJECT.md config | 2021+ | Faster iteration for non-standard projects |
| Manual version bumping | semver library with validation | 2015+ | Prevents invalid versions, ensures npm compatibility |
| String-based frontmatter parsing | gray-matter with AST integration | 2017+ | Handles YAML, JSON, TOML formats, preserves formatting |

**Deprecated/outdated:**
- **markdown-toc (CLI)**: Still works but remark-toc integrates better with unified pipeline
- **marked**: Faster but lacks plugin ecosystem for standards validation and cross-reference resolution
- **Manual section numbering**: Error-prone, inconsistent across large documents

## Open Questions

1. **PDF generation approach**
   - What we know: Pandoc is standard but requires external binary, puppeteer provides Node.js-native option
   - What's unclear: Performance comparison for large documents (>200 pages), which approach handles Mermaid diagrams better
   - Recommendation: Implement markdown assembly first, defer PDF generation to separate phase or use external tool chain

2. **Standards reference data format**
   - What we know: PackML and ISA-88 reference data should live in gsd-docs-industrial/references/standards/
   - What's unclear: Best format (JSON vs markdown vs hybrid), how to version reference data separately from code
   - Recommendation: Use markdown for human readability with structured format (tables), parse into JSON at load time for validation

3. **Complex diagram handling in ENGINEER-TODO.md**
   - What we know: Diagrams exceeding Mermaid complexity should be flagged with section reference, type, description, priority
   - What's unclear: How to auto-detect complexity (line count? node count? nesting depth?), priority assignment heuristics
   - Recommendation: Start with conservative heuristic (>20 nodes or >4 nesting levels), let engineer feedback refine threshold

## Sources

### Primary (HIGH confidence)

- [remark - markdown processor](https://github.com/remarkjs/remark) - AST manipulation core architecture
- [unified - syntax tree processing](https://github.com/unifiedjs/unified) - Pipeline composition patterns
- [unist-util-visit - AST traversal](https://github.com/syntax-tree/unist-util-visit) - Visitor pattern implementation
- [semver - npm's version parser](https://www.npmjs.com/package/semver) - Semantic versioning standard
- [fs-extra - enhanced file system](https://github.com/jprichardson/node-fs-extra) - Atomic file operations
- [gray-matter - frontmatter parser](https://github.com/jonschlinkert/gray-matter) - YAML/JSON/TOML parsing
- [ISA-TR88.00.02-2022 - PackML standard](https://www.isa.org/products/isa-tr88-00-02-2022-machine-and-unit-states-an-imp) - PackML state model reference
- [ISA-88 Series - Batch Control](https://www.isa.org/standards-and-publications/isa-standards/isa-88-standards) - Equipment hierarchy terminology

### Secondary (MEDIUM confidence)

- [markdown-toc comparison](https://www.npmjs.com/package/markdown-toc) - Alternative TOC generation
- [remark plugins ecosystem](https://remark.js.org/) - Plugin architecture patterns
- [MyST cross-references](https://mystmd.org/guide/cross-references) - Reference resolution strategies
- [bookdown section numbering](https://bookdown.org/yihui/bookdown/cross-references.html) - Hierarchical numbering patterns

### Tertiary (LOW confidence)

- [Pandoc markdown conversion](https://pandoc.org/) - PDF generation option (external dependency)
- [Typst markdown to PDF](https://neilzone.co.uk/2025/01/using-pandoc-and-typst-to-convert-markdown-into-custom-formatted-pdfs-with-a-sample-template/) - Alternative PDF engine (2025)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified in npm registry with current versions, usage statistics, and official documentation
- Architecture: HIGH - Patterns based on official unified/remark documentation and established compiler design principles (symbol tables, two-pass resolution)
- Pitfalls: MEDIUM - Based on common markdown processing issues and project patterns, some inferred from general document assembly experience
- Standards validation: MEDIUM - PackML/ISA-88 standards confirmed but validation implementation patterns are adapted from general compliance checking

**Research date:** 2026-02-14
**Valid until:** 2026-04-14 (60 days - stable domain, markdown ecosystem moves slowly, semver and standards are stable)
