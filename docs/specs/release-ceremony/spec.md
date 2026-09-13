# Release Ceremony Specification

## Purpose

How approved work enters `main` and how a release is sealed: merge commits, owner-signed tags verified against `KEYS`, and release notes compiled from merged pull requests.

## Requirements

### Requirement: Owner Attestation on Tags

The owner's hardware key MUST enter the ceremony at tags, not merges: release and checkpoint tags are annotated and owner-signed, a signed tag vouches for every commit reachable beneath it, and the root `KEYS` file plus the tag ruleset carry the trust anchor. The release workflow MUST verify the tag against `KEYS` before publication. Merging MUST NOT demand any additional signature ritual beyond the platform's own. The merge action is the owner's sign-off at credential strength, and the signed tag is the sign-off at hardware strength.

#### Scenario: Signed tag vouches for merged history

- **WHEN** the owner signs a release or checkpoint tag over `main`
- **THEN** every merge since the previous signed tag is attested by that signature

#### Scenario: Merge needs no ritual

- **WHEN** an approved, green pull request is merged from the platform interface
- **THEN** no additional signature is demanded at merge time

### Requirement: Release Notes Attestation

Every pull request body MUST carry a Release Notes section with at least one entry, `- N/A` legal for work with no user-facing effect, and the release workflow MUST compile the sections of merged pull requests into the release body the owner signs over. A pull request body MUST NOT change at or after merge. If it does, release compilation MUST fail because the public API cannot attest the merge-time body.

#### Scenario: Missing section

- **WHEN** a pull request body has no Release Notes section
- **THEN** the quality check fails naming the requirement

### Requirement: Merge and Release Ceremony

Approved work MUST enter `main` as a GitHub merge commit, and release tags MUST be annotated, signed by the owner, and verified before any release publishes.

#### Scenario: Merge preserves authorship

- **WHEN** the owner merges an approved pull request
- **THEN** every commit keeps its model author and contributor trailers on `main`

#### Scenario: Release verification

- **WHEN** the release workflow runs for a `v*` tag
- **THEN** it verifies the tag signature against the committed `KEYS` file before building, and fails on an unsigned or unknown signature

#### Scenario: Tag creation restricted

- **WHEN** an identity other than the owner attempts to create a `v*` tag
- **THEN** the tag rule refuses it
