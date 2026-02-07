<ui_patterns>

Visual patterns for user-facing GSD-Docs output. All /doc:* commands @-reference this file.

## Stage Banners

Use for major workflow transitions.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DOC > {STAGE NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Stage names (uppercase):**
- `CLASSIFYING` (project type determination during /doc:new-fds)
- `SCAFFOLDING` (creating .planning/ structure during /doc:new-fds)
- `DISCUSSING PHASE {N}` (gray area identification)
- `PLANNING PHASE {N}` (section plan generation)
- `WRITING WAVE {N}` (parallel content writing)
- `VERIFYING PHASE {N}` (goal-backward verification)
- `PHASE {N} COMPLETE` (phase verified and done)
- `FDS COMPLETE` (all phases assembled into final document)
- `GENERATING SDS` (FDS to SDS transformation)
- `EXPORTING` (DOCX export with corporate styling)

---

## Checkpoint Boxes

User action required. 62-character width.

```
╔══════════════════════════════════════════════════════════════╗
║  CHECKPOINT: {Type}                                          ║
╚══════════════════════════════════════════════════════════════╝

{Content}

──────────────────────────────────────────────────────────────
> {ACTION PROMPT}
──────────────────────────────────────────────────────────────
```

**Types:**
- `CHECKPOINT: Verification Required` --> `> Type "approved" or describe issues`
- `CHECKPOINT: Decision Required` --> `> Select: option-a / option-b`
- `CHECKPOINT: Action Required` --> `> Type "done" when complete`

---

## Status Symbols

```
✓  Complete / Passed / Verified
✗  Failed / Missing / Blocked
◆  In Progress
○  Pending
⚡ Auto-approved
⚠  Warning
```

---

## Progress Display

**Phase/milestone level:**
```
Progress: ████████░░ 80%
```

**Task level:**
```
Tasks: 2/4 complete
```

**Plan level:**
```
Plans: 3/5 complete
```

**Section level (writing):**
```
Sections: 4/6 written
```

---

## Spawning Indicators

```
◆ Spawning writer...

◆ Spawning 3 writers in parallel...
  > 03-01 EM-100 Waterbad
  > 03-02 EM-200 Bovenloopkraan
  > 03-03 EM-300 Vulunit

✓ Writer complete: 03-01-CONTENT.md written (2.3KB)
```

---

## Next Up Block

Always at end of major completions.

```
───────────────────────────────────────────────────────────────

## > Next Up

**{Identifier}: {Name}** -- {one-line description}

`{copy-paste command}`

<sub>`/clear` first -- fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `/doc:alternative-1` -- description
- `/doc:alternative-2` -- description

───────────────────────────────────────────────────────────────
```

---

## Error Box

```
╔══════════════════════════════════════════════════════════════╗
║  ERROR                                                       ║
╚══════════════════════════════════════════════════════════════╝

{Error description}

**To fix:** {Resolution steps}
```

---

## Tables

```
| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1     | ✓      | 3/3   | 100%     |
| 2     | ◆      | 1/4   | 25%      |
| 3     | ○      | 0/2   | 0%       |
```

---

## Verification Result Box

```
═══════════════════════════════════════════════════════════════
RESULT: {PASS / GAPS_FOUND}
═══════════════════════════════════════════════════════════════
```

---

## Anti-Patterns

- Varying box/banner widths
- Mixing banner styles (`===`, `---`, `***`)
- Using the GSD prefix in DOC command banners (namespace separation: DOC commands always use `DOC >` prefix)
- Random emoji -- only use status symbols defined above
- Missing Next Up block after completions
- Skipping `DOC >` prefix in banners

</ui_patterns>
