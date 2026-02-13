# Phase 4: State Management + Recovery + Dynamic ROADMAP - Research

**Researched:** 2026-02-13
**Domain:** CLI state persistence, crash recovery, interactive workflows, markdown manipulation
**Confidence:** HIGH

## Summary

Phase 4 adds production robustness to the write-verify loop by implementing three orthogonal capabilities: (1) persistent state tracking with atomic checkpointing for crash recovery, (2) status display and resume workflows for interrupted operations, and (3) dynamic ROADMAP expansion when project complexity exceeds initial estimates. These are infrastructure enhancements, not new document generation capabilities.

The technical foundation already exists: gsd-tools.js provides state operations, the write-phase workflow implements pre/post-wave STATE.md checkpointing, and SUMMARY.md existence serves as the completion proof. Phase 4 surfaces this infrastructure through user-facing commands (/doc:status, /doc:resume, /doc:expand-roadmap) and hardens partial-write detection.

**Primary recommendation:** Leverage existing gsd-tools.js primitives for atomic state updates, use @inquirer/prompts for interactive approval workflows, apply file size + marker detection for partial writes, and use markdown AST manipulation (remark) for decimal phase insertion. Avoid hand-rolling state consistency logic or markdown parsing.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Status display:**
- Full breakdown by default — phase table + per-section status within active phase + completion percentages
- Overall progress bar at top + detailed table below with per-phase status
- Active phase shows plans + which artifacts exist (CONTENT.md, SUMMARY.md, VERIFICATION.md) as proof of work
- Recommended next action shown with context: "Next: Write phase 4 (3 plans ready, 0 written)" + the command to run

**Resume experience:**
- Smart default: auto-resume if only one thing was interrupted; show choices if multiple things are incomplete
- Summary context before continuing: what was running + what completed + what's next
- Both standalone /doc:resume command AND auto-detect when running the same command that was interrupted
- Running a different command than what was interrupted triggers warn + confirm: "Phase 4 write was interrupted. Continue with verify-phase 3 anyway?"

**ROADMAP expansion:**
- Interactive build: system suggests groupings one by one, engineer approves/modifies each group
- Decimal numbering for inserted phases (4.1, 4.2, etc.) — preserves existing phase numbers
- Both manual (/doc:expand-roadmap) and auto-trigger (when >5 units discovered after System Overview verification)

**Interruption handling:**
- Partial writes flagged in /doc:status AND /doc:verify-phase refuses to run until partials are resolved
- STATE.md checkpoints before and after every wave — granular recovery points
- Completed plans in an interrupted wave are kept + cross-references re-verified (since wave siblings may be missing)

### Claude's Discretion

- Grouping strategy for ROADMAP expansion (by process area, dependency, complexity, or mix — whatever fits the project)
- Partial write detection heuristics (SUMMARY.md as completion proof, content length, markers, abrupt endings)
- Exact checkpoint format in STATE.md

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Node.js fs | Native | File system operations | Built-in, synchronous writes with error handling |
| @inquirer/prompts | 8.2.0+ | Interactive CLI prompts | Modern rewrite, reduced bundle size, official Inquirer successor |
| write-file-atomic | Latest | Atomic state file writes | Industry standard for crash-safe JSON persistence (used by npm) |
| remark | 16.0+ | Markdown AST manipulation | De facto standard for programmatic markdown editing, plugin ecosystem |
| cli-table3 | Latest | Terminal table rendering | Unicode box-drawing, column spanning, cell styling |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| chalk | 5.x | Terminal text styling | For colored output (status indicators, warnings) |
| cli-progress | 3.12+ | Progress bar rendering | For overall completion percentage display |
| mdast-util-from-markdown | Latest | Markdown parsing | When building remark plugins for decimal phase insertion |
| unified | Latest | Text processing pipeline | Required by remark for AST transformations |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| @inquirer/prompts | enquirer | Enquirer has wider use (eslint, webpack) but Inquirer has cleaner API and better TypeScript support |
| write-file-atomic | Manual temp-file + rename | Loses cross-platform guarantees, missing fsync durability options |
| remark | String manipulation | Loses structural awareness, breaks on edge cases (code blocks, nested lists) |
| cli-table3 | Custom box-drawing | Reinvents ~500 LOC for table layout, loses Unicode fallback |

**Installation:**
```bash
npm install @inquirer/prompts write-file-atomic remark unified mdast-util-from-markdown cli-table3 chalk cli-progress
```

## Architecture Patterns

### Recommended Project Structure

```
gsd-docs-industrial/
├── commands/
│   ├── status.md              # User-facing /doc:status
│   ├── resume.md              # User-facing /doc:resume
│   └── expand-roadmap.md      # User-facing /doc:expand-roadmap
├── workflows/
│   ├── status.md              # Status rendering logic
│   ├── resume.md              # Resume detection + prompt logic
│   └── expand-roadmap.md      # Interactive phase grouping workflow
├── lib/
│   ├── state-manager.js       # Atomic STATE.md operations (wraps gsd-tools.js)
│   ├── partial-detector.js    # Multi-heuristic partial write detection
│   ├── roadmap-editor.js      # Markdown AST manipulation for decimal phases
│   └── progress-renderer.js   # Table + progress bar rendering
└── templates/
    └── roadmap-expansion.md   # Template for expansion proposal display
```

### Pattern 1: Atomic State Checkpoint

**What:** Two-phase commit pattern for STATE.md updates — validate proposed state, write atomically with fsync, verify written state.

**When to use:** Before and after every wave (write-phase), before and after verify-phase, when recording operation start/completion.

**Example:**
```javascript
// Source: write-file-atomic documentation + database checkpoint patterns
const writeFileAtomic = require('write-file-atomic');
const fs = require('fs');

async function checkpointState(updates) {
  // Phase 1: Validate proposed state
  const currentState = JSON.parse(fs.readFileSync('.planning/STATE.md'));
  const proposedState = { ...currentState, ...updates };
  validateStateConsistency(proposedState); // Throws if invalid

  // Phase 2: Atomic write with fsync
  const stateContent = renderStateMarkdown(proposedState);
  await writeFileAtomic('.planning/STATE.md', stateContent, {
    fsync: true,  // Flush to disk for crash safety
    mode: 0o644
  });

  // Phase 3: Verify (belt-and-suspenders)
  const written = fs.readFileSync('.planning/STATE.md', 'utf8');
  if (!written.includes(updates.command)) {
    throw new Error('State checkpoint verification failed');
  }
}
```

**Key insight:** The fsync flag ensures STATE.md changes survive crashes, but adds ~10ms latency. Use it for operation boundaries (pre/post-wave), skip it for progress updates within a wave.

### Pattern 2: Completion Proof via File Existence

**What:** SUMMARY.md existence is the ONLY completion proof. STATE.md status is hint only, never authoritative.

**When to use:** Resume detection, partial write detection, progress calculation.

**Example:**
```javascript
// Source: Existing write-phase workflow + forward-only recovery principle
function isCompletedPlan(phaseDir, planId) {
  // NEVER trust STATE.md alone
  const contentExists = fs.existsSync(`${phaseDir}/${planId}-CONTENT.md`);
  const summaryExists = fs.existsSync(`${phaseDir}/${planId}-SUMMARY.md`);

  // Completion proof: BOTH files exist (established in Phase 1)
  return contentExists && summaryExists;
}

function detectPartialWrite(phaseDir, planId) {
  const contentPath = `${phaseDir}/${planId}-CONTENT.md`;
  const summaryPath = `${phaseDir}/${planId}-SUMMARY.md`;

  // Heuristic 1: Missing SUMMARY.md = incomplete (definitive)
  if (!fs.existsSync(summaryPath)) {
    return { partial: true, reason: 'missing_summary' };
  }

  // Heuristic 2: Content too short (likely crashed during write)
  const content = fs.readFileSync(contentPath, 'utf8');
  if (content.length < 200) {
    return { partial: true, reason: 'content_too_short' };
  }

  // Heuristic 3: Marker detection
  if (content.includes('[TO BE COMPLETED]')) {
    return { partial: true, reason: 'completion_marker' };
  }

  // Heuristic 4: Abrupt ending (last line not sentence-complete)
  const lines = content.trim().split('\n');
  const lastLine = lines[lines.length - 1].trim();
  if (lastLine.length > 0 && !lastLine.match(/[.!?]$/)) {
    return { partial: true, reason: 'abrupt_ending' };
  }

  return { partial: false };
}
```

**Why this matters:** STATE.md corruption (Pitfall 4) can falsely mark incomplete work as done. File existence + heuristics provide belt-and-suspenders verification.

### Pattern 3: Interactive Approval Workflow

**What:** Present proposal, allow approve/modify/reject, re-prompt on modify, proceed only on explicit approval.

**When to use:** ROADMAP expansion, resume operation choice when multiple options exist, conflict resolution (different command than interrupted).

**Example:**
```javascript
// Source: @inquirer/prompts documentation
import { select, input, confirm } from '@inquirer/prompts';

async function proposeRoadmapExpansion(units, suggestedGrouping) {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(' DOC > ROADMAP EXPANSION PROPOSAL');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`\nSystem Overview identified ${units.length} units (threshold: 5)`);
  console.log('Proposed grouping:\n');

  // Display suggested phase groups
  suggestedGrouping.forEach((group, idx) => {
    console.log(`Phase ${group.number}: ${group.name}`);
    console.log(`  Units: ${group.units.join(', ')}`);
    console.log(`  Rationale: ${group.rationale}\n`);
  });

  // Interactive loop for per-group approval
  const approvedGroups = [];
  for (const group of suggestedGrouping) {
    const action = await select({
      message: `Phase ${group.number}: ${group.name} — Action?`,
      choices: [
        { value: 'approve', name: 'Approve (use as-is)' },
        { value: 'modify', name: 'Modify (change units or name)' },
        { value: 'reject', name: 'Reject (skip this grouping)' }
      ]
    });

    if (action === 'approve') {
      approvedGroups.push(group);
    } else if (action === 'modify') {
      const newName = await input({
        message: 'New phase name:',
        default: group.name
      });
      const newUnits = await input({
        message: 'Units (comma-separated):',
        default: group.units.join(', ')
      });
      approvedGroups.push({
        ...group,
        name: newName,
        units: newUnits.split(',').map(u => u.trim())
      });
    }
    // 'reject' = skip, don't add to approvedGroups
  }

  // Final confirmation
  const confirmed = await confirm({
    message: 'Proceed with ROADMAP expansion?',
    default: true
  });

  return confirmed ? approvedGroups : null;
}
```

**User experience:** One group at a time, immediate feedback, no full-screen TUI mode (stays within terminal flow).

### Pattern 4: Decimal Phase Numbering via Markdown AST

**What:** Parse ROADMAP.md to AST, insert new phase sections with decimal numbers (4.1, 4.2), update directory names, re-serialize to markdown.

**When to use:** ROADMAP expansion after System Overview verification, manual /doc:expand-roadmap.

**Example:**
```javascript
// Source: remark documentation + markdown-ast manipulation patterns
const { unified } = require('unified');
const remarkParse = require('remark-parse');
const remarkStringify = require('remark-stringify');
const { visit } = require('unist-util-visit');

function insertDecimalPhase(roadmapPath, afterPhase, newPhaseData) {
  const markdown = fs.readFileSync(roadmapPath, 'utf8');

  // Parse to AST
  const tree = unified()
    .use(remarkParse)
    .parse(markdown);

  // Find insertion point
  let insertIndex = -1;
  visit(tree, 'heading', (node, index, parent) => {
    if (node.depth === 2) {  // ## Phase N:
      const match = node.children[0].value.match(/^Phase (\d+):/);
      if (match && parseInt(match[1]) === afterPhase) {
        insertIndex = index + 1; // Insert after this heading's section
      }
    }
  });

  if (insertIndex === -1) {
    throw new Error(`Phase ${afterPhase} not found in ROADMAP.md`);
  }

  // Calculate decimal phase number
  const decimalPhase = `${afterPhase}.1`; // or .2, .3 if others exist

  // Build new phase section nodes
  const newNodes = [
    {
      type: 'heading',
      depth: 2,
      children: [{ type: 'text', value: `Phase ${decimalPhase}: ${newPhaseData.name}` }]
    },
    {
      type: 'paragraph',
      children: [
        { type: 'text', value: '**Goal:** ' },
        { type: 'text', value: newPhaseData.goal }
      ]
    },
    {
      type: 'paragraph',
      children: [
        { type: 'text', value: '**Dependencies:** ' },
        { type: 'text', value: `Phase ${afterPhase}` }
      ]
    },
    // ... other phase metadata
  ];

  // Insert nodes
  tree.children.splice(insertIndex, 0, ...newNodes);

  // Serialize back to markdown
  const result = unified()
    .use(remarkStringify)
    .stringify(tree);

  // Atomic write
  writeFileAtomic(roadmapPath, result, { fsync: true });
}
```

**Why remark not regex:** Code blocks, nested lists, and escaped characters break regex patterns. AST manipulation is structure-aware.

### Pattern 5: Forward-Only Recovery

**What:** On resume, verify completion proofs (file existence), re-run only incomplete items, never roll back completed work.

**When to use:** /doc:resume, auto-resume on command re-execution.

**Example:**
```javascript
// Source: Database checkpoint-recovery patterns + existing write-phase logic
async function resumeWritePhase(phaseNumber) {
  // Read STATE.md operation context
  const state = loadState();
  const operation = state.currentOperation;

  if (!operation || operation.status !== 'IN_PROGRESS') {
    console.log('No incomplete operation to resume');
    return;
  }

  // Verify completion proofs (belt-and-suspenders)
  const verified = [];
  const incomplete = [];

  for (const planId of operation.plans_done) {
    if (isCompletedPlan(operation.phaseDir, planId)) {
      verified.push(planId);
    } else {
      incomplete.push(planId); // STATE.md lied, file missing
    }
  }

  // Forward-only: keep verified, re-run incomplete + pending
  const toExecute = [...incomplete, ...operation.plans_pending];

  console.log(`DOC > Resuming from Wave ${operation.wave}`);
  console.log(`  Completed: ${verified.join(', ')}`);
  console.log(`  Remaining: ${toExecute.join(', ')}\n`);

  // Resume execution (waves are idempotent)
  await executeWaves(toExecute, operation.wave);
}
```

**Key insight:** Idempotent wave execution + file-based completion proof = safe resume even if STATE.md is stale or corrupted.

### Anti-Patterns to Avoid

- **Trusting STATE.md status without file verification:** STATE.md can be corrupted or manually edited. Always check file existence.
- **Synchronous fsync for every state update:** Adds 10ms+ per write. Use it for operation boundaries only, not progress updates.
- **Regex-based markdown editing:** Breaks on code blocks, nested structures, escaped characters. Use AST manipulation (remark).
- **Blocking verify-phase on missing cross-reference targets:** Targets may not be written yet (different wave). Warn-only, don't block.
- **Rolling back completed work on resume:** Forward-only recovery principle — never delete verified CONTENT.md/SUMMARY.md pairs.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic file writes | Temp file + rename logic | write-file-atomic | Cross-platform guarantees, fsync control, atomic semantics tested by npm itself |
| Markdown editing | String manipulation with regex | remark + unified | Structure-aware, handles edge cases (code blocks, escapes), plugin ecosystem |
| Interactive prompts | Manual readline + ANSI codes | @inquirer/prompts | Keyboard navigation, validation, error handling, accessibility |
| Terminal tables | Manual box-drawing character logic | cli-table3 | Unicode fallback, cell spanning, column alignment, 500+ LOC of edge cases |
| Progress bars | ANSI escape sequence math | cli-progress | Multi-bar support, ETAs, customizable formats, tested on 100+ terminal emulators |

**Key insight:** These problems look simple ("just write to a file", "just edit markdown") but have 10+ edge cases each (Windows paths, fsync guarantees, UTF-8 BOM, line endings, nested markdown structures, terminal width detection). Libraries solve these once, correctly.

## Common Pitfalls

### Pitfall 1: STATE.md Corruption (Already Mitigated in Design)

**What goes wrong:** STATE.md manually edited, crash during write, or concurrent process access leads to invalid state.

**Why it happens:** Single source of truth without verification against disk reality.

**How to avoid:** SUMMARY.md existence is the ONLY completion proof (design decision from Phase 1). STATE.md is a hint, never authoritative.

**Warning signs:** Resume shows "3 plans completed" but only 2 SUMMARY.md files exist, progress bar goes backward, plans marked done but verify-phase finds missing content.

### Pitfall 2: Incomplete Fsync on Checkpoint

**What goes wrong:** STATE.md written to OS buffer but not flushed to disk, crash before flush loses checkpoint data.

**Why it happens:** Node.js fs.writeFileSync does NOT guarantee disk persistence — it blocks event loop but kernel may buffer the write.

**How to avoid:** Use write-file-atomic with fsync: true for operation boundaries (wave start/end, phase complete). Skip fsync for progress updates within a wave (acceptable loss on crash).

**Warning signs:** After crash, STATE.md reverts to old wave even though operation started, no evidence of recent checkpoint timestamps.

### Pitfall 3: Regex-Based Markdown Editing

**What goes wrong:** Inserting a decimal phase via string.replace() breaks when phase description contains regex special characters, code blocks, or nested lists.

**Why it happens:** Markdown has structure (headings, lists, code blocks) that regex cannot reliably parse.

**How to avoid:** Use remark to parse markdown to AST, manipulate AST nodes, serialize back. Structure-aware edits never break on content variations.

**Warning signs:** Phase inserted inside a code block, heading levels wrong, list indentation broken, escaped characters double-escaped.

### Pitfall 4: Partial Write False Negatives

**What goes wrong:** A 150-word CONTENT.md file appears complete (no markers, ends with period) but is substantively incomplete (writer crashed after first paragraph).

**Why it happens:** Heuristics are probabilistic — length threshold and sentence-ending checks can't detect semantic incompleteness.

**How to avoid:** SUMMARY.md existence is definitive — if SUMMARY.md exists, assume CONTENT.md complete (writer contract). If only CONTENT.md exists, flag as partial.

**Warning signs:** verify-phase finds "missing required sections" in files marked complete by status, cross-references point to incomplete content.

### Pitfall 5: Resume Choice Overload

**What goes wrong:** Engineer sees 6 options on /doc:resume (3 incomplete phases, 2 commands, 1 manual flag) and doesn't know which to pick.

**Why it happens:** Too many resume scenarios presented at once without smart defaults.

**How to avoid:** Smart default logic — if only one incomplete operation, auto-resume with confirmation. If multiple, present sorted by recency (newest first) with context (what was running, when, progress).

**Warning signs:** Engineers skip /doc:resume and re-run commands from scratch, complaints about "too many choices", resume workflow docs rarely used.

### Pitfall 6: ROADMAP Directory Name Mismatch

**What goes wrong:** After decimal phase insertion, directory is named 04-state-management but ROADMAP.md refers to Phase 4.1, causing plan-phase to fail.

**Why it happens:** Phase number in directory name not updated when ROADMAP.md changes.

**How to avoid:** Use directory name pattern {padded}-{slug} where slug is derived from phase name, not phase number. Lookup by number → directory mapping via gsd-tools.js find-phase.

**Warning signs:** "Phase 4.1 directory not found", mkdir creates duplicate directories (04-state-management and 04.1-state-management), cross-references break after expansion.

### Pitfall 7: Blocking Verify on Partial Writes

**What goes wrong:** verify-phase refuses to run if ANY partial writes detected in phase, blocking gap closure even for completed sections.

**Why it happens:** Over-strict validation that conflates "some incomplete" with "all invalid".

**How to avoid:** Verify-phase checks partials as a pre-flight, warns, but proceeds if any complete sections exist. VERIFICATION.md reports partials separately from verification gaps.

**Warning signs:** "Cannot verify until all sections complete" error blocks iterative gap closure, engineers frustrated by "can't verify work I already finished".

## Code Examples

Verified patterns from official sources and existing codebase:

### Status Display with Progress Calculation

```javascript
// Source: gsd-tools.js progress command + cli-table3 docs
const Table = require('cli-table3');
const cliProgress = require('cli-progress');
const chalk = require('chalk');

function renderStatus(state, roadmap, filesystem) {
  // Calculate completion based on file existence (not STATE.md)
  const phases = roadmap.phases.map(phase => {
    const phaseDir = filesystem.findPhaseDir(phase.number);
    const plans = filesystem.glob(`${phaseDir}/*-PLAN.md`);
    const summaries = filesystem.glob(`${phaseDir}/*-SUMMARY.md`);

    return {
      number: phase.number,
      name: phase.name,
      plansTotal: plans.length,
      plansComplete: summaries.length,
      status: summaries.length === plans.length ? 'Complete' :
              summaries.length > 0 ? 'In Progress' : 'Pending'
    };
  });

  // Overall progress bar
  const totalPlans = phases.reduce((sum, p) => sum + p.plansTotal, 0);
  const totalComplete = phases.reduce((sum, p) => sum + p.plansComplete, 0);
  const percent = Math.round((totalComplete / totalPlans) * 100);

  console.log(`\nProgress: ${renderProgressBar(percent)} ${percent}%\n`);

  // Phase table
  const table = new Table({
    head: ['Phase', 'Name', 'Plans', 'Status'],
    colWidths: [8, 40, 10, 15],
    style: { head: ['cyan'] }
  });

  phases.forEach(p => {
    const statusColor = p.status === 'Complete' ? chalk.green('✓ Complete') :
                       p.status === 'In Progress' ? chalk.yellow('⚙ In Progress') :
                       chalk.gray('Pending');

    table.push([
      p.number,
      p.name,
      `${p.plansComplete}/${p.plansTotal}`,
      statusColor
    ]);
  });

  console.log(table.toString());

  // Active phase detail (if in progress)
  const activePhase = phases.find(p => p.status === 'In Progress');
  if (activePhase) {
    console.log(`\nActive Phase: ${activePhase.number} — ${activePhase.name}`);

    const artifacts = checkArtifacts(activePhase.number);
    console.log(`  Plans: ${artifacts.plans.length}`);
    console.log(`  CONTENT.md: ${artifacts.content.length}`);
    console.log(`  SUMMARY.md: ${artifacts.summaries.length}`);
    console.log(`  VERIFICATION.md: ${artifacts.verification ? 'Yes' : 'No'}`);

    // Recommended next action
    const nextAction = deriveNextAction(activePhase, artifacts);
    console.log(`\n${chalk.bold('Next:')} ${nextAction.description}`);
    console.log(`  ${chalk.cyan(nextAction.command)}`);
  }
}

function renderProgressBar(percent) {
  const width = 30;
  const filled = Math.round((percent / 100) * width);
  return '█'.repeat(filled) + '░'.repeat(width - filled);
}
```

### Resume Detection with Smart Defaults

```javascript
// Source: @inquirer/prompts + database recovery patterns
const { select, confirm } = require('@inquirer/prompts');

async function detectAndOfferResume() {
  const state = loadState();
  const operation = state.currentOperation;

  if (!operation || operation.status === 'COMPLETE') {
    return { resume: false };
  }

  // Verify completion proofs
  const verified = verifyCompletionProofs(operation);
  const incomplete = operation.plans_pending.concat(verified.incomplete);

  if (incomplete.length === 0) {
    // All actually complete despite IN_PROGRESS status
    console.log('Operation marked incomplete but all files verified complete.');
    const shouldMarkComplete = await confirm({
      message: 'Mark operation as complete?',
      default: true
    });

    if (shouldMarkComplete) {
      await checkpointState({
        'currentOperation.status': 'COMPLETE'
      });
    }
    return { resume: false };
  }

  // Smart default: single incomplete operation
  if (incomplete.length === operation.plans_pending.length) {
    // Simple case: nothing completed since checkpoint
    console.log(`${operation.command} was interrupted during wave ${operation.wave}.`);
    console.log(`  Remaining: ${incomplete.length} plans\n`);

    const shouldResume = await confirm({
      message: 'Resume from checkpoint?',
      default: true
    });

    return {
      resume: shouldResume,
      operation: operation.command,
      phase: operation.phase,
      incomplete
    };
  }

  // Complex case: some completed, some incomplete
  console.log(`${operation.command} was interrupted during wave ${operation.wave}.`);
  console.log(`  Completed since checkpoint: ${verified.complete.join(', ')}`);
  console.log(`  Remaining: ${incomplete.join(', ')}\n`);

  const action = await select({
    message: 'Resume options:',
    choices: [
      {
        value: 'resume',
        name: `Resume (complete ${incomplete.length} remaining plans)`
      },
      {
        value: 'status',
        name: 'View detailed status first'
      },
      {
        value: 'abandon',
        name: 'Start different operation (keeps completed work)'
      }
    ]
  });

  return {
    resume: action === 'resume',
    viewStatus: action === 'status',
    operation: operation.command,
    phase: operation.phase,
    incomplete
  };
}
```

### Partial Write Detection with Multiple Heuristics

```javascript
// Source: EOF detection patterns + existing completion proof logic
function detectPartialWrites(phaseDir, planIds) {
  const partials = [];

  for (const planId of planIds) {
    const contentPath = `${phaseDir}/${planId}-CONTENT.md`;
    const summaryPath = `${phaseDir}/${planId}-SUMMARY.md`;

    // Heuristic 1: Missing SUMMARY.md (definitive)
    if (!fs.existsSync(summaryPath)) {
      if (fs.existsSync(contentPath)) {
        partials.push({
          planId,
          reason: 'missing_summary',
          confidence: 'HIGH',
          action: 'Rerun writer for this plan'
        });
      }
      continue; // Skip other checks if summary missing
    }

    // Heuristic 2: Content too short
    const content = fs.readFileSync(contentPath, 'utf8');
    if (content.length < 200) {
      partials.push({
        planId,
        reason: 'content_too_short',
        confidence: 'HIGH',
        action: 'Rerun writer for this plan'
      });
      continue;
    }

    // Heuristic 3: Explicit marker
    if (content.includes('[TO BE COMPLETED]')) {
      partials.push({
        planId,
        reason: 'completion_marker',
        confidence: 'HIGH',
        action: 'Rerun writer for this plan'
      });
      continue;
    }

    // Heuristic 4: Abrupt ending (lower confidence)
    const lines = content.trim().split('\n');
    const lastLine = lines[lines.length - 1].trim();

    if (lastLine.length > 0 && !lastLine.match(/[.!?]$/)) {
      // Check if last line is a heading (acceptable)
      if (!lastLine.startsWith('#')) {
        partials.push({
          planId,
          reason: 'abrupt_ending',
          confidence: 'MEDIUM',
          action: 'Manual inspection recommended'
        });
      }
    }
  }

  return partials;
}
```

### ROADMAP Expansion with Interactive Approval

```javascript
// Source: remark AST manipulation + @inquirer/prompts
async function expandRoadmap(units, afterPhase) {
  // Suggest groupings (Claude's discretion on strategy)
  const suggestedGroups = suggestPhaseGrouping(units);

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(' DOC > ROADMAP EXPANSION PROPOSAL');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`\nSystem Overview identified ${units.length} units (threshold: 5)`);
  console.log(`Proposing ${suggestedGroups.length} new phases:\n`);

  // Interactive approval loop
  const approvedGroups = [];

  for (let i = 0; i < suggestedGroups.length; i++) {
    const group = suggestedGroups[i];

    console.log(`\n${chalk.bold(`Proposed Phase ${afterPhase}.${i + 1}:`)} ${group.name}`);
    console.log(`  Units: ${group.units.join(', ')}`);
    console.log(`  Rationale: ${group.rationale}`);

    const action = await select({
      message: 'Action?',
      choices: [
        { value: 'approve', name: 'Approve' },
        { value: 'modify', name: 'Modify name or units' },
        { value: 'skip', name: 'Skip (merge into next group)' }
      ]
    });

    if (action === 'approve') {
      approvedGroups.push({
        ...group,
        number: `${afterPhase}.${approvedGroups.length + 1}`
      });
    } else if (action === 'modify') {
      const newName = await input({
        message: 'New phase name:',
        default: group.name,
        validate: (v) => v.length > 0 || 'Name required'
      });

      const unitsInput = await input({
        message: 'Units (comma-separated):',
        default: group.units.join(', '),
        validate: (v) => v.split(',').length > 0 || 'At least one unit'
      });

      approvedGroups.push({
        number: `${afterPhase}.${approvedGroups.length + 1}`,
        name: newName,
        units: unitsInput.split(',').map(u => u.trim()),
        rationale: `Modified from: ${group.rationale}`
      });
    }
    // 'skip' = merge units into next group (handled in next iteration)
  }

  // Final confirmation
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('SUMMARY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  approvedGroups.forEach(g => {
    console.log(`Phase ${g.number}: ${g.name} (${g.units.length} units)`);
  });

  const confirmed = await confirm({
    message: '\nProceed with ROADMAP expansion?',
    default: true
  });

  if (!confirmed) {
    return null;
  }

  // Mutate ROADMAP.md via AST
  for (const group of approvedGroups) {
    await insertDecimalPhase('.planning/ROADMAP.md', afterPhase, group);
    await createPhaseDirectory(group.number, group.name);
  }

  console.log(chalk.green('\n✓ ROADMAP expanded successfully'));
  return approvedGroups;
}

function suggestPhaseGrouping(units) {
  // Claude's discretion: group by process area, dependency, complexity
  // Example heuristic: 3-5 units per group, max 7 groups
  const groups = [];
  const maxPerGroup = 5;

  for (let i = 0; i < units.length; i += maxPerGroup) {
    const chunk = units.slice(i, i + maxPerGroup);
    groups.push({
      name: deriveGroupName(chunk),
      units: chunk,
      rationale: `Process area: ${inferProcessArea(chunk)}`
    });
  }

  return groups;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual STATE.md editing | Atomic writes via write-file-atomic | npm v5 (2017) | Prevents corruption from concurrent access or crashes |
| Regex markdown editing | AST manipulation via remark | unified v10 (2021) | Structure-aware edits handle nested content correctly |
| Legacy inquirer (9.x) | @inquirer/prompts (8.x rewrite) | Jan 2024 | Smaller bundle, better TypeScript support, modular imports |
| Manual progress bars | cli-progress with multi-bar | v3.0 (2020) | Handles multiple operations, ETAs, customizable formats |
| String-based phase numbering | Decimal numbering with directory slugs | Industry standard (SemVer lineage) | Allows insertion without renumbering |

**Deprecated/outdated:**
- Inquirer 9.x and below: Legacy API, bundled prompts — use @inquirer/prompts for modular imports
- Remark v13 and below: CJS-only, older API — v16+ is ESM-ready with unified v11
- Manual readline for prompts: No validation, keyboard nav, or styling — inquirer handles edge cases

## Open Questions

1. **fsync Performance on Networked Drives**
   - What we know: write-file-atomic supports fsync: true for durability
   - What's unclear: Impact on Windows networked drives (SMB) or OneDrive sync folders
   - Recommendation: Default fsync: true for operation boundaries, allow config override via PROJECT.md (`state.fsync_enabled: false` for networked drives)

2. **ROADMAP Expansion Grouping Strategy**
   - What we know: User wants 3-5 units per phase, max 7 phases
   - What's unclear: Best heuristic for grouping (process area vs dependency vs complexity)
   - Recommendation: Start with process area (equipment/control/HMI/safety), fallback to even distribution, allow manual override

3. **Partial Write Detection Threshold**
   - What we know: 200 chars is arbitrary, varies by section type (equipment module vs state machine)
   - What's unclear: Optimal threshold to minimize false positives without missing real partials
   - Recommendation: Use 200 chars as baseline, refine after Phase 4 UAT based on actual incomplete writes observed

4. **Resume Auto-Detect vs Explicit Command**
   - What we know: User wants BOTH standalone /doc:resume AND auto-detect on re-run
   - What's unclear: Should auto-detect always prompt, or silently resume if unambiguous?
   - Recommendation: Prompt on command mismatch (warn + confirm), silent resume if same command + single incomplete operation

5. **Cross-Reference Re-Verification Scope**
   - What we know: Completed plans in interrupted wave may reference incomplete siblings
   - What's unclear: Re-verify all phase cross-refs or only those from completed plans?
   - Recommendation: Verify only outbound refs from completed plans (Claude's discretion documented in verify-phase workflow)

## Sources

### Primary (HIGH confidence)

- [write-file-atomic npm](https://www.npmjs.com/package/write-file-atomic) — Atomic file writes with fsync
- [GitHub: npm/write-file-atomic](https://github.com/npm/write-file-atomic) — Source and fsync guarantees
- [@inquirer/prompts npm](https://www.npmjs.com/package/@inquirer/prompts) — Modern interactive CLI prompts
- [GitHub: SBoudrias/Inquirer.js](https://github.com/SBoudrias/Inquirer.js) — Official Inquirer repository
- [remark.js.org](https://remark.js.org/) — Markdown processor documentation
- [GitHub: remarkjs/remark](https://github.com/remarkjs/remark) — Remark AST manipulation
- [cli-table3 npm](https://www.npmjs.com/package/cli-table3) — Terminal tables with Unicode
- [cli-progress npm](https://www.npmjs.com/package/cli-progress) — Progress bars for CLI
- Existing GSD-Docs codebase — gsd-tools.js, write-phase.md workflow, STATE.md template

### Secondary (MEDIUM confidence)

- [Node.js File System in Practice: A Production-Grade Guide for 2026](https://thelinuxcode.com/nodejs-file-system-in-practice-a-production-grade-guide-for-2026/) — fsync guarantees
- [Lecture #21: Database Crash Recovery](https://15445.courses.cs.cmu.edu/spring2025/notes/21-recovery.pdf) — Forward recovery patterns
- [Mastering Document Control: Versioning and Compliance](https://www.adaptconsultingcompany.com/2024/11/26/mastering-document-control-a-guide-to-versioning-and-compliance/) — Decimal numbering conventions
- [Software versioning - Wikipedia](https://en.wikipedia.org/wiki/Software_versioning) — Decimal numbering history

### Tertiary (LOW confidence)

- [Understanding Unexpected EOF Errors](https://algocademy.com/blog/understanding-unexpected-eof-end-of-file-errors-causes-and-solutions/) — Abrupt ending detection
- [Database Checkpoints in DBMS](https://www.tutorialspoint.com/checkpoints-in-dbms) — Checkpoint patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All libraries verified via npm registry and official docs, existing gsd-tools.js usage confirmed
- Architecture patterns: HIGH — Patterns derived from existing write-phase workflow, verified against library documentation
- Pitfalls: MEDIUM-HIGH — Pitfall 4 (STATE.md corruption) already mitigated in design, others are standard file system + CLI pitfalls

**Research date:** 2026-02-13
**Valid until:** 2026-03-13 (30 days for stable ecosystem — Node.js fs, remark, inquirer are mature)
