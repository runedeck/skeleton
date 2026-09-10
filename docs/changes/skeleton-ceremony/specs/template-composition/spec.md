## MODIFIED Requirements

### Requirement: Tagged Updates

Generated repositories SHALL record the skeleton source, release reference, and rendering answers in `answers.yaml`. The reference MAY be a tag or a commit. `make install` SHALL require the full pinned toolchain, Copier included. `make validate` and the review lanes SHALL run without Copier.

#### Scenario: New template release

- **WHEN** Copier updates a consumer from its recorded reference to a newer one
- **THEN** downstream edits are reapplied and the owner reviews the result before it reaches `main`

#### Scenario: Copier is unavailable

- **WHEN** Copier cannot run
- **THEN** template installation and updates are unavailable while repository checks and review lanes continue

#### Scenario: Update targets a commit

- **WHEN** the recorded reference is a commit and skeleton has no newer tag
- **THEN** `copier update --vcs-ref <commit>` applies the template at that commit and records it

## ADDED Requirements

### Requirement: Shared Pinned Lint Tools

`templates/base/scripts/tool-versions` SHALL pin one version and one SHA-256 digest per supported platform for every tool the prek hooks call, and `scripts/install-tools` SHALL install each from a digest-verified release archive.

#### Scenario: Installer receives a mismatched archive

- **WHEN** a downloaded archive's digest differs from the pinned value
- **THEN** the installer fails before extraction and installs nothing

#### Scenario: Required tool is absent under REQUIRE_GATES

- **WHEN** `REQUIRE_GATES` is set and a guarded hook's binary is not on the path
- **THEN** the hook fails instead of skipping

#### Scenario: Hook names an unpinned binary

- **WHEN** a guarded hook calls a binary with no version in `tool-versions`
- **THEN** the tool installer contract test fails

### Requirement: Generated STE Style

The Vale STE style SHALL be generated from a frozen snapshot of the Simplified Technical English rule source by `scripts/generate-vale-style.py`, and a check hook SHALL fail when a generated file is stale, missing, or foreign to the generator.

#### Scenario: Rule source changes

- **WHEN** the snapshot changes without regeneration
- **THEN** the check reports the digest mismatch and every stale style file

#### Scenario: Prose contains a blockquote

- **WHEN** a blockquote holds a semicolon
- **THEN** the style reports it, because captured output belongs in a fence

#### Scenario: Captured output uses a fence

- **WHEN** a fenced or inline code span holds a semicolon or a contraction
- **THEN** the style reports nothing

#### Scenario: File starts with front matter

- **WHEN** a YAML front matter block holds a contraction or a semicolon
- **THEN** the style reports nothing, because every generated rule is scoped to sentences and metadata is not prose
