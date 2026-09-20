## ADDED Requirements

### Requirement: Skeleton prose stays under the rune caps

Every requirement statement in `docs/specs/` and `docs/changes/` MUST stay at or under 100 words, every scenario step at or under 30 words, and every canonical specification at or under 150 lines. Every capability id and change id MUST carry at least three hyphen-separated words. Every `CHANGELOG.md` entry MUST be one line of at most 200 characters that starts with a present-tense verb, in the Keep a Changelog group order.

#### Scenario: Requirement grows past the cap

- **WHEN** a change adds a requirement statement of 120 words
- **THEN** `rune spec doctor` fails the commit-stage hook and names the file

#### Scenario: Two-word capability is added

- **WHEN** a change adds a delta under `specs/merge-checks/`
- **THEN** `rune spec doctor` fails with `capability-name-short`

#### Scenario: Changelog entry becomes a paragraph

- **WHEN** a change adds a `CHANGELOG.md` line of 400 characters
- **THEN** `rune docs check` fails with `entry-length` and the line number
