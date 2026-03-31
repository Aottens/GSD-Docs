# Pitfalls Research

**Domain:** Docs Engine Rearchitecture — Flexible FDS Structure, LLM Provider Abstraction, Engine Visibility
**Researched:** 2026-03-31
**Confidence:** HIGH

---

## PILLAR 1: Flexible FDS Structure

---

### Pitfall 1: Destroying the EM-First Domain Knowledge Encoded in 194 Files

**What goes wrong:**
The new "system-first discovery" approach requires changing how templates and workflows trigger their EM-centric sections. Developers read this as "replace the equipment module structure" and refactor section templates to be decomposition-neutral. In doing so, they strip ISA-88 terminology, PackML state names, and EM-specific subsections (interlocks, I/O table, operating states) from the templates. The result: templates that look flexible but have lost the interlock logic, signal-range patterns, and fail-safe state definitions that took years to accumulate.

**Why it happens:**
"System-first" sounds like an architectural inversion. Developers conflate the discovery order (what gets asked first) with the structure of what gets written. The EM section template is assumed to be ISA-88-specific when it is actually standard-agnostic industrial domain knowledge. ISA-88 is opt-in; the template content (interlocks, I/O, states) is always needed.

**How to avoid:**
Treat EM sections as a composable section type — not an ISA-88 artifact. The flexible structure change is in the ROADMAP scaffolding logic (what phases exist and in what order) and the discovery conversation (what the engineer is asked), NOT in the section content templates. Audit: every `{PLACEHOLDER}` in `section-equipment-module.md` maps to actual hardware. Do not remove any of these. Add section types (process-flow unit, functional block, loop) alongside the existing EM type.

**Warning signs:**
- Section template PRs that remove subsections from `section-equipment-module.md`
- Template headers losing `standards: [packml, isa88]` frontmatter
- `EQUIPMENT-HIERARCHY.md` or `STATE-MODEL.md` references being removed from context-loading rules
- New section types created as blank-slate replacements rather than additions

**Phase to address:**
Flexible Structure foundation phase. Define section type catalogue (EM, functional-block, process-flow-unit, loop) before any template changes. Lock `section-equipment-module.md` as read-only for this milestone.

---

### Pitfall 2: Breaking `doc:write-phase` Wave Assignments When ROADMAP Structure Changes

**What goes wrong:**
Wave-based parallelism (`write-phase.md`) reads ROADMAP.md to find phase entries and then resolves `PLAN.md` files for wave-dependency graphs. If the new flexible ROADMAP templates use different heading formats or phase naming conventions, `write-phase.md` fails silently — sections get written in the wrong order or sequentially instead of in parallel. Engineers don't notice until a Type A project with 8 EMs runs 40% slower.

**Why it happens:**
The write-phase workflow uses grep-based ROADMAP parsing (`grep -A 5 "^## Phase ${PHASE}:"`). Any new ROADMAP template that uses a different phase heading format (`## Phase 2 — System Discovery` instead of `## Phase 2: System Discovery`) silently breaks the dependency resolver.

**How to avoid:**
Define a single canonical ROADMAP heading format in the template authoring guide before writing any new ROADMAP templates. Add an explicit format-validation step to `new-fds.md`: after scaffolding a ROADMAP, parse all phase headings and verify they match the expected pattern before writing the file to disk. Do not change the parsing pattern in `write-phase.md` — change the templates to fit it.

**Warning signs:**
- New ROADMAP templates using different heading punctuation than existing Type A/B/C/D templates
- `write-phase.md` tests passing on Type A but not on a new "system-first" ROADMAP
- Sections written without SUMMARY.md files (indicates silent failure in wave orchestration)

**Phase to address:**
ROADMAP template authoring phase. Add ROADMAP schema validation to `new-fds.md` as a post-scaffolding check.

---

### Pitfall 3: Dynamic Structure Discovery Creating an Undetermined ROADMAP at Project Start

**What goes wrong:**
The v1.0 system commits a complete ROADMAP at `/doc:new-fds` time. The new system-first approach discovers structure during Phase 1-2 conversations. Developers implement this as: "don't write ROADMAP.md until Phase 2 completes." This breaks every downstream command that reads ROADMAP.md at startup (`discuss-phase`, `plan-phase`, `verify-phase` all assume ROADMAP.md exists and is complete).

**Why it happens:**
"Dynamic structure" sounds like a deferred commitment. But the existing commands are built on the forward-only pattern: ROADMAP is the contract between phases. Making it dynamic in discovery doesn't mean it should be absent.

**How to avoid:**
Write a provisional ROADMAP at `/doc:new-fds` time with placeholder phase entries. Use the existing `expand-roadmap` mechanism (already exists for >5 units discovered) as the contract for how the ROADMAP evolves — it emits a user-confirmed ROADMAP update, not a partial omission. The `expand-roadmap.md` workflow is the correct pattern to follow for dynamic structure.

**Warning signs:**
- `new-fds.md` changes that skip ROADMAP.md generation until "after discovery"
- `discuss-phase.md` failing with "ROADMAP.md not found"
- Engineers reporting that `/doc:status` shows 0 phases after project creation

**Phase to address:**
Flexible structure design phase. The ROADMAP format spec must define how provisional entries are represented before any command changes.

---

### Pitfall 4: Mixed Decomposition Projects Losing ISA-88 Compliance Selectively

**What goes wrong:**
A project uses functional decomposition for high-level phases but drops to EM-level for a sub-system that requires PackML compliance. The system generates a Phase 3 (Functional Units) and a Phase 4 (Equipment Modules for Filling Station). The `check-standards.md` command checks ISA-88 compliance per section but doesn't know that Phase 3 sections are intentionally not EM-structured. It either flags false positives (non-EM sections fail ISA-88 check) or the developer disables standards checking for the whole project to avoid the noise.

**Why it happens:**
Standards compliance is currently project-scoped (on/off in PROJECT.md). A hybrid decomposition project needs section-scoped standards applicability. The current design has no way to mark "this section is a functional block, ISA-88 does not apply here."

**How to avoid:**
Add `standards_applicability` to section PLAN.md frontmatter: `isa88: false` for functional-block sections. Update `check-standards.md` to read this flag before applying ISA-88 checks. This is a small extension, not a redesign — the opt-in principle is preserved.

**Warning signs:**
- `check-standards.md` generating compliance warnings on functional-block sections
- Engineers disabling `standards.isa88.enabled` for projects that need ISA-88 on some sections
- VERIFICATION.md files full of ignored ISA-88 warnings

**Phase to address:**
Standards integration phase within flexible structure work. Document this as a known extension point.

---

## PILLAR 2: LLM Provider Abstraction

---

### Pitfall 5: Lowest-Common-Denominator Prompts That Work Everywhere But Poorly

**What goes wrong:**
Developers abstract the LLM provider and then "normalize" prompts to work across Claude, GPT-4, and local models. They remove Claude-specific instruction patterns (role headers in `<role>` tags, `<context>` blocks, structured output guidance). They shorten prompts to fit GPT's tighter context window. They remove multi-step reasoning instructions because "the local model can't follow them." The resulting prompts produce technically valid FDS content that lacks the engineering precision and interlock completeness the domain requires. An EM section that previously had 12 interlocks now generates 4.

**Why it happens:**
Prompt portability does not exist — this is confirmed industry consensus as of 2025. If you change models, you must re-evaluate and re-tune all prompts. The temptation to normalize prompts for portability is a false economy: you pay in output quality, which in an industrial safety document context is not acceptable.

**How to avoid:**
Implement provider-specific prompt profiles. The abstraction layer routes to the correct provider; each provider has its own prompt variant for each workflow step. The domain knowledge (what an EM section must contain) is shared. The instruction style (how to address each model) is provider-specific. Claude prompts keep their XML structure and multi-step reasoning. GPT prompts use its system/user message conventions. Local model prompts use simpler instruction patterns with more explicit output examples.

Use a prompt registry: `prompts/write-em-section/{claude,gpt,local}.md`. The provider abstraction selects the correct variant at runtime.

**Warning signs:**
- Prompt commits that "simplify" or "generalize" existing workflows
- EM sections generated via GPT missing interlock tables
- Verification pass rates dropping after provider switch
- Engineers reporting "the output looks thinner" on non-Claude providers

**Phase to address:**
LLM abstraction design phase (before any provider integration). The prompt registry pattern must be defined before writing provider connectors.

---

### Pitfall 6: Context Window Differences Silently Truncating SPECIFICATION.md Context

**What goes wrong:**
Claude (200K tokens) handles the full SPECIFICATION.md (48,700 lines ≈ ~130K tokens) as context without issue. GPT-4o (128K tokens) clips the tail of the document silently. Local models (Llama 3.1 8B: 8K-32K effective context) cannot load even a single phase's context without truncation. The system appears to work — API calls succeed — but the model is generating content from a truncated context. Engineers only notice when sections reference concepts from the beginning of the SPECIFICATION but miss critical details from sections that were cut off.

**Why it happens:**
Context window limits are not enforced at the application layer. The prompt builder assembles context and sends it. The LLM silently truncates. No error is raised.

**How to avoid:**
Add context budget enforcement to the prompt builder. Each provider registers its `max_context_tokens`. The prompt builder calculates token estimates before sending, and if context exceeds budget: (1) trigger selective context loading (only relevant sections from SPECIFICATION), (2) log a warning, (3) do NOT truncate silently. For local models, selective context loading is mandatory by default — load only the relevant section template, standards references, and project-specific context. Do not attempt to load the full SPECIFICATION.

Provide per-provider context budget configuration in `PROJECT.md`:
```yaml
llm_provider: local
llm_context_budget: 8000  # tokens, conservative for 8B models
```

**Warning signs:**
- Provider switching without context budget configuration
- Local model prompt builder sending the same payload as Claude provider
- Engineers switching to local model and seeing "generic" output that doesn't reference their project specifics
- Context loading rules in `write-phase.md` not being provider-aware

**Phase to address:**
LLM abstraction design phase. Context budget enforcement is a non-negotiable guard before any local model support.

---

### Pitfall 7: Local Model Quality Gate Absent — IP-Sensitive Projects Getting Degraded Output

**What goes wrong:**
The primary stated reason for local LLM support is IP-sensitive industrial content. Engineers working on confidential projects switch to local models. Local models (even quantized DeepSeek R1 or Llama 3.1 70B) produce structurally valid FDS output, but domain precision degrades: vague interlock conditions instead of specific sensor tag references, generic PackML state descriptions instead of process-specific transitions. The engineer, who is an industrial automation specialist not a prompt engineer, doesn't know if this degradation is acceptable for their document. They either ship a low-quality document or spend days manually correcting it.

**Why it happens:**
Local model quality is genuinely lower than Claude for technical domain content generation. There is no mechanism to warn the engineer about this tradeoff before they commit to local mode for a project.

**How to avoid:**
Add a quality disclosure to the provider selection step in `new-fds.md`. When local provider is selected, display a factual capability matrix:
- Context window available
- Known quality characteristics vs. Claude for technical documentation
- Recommendation: use local for draft iteration, Claude for final verification

Additionally, add an output quality check to `verify-phase.md` that counts quantifiable completeness markers: interlocks defined (count), parameters with ranges (count), I/O points with tag IDs (count). A local model generating 3 interlocks where Claude generates 12 should trigger a completeness warning, not a silent pass.

**Warning signs:**
- Local provider selected without any quality acknowledgment dialog
- `verify-phase.md` applying the same pass criteria regardless of provider
- EM sections generated locally with fewer than expected interlocks
- Engineers asking "why is the output shorter?" after provider switch

**Phase to address:**
LLM abstraction + verification integration phase. The quality gate must be built alongside the provider, not retrofitted later.

---

### Pitfall 8: Provider Abstraction Over-Engineering — Building a Framework Instead of a Connector

**What goes wrong:**
Developers implement a full LLM orchestration framework with retry logic, streaming, tool calling abstractions, and plugin architecture. This replicates what LangChain/LiteLLM already provide, takes 3x longer to build, and introduces its own bugs. The system reaches v3.0 without a working local model because the abstraction layer is still being designed.

**Why it happens:**
The scope feels open-ended: "support Claude, GPT, and local models." Developers see this as an opportunity to build a proper framework. The existing system has no abstraction layer at all, so starting from scratch with a clean design feels right.

**How to avoid:**
Build the thinnest abstraction that solves the actual use case. The use case is: swap the provider for a `/doc:write-phase` call. This requires:
1. A provider config in `PROJECT.md` (`llm_provider: claude|gpt|local`)
2. A provider factory that returns a configured client
3. Per-provider prompt variant selection (from Pitfall 5)
4. Context budget enforcement (from Pitfall 6)

That is four pieces, not a framework. Reject any abstraction work that isn't one of these four. Use liteLLM or a direct SDK for the actual API calls — do not write HTTP clients.

**Warning signs:**
- Abstraction layer designs with plugin registries, middleware chains, or "provider capabilities negotiation"
- More than one new Python module per provider
- Any design document that uses the word "framework"
- Sprint review showing abstraction work but no working provider swap yet

**Phase to address:**
LLM abstraction design phase. Timebox the design to one day. If the design takes longer, it's too complex.

---

## PILLAR 3: Docs Engine Visibility

---

### Pitfall 9: Building a Template Viewer When Git Already Provides One

**What goes wrong:**
Engineers want to see what the docs engine does — which templates are being used, what's in the prompts, what changed since last month. Developers build a custom web-based template browser with syntax highlighting, diff views, and change history. This takes 6 weeks. Engineers use it twice and then go back to looking at the files directly. The 194 Markdown files are already in git with full history. `git log --oneline gsd-docs-industrial/templates/` already shows every change.

**Why it happens:**
"Visibility layer" sounds like a UI feature. The requirement (engineers can inspect templates/prompts) doesn't specify that a custom UI is needed. Developers default to building what they know: a React component.

**How to avoid:**
Define "visibility" by asking what specific action the engineer cannot perform today that they need to perform. If the answer is "see what template will be used for my project," that is a `doc:status` enhancement (show template paths resolved for this project type). If the answer is "see what changed in the engine last week," that is a structured git log command, not a UI. Build the minimum that closes the gap: a `doc:engine-status` command that prints resolved template paths, provider config, and standards loaded for the current project. That is a 2-hour task, not a 6-week feature.

**Warning signs:**
- Sprint items for "template viewer UI" without a user story describing what the engineer cannot do today
- React components being added to the frontend for template browsing
- New backend endpoints for reading gsd-docs-industrial/ file contents

**Phase to address:**
Visibility scoping phase (must precede any implementation). Requirements gathering: what specific information gap does each user story address?

---

### Pitfall 10: Engine Visibility Exposing Editable Templates — Engineers Diverging from SSOT

**What goes wrong:**
The visibility layer allows engineers to see templates and prompts. Someone adds an "edit" button "just to fix a typo." An engineer modifies `section-equipment-module.md` for their project. Now their local template diverges from the shared SSOT. Future updates to the template don't reach their project. When two engineers edit the same template for different projects, merge conflicts occur. The 194-file SSOT becomes 194 × N files.

**Why it happens:**
Visibility and editability look like a natural pair. Once engineers can see a template, the instinct to fix it in place is strong. The system doesn't distinguish between "view" and "modify."

**How to avoid:**
Visibility is strictly read-only for engine templates. Per-project overrides are allowed only via an explicit override mechanism (a `templates/overrides/` directory in the project folder with a documented escape hatch). The SSOT in `gsd-docs-industrial/` is never modified through the GUI. If an engineer wants to change a template, the correct path is: file an issue, update the SSOT in git, deploy the update.

Make this explicit in the UI: templates shown in the viewer have a header "Read-only — part of GSD-Docs engine v0.1.0. Changes require a framework update."

**Warning signs:**
- Any "edit" affordance (button, inline editor) in the visibility layer
- Template files showing up in per-project git diffs
- Engineers asking "how do I customize the template for this project?"

**Phase to address:**
Visibility design phase. The read-only constraint must be in the spec before implementation starts.

---

### Pitfall 11: Visibility Scope Creep — Adding "Manage Prompts" to a Read-Only Viewer

**What goes wrong:**
The visibility layer starts as a read-only inspector. After shipping, engineers ask for the ability to annotate prompts ("this section always needs more interlocks"), tune parameters ("set temperature to 0.2 for this project"), or override sections ("skip the manual controls subsection for this EM"). Each request is reasonable individually. Collectively they transform the visibility layer into a prompt management system that duplicates functionality that should live in `PROJECT.md` and PLAN.md configuration.

**Why it happens:**
Engineers have legitimate customization needs. The visibility layer is the obvious place to expose controls because it's where they see what the engine does. The "one more feature" requests feel like small additions.

**How to avoid:**
Define the boundary at design time: the visibility layer answers "what is the engine doing?" not "how do I change what the engine does." Project-level customization already has a home (PROJECT.md standards config, PLAN.md optional subsection flags). Any customization request should be routed to those mechanisms, not the visibility layer. Document this boundary explicitly in the milestone spec.

**Warning signs:**
- Visibility layer backlog growing with "configure" or "manage" stories
- New PROJECT.md fields being added through the visibility UI
- Engineers using the visibility layer to change settings mid-project

**Phase to address:**
Visibility design phase. Write the boundary statement in the phase spec before any implementation.

---

## CROSS-PILLAR INTEGRATION PITFALLS

---

### Pitfall 12: Flexible Structure + Provider Abstraction Combination Breaking Context Isolation

**What goes wrong:**
Flexible FDS structure means section types vary per project. The new section types (functional-block, process-flow-unit) need different prompt variants than EM sections. The LLM provider abstraction adds another dimension: provider-specific prompt variants. The cross-product (section-type × provider) creates a prompt registry with many variants. Developers short-circuit this complexity by having all non-EM sections fall back to a generic "describe this functional unit" prompt regardless of provider. The context isolation principle (each writer gets only its scoped context) is maintained, but the prompts become generic.

**Why it happens:**
The cross-product of section types × providers feels combinatorially explosive. Developers simplify by defaulting to the lowest-specificity prompt.

**How to avoid:**
The cross-product is not as large as it appears. For v3.0, the realistic matrix is: 3 section types (EM, functional-block, process-flow-unit) × 3 providers (Claude, GPT, local) = 9 variants. Each variant is a small Markdown file. Map this out before writing any prompts. The domain content of each section type is shared; only the instruction style differs per provider. Use a layered approach: `prompts/{section-type}/base.md` (domain requirements) + `prompts/{section-type}/{provider}.md` (instruction style overlay).

**Warning signs:**
- Prompt files containing both section-type and provider specifics in a single template
- Functional-block sections using EM prompt variants
- "Works for Claude but not local" bugs on new section types

**Phase to address:**
The phase that integrates flexible structure with LLM abstraction (must happen after both pillars are individually designed, before combined testing).

---

### Pitfall 13: Visibility Layer Exposing Provider Config — Engineers Switching Mid-Project

**What goes wrong:**
The visibility layer shows the current provider config (which model is selected, context budget). Engineers see this and decide to switch from Claude to local mid-project to avoid API costs. The first half of the project's sections were generated with Claude prompts and have 12 interlocks per EM. The second half, written with local model prompts, have 4. The final FDS is inconsistent. `verify-phase.md` catches individual section completeness but has no cross-project consistency check.

**Why it happens:**
Visibility implies control. If engineers can see the provider, they expect to change it. Mid-project provider switching is a natural but destructive action.

**How to avoid:**
Provider selection is locked at project creation (`new-fds.md`) and stored in `PROJECT.md`. The visibility layer shows the locked config as read-only for in-progress projects. Mid-project provider changes require an explicit override that triggers a warning: "Changing provider mid-project may create inconsistent output quality. All sections written so far remain unchanged. Proceed?" Only allow this via a deliberate CLI command, not a visibility layer control.

**Warning signs:**
- Provider config shown with edit affordance in visibility layer
- `PROJECT.md` provider field being writable through the GUI
- No provider-lock behavior in `new-fds.md`

**Phase to address:**
The provider lock must be implemented in the flexible structure / new-fds phase, before visibility work begins.

---

### Pitfall 14: All Three Pillars Attempting Independent State Changes to the Same Project Files

**What goes wrong:**
Flexible structure changes ROADMAP.md generation. LLM abstraction adds provider config to PROJECT.md. Visibility layer reads both files and potentially exposes edit interfaces. All three pillars are developed in parallel phases and each makes assumptions about the schema of PROJECT.md and ROADMAP.md. The phases are integrated for the first time in the final milestone and the schemas are incompatible: flexible structure added `decomposition_model` to PROJECT.md; provider abstraction added `llm_provider`; visibility layer expects a specific `engine_version` field that neither added.

**Why it happens:**
Parallel development without a shared schema contract. Each pillar's phase specifies its own PROJECT.md changes.

**How to avoid:**
Define the full v3.0 PROJECT.md schema before any pillar implementation begins. This is a one-page spec listing every new field, its type, its default, and which pillar owns it. This schema is the integration contract. No pillar may add fields outside the pre-approved set without a schema revision.

```yaml
# v3.0 PROJECT.md additions (schema contract)
decomposition_model: system-first | em-first | functional | hybrid   # flexible structure pillar
llm_provider: claude | gpt | local                                    # abstraction pillar
llm_context_budget: 128000                                            # abstraction pillar
engine_version: "0.2.0"                                               # visibility pillar
```

**Warning signs:**
- Each pillar's design doc showing its own PROJECT.md schema additions without cross-referencing
- Integration test failures on PROJECT.md parsing
- `doc:status` showing "unknown field" warnings after pillar combination

**Phase to address:**
Milestone kickoff — write and approve the shared schema contract before any pillar work begins.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Normalize prompts for all providers | Single prompt file per workflow step | Output quality degrades on non-Claude providers; interlock completeness drops silently | Never — provider-specific prompt variants are required |
| Ship visibility layer with edit affordances "disabled by default" | Faster to build one UI with hidden edit mode | Engineers find the hidden edit mode; template SSOT corrupts over time | Never — read-only must be architectural, not UI-level |
| Skip context budget enforcement for MVP | Provider abstraction ships faster | Local model silently truncates context; engineers discover only when output quality is wrong | Never — enforce before any local model is tested |
| Defer provisional ROADMAP to post-discovery | Cleaner discovery flow | All downstream commands break on missing ROADMAP.md | Never — provisional ROADMAP at project creation is load-bearing |
| Use single generic section prompt for all new section types | Avoids prompt × provider matrix | Functional-block and process-flow-unit sections produce generic content without engineering precision | Only acceptable during internal development testing, not for real projects |

---

## Integration Gotchas

Common mistakes when connecting the three pillars.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Flexible structure + write-phase | New section types inherit EM wave-dependency logic | Each section type declares its own dependency rules in PLAN.md frontmatter |
| Provider abstraction + verify-phase | Verification criteria identical regardless of provider | Add provider-aware completeness thresholds in verify-phase config |
| Visibility layer + PROJECT.md | Visibility reads PROJECT.md and offers to update it | PROJECT.md is CLI-owned; visibility layer reads it, never writes it |
| Flexible structure + check-standards | ISA-88 compliance check runs on all sections regardless of section type | check-standards reads section-type from PLAN.md frontmatter before applying checks |
| Provider abstraction + context-loading | All providers receive same context assembly | Context budget enforcement is per-provider; local model gets selective context loading by default |

---

## Performance Traps

Patterns that work at small scale but fail at the scale of this project.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading full SPECIFICATION.md context for local model | API call succeeds but model returns generic output | Enforce context budget before prompt assembly | Every local model call — 48,700 lines far exceeds 8K-32K effective context |
| Template registry scanning all 194 files per request | Slow template resolution on first command run | Cache resolved template paths per project type at `new-fds` time | Noticeable at 30+ file scan; problematic if template directory grows |
| Generating all ROADMAP phases at once for large system-first discovery | Phase list generated but engineer immediately changes it | Use `expand-roadmap` mechanism for confirmed incremental additions | Projects with >10 discovered units where engineer rejects proposed groupings |

---

## Security Mistakes

Domain-specific security issues for this project.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Local model provider leaking prompt context to external endpoint | IP-sensitive FDS content (plant topology, safety interlocks) sent to third-party | Verify local model endpoint is truly local (Ollama/llama.cpp on localhost or intranet); block any provider config pointing to external URL when `ip_sensitive: true` in PROJECT.md |
| Visibility layer proxying template files through FastAPI backend | Backend becomes a file server for gsd-docs-industrial/ directory; path traversal risk | Serve only pre-registered file paths from a template manifest, never serve arbitrary file paths |
| Provider API keys stored in PROJECT.md | Keys committed to project git repo alongside FDS content | Provider credentials belong in environment variables only; PROJECT.md must never accept `api_key` fields |

---

## UX Pitfalls

Common user experience mistakes for this user base (industrial automation engineers, not developers).

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing provider selection without quality context | Engineer selects local model expecting same output quality as Claude, discovers degradation after writing 3 phases | Show capability matrix at provider selection: context window, known quality characteristics, recommendation for each use case |
| Decomposition model selection requiring ISA-88 knowledge to choose | Engineers who don't know ISA-88 cannot choose between "EM-first" and "functional" | Use project description to infer decomposition model (system-first discovery); offer "I'll figure it out from your description" as the default |
| Engine visibility using internal names (template IDs, provider identifiers) | Engineers see "fds/section-equipment-module.md (isa88:true, packml:true)" and don't know what to do with it | Show human-readable descriptions: "Using Equipment Module template — covers states, interlocks, I/O" with a "Learn more" that links to the CLAUDE-CONTEXT.md section |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Flexible structure:** Template section types defined, but no migration test on an actual Type A project to verify all existing ROADMAP phases still resolve correctly
- [ ] **Flexible structure:** ROADMAP generation works for new section types, but `expand-roadmap.md` not updated to handle non-EM phase groupings
- [ ] **LLM abstraction:** Provider swap works for a single `/doc:write-phase` call, but not tested end-to-end through `discuss → plan → write → verify` pipeline
- [ ] **LLM abstraction:** Context budget enforcement implemented, but no test with a local model on a project with standards references loaded (standards refs add ~8K tokens)
- [ ] **LLM abstraction:** Prompt variants exist for Claude and GPT, but local model prompt variants are stubs that default to GPT variants (silent quality degradation)
- [ ] **Visibility layer:** Template viewer shows correct files for a fresh project, but not tested on a mid-project state where some templates are overridden
- [ ] **Visibility layer:** Read-only enforced in UI, but no backend enforcement — direct API call can still overwrite template files
- [ ] **Cross-pillar:** PROJECT.md schema contract defined, but `doc:status` not updated to display v3.0 fields (engineers cannot see provider or decomposition model in status output)
- [ ] **Cross-pillar:** Provider locked at project creation, but `doc:resume` (crash recovery) doesn't re-validate provider lock after resume

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Templates stripped of EM domain knowledge | HIGH | Restore from git history; audit all new section types against original EM template for missing subsections; re-test with full Type A project |
| ROADMAP heading format changed, wave assignments broken | MEDIUM | Fix ROADMAP template format; re-run `new-fds` on a test project; add format validation to CI |
| Provider switched mid-project, inconsistent output quality | MEDIUM | Document which sections used which provider in CONTEXT.md; re-write affected sections with original provider; add provider-lock to PROJECT.md |
| Local model truncating context silently | LOW (if caught early) | Add context budget logging to prompt builder; re-run affected sections with context budget enforced |
| Visibility layer enabling template edits, SSOT corrupted | HIGH | Restore templates from git; audit all projects for local template overrides; disable edit affordance and deploy fix before next project starts |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Destroying EM domain knowledge in templates | Flexible structure foundation — lock section-equipment-module.md as read-only | Run Type A project end-to-end; compare EM section output to v2.0 baseline |
| Breaking write-phase wave assignments | ROADMAP template authoring — define canonical heading format | Run `write-phase` on new ROADMAP types; verify SUMMARY.md files created per section |
| Undetermined ROADMAP at project start | Flexible structure design — provisional ROADMAP spec | `doc:discuss-phase 1` succeeds immediately after `doc:new-fds` for all decomposition models |
| Selective ISA-88 compliance in hybrid projects | Standards integration within flexible structure | `check-standards` on a hybrid project produces no false positives for functional-block sections |
| Lowest-common-denominator prompts | LLM abstraction design — prompt registry pattern | Run EM section generation via each provider; compare interlock counts against Claude baseline |
| Context window truncation | LLM abstraction design — context budget enforcement | Test local model call with standards references loaded; verify warning triggered when budget exceeded |
| IP-sensitive projects using local model without quality gate | LLM abstraction + verification integration | Verify `new-fds` provider selection shows quality matrix; verify `verify-phase` completeness thresholds are provider-aware |
| Provider abstraction over-engineering | LLM abstraction design — one-day timebox | Design doc must fit one page; implementation ≤ 2 new Python files per provider |
| Building custom template viewer instead of CLI command | Visibility scoping — requirements gathering phase | User story must name specific information gap before any implementation begins |
| Visibility enabling template edits | Visibility design — read-only constraint in spec | Penetration test: attempt to modify template via API; must return 403 |
| Visibility scope creep to prompt management | Visibility design — boundary statement in spec | Backlog review: any story with "configure" or "manage" is deferred to its owning mechanism |
| Cross-pillar context isolation break | Cross-pillar integration phase (after both pillars individually tested) | Run functional-block section on each provider; verify output matches section-type, not provider default |
| Mid-project provider switching | Provider lock in new-fds phase (before visibility work) | Attempt provider change mid-project via CLI; verify warning dialog shown and lock enforced |
| Incompatible PROJECT.md schemas across pillars | Milestone kickoff — shared schema contract | Run `doc:status` on project created with all three pillar features; no unknown field warnings |

---

## Sources

- Project context: `.planning/PROJECT.md` — v3.0 milestone definition, existing constraints
- System architecture: `gsd-docs-industrial/CLAUDE-CONTEXT.md` — SSOT for existing system behavior
- Existing templates: `gsd-docs-industrial/templates/fds/section-equipment-module.md`, `templates/roadmap/type-a-nieuwbouw-standaard.md`
- Existing workflows: `gsd-docs-industrial/workflows/write-phase.md`, `commands/new-fds.md`
- Prompt portability (industry consensus): [Portability of LLM Prompts — Vivek Haldar](https://vivekhaldar.com/articles/portability-of-llm-prompts/), [OpenAI Community Thread](https://community.openai.com/t/the-portability-of-a-llm-prompt/311147)
- Over-abstraction anti-pattern: [Moving Beyond Over Abstraction — HatchWorks AI](https://hatchworks.com/blog/gen-ai/llm-projects-production-abstraction/), [LLM Abstraction Layer — ProxAI](https://www.proxai.co/blog/archive/llm-abstraction-layer)
- LLM routing and fallback strategies: [Failover Routing — Portkey](https://portkey.ai/blog/failover-routing-strategies-for-llms-in-production/), [LiteLLM Router](https://docs.litellm.ai/docs/routing)
- Local LLM deployment for confidential content: [On-Prem LLMs vs Cloud APIs — Unified AI Hub](https://www.unifiedaihub.com/blog/on-premise-llms-vs-cloud-apis-when-to-run-your-ai-models-on-premise)
- ISA-88 flexible decomposition pitfalls: [6 Steps to Flexible Control System — Control Engineering](https://www.controleng.com/6-steps-to-designing-a-flexible-control-system-with-isa-88/), [ISA-88 Unit Boundary Design — Cross Company](https://www.crossco.com/resources/articles/6-steps-to-designing-a-flexible-control-system-with-isa-88/)
- Git-based audit trails vs custom tooling: [Audit Trails and GitOps — Harness](https://www.harness.io/blog/audit-trails), [Best Prompt Versioning Tools — Braintrust](https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025)
- Schema migration patterns: [Schema Migrations Pitfalls — Quesma](https://quesma.com/blog/schema-migrations/), [Expand-Migrate-Contract — Defacto](https://www.getdefacto.com/article/database-schema-migrations)

---
*Pitfalls research for: Docs Engine Rearchitecture — GSD-Docs Industrial v3.0*
*Researched: 2026-03-31*
