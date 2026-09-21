## ADDED Requirements

### Requirement: Generated display name carries the version

When the policy formats an identity for a model with no roster line, the display name MUST derive from the model ID: each hyphen-separated word title-cased, a run of numeric segments joined with dots, and the harness name first unless the model ID already starts with it. The display name MUST NOT drop a version segment.

#### Scenario: Point release under the claude harness

- **WHEN** `resolve` runs for model `claude-fable-5-1` and harness `claude`
- **THEN** the identity is `Claude Fable 5.1 (claude-fable-5-1) <claude-fable-5-1@claude.noreply.nexus.local>`

#### Scenario: Vendor model under another harness

- **WHEN** `resolve` runs for model `gpt-6-astra` and harness `codex`
- **THEN** the identity is `Codex Gpt 6 Astra (gpt-6-astra) <gpt-6-astra@codex.noreply.nexus.local>`

#### Scenario: Roster line reproduces

- **WHEN** the derivation runs on the model ID and harness of any listed identity
- **THEN** it returns that identity's display name
