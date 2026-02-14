---
name: doc:export
description: Export FDS/SDS document to DOCX with corporate styling
argument-hint: "[document] [--draft] [--skip-diagrams] [--output path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>

Export assembled FDS/SDS markdown document to client-ready DOCX format with corporate styling, auto-generated lists (TOC, figures, tables), and embedded Mermaid diagrams rendered to PNG.

**Core promise:** This command transforms technical markdown documentation into professional Word documents ready for client delivery, bridging the gap between engineer-friendly markdown and client-expected DOCX format.

**Process:**
- Validate prerequisites (Pandoc, optional mermaid-cli, huisstijl.docx reference doc)
- Auto-detect input document if not specified (latest in output/ directory)
- Render Mermaid diagrams to PNG with complexity budget enforcement
- Convert markdown to DOCX using Pandoc with corporate styling reference
- Handle draft exports (omit lists, add DRAFT watermark)
- Gracefully degrade when mermaid-cli unavailable (--skip-diagrams)
- Route complex/failed diagrams to ENGINEER-TODO.md

**Output:** Professional DOCX file in export/ directory with styled formatting, embedded diagrams, and auto-generated lists

**Optional flags:**
- `--draft` - Work-in-progress export: omits list of figures/tables, adds DRAFT suffix, skips size validation
- `--skip-diagrams` - Skip Mermaid rendering entirely, use text placeholders instead
- `--output [path]` - Custom output path (default: export/{document-name}.docx)

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/export.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

@.planning/STATE.md
@.planning/PROJECT.md

</context>

<process>

Follow the workflow in export.md exactly. The workflow contains 10 comprehensive steps covering the full DOCX export pipeline from prerequisite validation through Pandoc conversion, Mermaid rendering, and ENGINEER-TODO generation for deferred diagrams.

**Prerequisite checks (before workflow delegation):**

1. **Check Pandoc installed:**
   ```bash
   pandoc --version
   ```
   If not found: Display error with installation instructions (brew install pandoc / apt-get install pandoc / choco install pandoc)

2. **Verify input document:**
   - If `[document]` argument provided: verify file exists
   - If no argument: scan `output/` for latest assembled FDS or SDS document (by modification time)
   - If no documents found: Display error "No assembled documents found in output/. Run /doc:complete-fds first."

3. **Check huisstijl.docx reference document:**
   ```bash
   ls ~/.claude/gsd-docs-industrial/references/huisstijl.docx
   ```
   If missing: Display warning "Corporate style template not found at gsd-docs-industrial/references/huisstijl.docx. Export will use Pandoc defaults. Place your reference template there for branded output."
   Continue (non-blocking warning)

4. **Check mermaid-cli (optional):**
   ```bash
   mmdc --version
   ```
   If not found AND --skip-diagrams NOT set: Display info "mermaid-cli not found. Auto-enabling --skip-diagrams flag. Install @mermaid-js/mermaid-cli via npm to render diagrams."
   Auto-enable --skip-diagrams flag

After prerequisite checks pass, delegate ALL export logic to the workflow.

</process>

<success_criteria>

- [ ] Pandoc available (blocks if missing)
- [ ] Input document found (auto-detect or explicit path)
- [ ] huisstijl.docx checked (warning if missing, continue)
- [ ] mermaid-cli checked (auto-enable --skip-diagrams if missing)
- [ ] Workflow invoked with correct arguments
- [ ] DOCX file generated in export/ directory
- [ ] Mermaid diagrams rendered to PNG (unless --skip-diagrams)
- [ ] Complex diagrams routed to ENGINEER-TODO.md
- [ ] Draft exports marked with DRAFT suffix
- [ ] Export completion banner displayed with file size and diagram count

</success_criteria>
