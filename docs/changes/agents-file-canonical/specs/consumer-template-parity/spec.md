## ADDED Requirements

### Requirement: Ignore Baseline Survives Seeding

The template's `.gitignore` MUST name every runtime and working-layer path no repository of the stack may track. The parity audit MUST report a consumer whose `.gitignore` lacks any pattern of the template's file, and MUST NOT report patterns the consumer adds.

#### Scenario: Consumer dropped a baseline pattern

- **WHEN** a consumer's `.gitignore` has no `.trash/` line and the template's file has one
- **THEN** the report lists `.gitignore` under drift and names `.trash/`

#### Scenario: Consumer added its own patterns

- **WHEN** a consumer's `.gitignore` holds every template pattern plus `node_modules/`
- **THEN** the report lists nothing for `.gitignore`

### Requirement: One Instruction File

The template MUST render `AGENTS.md` as the only agent instruction file and MUST NOT render `CLAUDE.md` or `GEMINI.md`. A consumer that still carries either file MUST appear in the parity report as a file removed from the template.

#### Scenario: Consumer keeps a stub

- **WHEN** a consumer has `CLAUDE.md` after the template dropped it
- **THEN** the report lists `CLAUDE.md` as removed from the template, still present
