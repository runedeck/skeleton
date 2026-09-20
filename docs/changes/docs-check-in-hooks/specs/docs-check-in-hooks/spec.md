## ADDED Requirements

### Requirement: Commit stage runs the docs check

The base hook config MUST run `rune docs check` in the commit stage when a file under `docs/` or `CHANGELOG.md` is in the range, and MUST skip when the `rune` binary is absent, the same way `rune spec doctor` skips.

#### Scenario: Changelog-only commit

- **WHEN** a commit changes `CHANGELOG.md` alone
- **THEN** the commit stage runs `rune docs check` and fails on a changelog line over 200 characters

#### Scenario: Fresh clone without rune

- **WHEN** a contributor commits without `rune` installed
- **THEN** the hook skips and the commit proceeds
