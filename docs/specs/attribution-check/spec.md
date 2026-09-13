# Attribution Check Specification

## Purpose

How the attribution rules are applied: the commit range the `ci/authorship` check reads, the trusted inputs it runs from, and the local pre-push hook that applies the same rules before commits leave the machine.

## Requirements

### Requirement: Attribution Check Range

The `ci/authorship` check MUST read the commits from the *merge base* of the pull request to its head, the range the pull request introduces, and MUST fail when the merge base cannot be resolved.

#### Scenario: Range resolved

- **WHEN** the check runs on a pull request whose merge base resolves
- **THEN** it examines every commit in that range and no commit outside it

#### Scenario: Unresolvable merge base

- **WHEN** the merge base cannot be resolved from the fetched history
- **THEN** the check fails rather than examining a partial range

### Requirement: Local Pre-Push Attribution Check

Every repository built from this template MUST contain `scripts/check-authorship`. The script MUST run as a prek hook at the pre-push stage. The script MUST apply the same attribution rules as the `ci/authorship` check to the outgoing commit range. A violation MUST block the push before the commits leave the machine.

#### Scenario: Bad identity blocked locally

- **WHEN** a push range contains a commit whose author repeats as a `Co-Authored-By` trailer
- **THEN** the pre-push hook fails, names the commit and the rule, and the push does not happen

#### Scenario: New branch push

- **WHEN** the push creates the remote branch and prek reports the zero object id as the from-ref
- **THEN** the check falls back to the merge base with `origin/main` and examines that range

### Requirement: Trusted Attribution Inputs

CI MUST execute the checker, helper, and policy from the pull request base SHA.
It MUST fetch the head only as commit metadata.
Local checks MUST read `origin/main:authors.yaml` unless the caller supplies an explicit trusted policy file.
Both paths MUST use the same parser and identity validator.

The parser MUST accept only the documented plain block-list policy format.
It MUST fail on unreadable policy, unknown keys, duplicate keys, duplicate entries, unsupported YAML syntax, or an empty author list.
Policy validation MUST run even when the selected commit range is empty.
Attribution validation MUST describe syntax and policy compliance, not proof that the named model executed.

#### Scenario: Head attempts to approve itself

- **WHEN** a pull request adds its own address domain or modifies the validator
- **THEN** CI evaluates its commits with the base checker, helper, and policy

#### Scenario: Empty range with malformed policy

- **WHEN** the selected range is empty and policy is malformed
- **THEN** the check fails instead of reporting compliance

#### Scenario: Local and CI parity

- **WHEN** both entrypoints receive the same commit range and trusted policy
- **THEN** both report the same attribution result
