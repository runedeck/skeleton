# Merge Checks Specification

## Purpose

The deterministic checks that hold a merge closed independently of any review: tests and lint, range-scoped secret scanning, and the specification-presence check on protected paths. A passing review substitutes for none of them.

## Requirements

### Requirement: Deterministic Checks Independent of Review

The tests, lint, secret scan, schema validation, authorship, and specification checks MUST be required independently of the review lanes, and a passing review MUST NOT substitute for any of them.

#### Scenario: Review passes while a test fails

- **WHEN** every review lane passes and a test job fails
- **THEN** `main` refuses the merge

### Requirement: Range-Scoped Secret Scanning

Secret scanning MUST examine only the commits a push or pull request introduces, resolved as an explicit commit range. A full-history scan MUST run on a schedule, not per push or pull request.

#### Scenario: Pull-request scan

- **WHEN** the secret scan runs on a pull request
- **THEN** it scans from the merge base to the head commit and no earlier history

#### Scenario: Pre-push scan

- **WHEN** the pre-push hook receives a ref update for an existing remote branch
- **THEN** it scans from the remote commit to the local commit

#### Scenario: New branch push

- **WHEN** the pushed ref does not exist on the remote
- **THEN** the hook scans from the merge base with the default branch to the local commit

#### Scenario: Scheduled full scan

- **WHEN** the scheduled scan fires
- **THEN** it scans the full history, and no per-push or per-pull-request scan does

### Requirement: Specification Presence on Protected Paths

A pull request touching protected paths MUST either carry a specification change or an `ignore:spec` label with a stated reason in the body. `ignore:spec` belongs to the ignore family of allowed defects: the change enters `main` unspecified, and the label records that the owner accepted that.

#### Scenario: Protected path with a specification

- **WHEN** a pull request modifies a protected path and includes a specification change
- **THEN** the specification check passes

#### Scenario: Protected path with an active delta specification

- **WHEN** a pull request modifies a protected path and includes `docs/changes/<change>/specs/<capability>/spec.md`
- **THEN** the specification check accepts that delta as a specification change

#### Scenario: Proposal without a specification

- **WHEN** a protected-path pull request includes only proposal, design, or task documents and has no `ignore:spec` label
- **THEN** the specification check fails

#### Scenario: Protected path without either

- **WHEN** a pull request modifies a protected path with no specification change and no `ignore:spec` label
- **THEN** the specification check fails

#### Scenario: Unprotected path

- **WHEN** a pull request touches only files outside the protected paths
- **THEN** the specification check passes without requiring a specification change
