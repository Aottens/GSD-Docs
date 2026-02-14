<workflow>

# Release Version Management Workflow

Comprehensive version management workflow for FDS document releases. Handles internal draft bumps (v0.3 → v0.4, v1.2 → v1.3) and client release promotions (v0.4 → v1.0, v1.3 → v2.0) with verification gates, source archiving, revision history generation, and independent FDS/SDS versioning.

**Invoked by:** /doc:release command
**Tools required:** Read, Write, Bash, Glob, Grep
**Expected duration:** 30-60 seconds

---

## Step 1: Parse Arguments and Determine Version

**Objective:** Validate release type, read current version from STATE.md, calculate next version, and display transition to engineer.

**Actions:**

1. **Validate --type argument:**
   ```bash
   if [[ "$TYPE" != "client" && "$TYPE" != "internal" ]]; then
     echo "ERROR: --type must be 'client' or 'internal'"
     exit 1
   fi
   ```

2. **Read current FDS version from STATE.md:**
   - Read `.planning/STATE.md`
   - Look for `## Versions` section
   - Extract line starting with `- FDS: v`
   - Parse version number (e.g., "v0.3", "v1.2", "v2.0")

3. **Handle initialization case:**
   - If Versions section doesn't exist OR shows "v0.0 (not started)":
     - For `--type internal`: Initialize at v0.1 (first internal draft)
     - For `--type client`: Display error and exit
       ```
       ╔══════════════════════════════════════════════════════════════╗
       ║  ERROR                                                       ║
       ╚══════════════════════════════════════════════════════════════╝

       No assembled FDS exists yet. Cannot create client release.

       **To fix:**
       1. Run /doc:complete-fds to assemble the FDS document
       2. Run /doc:release --type internal for first internal version
       3. After verification, run /doc:release --type client for first client release
       ```

4. **Calculate next version:**
   - Parse current version into major.minor (e.g., "v1.2" → major=1, minor=2)
   - **Internal release:** Increment minor, keep major (v0.3 → v0.4, v1.2 → v1.3)
   - **Client release:** Increment major, reset minor to 0 (v0.4 → v1.0, v1.3 → v2.0)

5. **Display version transition:**
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DOC > RELEASING FDS VERSION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Current: v{current} → Target: v{next} ({type})

   Version scheme:
   - v0.x internal drafts (pre-release)
   - v1.0 first customer-facing release
   - v1.1, v1.2 internal revisions
   - v2.0 next customer release
   ```

6. **Confirmation prompt:**
   ```
   ──────────────────────────────────────────────────────────────
   > Proceed with release? (Y/n)
   ──────────────────────────────────────────────────────────────
   ```
   - If user types 'n' or 'no': exit gracefully
   - If user types 'Y', 'y', or Enter: continue

**Verification:**
- [ ] --type argument is "client" or "internal"
- [ ] Current version extracted from STATE.md
- [ ] Next version calculated correctly
- [ ] Version transition displayed to engineer

---

## Step 2: Verification Gate (Client Releases Only)

**Objective:** Enforce quality gate for client releases — all phases must be verified. Internal releases skip this step.

**Actions:**

1. **Skip for internal releases:**
   - If `--type internal`: skip to Step 3
   - Display: "◆ Skipping verification gate for internal release (drafts can be incomplete)"

2. **Client release verification gate:**
   - Read `.planning/STATE.md`
   - Read `.planning/ROADMAP.md`
   - Extract all phase numbers and their status from STATE.md Progress table

3. **Check phase statuses:**
   - For each phase in ROADMAP:
     - Look for status in STATE.md Progress table
     - Collect phases that are NOT "Verified" or "✓ Verified"
     - Phases can be: Pending, In Progress, Complete (not verified), Verified, Blocked

4. **If unverified phases found:**
   - Display error box with unverified phase list
   - Check if `--force` flag is present:
     - If `--force` present: continue with warning
     - If `--force` NOT present: block and exit

   **Without --force (block):**
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║  ERROR: Verification Required                                ║
   ╚══════════════════════════════════════════════════════════════╝

   Client releases require all phases to pass verification.

   **Unverified phases:**
   - Phase 3: Write + Verify (Core Value) - Status: Complete
   - Phase 5: Complete-FDS + Standards - Status: In Progress

   **To fix:**
   1. Run /doc:verify-phase for each unverified phase
   2. Address any gaps found during verification
   3. Re-run /doc:release --type client

   **Or to force release with warnings:**
   /doc:release --type client --force
   (Document will carry 'DRAFT' annotation)
   ```

   **With --force (warn but continue):**
   ```
   ⚠ WARNING: FORCED RELEASE

   Some phases are not fully verified. Document will carry 'DRAFT' annotation.
   Unverified phases: 3, 5

   ◆ Continuing with forced release...
   ```

5. **If all phases verified:**
   - Display: "✓ All phases verified — quality gate passed"
   - Continue to Step 3

**Verification:**
- [ ] Internal releases skip verification gate
- [ ] Client releases check all phase statuses
- [ ] Blocks without --force if phases unverified
- [ ] Continues with warning if --force used
- [ ] Passes if all phases verified

---

## Step 3: Check for Assembled FDS Document

**Objective:** Ensure an assembled FDS document exists before creating a release. Without an assembled document, there's nothing to version.

**Actions:**

1. **Read PROJECT.md to get project name:**
   - Read `.planning/PROJECT.md`
   - Extract project name from metadata section
   - Normalize for filename (replace spaces with hyphens, uppercase)

2. **Look for current version FDS document:**
   - Check for file: `FDS-{PROJECT_NAME}-v{current}.md` in project root
   - Also check for: `FDS-{PROJECT_NAME}-v{current}-DRAFT.md` (previous forced release)

3. **If not found:**
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║  ERROR: No Assembled FDS Document                            ║
   ╚══════════════════════════════════════════════════════════════╝

   No assembled FDS document found for v{current}.

   Expected file: FDS-{PROJECT_NAME}-v{current}.md

   **To fix:**
   1. Run /doc:complete-fds to assemble the FDS document
   2. Verify assembly completed successfully
   3. Re-run /doc:release
   ```
   - Exit

4. **If found, validate file:**
   - Check file size > 0 bytes
   - If zero bytes: display error "FDS document is empty — assembly may have failed"
   - Read first 10 lines to confirm it's a markdown document
   - Display: "✓ Found assembled FDS document: FDS-{PROJECT_NAME}-v{current}.md ({SIZE})"

**Verification:**
- [ ] FDS document filename constructed correctly
- [ ] File existence checked
- [ ] Zero-byte validation performed
- [ ] Blocks release if document missing or invalid

---

## Step 4: Archive Current Version

**Objective:** Preserve complete source documentation at each version for historical tracking and comparison. Archive includes all phase files, ROADMAP, FDS document, and assembly reports.

**Actions:**

1. **Determine archive directory:**
   - Archive path: `.planning/archive/v{next}/`
   - Example: For v1.0 release, archive to `.planning/archive/v1.0/`

2. **Check if archive already exists:**
   ```bash
   if [ -d ".planning/archive/v{next}" ]; then
     echo "ERROR: Archive v{next} already exists"
     exit 1
   fi
   ```
   - This prevents accidental overwrite of previous releases
   - If archive exists, version was already released
   - Display error:
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║  ERROR: Version Already Released                             ║
   ╚══════════════════════════════════════════════════════════════╝

   Archive directory .planning/archive/v{next}/ already exists.
   Version v{next} was already released.

   **Current version is v{next}, not v{current}.**
   Update STATE.md Versions section if out of sync.
   ```

3. **Create archive directory structure:**
   ```bash
   mkdir -p .planning/archive/v{next}
   ```

4. **Archive phase files:**
   ```bash
   cp -r .planning/phases/ .planning/archive/v{next}/phases/
   ```
   - Preserves all PLAN.md, CONTENT.md, SUMMARY.md, VERIFICATION.md files
   - Captures complete project state at this version

5. **Archive ROADMAP:**
   ```bash
   cp .planning/ROADMAP.md .planning/archive/v{next}/ROADMAP.md
   ```

6. **Archive FDS document:**
   ```bash
   cp FDS-{PROJECT_NAME}-v{current}.md .planning/archive/v{next}/
   ```
   - Or copy DRAFT version if that's what exists

7. **Archive assembly reports (if they exist):**
   ```bash
   [ -f .planning/assembly/XREF-REPORT.md ] && cp .planning/assembly/XREF-REPORT.md .planning/archive/v{next}/
   [ -f .planning/assembly/COMPLIANCE.md ] && cp .planning/assembly/COMPLIANCE.md .planning/archive/v{next}/
   [ -f .planning/assembly/ENGINEER-TODO.md ] && cp .planning/assembly/ENGINEER-TODO.md .planning/archive/v{next}/
   ```

8. **Display archive summary:**
   ```
   ✓ Archived to .planning/archive/v{next}/
     - phases/ ({COUNT} files)
     - ROADMAP.md
     - FDS-{PROJECT_NAME}-v{current}.md
     - Assembly reports (if present)
   ```

**Verification:**
- [ ] Archive directory doesn't already exist (prevents overwrite)
- [ ] Archive created at .planning/archive/v{next}/
- [ ] All phase files copied
- [ ] ROADMAP.md copied
- [ ] FDS document copied
- [ ] Assembly reports copied if they exist

---

## Step 5: Generate Revision History Entry

**Objective:** Auto-generate revision history entry from git commits as a draft, flagged for engineer review before client release distribution.

**Actions:**

1. **Find last release tag:**
   ```bash
   LAST_TAG=$(git tag --list "fds-v*" --sort=-version:refname | head -1)
   ```
   - Tags follow pattern: fds-v0.1, fds-v0.2, fds-v1.0, etc.
   - If no tags exist: this is first release, use all history

2. **Extract git log since last release:**
   ```bash
   if [ -z "$LAST_TAG" ]; then
     # First release: all history
     git log --pretty=format:"%ai|%an|%s" --reverse
   else
     # Since last tag
     git log ${LAST_TAG}..HEAD --pretty=format:"%ai|%an|%s" --reverse
   fi
   ```
   - Format: timestamp|author|subject
   - Reverse order: oldest first (chronological)

3. **Group commits by phase/plan:**
   - Parse commit messages for pattern: "feat(XX-YY):", "fix(XX-YY):", etc.
   - Extract phase-plan prefix (e.g., "05-04" from "feat(05-04): create release command")
   - Group commits by phase-plan, preserving chronology within groups

4. **Generate description from commits:**
   - For each phase-plan group:
     - Extract the feature/fix descriptions
     - Summarize in one line: "Phase X Plan Y: {summary of changes}"
   - If commits don't match pattern: include as "Miscellaneous: {commit message}"

5. **Format as revision history table entry:**
   ```
   | v{next} | {DATE} | {AUTHOR} | {DESCRIPTION} |
   ```
   - DATE: Current date in YYYY-MM-DD format
   - AUTHOR: Primary author from git log (most commits) or "Engineering Team"
   - DESCRIPTION: Generated summary from commit grouping

6. **Add engineer review marker for client releases:**
   - If `--type client`:
     ```
     <!-- ENGINEER: Review and edit revision history before distribution -->
     <!-- Auto-generated from git commits. Edit description as needed for client clarity. -->
     ```
   - If `--type internal`: no marker needed (internal audiences understand git-style language)

7. **Include custom notes if provided:**
   - If `--notes` argument provided:
     - Append to auto-generated description
     - Format: "{auto_description}. {custom_notes}"

8. **Store generated revision history:**
   - Save to temporary variable for inclusion in Step 6
   - Display preview:
   ```
   ◆ Generated revision history entry:

   | v{next} | {DATE} | {AUTHOR} | {DESCRIPTION} |

   ⚠ Remember to review revision history in document before client distribution
   ```

**Verification:**
- [ ] Git log extracted since last release tag
- [ ] Commits grouped by phase/plan
- [ ] Description generated from commit messages
- [ ] Revision history table entry formatted
- [ ] Engineer review marker added for client releases
- [ ] Custom notes included if provided

---

## Step 6: Rename/Create Versioned FDS Document

**Objective:** Create new versioned FDS document with updated revision history. For client releases with unverified phases, mark as DRAFT.

**Actions:**

1. **Determine target filename:**
   - **Internal release:** `FDS-{PROJECT_NAME}-v{next}.md`
   - **Client release (verified):** `FDS-{PROJECT_NAME}-v{next}.md`
   - **Client release (forced with --force):** `FDS-{PROJECT_NAME}-v{next}-DRAFT.md`

2. **Copy current FDS document to new version:**
   ```bash
   cp FDS-{PROJECT_NAME}-v{current}.md FDS-{PROJECT_NAME}-v{next}.md
   ```
   - Or to DRAFT filename if forced client release

3. **Read document to locate revision history section:**
   - Read the new FDS document
   - Look for `## Revision History` or `## Revisie Historie` (bilingual support)
   - Find the table start (markdown table with headers)

4. **Insert new revision history entry:**
   - Locate the last row of the revision history table
   - Insert new row at the end:
   ```
   | v{next} | {DATE} | {AUTHOR} | {DESCRIPTION} |
   ```
   - If table doesn't exist yet, create it:
   ```markdown
   ## Revision History

   | Version | Date | Author | Description |
   |---------|------|--------|-------------|
   | v{next} | {DATE} | {AUTHOR} | {DESCRIPTION} |
   ```

5. **For forced client releases, add DRAFT watermark:**
   - If `--force` used for client release:
     - Locate title page section (first heading or front matter)
     - Add immediately after title:
   ```markdown
   # {PROJECT_NAME} - Functional Design Specification

   **⚠ DRAFT VERSION - NOT FULLY VERIFIED**

   This is a forced release with unverified phases.
   See revision history for details.
   ```

6. **Write updated document:**
   - Write the modified FDS document back to disk
   - Keep previous version file unchanged (already archived in Step 4)

7. **Display document summary:**
   ```
   ✓ Created versioned FDS document: FDS-{PROJECT_NAME}-v{next}.md
     - Revision history updated with v{next} entry
     - Previous version preserved: v{current}
   ```
   - Or if DRAFT:
   ```
   ⚠ Created DRAFT FDS document: FDS-{PROJECT_NAME}-v{next}-DRAFT.md
     - DRAFT watermark added to title page
     - Revision history updated with v{next} entry
   ```

**Verification:**
- [ ] Target filename determined correctly (DRAFT suffix if forced client)
- [ ] New document created by copying current version
- [ ] Revision history section located
- [ ] New revision entry inserted
- [ ] DRAFT watermark added if forced client release
- [ ] Document written to disk

---

## Step 7: Update STATE.md

**Objective:** Update STATE.md Versions section (FDS line only), add decision entry, update current focus, and record session continuity.

**Actions:**

1. **Read STATE.md:**
   - Read `.planning/STATE.md`

2. **Update Versions section:**
   - Locate `## Versions` section
   - Find line starting with `- FDS: v`
   - Replace with:
     - Internal: `- FDS: v{next} (internal release, {DATE})`
     - Client: `- FDS: v{next} (client release, {DATE})`
     - Forced client: `- FDS: v{next} (client release DRAFT, {DATE})`
   - **IMPORTANT:** Do NOT modify the SDS line
     - SDS versioning is independent (ASBL-12)
     - SDS is managed by /doc:generate-sds (Phase 7)
   - If Versions section doesn't exist (first release):
     ```markdown
     ## Versions

     - FDS: v{next} (internal release, {DATE})
     - SDS: - (not started)
     ```

3. **Add decision entry:**
   - Locate `## Decisions` section
   - Remove "(Populated during /doc:discuss-phase)" placeholder if present
   - Append new decision:
     - Internal: `- [Phase 05]: FDS v{next} released (internal) - {DATE}`
     - Client: `- [Phase 05]: FDS v{next} released (client) - {DATE}`
     - Forced: `- [Phase 05]: FDS v{next} released (client DRAFT, forced) - {DATE}`

4. **Update Current focus:**
   - Locate `## Project Reference` section
   - Find line starting with `**Current focus:**`
   - Update to:
     - Internal: `**Current focus:** FDS v{next} released (internal). Continue development.`
     - Client: `**Current focus:** FDS v{next} released (client). Ready for distribution.`

5. **Update Session Continuity:**
   - Locate `## Session Continuity` section
   - Update fields:
   ```markdown
   Last session: {DATE}
   Stopped at: FDS v{next} released ({type})
   Resume: Continue development or run /doc:status for next steps
   ```

6. **Update Last updated timestamp:**
   - Bottom of file: `*Last updated: {DATE}*`

7. **Write STATE.md back to disk**

8. **Display STATE.md updates:**
   ```
   ✓ STATE.md updated:
     - Versions: FDS v{next} ({type} release)
     - Decision recorded
     - Current focus updated
     - Session continuity updated
   ```

**Verification:**
- [ ] STATE.md Versions section updated (FDS line only)
- [ ] SDS line unchanged
- [ ] Decision entry added
- [ ] Current focus updated
- [ ] Session continuity updated
- [ ] Last updated timestamp refreshed

---

## Step 8: Git Commit and Tag

**Objective:** Create atomic commit for release and tag the release version for historical tracking.

**Actions:**

1. **Stage files for commit:**
   ```bash
   git add FDS-{PROJECT_NAME}-v{next}.md
   git add .planning/STATE.md
   git add .planning/archive/v{next}/
   ```
   - Or DRAFT filename if forced client release

2. **Create commit:**
   ```bash
   git commit -m "release: FDS v{next} ({type})"
   ```
   - Commit message format:
     - Internal: `release: FDS v0.4 (internal)`
     - Client: `release: FDS v1.0 (client)`
     - Forced: `release: FDS v2.0 (client DRAFT)`

3. **Create git tag:**
   ```bash
   git tag fds-v{next}
   ```
   - Tag naming: fds-v0.1, fds-v0.2, fds-v1.0, etc.
   - Enables git log filtering in future releases (Step 5)

4. **Display commit summary:**
   ```
   ✓ Git commit created: {COMMIT_HASH}
   ✓ Git tag created: fds-v{next}
   ```

5. **Remind engineer NOT to push automatically:**
   - Per GSD convention, engineer pushes explicitly
   - Display:
   ```
   ⚠ Reminder: Changes are committed locally, not pushed to remote
   Run git push && git push --tags to share the release
   ```

**Verification:**
- [ ] FDS document staged
- [ ] STATE.md staged
- [ ] Archive directory staged
- [ ] Commit created with correct message format
- [ ] Git tag created with fds-v{next} pattern
- [ ] No automatic push performed

---

## Step 9: Display Summary

**Objective:** Present comprehensive release summary to engineer with next steps based on release type.

**Actions:**

1. **Display release banner:**
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DOC > FDS v{next} RELEASED ({type})
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

2. **Display version transition:**
   ```
   Previous version: v{current}
   New version:      v{next}
   Release type:     {type}
   ```

3. **Display artifacts:**
   ```
   **Artifacts created:**
   - Document: FDS-{PROJECT_NAME}-v{next}.md ({SIZE})
   - Archive:  .planning/archive/v{next}/ ({FILE_COUNT} files)
   - Git tag:  fds-v{next}
   ```

4. **Display revision history note:**
   - For client releases:
   ```
   ⚠ Revision history was auto-generated from git commits.
   Review the "Revision History" section in the FDS document
   and edit for client clarity before distribution.
   ```
   - For internal releases:
   ```
   ✓ Revision history auto-generated from git commits.
   ```

5. **Display next steps based on release type:**

   **For internal releases:**
   ```
   ───────────────────────────────────────────────────────────────

   ## > Next Up

   **Continue Development**

   Work on the FDS continues. When ready for next version:

   1. Run /doc:complete-fds after making changes
   2. Run /doc:release --type internal for next internal version
   3. Or run /doc:release --type client when ready for client release

   <sub>/clear first -- fresh context window</sub>

   ───────────────────────────────────────────────────────────────

   **Also available:**
   - /doc:status -- View project status and progress
   - /doc:verify-phase -- Verify phases before client release

   ───────────────────────────────────────────────────────────────
   ```

   **For client releases (verified):**
   ```
   ───────────────────────────────────────────────────────────────

   ## > Next Up

   **Client Release Ready**

   1. Review revision history in FDS-{PROJECT_NAME}-v{next}.md
   2. Edit revision history description for client clarity (if needed)
   3. Run: git push && git push --tags
   4. Distribute FDS document to client

   <sub>/clear first -- fresh context window</sub>

   ───────────────────────────────────────────────────────────────

   **Also available:**
   - /doc:generate-sds -- Generate SDS from FDS (Phase 7)
   - /doc:export -- Export to DOCX with corporate styling

   ───────────────────────────────────────────────────────────────
   ```

   **For forced client releases:**
   ```
   ───────────────────────────────────────────────────────────────

   ## > Next Up

   **Client Release DRAFT (Forced)**

   ⚠ This is a DRAFT release with unverified phases.
   Document carries DRAFT watermark.

   1. Review revision history in FDS-{PROJECT_NAME}-v{next}-DRAFT.md
   2. Review DRAFT watermark on title page
   3. Run: git push && git push --tags
   4. Notify client this is a draft version

   **To create verified client release:**
   1. Run /doc:verify-phase for each unverified phase
   2. Address gaps found during verification
   3. Run /doc:release --type client (without --force)

   <sub>/clear first -- fresh context window</sub>

   ───────────────────────────────────────────────────────────────
   ```

**Verification:**
- [ ] Release banner displayed
- [ ] Version transition shown
- [ ] Artifacts listed with details
- [ ] Revision history reminder shown
- [ ] Next steps appropriate for release type
- [ ] Alternative commands suggested

---

## SDS Versioning Note (ASBL-12)

This workflow handles **FDS versioning only**. SDS has independent versioning:

**FDS versioning (this workflow):**
- Managed by /doc:release command
- Version stored in STATE.md: `- FDS: vX.Y`
- Tagged in git: fds-vX.Y

**SDS versioning (separate workflow):**
- Managed by /doc:generate-sds command (Phase 7)
- Version stored in STATE.md: `- SDS: vX.Y (based on FDS vA.B)`
- Tagged in git: sds-vX.Y
- SDS references its source FDS version on frontpage

**STATE.md Versions section example:**
```markdown
## Versions

- FDS: v1.2 (internal release, 2026-02-14)
- SDS: v1.0 (based on FDS v1.0, client release, 2026-01-20)
```

This workflow:
- Updates ONLY the FDS line
- Never touches the SDS line
- Preserves SDS version information unchanged

---

## Error Handling

**Common errors and resolutions:**

1. **"--type must be 'client' or 'internal'"**
   - Fix: Use correct argument format
   - Example: /doc:release --type client

2. **"No assembled FDS exists yet"**
   - Fix: Run /doc:complete-fds first
   - Then: /doc:release --type internal

3. **"Verification Required" (client release blocked)**
   - Fix option A: Verify all phases with /doc:verify-phase
   - Fix option B: Use --force flag (creates DRAFT)

4. **"Archive vX.Y already exists"**
   - Cause: Version already released
   - Fix: Check STATE.md Versions section, may be out of sync
   - Or: Increment version manually if needed

5. **"No git repository"**
   - Fix: Initialize git repository
   - Example: git init && git add . && git commit -m "Initial commit"

6. **"FDS document is empty"**
   - Cause: /doc:complete-fds failed
   - Fix: Re-run /doc:complete-fds and check for errors

---

## Performance Notes

**Expected duration:** 30-60 seconds

**Breakdown:**
- Step 1 (version calc): 2-3 seconds
- Step 2 (verification gate): 5-10 seconds (if client release)
- Step 3 (document check): 1-2 seconds
- Step 4 (archive): 10-20 seconds (depends on file count)
- Step 5 (revision history): 5-10 seconds (depends on commit count)
- Step 6 (document update): 3-5 seconds
- Step 7 (STATE.md update): 2-3 seconds
- Step 8 (git commit/tag): 2-3 seconds
- Step 9 (summary display): 1-2 seconds

**Optimization tips:**
- Archive can be slow for large projects (hundreds of files)
- Git log extraction is fast (< 100ms for typical projects)
- Document updates are in-memory before write (fast)

---

## ASBL Requirements Coverage

This workflow implements all Phase 5 versioning requirements:

- **ASBL-09:** Client release verification gate (Step 2)
- **ASBL-10:** Version scheme enforcement (Step 1)
- **ASBL-11:** Archive creation (Step 4)
- **ASBL-12:** Independent FDS/SDS versioning (Step 7, SDS Note)

</workflow>
