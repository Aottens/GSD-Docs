# Stack Research: Claude Code Plugin for Industrial Documentation

**Domain:** Claude Code custom command plugin (documentation generation)
**Researched:** 2026-02-06
**Confidence:** HIGH

## Executive Summary

GSD-Docs Industrial is not a traditional software project with npm packages and frameworks. It is a **Claude Code plugin** consisting entirely of:

1. **Markdown command files** with YAML frontmatter (the commands themselves)
2. **Markdown reference/template files** (injected into prompts via `@`-references)
3. **JSON configuration** (CATALOG.json, config.json)
4. **One DOCX template** (huisstijl.docx for Pandoc export)
5. **Two external CLI tools** (Pandoc and mermaid-cli, not bundled)

The "stack" is Claude Code's built-in plugin system. There is no build step, no transpilation, no package.json. The entire plugin is plain files that Claude Code discovers and loads.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Claude Code custom commands | Current | Slash command registration | The ONLY way to add `/doc:*` commands to Claude Code. Files in `~/.claude/commands/doc/` become `/doc:filename` commands |
| Claude Code subagents | Current | Subagent delegation for writing/verification | Files in `~/.claude/agents/` define specialized agents. GSD uses the Task tool to spawn subagents; GSD-Docs should do the same for write/verify operations |
| Markdown + YAML frontmatter | CommonMark + YAML 1.2 | Command file format, reference files, templates | This is what Claude Code parses. Not negotiable |
| JSON | Standard | Configuration (config.json, CATALOG.json) | Claude Code parses JSON natively. Used for structured data (typicals catalog, planning config) |

### Supporting Tools (External Dependencies)

| Tool | Version | Purpose | When Needed |
|------|---------|---------|-------------|
| Pandoc | 3.x (latest stable) | Markdown-to-DOCX conversion | Only at `/doc:export` time. Not needed for core workflow |
| @mermaid-js/mermaid-cli (mmdc) | 11.x (latest) | Render Mermaid diagrams to PNG | Only at `/doc:export` time. Called via `mmdc -i input.mmd -o output.png` |
| Git | 2.x | Version control for planning artifacts | Optional per config.json `git_integration` flag |
| Node.js | 18+ LTS | Required runtime for mermaid-cli | Only if mermaid-cli is used |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Any text editor | Authoring .md command files | VS Code recommended for YAML frontmatter highlighting |
| Claude Code CLI | Testing commands during development | Run `/doc:new-fds` etc. to test in real environment |
| `/agents` command | Managing subagent definitions | Interactive UI for creating/editing subagents in Claude Code |

---

## Command File Format (Exact Schema)

### Frontmatter Fields

Based on the GSD reference implementation and official Claude Code documentation, these are the supported frontmatter fields for custom command files:

```yaml
---
name: doc:command-name           # REQUIRED. Slash command name. "doc:" prefix for namespace
description: What this command does  # REQUIRED. Shows in /help and autocomplete
argument-hint: "<phase-number>"  # OPTIONAL. Hint shown during autocomplete
allowed-tools:                   # OPTIONAL. Tools the command can use without asking
  - Read
  - Write
  - Edit
  - Bash
  - Task                         # CRITICAL: Required for subagent spawning
  - Glob
  - Grep
  - AskUserQuestion              # For interactive user prompts
  - TodoWrite                    # For todo tracking
model: inherit                   # OPTIONAL. "sonnet", "opus", "haiku", or "inherit"
---
```

**Confidence: HIGH** -- Verified against GSD v1.6.4 command files (`new-project.md`, `execute-phase.md`, `verify-work.md`) and official Claude Code documentation at code.claude.com/docs/en/slash-commands.

### Frontmatter Rules

1. **`name` field**: Use `doc:command-name` format. The colon creates a namespace. Claude Code renders this as `/doc:command-name` in the interface.

2. **`allowed-tools` field**: List specific tools. If omitted, the command inherits tools from the current conversation. Including `Task` is **mandatory** for any command that spawns subagents.

3. **`argument-hint` field**: Shows in autocomplete. Use angle brackets for required args, square brackets for optional. Example: `"<phase-number> [--gaps]"`

4. **`description` field**: Keep under 80 characters. Shows in `/help` output.

5. **`model` field**: Omit to inherit from conversation. Set to `haiku` for fast, lightweight commands like `/doc:status`.

### Command Body Structure

The GSD reference implementation uses a consistent body structure with XML-style semantic sections:

```markdown
---
[frontmatter]
---

<objective>
What this command accomplishes.
What artifacts it creates.
What to run next.
</objective>

<execution_context>
@~/.claude/gsd-docs-industrial/references/some-reference.md
@~/.claude/gsd-docs-industrial/templates/some-template.md
@~/.claude/gsd-docs-industrial/workflows/some-workflow.md
</execution_context>

<context>
Phase: $ARGUMENTS

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>
## Phase 1: [Step Name]
[Instructions with bash commands, tool usage, decision logic]

## Phase 2: [Step Name]
[More instructions]
</process>

<success_criteria>
- [ ] Criterion 1
- [ ] Criterion 2
</success_criteria>
```

**Confidence: HIGH** -- Every GSD command file follows this exact pattern.

---

## @-Reference Pattern (Context Injection)

The `@` prefix injects file contents into the prompt at that position. This is the primary mechanism for giving Claude access to templates, references, and project state.

### Syntax

```markdown
# Absolute paths (for framework files)
@~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
@~/.claude/gsd-docs-industrial/templates/fds/section-equipment-module.md

# Relative paths (for project files)
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/phases/03-equipment/CONTEXT.md

# Dynamic (using $ARGUMENTS)
Phase: $ARGUMENTS
```

### Rules

1. **@-references are resolved at command invocation time** -- Claude sees the file contents inline, not the path.
2. **Use `~` for user-home paths** -- Works cross-platform in Claude Code.
3. **Use relative paths for project files** -- These are relative to the current working directory.
4. **`$ARGUMENTS` captures everything after the command name** -- `/doc:write-phase 3` sets `$ARGUMENTS` to `3`.
5. **`$1`, `$2` for positional args** -- Less commonly used; GSD prefers `$ARGUMENTS`.
6. **`!command` syntax executes bash inline** -- `!\`git diff HEAD\`` runs git diff and injects output. Requires `Bash` in `allowed-tools`.

**Confidence: HIGH** -- Verified against GSD command files and official Claude Code docs.

---

## Subagent Pattern

### Where Subagents Live

GSD-Docs needs subagents for:
- **doc-writer**: Writes CONTENT.md for a single plan (fresh context, no cross-contamination)
- **doc-verifier**: Runs goal-backward verification on a phase
- **doc-reviewer**: Simulates fresh-eyes review
- **doc-sds-generator**: Transforms FDS to SDS with typicals matching

Subagent files go in `~/.claude/agents/` (user-level, available in all projects):

```
~/.claude/agents/
  doc-writer.md
  doc-verifier.md
  doc-reviewer.md
  doc-sds-generator.md
```

### Subagent File Format

```markdown
---
name: doc-writer
description: Writes FDS content for a single section plan. Loads only the plan, context, and standards needed. Use for parallel section writing in /doc:write-phase.
tools: Read, Write, Bash, Glob, Grep
model: inherit
permissionMode: acceptEdits
---

You are a technical documentation writer for industrial FDS documents.

[System prompt with domain expertise, writing guidelines, output format...]
```

**Supported subagent frontmatter fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase + hyphens) |
| `description` | Yes | When Claude should delegate to this agent |
| `tools` | No | Tools available (inherits all if omitted) |
| `disallowedTools` | No | Tools to deny |
| `model` | No | "sonnet", "opus", "haiku", or "inherit" |
| `permissionMode` | No | "default", "acceptEdits", "dontAsk", "bypassPermissions", "plan" |
| `skills` | No | Skills to preload into subagent context |
| `hooks` | No | Lifecycle hooks scoped to this subagent |
| `memory` | No | Persistent memory: "user", "project", or "local" |

**Confidence: HIGH** -- Verified against official Claude Code documentation at code.claude.com/docs/en/sub-agents.

### How Commands Spawn Subagents

Commands use the `Task` tool to spawn subagents. The GSD pattern:

```
Task(
  prompt="<context>
    @.planning/PROJECT.md
    @.planning/phases/03-equipment/CONTEXT.md
    @.planning/phases/03-equipment/03-02-PLAN.md
  </context>

  Write the CONTENT.md for plan 03-02.
  Follow the plan exactly.
  Create 03-02-CONTENT.md and 03-02-SUMMARY.md in the phase directory.",

  subagent_type="doc-writer",
  description="Write section 03-02"
)
```

**Key constraint: Subagents cannot spawn other subagents.** This means orchestrator commands (`/doc:write-phase`) must handle all wave coordination in the main context, spawning leaf-level writers as subagents.

**For parallel execution**, spawn multiple Task calls in a single message:

```
Task(prompt="...", subagent_type="doc-writer", description="Write 03-01")
Task(prompt="...", subagent_type="doc-writer", description="Write 03-02")
Task(prompt="...", subagent_type="doc-writer", description="Write 03-03")
```

All three run in parallel. The Task tool blocks until all complete.

---

## File Layout

### Framework Files (Plugin)

```
~/.claude/
  commands/
    doc/                          # Command files -> /doc:* slash commands
      new-fds.md
      discuss-phase.md
      plan-phase.md
      write-phase.md
      verify-phase.md
      review-phase.md
      complete-fds.md
      generate-sds.md
      export.md
      status.md
      resume.md
      release.md
      help.md

  agents/                         # Subagent definitions
    doc-writer.md
    doc-verifier.md
    doc-reviewer.md
    doc-sds-generator.md

  gsd-docs-industrial/            # Supporting files (@-referenced)
    references/
      standards/
        packml/
          STATE-MODEL.md
          UNIT-MODES.md
        isa-88/
          EQUIPMENT-HIERARCHY.md
          TERMINOLOGY.md
      typicals/
        CATALOG.json
        library/
      verification-patterns.md
      writing-guidelines.md
      ui-brand.md                  # UI patterns (banners, symbols)
    templates/
      roadmap/
        type-a-nieuwbouw-standaard.md
        type-b-nieuwbouw-flex.md
        type-c-modificatie.md
        type-d-twn.md
      fds/
        section-equipment-module.md
        section-state-machine.md
        section-interface.md
      project.md
      requirements.md
      context.md
      plan.md
      verification-report.md
      summary.md
      huisstijl.docx               # Pandoc reference document
    workflows/
      write-phase.md               # Detailed workflow for write execution
      verify-phase.md              # Verification workflow
      discuss-phase.md             # Discussion workflow
    CLAUDE-CONTEXT.md              # Quick-load context summary
    VERSION                        # Current version number
```

### Project Files (Per-Project, Created by Commands)

```
<project-dir>/
  .planning/
    PROJECT.md
    REQUIREMENTS.md
    ROADMAP.md
    BASELINE.md                    # Type C/D only
    STATE.md
    config.json
    CROSS-REFS.md                  # Cross-reference registry
    phases/
      01-foundation/
        CONTEXT.md
        01-01-PLAN.md
        01-01-CONTENT.md
        01-01-SUMMARY.md
        VERIFICATION.md
        REVIEW.md                  # Optional
      02-architecture/
        ...
    archive/
      v1.0/
  output/
    FDS-[Project]-v[X.Y].md
    SDS-[Project]-v[X.Y].md
    RATIONALE.md
    EDGE-CASES.md
    TRACEABILITY.md
    ENGINEER-TODO.md
  diagrams/
    mermaid/                       # Source .mmd files
    rendered/                      # Output .png files
  export/
    FDS-[Project]-v[X.Y].docx
    SDS-[Project]-v[X.Y].docx
```

---

## Registration Mechanism

### How Claude Code Discovers Commands

Claude Code scans two directories for command files:

| Location | Scope | When to Use |
|----------|-------|-------------|
| `~/.claude/commands/doc/` | **User-level** (all projects) | GSD-Docs commands. Available everywhere, just like GSD's `/gsd:*` |
| `.claude/commands/` | **Project-level** (one project) | Not recommended for GSD-Docs. Commands should be global. |

The filename (minus `.md`) becomes the command name. The `name` field in frontmatter takes precedence if present.

**GSD-Docs commands go in `~/.claude/commands/doc/`** -- this creates the `/doc:` namespace and makes commands available in every project directory.

### How Claude Code Discovers Subagents

| Location | Scope | Priority |
|----------|-------|----------|
| `.claude/agents/` | Project-level | 2 (higher) |
| `~/.claude/agents/` | User-level | 3 (lower) |
| Plugin `agents/` dir | Plugin scope | 4 (lowest) |

**GSD-Docs subagents go in `~/.claude/agents/`** -- user-level, available in all projects. This matches the pattern: commands are global, so agents must be global too.

### Plugin Registration Alternative

Claude Code supports a formal plugin system with `.claude-plugin/plugin.json`. For distribution, GSD-Docs could be packaged as a plugin:

```
gsd-docs-industrial/
  .claude-plugin/
    plugin.json
  commands/
    new-fds.md
    ...
  agents/
    doc-writer.md
    ...
  skills/
    (none currently)
```

**plugin.json:**
```json
{
  "name": "gsd-docs-industrial",
  "version": "1.0.0",
  "description": "GSD workflow adapted for FDS/SDS industrial documentation",
  "author": {
    "name": "Author"
  },
  "commands": ["./commands/"],
  "agents": "./agents/"
}
```

**Recommendation:** Start with the simple approach (files in `~/.claude/commands/doc/` and `~/.claude/agents/`). Migrate to plugin format when distribution becomes a priority. The underlying file format is identical.

**Confidence: HIGH** -- Plugin system verified against code.claude.com/docs/en/plugins-reference.

---

## Dependencies and Installation

### External Dependencies

```bash
# Required for /doc:export only
# Windows (via Chocolatey or Scoop)
choco install pandoc
# OR
scoop install pandoc

# Mermaid CLI (requires Node.js 18+)
npm install -g @mermaid-js/mermaid-cli

# Verify installations
pandoc --version    # Expected: 3.x
mmdc --version      # Expected: 0.x or 11.x (mermaid-cli)
```

### No Build Step

There is **no package.json, no npm install, no build step** for the plugin itself. All files are plain Markdown and JSON. Claude Code reads them directly.

### Installation of GSD-Docs

```bash
# Create command directory
mkdir -p ~/.claude/commands/doc

# Copy command files
cp commands/*.md ~/.claude/commands/doc/

# Copy agent files
cp agents/*.md ~/.claude/agents/

# Copy supporting files
cp -r references templates workflows CLAUDE-CONTEXT.md VERSION ~/.claude/gsd-docs-industrial/
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| User-level commands (`~/.claude/commands/doc/`) | Plugin package (`.claude-plugin/plugin.json`) | When distributing to other users or installing via marketplace |
| User-level agents (`~/.claude/agents/`) | Plugin agents (`agents/` in plugin dir) | Same as above -- distribution |
| Pandoc for DOCX export | python-docx library | If you need programmatic DOCX manipulation beyond what Pandoc templates offer |
| mermaid-cli for diagram rendering | PlantUML, Kroki API | If Mermaid syntax is insufficient for your diagram types |
| Markdown as source format | reStructuredText, AsciiDoc | Not applicable -- Claude Code commands must be Markdown |
| `~/.claude/gsd-docs-industrial/` for refs | Embedding content directly in commands | If commands become too large. But @-references keep commands lean and references reusable |

---

## What NOT to Use and Why

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `.claude/commands/` (project-level) for GSD-Docs commands | Commands would only work in one project. GSD-Docs is a tool, not a project-specific config | `~/.claude/commands/doc/` (user-level) |
| Skills system (`.claude/skills/`) for commands | Skills are auto-invoked by Claude based on context, which is wrong for explicit user-triggered workflows like `/doc:write-phase 3` | Standard commands in `~/.claude/commands/doc/` |
| Nested subagent spawning | Subagents CANNOT spawn other subagents in Claude Code. This is a hard constraint | Orchestrator command spawns leaf-level subagents directly |
| `git add .` or `git add -A` in commands | Can accidentally stage sensitive files or large binaries | Always stage files individually by name |
| Hardcoded standards content in commands | Violates opt-in principle. Not all projects use PackML/ISA-88 | Conditional @-references: load standards only when `PROJECT.md` has `standards.packml.enabled: true` |
| Large monolithic command files | Claude Code loads the entire command file into context. A 2000-line command wastes tokens | Split into command file (lean orchestrator) + workflow file (@-referenced) + template files |
| `model: haiku` for writing/verification agents | Haiku lacks the reasoning depth for technical documentation and verification | `model: inherit` or `model: sonnet` for quality-critical agents. Use `haiku` only for fast read-only tasks like `/doc:status` |
| `bypassPermissions` on writer agents | Writer agents modify files; you want at least `acceptEdits` for safety | `permissionMode: acceptEdits` |
| Embedding Pandoc/mermaid logic in command files | Export is a separate concern from the documentation workflow | Isolate export logic in `/doc:export` command and its workflow file |
| Forking GSD and modifying it | GSD and GSD-Docs have different outputs (code vs docs). Forking creates maintenance burden | Standalone plugin that follows GSD's patterns |

---

## Stack Patterns by Context

### Pattern: Command as Lean Orchestrator

Commands should be lean orchestrators that delegate heavy work.

**Do this:**
```markdown
---
name: doc:write-phase
description: Write all sections of a phase with parallel execution
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
  - Glob
  - AskUserQuestion
---

<objective>
Write all sections of phase N using wave-based parallel execution.
</objective>

<execution_context>
@~/.claude/gsd-docs-industrial/workflows/write-phase.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
</execution_context>

<process>
[Lean orchestration: discover plans, group waves, spawn doc-writer agents]
</process>
```

**Not this:**
```markdown
---
name: doc:write-phase
---

[2000 lines of inline writing logic, templates, verification, everything...]
```

### Pattern: Conditional Standards Loading

```markdown
<process>
## Step 1: Check Standards Config

Read PROJECT.md and check standards configuration.

If packml.enabled:
  Load @~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md
  Include PackML state names in writing instructions

If isa88.enabled:
  Load @~/.claude/gsd-docs-industrial/references/standards/isa-88/TERMINOLOGY.md
  Include ISA-88 hierarchy in writing instructions

If neither:
  Use flexible terminology per project preferences
</process>
```

### Pattern: Fresh Context per Section

Each writer subagent gets ONLY what it needs:

```
Task(prompt="
  Context:
  @.planning/PROJECT.md                          # Project config
  @.planning/phases/03-equipment/CONTEXT.md      # Phase decisions
  @.planning/phases/03-equipment/03-02-PLAN.md   # This specific plan

  Standards (if enabled):
  @~/.claude/gsd-docs-industrial/references/standards/packml/STATE-MODEL.md

  Template:
  @~/.claude/gsd-docs-industrial/templates/fds/section-equipment-module.md

  DO NOT load other PLAN.md or CONTENT.md files.
  Write ONLY 03-02-CONTENT.md and 03-02-SUMMARY.md.
", subagent_type="doc-writer", description="Write 03-02 EM-200")
```

---

## Version Compatibility

| Component A | Compatible With | Notes |
|-------------|-----------------|-------|
| Claude Code CLI | Any version with custom commands support | Custom commands have been stable since 2024 |
| Pandoc 3.x | huisstijl.docx reference template | Generate initial reference with `pandoc -o ref.docx --print-default-data-file reference.docx`, then customize styles |
| mermaid-cli 11.x | Mermaid syntax in CONTENT.md | Supports `stateDiagram-v2`, `flowchart`, `sequenceDiagram`. Block-beta support limited |
| Node.js 18+ LTS | mermaid-cli | Required runtime. Node 20 or 22 LTS also work |

---

## Key Differences from GSD

Understanding where GSD-Docs diverges from GSD is critical for avoiding copy-paste mistakes:

| Aspect | GSD | GSD-Docs |
|--------|-----|----------|
| Output of execution | Source code files | CONTENT.md documentation files |
| Subagent type for execution | `gsd-executor` (writes code) | `doc-writer` (writes documentation) |
| Commit strategy | Per-task atomic commits | Optional (configurable via `git_integration` in config.json) |
| Plan output | Code changes + SUMMARY.md | CONTENT.md + SUMMARY.md |
| Verification | Codebase inspection (files exist, exports work) | Content inspection (sections complete, standards compliant, facts consistent) |
| Extra outputs | None | RATIONALE.md, EDGE-CASES.md, CROSS-REFS.md, ENGINEER-TODO.md |
| Post-milestone | Archive + next milestone | Complete-FDS + generate-SDS + export DOCX |
| Project types | Single type | 4 types (A/B/C/D) with different ROADMAP templates |
| Dynamic roadmap | Fixed at creation | Evolves after System Overview phase |

---

## Windows-Specific Considerations

The development environment is Windows. Key notes:

1. **Path separators**: Claude Code handles `~` expansion cross-platform. Use forward slashes in @-references.
2. **Bash commands in commands**: Claude Code's Bash tool runs Git Bash or WSL on Windows. Most Unix commands work.
3. **Pandoc**: Available via `choco install pandoc` or direct MSI installer.
4. **mermaid-cli**: Requires Node.js. Install via `npm install -g @mermaid-js/mermaid-cli`.
5. **Line endings**: Markdown files should use LF (not CRLF) for consistency. Configure git: `git config core.autocrlf input`.

---

## Sources

- GSD reference implementation v1.6.4 at `~/.claude/get-shit-done/` -- 24 command files, 7 reference files, 6 workflow files examined directly
- GSD-Docs SPECIFICATION.md v2.7.0 -- the SSOT for all GSD-Docs behavior
- [Claude Code Slash Commands Documentation](https://code.claude.com/docs/en/slash-commands) -- official frontmatter fields, file format
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- skills vs commands relationship
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) -- subagent file format, frontmatter fields, spawning patterns, permission modes
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference) -- plugin.json schema, directory structure, component specifications
- [Claude Code Customization Guide](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) -- frontmatter schema reference
- [BioErrorLog Custom Slash Commands](https://en.bioerrorlog.work/entry/claude-code-custom-slash-command) -- @-reference syntax, $ARGUMENTS handling
- [Pandoc User's Guide](https://pandoc.org/MANUAL.html) -- --reference-doc for DOCX templates
- [mermaid-cli GitHub](https://github.com/mermaid-js/mermaid-cli) -- mmdc CLI usage for diagram rendering

---
*Stack research for: Claude Code plugin for industrial FDS/SDS documentation*
*Researched: 2026-02-06*
