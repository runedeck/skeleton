## MODIFIED Requirements

### Requirement: Trusted Attribution Inputs

CI MUST execute the checker, helper, and policy from the pull request base SHA.
It MUST fetch the head only as commit metadata.
Local checks MUST read `origin/main:authors.yaml` unless the caller supplies an explicit trusted policy file.
When `origin/main` resolves and carries no `authors.yaml`, the local check MUST read the target commit's `authors.yaml` instead and MUST print which policy judged the range.
A base that carries any `authors.yaml` MUST stay the trusted policy, whether or not it is valid.
Both paths MUST use the same parser and identity validator.

#### Scenario: Head attempts to approve itself

- **WHEN** a pull request adds its own address domain or modifies the validator
- **THEN** CI evaluates its commits with the base checker, helper, and policy

#### Scenario: Local and CI parity

- **WHEN** both entrypoints receive the same commit range and trusted policy
- **THEN** both report the same attribution result

#### Scenario: First adoption

- **WHEN** `origin/main` carries no `authors.yaml` and the target commit does
- **THEN** the check judges the range by the target's policy and prints that it did

#### Scenario: First adoption without a policy

- **WHEN** neither `origin/main` nor the target commit carries `authors.yaml`
- **THEN** the check fails
