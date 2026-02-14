---
name: doc:release
description: Manage document versioning — promote draft to client release or bump internal version
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

<objective>

Version management for FDS documents following a two-tier versioning scheme:

**Version scheme:**
- **v0.x** - Internal drafts (pre-release)
- **v1.0** - First client release
- **v1.1, v1.2, v1.3** - Internal revisions of v1.0 (post-release drafts)
- **v2.0** - Second client release
- **v2.1, v2.2** - Internal revisions of v2.0
- And so on...

**Release types:**

1. **Internal release** (`--type internal`):
   - Minor version bump: v0.3 → v0.4, v1.2 → v1.3
   - No verification gate required (drafts can be incomplete)
   - Archives current version for historical tracking
   - Creates git tag for version tracking

2. **Client release** (`--type client`):
   - Major version bump with minor reset: v0.4 → v1.0, v1.3 → v2.0
   - Requires all phases to pass verification (blocks unless --force used)
   - Archives complete source documentation
   - Generates revision history from git commits (flagged for engineer review)
   - Creates git tag for release tracking

**Independent versioning:**
- FDS and SDS are versioned independently
- This command manages FDS versions only
- SDS versioning is handled by /doc:generate-sds (Phase 7)
- Both tracked in STATE.md Versions section

**Output:** Versioned FDS document, archive directory, updated STATE.md, git tag.

</objective>

<execution_context>

@~/.claude/gsd-docs-industrial/workflows/release.md
@~/.claude/gsd-docs-industrial/references/ui-brand.md
@~/.claude/gsd-docs-industrial/CLAUDE-CONTEXT.md

</execution_context>

<context>

@.planning/PROJECT.md
@.planning/STATE.md
@.planning/ROADMAP.md

</context>

<process>

**Required argument:**
- `--type {client|internal}` - Which version bump to perform

**Optional flags:**
- `--force` - Allow client release even with verification warnings (document will carry 'DRAFT' annotation)
- `--notes "Release notes text"` - Additional notes to include in revision history entry

**Pre-flight display:**
1. Read STATE.md to determine current version
2. Calculate target version based on --type argument
3. Display: "Current: v{current} → Target: v{next} ({type})"
4. Confirm with engineer before proceeding

**Execution:**
Follow the workflow in release.md exactly. The workflow handles:
- Version calculation (minor bump for internal, major bump for client)
- Verification gate (client releases only, with --force override)
- Archive creation at .planning/archive/vX.Y/
- Revision history auto-generation from git
- FDS document versioning
- STATE.md updates (Versions section, FDS only)
- Git commit and tag creation

</process>

<success_criteria>

- [ ] --type argument validated (must be "client" or "internal")
- [ ] Current and target versions displayed before execution
- [ ] Client releases blocked if phases not verified (unless --force)
- [ ] Archive created at .planning/archive/vX.Y/ with complete source
- [ ] Revision history auto-generated from git, flagged for review on client releases
- [ ] STATE.md Versions section updated (FDS line only, SDS unchanged)
- [ ] Git tag created (fds-vX.Y)
- [ ] DOC > prefix used in all output

</success_criteria>
