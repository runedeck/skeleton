## ADDED Requirements

### Requirement: Trusted Check State

A pull request MUST NOT select or weaken the checks that judge it. The specification-presence check, the authorship policy, and the protected-path list MUST execute from the base ref. The head `.pre-commit-config.yaml` MAY run, because every change to it is itself a protected path that needs a specification or an `ignore:spec` waiver.

#### Scenario: Head edits the check policy

- **WHEN** a pull request changes `.pre-commit-config.yaml`, `authors.yaml`, or a workflow under `.github/workflows/`
- **THEN** the specification-presence check runs from the base ref and requires a specification change or an `ignore:spec` label

#### Scenario: Head removes a hook

- **WHEN** a pull request deletes a hook from `.pre-commit-config.yaml` without a specification change
- **THEN** the specification-presence check fails before the weakened configuration can pass the merge
