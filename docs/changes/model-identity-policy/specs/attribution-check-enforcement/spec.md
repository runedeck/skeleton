## ADDED Requirements

### Requirement: Trusted Attribution Inputs

CI MUST execute the checker, helper, and policy from the pull request base SHA.
It MUST fetch the head only as commit metadata.
Local checks MUST read `origin/main:authors.yaml` unless the caller supplies an explicit trusted policy file.
Both paths MUST use the same parser and identity validator.

#### Scenario: Head attempts to approve itself

- **WHEN** a pull request adds its own address domain or modifies the validator
- **THEN** CI evaluates its commits with the base checker, helper, and policy

#### Scenario: Local and CI parity

- **WHEN** both entrypoints receive the same commit range and trusted policy
- **THEN** both report the same attribution result

### Requirement: Attribution Policy Parser

The parser MUST accept only the documented plain block-list policy format.
It MUST fail on unreadable policy, unknown keys, duplicate keys, duplicate entries, unsupported YAML syntax, or an empty author list.
Policy validation MUST run even when the selected commit range is empty.
Attribution validation MUST describe syntax and policy compliance, not proof that the named model executed.

#### Scenario: Empty range with malformed policy

- **WHEN** the selected range is empty and policy is malformed
- **THEN** the check fails instead of reporting compliance
