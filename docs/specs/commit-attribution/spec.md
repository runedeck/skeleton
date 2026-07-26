# Commit Attribution Specification

## Purpose

Every commit in a runedeck repository answers who wrote it, which model, from the commit object alone. Identities are allowlisted, multi-model work is attributed through trailers, and a required check enforces the format on every pull request.

## Requirements

### Requirement: Allowlisted Model Identities

Every non-merge commit reaching `main` SHALL carry an author identity listed in `authors.yaml`, formatted as a display name ending in a parenthesized model id and a per-model non-routable address.

#### Scenario: Allowlisted author

- **WHEN** a commit is authored by `Claude Fable 5 (claude-fable-5) <claude-fable-5@claude.noreply.nexus.local>` and that identity appears in `authors.yaml`
- **THEN** the `ci/authorship` check passes for that commit

#### Scenario: Unlisted address

- **WHEN** a commit carries an author address absent from `authors.yaml`
- **THEN** the `ci/authorship` check fails and names the commit and the address

#### Scenario: Missing model id

- **WHEN** a commit's author display name carries no parenthesized model id
- **THEN** the `ci/authorship` check fails and names the expected format

### Requirement: Contributor Trailers

A commit produced by several models SHALL name the orchestrator as author and every other contributor as a `Co-Authored-By` trailer in the same identity format, without repeating the author.

#### Scenario: Distinct contributors

- **WHEN** a commit authored by one allowlisted model carries trailers for two other allowlisted models
- **THEN** the `ci/authorship` check passes

#### Scenario: Author repeated as contributor

- **WHEN** a commit's author identity also appears in a `Co-Authored-By` trailer
- **THEN** the `ci/authorship` check fails

### Requirement: Attribution Check Range

The `ci/authorship` check SHALL read commits from the merge base of the pull request to its head, and SHALL fail when the merge base cannot be resolved.

#### Scenario: Range resolved

- **WHEN** the check runs on a pull request whose merge base resolves
- **THEN** it examines every non-merge commit in that range and no commit outside it

#### Scenario: Unresolvable merge base

- **WHEN** the merge base cannot be resolved from the fetched history
- **THEN** the check fails rather than examining a partial range

### Requirement: Unsigned Model Commits

Commits authored by models SHALL be unsigned, and no branch rule SHALL require commit signatures on `main`.

#### Scenario: Unsigned commit accepted

- **WHEN** an allowlisted model pushes an unsigned commit to a pull request branch
- **THEN** no check rejects the commit for lacking a signature
