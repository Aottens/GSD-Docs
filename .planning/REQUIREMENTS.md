# Requirements: GSD-Docs Industrial v3.0 Docs Engine Rearchitecture

**Defined:** 2026-03-31
**Core Value:** Rearchitect the docs backend from rigid EM-first structure to flexible system-first approach, add LLM provider abstraction, and create engine visibility for engineers

## v1 Requirements

Requirements for v3.0 release. Each maps to roadmap phases.

### Flexible Structure

- [ ] **FLEX-01**: Engineer classifies project type (A/B/C/D) first, then describes the system functionally before choosing a decomposition model
- [ ] **FLEX-02**: Engineer can select a decomposition model (isa88_em, functional, process_flow, hybrid) after system discovery
- [ ] **FLEX-03**: Decomposition model is stored in PROJECT.md and read by all downstream commands
- [ ] **FLEX-04**: ROADMAP generation adapts phase structure based on both project type AND decomposition model
- [ ] **FLEX-05**: Section templates are selected based on decomposition model at write time
- [ ] **FLEX-06**: Project type (A/B/C/D) and decomposition model are independent dimensions — any type can use any model
- [ ] **FLEX-07**: Hybrid decomposition allows per-phase model selection (e.g., Phase 2 = isa88_em, Phase 3 = functional)
- [ ] **FLEX-08**: Standards checking (PackML/ISA-88) applies only to isa88_em and hybrid-EM phases
- [ ] **FLEX-09**: During decomposition model selection, the system explains each model and shows a preview of the resulting FDS structure
- [ ] **FLEX-10**: Engineer can create a custom decomposition model via `/doc:create-decomposition` that defines section types, hierarchy, and phase structure
- [ ] **FLEX-11**: Engineer can extract a decomposition model from an existing FDS document via `/doc:extract-decomposition`

### LLM Abstraction

- [ ] **LLM-01**: All CLI commands use a single provider abstraction interface instead of direct Anthropic SDK calls
- [ ] **LLM-02**: LLM provider and model are configured per project in PROJECT.md
- [ ] **LLM-03**: Claude (Anthropic) works as a provider through the abstraction layer
- [ ] **LLM-04**: OpenAI/GPT works as a provider through the abstraction layer
- [ ] **LLM-05**: Local models via Ollama work as a provider through the abstraction layer
- [ ] **LLM-06**: API keys are managed via environment variables, never stored in project files
- [ ] **LLM-07**: Misconfigured provider gives a clear error message before any LLM call
- [ ] **LLM-08**: Fallback chain allows automatic failover between providers
- [ ] **LLM-09**: Token usage and cost are logged per project
- [ ] **LLM-10**: Context budget enforcement prevents silent truncation on smaller-context models

### Engine Visibility

- [ ] **ENGV-01**: Engineer can browse all templates, commands, and workflows in a read-only GUI viewer
- [ ] **ENGV-02**: Engineer can see per-project config summary (provider, model, decomposition model, standards flags)
- [ ] **ENGV-03**: Generated sections show which template and prompts were used (template_ref/prompt_ref in PLAN.md)
- [ ] **ENGV-04**: Engineer can browse command documentation rendered as readable pages
- [ ] **ENGV-05**: Engine version is displayed in GUI header and exported document frontmatter
- [ ] **ENGV-06**: Engineer can view changelog of engine updates via git history
- [ ] **ENGV-07**: Engineer can browse verification criteria per section type
- [ ] **ENGV-08**: Template health indicators flag stale or incomplete templates

## v2 Requirements

Deferred to v3.x releases. Tracked but not in current roadmap.

### Extended Structure

- **XFLEX-01**: Structure evolution / late promotion — project starts functional, promotes to ISA-88 mid-project
- **XFLEX-02**: ISA-88 conformance check on functional projects — suggest EM/CM boundaries from functional description

### Extended LLM

- **XLLM-01**: Per-phase provider override via environment variable
- **XLLM-02**: OpenAI-compatible custom endpoint support (Azure OpenAI, self-hosted gateways)

### Extended Visibility

- **XENGV-01**: Usage statistics per template across all projects
- **XENGV-02**: Template comparison view (diff between versions)

### Deferred from v2.0

- **SYST-02**: VM deployment with Nginx reverse proxy and systemd services
- **SYST-03**: CLI compatibility verification

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Free-form structure (no decomposition model) | No structure = no templates, no verification criteria, no consistent output |
| Automatic structure detection from description | LLM classification unreliable; wrong choice poisons entire project ROADMAP |
| GUI-driven structure editor (drag-and-drop) | Massive scope; breaks file-backed state; CLI incompatibility |
| GUI-based provider configuration | GUI has no LLM operations (cockpit pivot decision); provider config stays in CLI/PROJECT.md |
| Real-time model comparison (A/B output) | Doubles token cost; creates decision fatigue; FDS content should be deterministic |
| Fine-tuned models | Training data management, infrastructure, and retraining cycles are enormous scope |
| In-GUI template editing | File-backed templates are SSOT; GUI edits create divergence and break version control |
| Per-project template overrides | Template divergence across projects makes QA impossible |
| AI-assisted template improvement | Meta-prompting loop; safety risk for standards-adjacent content |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FLEX-01 | TBD | Pending |
| FLEX-02 | TBD | Pending |
| FLEX-03 | TBD | Pending |
| FLEX-04 | TBD | Pending |
| FLEX-05 | TBD | Pending |
| FLEX-06 | TBD | Pending |
| FLEX-07 | TBD | Pending |
| FLEX-08 | TBD | Pending |
| FLEX-09 | TBD | Pending |
| FLEX-10 | TBD | Pending |
| FLEX-11 | TBD | Pending |
| LLM-01 | TBD | Pending |
| LLM-02 | TBD | Pending |
| LLM-03 | TBD | Pending |
| LLM-04 | TBD | Pending |
| LLM-05 | TBD | Pending |
| LLM-06 | TBD | Pending |
| LLM-07 | TBD | Pending |
| LLM-08 | TBD | Pending |
| LLM-09 | TBD | Pending |
| LLM-10 | TBD | Pending |
| ENGV-01 | TBD | Pending |
| ENGV-02 | TBD | Pending |
| ENGV-03 | TBD | Pending |
| ENGV-04 | TBD | Pending |
| ENGV-05 | TBD | Pending |
| ENGV-06 | TBD | Pending |
| ENGV-07 | TBD | Pending |
| ENGV-08 | TBD | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 0 (pending roadmap creation)
- Deferred (v3.x): 7

---
*Requirements defined: 2026-03-31*
