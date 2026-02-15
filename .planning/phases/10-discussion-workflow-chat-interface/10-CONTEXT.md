# Phase 10: Discussion Workflow & Chat Interface - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Engineers can conduct discussion phases through an embedded chat panel with real-time AI interaction and conversation persistence. Includes a phase timeline for workflow progress visibility and operation triggering. Planning, writing, verification, and review workflows are separate phases — this phase delivers only discussion.

</domain>

<decisions>
## Implementation Decisions

### Phase timeline
- Horizontal timeline bar above the main workspace content — always visible, compact
- Each phase node shows colored icon + sub-status detail (Besproken, Gepland, Geschreven, Geverifieerd, Beoordeeld)
- Clicking a phase node opens an inline popover with status summary and action buttons (only valid next actions enabled)
- Separate "Fasering" tab available for full detailed phase view with all phases expanded
- Compact bar is the quick entry point; Fasering tab gives the full picture

### Chat panel design
- Reuse the slide-in Sheet component (from Phase 8) — discussion opens from the right side
- Hybrid question cards: AI presents questions as styled cards with clickable option chips AND a text input for freeform/detailed answers
- Multi-select card for initial gray area selection (direct v1.0 AskUserQuestion translation)
- Text input with file attach button — engineer can reference project files while answering
- Supported file types for attachment include .md files (gap from Phase 9: add .md to accepted upload types)

### Discussion flow
- AI-driven with backend guardrails: Claude API drives the conversation, backend enforces structure (topic selection step, scope boundary, question pacing)
- Extract and optimize v1.0 discussion patterns into a chat-optimized prompt (NOT verbatim workflow injection). Fallback: if extracted version lacks depth, switch to full v1.0 workflow as system prompt
- Summary card posted in chat after each topic completes — engineer confirms, edits, or adds before moving on
- Running summary panel visible alongside the chat — accumulates decisions as discussion progresses, always shows the full picture
- Engineer can edit decisions two ways: click in the summary panel to edit directly, OR type a correction in chat and AI updates the summary
- Scope creep handling preserved from v1.0: redirect to deferred ideas, don't discuss new capabilities

### Conversation history
- Past discussions accessible from both the phase timeline (contextual: "Bekijk bespreking") and a dedicated "Gesprekken" tab (full overview)
- Past conversations are read-only — "Bijwerken" (Update) button starts a new discussion pre-loaded with existing context
- Clean separation between original discussion and revision sessions

### Claude's Discretion
- CONTEXT.md decision surfacing approach (summary panel, rendered document, or hybrid)
- Conversation message storage (SQLite vs file-based)
- Chat message styling and bubble design
- Popover layout for timeline phase detail
- Fasering tab detailed view layout

</decisions>

<specifics>
## Specific Ideas

- **V1.0 fidelity (HARD GUARDRAIL):** The discussion engine MUST source domain content from v1.0 files — project types A/B/C/D, content type detection, question depth patterns, delta framing for Type C/D. These must be read from v1.0 source files (path + section), not assumed or paraphrased. Previous phase (9) failed this by assuming project type definitions.
- Plans MUST reference specific v1.0 source files for: content type mappings, gray area patterns per content type, specification-depth question examples, scope creep handling rules, CONTEXT.md generation format
- Reuse Sheet component from Phase 8 for the chat panel (consistent UX pattern)
- All UI in Dutch (consistent with Phase 8/9 decision)
- .md files must be added as accepted upload type (fix gap from Phase 9)

</specifics>

<deferred>
## Deferred Ideas

- Phase 9 fix: add .md to accepted file upload types in backend validation — could be addressed as Phase 10 prerequisite or separate fix

</deferred>

---

*Phase: 10-discussion-workflow-chat-interface*
*Context gathered: 2026-02-15*
