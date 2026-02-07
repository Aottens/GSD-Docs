<writing_guidelines>

# FDS Writing Guidelines

**Status:** Starter rules for doc-writer agents. Will be expanded in Phase 3 (Write + Verify).

---

## Language

- Write in the language configured in PROJECT.md (`output.language`: `nl` or `en`)
- Use consistent language throughout -- do not mix Dutch and English within a section
- Technical terms from enabled standards (PackML, ISA-88) remain in their original English form

## Style

- **Technical precision:** Use concrete values, never vague descriptions
  - Good: "Temperature range: 20-80 C, resolution 0.1 C"
  - Bad: "The temperature can be adjusted as needed"
- **No marketing language:** No superlatives, no promotional tone
- **Active voice preferred:** "The system opens the valve" not "The valve is opened by the system"
- **Structured tables** for parameters, interlocks, and I/O -- never free-text lists for these

## Cross-References

- Use **symbolic references** during writing: "see phase-4/04-02" or "see interlock IL-200-01"
- Never hardcode section numbers (these are assigned at /doc:complete-fds assembly time)
- Reference format within document: "zie phase-N/NN-MM" (Dutch) or "see phase-N/NN-MM" (English)

## Terminology Discipline

- When standards are enabled, use **exact standard terms** (e.g., PackML state names: IDLE, EXECUTE, not "idle", "running")
- Use consistent terminology throughout the entire FDS -- same concept, same word, every time
- Define terms on first use if not part of an enabled standard

## Section Structure

- Each section starts with a brief functional description (2-3 sentences max)
- Parameters table: Parameter | Range | Unit | Default | Description
- Interlocks table: ID | Condition | Action | Priority
- I/O table: Tag | Type (DI/DO/AI/AO) | Description

</writing_guidelines>
