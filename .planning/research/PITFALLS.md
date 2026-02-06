# Domain Pitfalls

**Domain:** Claude Code documentation generation plugin (FDS/SDS for industrial automation)
**Researched:** 2026-02-06
**Confidence:** HIGH (derived from GSD reference implementation analysis + SPECIFICATION.md + domain research)

---

## Critical Pitfalls

Mistakes that cause rewrites, data loss, or fundamental architecture failure.

---

### Pitfall 1: Context Cross-Contamination Between Sections

**What goes wrong:** A subagent writing section 03-04 (EM-400 Losunit) inadvertently loads or inherits context from section 03-02 (EM-200 Bovenloopkraan). Parameters, interlocks, or operating states from one equipment module bleed into another. The resulting FDS contains factually wrong information that passes superficial review because the content *looks* plausible -- it is real technical content, just from the wrong module.

**Why it happens:**
- The GSD execute-phase orchestrator passes too much context to writer subagents (e.g., loading all CONTENT.md files instead of only the current PLAN.md)
- STATE.md accumulates decisions from previous sections that leak into new section context
- Parallel writers in the same wave share an orchestrator that has read multiple plans
- Template variable substitution fails silently: `{EM_ID}` resolves to a cached value from a previous run

**Consequences:**
- FDS sections describe wrong equipment behavior (safety risk in industrial automation)
- Cross-references point to correct section numbers but contain incorrect interlock descriptions
- Verification pass looks clean because content is substantive (not stubs) -- it is just wrong
- Client review catches errors late, destroying confidence in the entire document

**Warning signs:**
- Two equipment modules share suspiciously similar parameter tables
- Interlock references mention equipment IDs not in the current section
- SUMMARY.md "Dependencies" section lists items not in the current PLAN.md
- Parameter names follow conventions from a different module

**Prevention:**
1. Each writer subagent loads ONLY: PROJECT.md + phase CONTEXT.md + its own PLAN.md + standards references (if enabled). Nothing else.
2. The orchestrator NEVER reads CONTENT.md files from other plans before spawning a writer
3. PLAN.md must contain ALL information the writer needs (extracted from CONTEXT.md during planning). Writers should not need to read CONTEXT.md sections for other plans.
4. Verification explicitly cross-checks: "Does section X reference any equipment IDs that do not belong to section X?"
5. Template rendering must use fresh variable scopes per subagent -- no shared state between parallel writers

**Detection (automated):**
```
For each CONTENT.md in a phase:
  Extract all EM-XXX, IL-XXX, TAG-XXX identifiers
  Compare against PLAN.md expected identifiers
  Flag any identifier not in the plan's scope
```

**Milestone mapping:** Must be addressed in Phase 1 (Framework Basis) and validated in Phase 3 (Write & Verify). This is a foundational architecture constraint.

**GSD lesson learned:** The GSD reference implementation explicitly documents "Context budget: ~15% orchestrator, 100% fresh per subagent" in execute-phase.md. GSD-Docs must enforce this even more strictly because documentation cross-contamination is harder to detect than code cross-contamination (no compiler to catch mismatched types).

---

### Pitfall 2: Infinite Verification-Fix Loops

**What goes wrong:** The verify-phase command finds gaps. Plan-phase --gaps creates fix plans. Execute-phase runs fixes. Verify-phase runs again and finds *new* gaps introduced by the fixes, or finds that the fixes didn't actually resolve the original gaps. The system enters an unbounded cycle.

**Why it happens:**
- Fix plans are too narrow: they address the symptom (missing parameter range) but not the root cause (PLAN.md lacked parameter specifications)
- Fix writers have insufficient context about *why* the gap existed, so they introduce content that creates new inconsistencies
- Verification criteria are too strict relative to the fix scope -- fixing parameter ranges triggers new checks on parameter dependencies
- No termination condition: the system has no concept of "good enough" or maximum retry count

**Consequences:**
- User observes the system spinning: plan-fix-verify-plan-fix-verify without converging
- Token costs escalate rapidly (each cycle consumes full context windows)
- Accumulated fix plans create a messy phase directory (03-01-fix-PLAN.md, 03-01-fix2-PLAN.md, etc.)
- User loses trust in the verification system and starts bypassing it

**Warning signs:**
- Phase has more than 2 fix plan iterations
- VERIFICATION.md gap count is not decreasing between iterations
- Fix plans reference the same sections repeatedly
- New gaps appear in sections that previously passed

**Prevention:**
1. Maximum retry limit: 2 gap-closure cycles per phase. After that, status escalates to `human_needed`
2. Fix plans must include a "Root Cause" field linking back to the original verification gap
3. Re-verification after fixes checks ONLY the gaps that were targeted, not the entire phase (scoped re-verification)
4. VERIFICATION.md tracks gap history: "Gap X: found in cycle 1, fix attempted in cycle 2, status in cycle 3"
5. The `--force` flag on complete-fds exists for a reason: some gaps are acceptable with documented warnings

**Detection:**
- Count fix plan files per phase: >2 iterations = warning
- Compare gap counts across VERIFICATION.md versions: non-decreasing = problem
- Check if fix plans target same sections as previous fixes

**Milestone mapping:** Phase 3 (Write & Verify) must implement the retry limit. Phase 5 (Complete & Export) must handle graceful degradation with `--force`.

**GSD lesson learned:** GSD's execute-phase.md has the gap closure loop but relies on user intervention to break cycles ("offer `/gsd:plan-phase {X} --gaps`"). GSD-Docs should add automatic termination because documentation verification loops are more prone to subjectivity than code verification.

---

### Pitfall 3: Section Numbering Collapse During Document Assembly

**What goes wrong:** The complete-fds command merges all CONTENT.md files into a single document. Section numbers that were correct within each phase (e.g., "3.2.1" for the second equipment module in phase 3) collide or become incorrect in the final assembled document because the assembly logic does not properly renumber sections based on the full document structure.

**Why it happens:**
- Each phase writer assigns section numbers relative to its own phase, not the full FDS
- Dynamic ROADMAP evolution (section 3.5 of SPECIFICATION) changes the phase count mid-project, invalidating earlier section number assumptions
- Cross-references written as "see 5.3" become wrong when phase insertion shifts section 5 to section 7
- CONTENT.md files use hardcoded section numbers instead of symbolic references

**Consequences:**
- Final FDS has duplicate section numbers (two "5.1" sections)
- Cross-references point to wrong sections (every reference after the insertion point is off)
- Table of contents does not match actual section locations
- Client receives a document that looks unprofessional and untrustable

**Warning signs:**
- ROADMAP evolution (section 3.5) was triggered mid-project, changing phase count
- CROSS-REFS.md has entries with section numbers that don't match the current ROADMAP
- Multiple CONTENT.md files start with the same heading level and number

**Prevention:**
1. Use symbolic section references during writing, not hardcoded numbers. Write "see {EM-200-interlocks}" not "see 5.3"
2. Section numbering is a FINAL step in complete-fds, applied during assembly -- never embedded in CONTENT.md
3. CROSS-REFS.md stores references as symbolic IDs (plan-id + section-id), resolved to numbers only at assembly time
4. After ROADMAP evolution, run a cross-reference audit that flags any hardcoded section numbers in existing CONTENT.md files
5. Assembly algorithm: walk phases in ROADMAP order, assign numbers sequentially, then resolve all symbolic references

**Detection:**
```
Scan all CONTENT.md for patterns like:
  "zie $X.Y"  or  "see $X.Y"  where X.Y is a digit pattern
  Flag as WARNING: hardcoded section reference
  Suggest: replace with symbolic reference
```

**Milestone mapping:** Phase 1 (Framework Basis) must establish the symbolic reference convention. Phase 5 (Complete & Export) implements the numbering algorithm. Phase 3 (Write & Verify) should validate that writers produce symbolic references.

**GSD lesson learned:** GSD does not have this problem because code does not have sequential section numbers. This is a documentation-specific pitfall that has no GSD precedent to copy from. The specification (section 9.6) defines the cross-reference format but does not address the numbering-at-assembly-time pattern. This must be designed from scratch.

---

### Pitfall 4: STATE.md Corruption During Parallel Writer Crashes

**What goes wrong:** Two parallel writer subagents are executing in wave 2. Writer A crashes (token limit, network error). Writer B completes successfully and updates STATE.md. When the user resumes, STATE.md shows wave 2 as complete, but plan A's CONTENT.md is partial or missing. The resume logic skips plan A because STATE.md says it is done.

**Why it happens:**
- STATE.md is a shared mutable resource that multiple agents write to
- The specification (section 9.7) defines forward-only recovery, but the detection of "partial" writes relies on content heuristics (length < 200, "[TO BE COMPLETED]" marker, abrupt ending) that may miss sophisticated partial content
- The orchestrator updates STATE.md based on which wave completed, not which individual plans completed
- If the orchestrator itself crashes between spawning agents and collecting results, STATE.md may reflect the start state but not the actual outcome

**Consequences:**
- Lost work: a partially written section is silently accepted as complete
- Final FDS has a section that ends mid-sentence or contains incomplete tables
- Verification may still pass if the partial content is long enough and lacks obvious stub markers
- Data integrity is compromised silently -- the worst kind of failure

**Warning signs:**
- STATE.md shows a plan as done but no SUMMARY.md exists for that plan
- CONTENT.md file size is unusually small compared to its siblings
- CONTENT.md ends without a proper closing section (no final table, no summary paragraph)
- Git log shows no commit for a plan that STATE.md marks as complete

**Prevention:**
1. SUMMARY.md existence is the ONLY indicator of plan completion. Not STATE.md entries, not file existence alone.
2. STATE.md tracks `plans_done` as a list of plan IDs, updated ONLY when SUMMARY.md is confirmed to exist
3. The partial write detection from section 9.7.4 must also check: does SUMMARY.md exist? If CONTENT.md exists but SUMMARY.md does not, the plan is INCOMPLETE regardless of content quality
4. Resume logic: scan for PLAN.md files without matching SUMMARY.md files. This is already the GSD pattern (discover_plans step checks for SUMMARY existence). GSD-Docs must not deviate.
5. STATE.md writes should be atomic: read-modify-write with a temp file, not append-in-place

**Detection:**
```
For each phase directory:
  List all *-PLAN.md files
  List all *-SUMMARY.md files
  If PLAN exists without SUMMARY: flag as INCOMPLETE
  If STATE.md says plan is done but SUMMARY missing: flag as CORRUPTION
```

**Milestone mapping:** Phase 1 (Framework Basis) must implement the SUMMARY-as-completion-proof pattern. Phase 3 (Write & Verify) must test crash recovery scenarios.

**GSD lesson learned:** GSD's discover_plans step already uses SUMMARY.md existence as the completion check. This is a proven pattern. The risk for GSD-Docs is that someone shortcuts this during implementation and uses STATE.md status instead, because it seems simpler. The framework MUST enforce the SUMMARY check.

---

### Pitfall 5: Template Explosion Across 4 Project Types

**What goes wrong:** The framework has 4 project types (A/B/C/D) with different ROADMAP templates, different phase structures, and different section templates. Each type also has optional standards (PackML, ISA-88) and configurable language. The template matrix explodes: 4 types x 2 standards combinations x N languages = dozens of template variations. Maintaining consistency across all combinations becomes impossible.

**Why it happens:**
- Each project type was initially implemented as a separate template file with copy-pasted structure
- Standards integration was added as conditional blocks inside templates, creating nested if-else logic
- Language support was added as parallel template trees (nl/, en/) instead of a localization layer
- Bug fixes are applied to one template but forgotten in others

**Consequences:**
- Type B projects silently skip a verification check that Type A has
- ISA-88 terminology correction works for Type A but not Type C
- Dutch language templates have a feature that English templates lack
- The framework "works" for the first project type tested but breaks on others

**Warning signs:**
- Templates contain copy-pasted blocks with minor variations
- A bug fix requires changes in more than 2 files
- New feature works for one project type but not others
- Template files exceed 200 lines

**Prevention:**
1. Template inheritance: base template with type-specific overrides, not copy-paste
2. Standards as composable modules, not conditional blocks. PackML module adds state machine sections. ISA-88 module adds hierarchy terminology. Modules compose, they don't interleave.
3. Language as a late-binding concern: templates use language-neutral keys, localization resolves at render time
4. Template testing: each command is tested against ALL 4 project types before release. A simple matrix test: `for type in A B C D; do /doc:new-fds --type $type --dry-run; done`
5. Maximum 1 level of template nesting. If a template includes another template that includes another template, the design is too complex.

**Detection:**
- Count lines of duplicated content across template files (>30% duplication = red flag)
- Run each command against all 4 types in test mode
- Check that every conditional block (standards, language) has test coverage

**Milestone mapping:** Phase 1 (Framework Basis) must establish the template architecture. Phase 4 (Standards & Typicals) adds composable modules. Template testing should be part of Phase 7 (Pilot).

**GSD lesson learned:** GSD has one workflow per command with no type variants. GSD-Docs introduces a new dimension (project type) that GSD never had to handle. The temptation to "just copy the template and modify it" is strong but leads to maintenance hell. Invest in template composition early.

---

## Moderate Pitfalls

Mistakes that cause delays, technical debt, or degraded quality.

---

### Pitfall 6: Dynamic ROADMAP Evolution Breaks In-Progress State

**What goes wrong:** After completing System Overview (Phase 2), the system identifies 18 units and proposes expanding the ROADMAP from 5 phases to 9 phases. The user approves. But STATE.md, REQUIREMENTS.md, and any existing PLAN.md files still reference the old phase numbering. Phase 3 plans created before the expansion now conflict with the new Phase 3 definition.

**Why it happens:**
- ROADMAP evolution (specification section 3.5) changes the semantic meaning of phase numbers
- Previously planned phases (3, 4, 5) shift to new numbers (8, 9) but existing artifacts reference old numbers
- Requirements mapped to "Phase 3: Functional Units" are now split across Phases 3-7
- STATE.md progress tracking uses phase numbers as keys

**Prevention:**
1. ROADMAP evolution is ONLY allowed when no plans exist for future phases. If plans already exist, migration is required.
2. When evolution occurs: automatically update REQUIREMENTS.md phase mappings, STATE.md references, and any existing PLAN.md phase numbers
3. Use phase directory names (not numbers) as primary identifiers: "03-intake/" not just "03-/"
4. Commit the old ROADMAP.md before evolution as a reference point
5. Evolution trigger should check: "Are there any artifacts referencing phases that will be renumbered?" If yes, run migration before confirming.

**Warning signs:**
- Phase directory names don't match ROADMAP phase names after evolution
- REQUIREMENTS.md has orphaned phase mappings
- STATE.md references a phase number that no longer exists in ROADMAP.md

**Milestone mapping:** Phase 1 (Framework Basis) must implement evolution-safe phase identification. The evolution trigger itself is Phase 3 territory.

---

### Pitfall 7: CONTEXT.md Over-Loading in Discuss Phase

**What goes wrong:** The discuss-phase command identifies gray areas and asks the user questions. For a phase with 6 equipment modules, this generates 40-60 questions. The resulting CONTEXT.md becomes 3000+ words. When writer subagents load CONTEXT.md, it consumes significant context window, leaving less room for actual writing. Quality of generated content degrades as the context grows.

**Why it happens:**
- The specification (section 3.5) acknowledges this: "Een discuss-phase met 60+ gray area vragen is onbeheersbaar"
- Even with dynamic ROADMAP evolution splitting into smaller phases, individual phases can still accumulate extensive context
- Engineers provide detailed answers (as they should), and every answer is captured verbatim
- CONTEXT.md lacks a priority hierarchy: all decisions are stored at the same level of importance

**Prevention:**
1. CONTEXT.md has a hard limit: 1500 words. If it exceeds this, the discuss-phase command must summarize lower-priority items.
2. Structure CONTEXT.md with priority tiers: "Critical Decisions" (loaded by all writers), "Module-Specific" (loaded only by relevant writer), "Nice-to-Have" (omitted from writer context)
3. Each PLAN.md should embed its relevant CONTEXT.md subset in the "Context" section, pre-extracted during planning. Writers load the PLAN.md context section, not the full CONTEXT.md.
4. Dynamic ROADMAP evolution (3-5 units per phase) is the primary mitigation: smaller phases = smaller CONTEXT.md

**Warning signs:**
- CONTEXT.md exceeds 2000 words
- Writer agents produce shorter/lower-quality content for phases with larger CONTEXT.md
- Users report the discuss-phase taking too long (>30 minutes for one phase)

**Milestone mapping:** Phase 2 (Discuss & Plan) must implement the CONTEXT.md size constraint. The PLAN.md context extraction happens in the planning step.

---

### Pitfall 8: Standards Terminology Drift

**What goes wrong:** PackML defines specific state names (IDLE, STARTING, EXECUTE, COMPLETING, etc.) and ISA-88 defines specific hierarchy terminology (Unit, Equipment Module, Control Module). Over the course of a large document, writers subtly drift from these standards: using "Running" instead of "EXECUTE", "device" instead of "Equipment Module", "mode" inconsistently.

**Why it happens:**
- Standards reference files are loaded into context but compete with the model's training data, which contains many non-standard automation documents
- Context window pressure causes later sections to lose standards context (the "lost in the middle" phenomenon documented by Chroma's Context Rot research)
- Different writer subagents have slightly different context window states, leading to inconsistent terminology across sections
- User answers in discuss-phase use colloquial terms ("de motor draait" / "the motor runs") which writers may echo instead of standardizing

**Prevention:**
1. Standards terminology is enforced by a post-processing step, not just context loading. After writing, a terminology check scans for non-standard terms.
2. PLAN.md should include a "Standards Reminder" section with the exact terms to use for this section (not the entire standard, just the relevant subset)
3. Verification explicitly checks PackML state names and ISA-88 terminology against a reference list
4. Templates embed standards terminology directly: the section-equipment-module.md template uses "Operating States" with PackML state names pre-filled, not free-text

**Detection:**
```
Scan CONTENT.md for:
  PackML: grep for non-standard state names (Running, Stopped, Waiting vs EXECUTE, STOPPED, IDLE)
  ISA-88: grep for non-standard hierarchy terms (device, subsystem, component vs Unit, EM, CM)
  Flag each occurrence with line number and suggested correction
```

**Warning signs:**
- Different CONTENT.md files use different terms for the same concept
- verify-phase reports ISA-88 or PackML gaps that are purely terminology issues
- User review feedback consistently notes "this doesn't match our standard"

**Milestone mapping:** Phase 4 (Standards & Typicals) must implement terminology enforcement. Phase 3 (Write & Verify) adds the terminology check to verification.

---

### Pitfall 9: SUMMARY.md Quality Degradation Enables Hidden Failures

**What goes wrong:** SUMMARY.md files are supposed to be "compact summaries for AI agents" (specification section 4.4) enabling other agents to understand section content without loading full CONTENT.md. But writers produce superficial summaries that omit critical details: dependencies, cross-references, and key decisions. Downstream agents (verifiers, assemblers) make incorrect decisions because they trust SUMMARY.md claims.

**Why it happens:**
- Summary generation happens at the END of writing, when context is fullest and the model is most likely to produce abbreviated output
- The specification mandates "max 150 words" which is aggressive for complex equipment modules
- Writers treat SUMMARY.md as a completion formality, not as a critical handoff document
- No validation checks whether SUMMARY.md actually reflects CONTENT.md content

**Prevention:**
1. SUMMARY.md has a required structure (enforced by template): Feiten, Key Decisions, Dependencies, Cross-refs. All sections mandatory.
2. Verification checks SUMMARY.md against CONTENT.md: are the claimed facts consistent?
3. Cross-reference entries in SUMMARY.md are validated: if SUMMARY says "interlock with EM-100", does CONTENT.md actually describe that interlock?
4. Consider increasing the word limit to 250 words for equipment module summaries -- 150 words is insufficient for complex modules

**Warning signs:**
- SUMMARY.md is under 50 words (too superficial)
- Dependencies section is empty for a section that clearly depends on other equipment
- Cross-refs section omits references that exist in CONTENT.md
- Verifier or assembler makes incorrect decisions based on SUMMARY.md data

**Milestone mapping:** Phase 3 (Write & Verify) must implement SUMMARY validation. Template design happens in Phase 1.

---

### Pitfall 10: Export Pipeline Fragility (Mermaid + Pandoc)

**What goes wrong:** The export pipeline (Markdown -> Mermaid rendering -> Pandoc -> DOCX) has multiple failure points. Complex Mermaid diagrams fail to render. Pandoc does not correctly format all table styles. The huisstijl.docx template produces different results across Pandoc versions. Diagrams render at wrong resolution for print.

**Why it happens:**
- Mermaid has limits on diagram complexity (specification section 8.2.3: >15 nodes, >10 states, >4 participants)
- Pandoc markdown interpretation differs from GitHub-flavored markdown in subtle ways
- The huisstijl.docx template uses Word features that Pandoc does not fully support
- Export is tested last and gets the least attention during development

**Prevention:**
1. ENGINEER-TODO.md pattern (specification section 8.2.3) is correct: detect complexity limits and flag for manual diagram creation instead of silent failure
2. Pandoc version should be pinned in project dependencies, not "whatever is installed"
3. Export testing should use a standard reference document with all element types (tables, diagrams, cross-references, appendices)
4. Export should produce TWO outputs: the rendered DOCX and a validation report listing any rendering issues
5. Consider maintaining a Mermaid complexity budget per diagram: warn during writing, not during export

**Warning signs:**
- Mermaid CLI errors during export (usually visible in console but not in output)
- DOCX formatting looks different from expected (missing headers, wrong fonts, broken tables)
- Diagram images are blurry or misaligned in final document
- Export works on developer machine but fails in CI or on client machine

**Milestone mapping:** Phase 5 (Complete & Export) implements the pipeline. Phase 7 (Pilot) validates with real documents.

---

## Minor Pitfalls

Mistakes that cause annoyance but are fixable without major rework.

---

### Pitfall 11: Git Commit Noise from Documentation Workflows

**What goes wrong:** The GSD pattern commits after every task. For documentation generation, this creates many small commits: "docs(03-01): write EM-100 beschrijving", "docs(03-01): write EM-100 parameters", "docs(03-01): write EM-100 interlocks". The git history becomes noisy and hard to navigate for documentation projects where individual section changes are less meaningful than phase-level changes.

**Prevention:**
1. GSD-Docs should commit per-plan (after all tasks in a plan), not per-task. Documentation writing tasks within a single plan are not independently useful.
2. The specification already hints at this: "Git commit per plan (optioneel)" in section 4.4. Make per-plan the default.
3. Phase-level squash option: `complete-fds` could offer to squash all phase commits into single phase commits for clean history.

**Milestone mapping:** Phase 1 decision: commit granularity policy.

---

### Pitfall 12: Language Mixing in Bilingual Projects

**What goes wrong:** PROJECT.md and CONTEXT.md are in the user's language (Dutch in most cases). PLAN.md and workflow commands are in English (following GSD convention). Standards references are in English. The FDS output should be in the configured language. Writers sometimes produce content in the wrong language or mix languages within a section.

**Prevention:**
1. PLAN.md explicitly states the output language: "Output language: nl" or "Output language: en"
2. Standards terminology has a language mapping: "EXECUTE" (standard) -> "EXECUTE" (output, terms are not translated)
3. Workflow metadata (PLAN.md frontmatter, SUMMARY.md structure) is always English. Only CONTENT.md body text follows the configured language.
4. Verification includes a language check: content should be predominantly in the configured language

**Milestone mapping:** Phase 1 should establish the language convention. Phase 3 adds language verification.

---

### Pitfall 13: Typicals Catalog Staleness

**What goes wrong:** The CATALOG.json used for SDS generation contains typical function blocks. Over time, typicals are updated (new versions, parameters change) but CATALOG.json is not kept in sync. The SDS references outdated typical versions, or worse, typical interfaces have changed but the SDS still maps to old interface definitions.

**Prevention:**
1. CATALOG.json includes version numbers per typical (already in specification section 7.1)
2. SDS generation should warn when typical version is older than a configurable threshold
3. CATALOG.json should have a "last_verified" date per typical
4. The "NEW TYPICAL NEEDED" flag (specification section 7.2) should also trigger when a typical exists but its version is too old

**Milestone mapping:** Phase 4 (Standards & Typicals) implements the catalog. Phase 7 (Pilot) validates with real typicals.

---

### Pitfall 14: Orphan Content After Phase Restructuring

**What goes wrong:** After dynamic ROADMAP evolution, some CONTENT.md files may become orphaned: they were written for the old phase structure but are no longer referenced by any plan in the new structure. These files waste disk space and confuse the assembly process.

**Prevention:**
1. ROADMAP evolution should produce a migration report: "Moved: plan X -> phase Y. Orphaned: [list]"
2. Assembly (complete-fds) scans for CONTENT.md files not referenced by any current PLAN.md
3. Orphan detection is part of the verify-phase step, not just complete-fds

**Milestone mapping:** Phase 5 (Complete & Export) implements orphan detection.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Severity | Mitigation |
|-------------|---------------|----------|------------|
| Phase 1: Framework Basis | Pitfall 5 (Template explosion) | Critical | Invest in template composition architecture before writing first template |
| Phase 1: Framework Basis | Pitfall 4 (STATE.md corruption) | Critical | SUMMARY.md = completion proof from day one |
| Phase 2: Discuss & Plan | Pitfall 7 (CONTEXT.md overload) | Moderate | Hard word limit + priority tiers |
| Phase 2: Discuss & Plan | Pitfall 6 (ROADMAP evolution breaks state) | Moderate | Phase identifiers, not just numbers |
| Phase 3: Write & Verify | Pitfall 1 (Context contamination) | Critical | Fresh context per writer, strict context loading rules |
| Phase 3: Write & Verify | Pitfall 2 (Infinite verification loops) | Critical | Max 2 retry cycles + scoped re-verification |
| Phase 3: Write & Verify | Pitfall 8 (Standards drift) | Moderate | Terminology enforcement post-processing |
| Phase 4: Standards & Typicals | Pitfall 8 (Standards drift) | Moderate | Composable modules, not conditional blocks |
| Phase 4: Standards & Typicals | Pitfall 13 (Catalog staleness) | Minor | Version tracking + freshness warnings |
| Phase 5: Complete & Export | Pitfall 3 (Section numbering collapse) | Critical | Symbolic references, numbering at assembly only |
| Phase 5: Complete & Export | Pitfall 10 (Export fragility) | Moderate | Pinned dependencies + reference document testing |
| Phase 6: Kennisoverdracht | Pitfall 9 (SUMMARY quality) | Moderate | Mandatory structure + validation |
| Phase 7: Pilot | Pitfall 5 (Template explosion) | Critical | Test ALL 4 project types, not just Type A |

---

## Cross-Cutting Concerns

These pitfalls span multiple phases and require architectural decisions early:

### Concern A: Context Budget Discipline

Every command in GSD-Docs must have a documented context budget:
- What files does the orchestrator load? (should be <15% of 200K)
- What files does each subagent load? (list explicitly)
- What files are explicitly NOT loaded? (document the exclusions)

Without this discipline, context contamination (Pitfall 1) and context overload (Pitfall 7) are inevitable. Research shows context quality degrades with length -- Chroma's 2025 study found "models do not use their context uniformly; performance grows increasingly unreliable as input length grows."

### Concern B: Symbolic Over Literal References

Every reference between sections must be symbolic until the final assembly step:
- Write "see {EM-200-interlocks}" not "see 5.3"
- Store cross-refs as plan-ID + section-ID not section numbers
- Resolve to numbers only in complete-fds

This prevents Pitfall 3 (section numbering collapse) and makes Pitfall 6 (ROADMAP evolution) less dangerous.

### Concern C: Completion Proof Hierarchy

The system needs an explicit hierarchy of "what proves something is done":
1. PLAN.md exists -> planning happened
2. CONTENT.md exists + SUMMARY.md exists -> writing completed
3. VERIFICATION.md exists with status "passed" -> phase verified
4. REVIEW.md exists (optional) -> client reviewed

STATE.md reflects this hierarchy but is never the primary source of truth. Artifacts on disk are the source of truth. This prevents Pitfall 4 (STATE.md corruption from silently hiding incomplete work).

---

## Sources

**Primary (HIGH confidence -- direct analysis):**
- GSD reference implementation: `~/.claude/get-shit-done/workflows/` (all workflow files)
- GSD-Docs SPECIFICATION.md v2.7.0 (sections 3.5, 4.4, 9.6, 9.7)
- GSD execute-phase.md context budget documentation
- GSD verification-patterns.md stub detection patterns

**Secondary (MEDIUM confidence -- web research):**
- [Multi-Agent LLM System Failures (arXiv 2025)](https://arxiv.org/html/2503.13657v1) -- inter-agent misalignment patterns
- [Context Rot research by Chroma (2025)](https://tilburg.ai/2025/03/context-window-management/) -- performance degradation with input length
- [Context Window Management Strategies](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/) -- pruning and offloading techniques
- [Cross-Document Referencing Problems](https://www.yomu.ai/blog/5-common-problems-in-cross-document-referencing) -- broken links and version control
- [FDS for Industrial Automation (RealPars)](https://www.realpars.com/blog/fds) -- FDS/SDS scope boundary issues
- [Claude Code Plugin Architecture](https://code.claude.com/docs/en/plugins) -- official plugin documentation
- [Multi-Agent Orchestration (Towards Data Science)](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/) -- coordination overhead vs task complexity tradeoffs
