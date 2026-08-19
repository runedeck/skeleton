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

A commit produced by several models SHALL name the orchestrator as author and every other model contributor as a `Co-Authored-By` trailer in the same identity format, without repeating the author. Tooling-attribution trailers listed under `trailers:` in `authors.yaml` MAY also appear, but a `trailers:` entry SHALL NOT be accepted as a commit author. Context-window suffixes such as `[1m]` SHALL NOT create separate model identities.

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

### Requirement: Local Pre-Push Attribution Check

Every repository built from this template SHALL contain `scripts/check-authorship`. The script SHALL run as a prek hook at the pre-push stage. The script SHALL apply the same attribution rules as the `ci/authorship` check to the outgoing commit range. A violation SHALL block the push before the commits leave the machine.

#### Scenario: Bad identity blocked locally

- **WHEN** a push range contains a commit whose author repeats as a `Co-Authored-By` trailer
- **THEN** the pre-push hook fails, names the commit and the rule, and the push does not happen

#### Scenario: New branch push

- **WHEN** the push creates the remote branch and prek reports the zero object id as the from-ref
- **THEN** the check falls back to the merge base with `origin/main` and examines that range

### Requirement: Worktree Identity Provisioning

`make worktree BRANCH=<branch> IDENTITY=<model-id>` SHALL create a git worktree on the named branch. The target SHALL set a listed model identity as the local `user.name` and `user.email` of that worktree. The target SHALL refuse an identity that the `authors:` list of `authors.yaml` does not contain.

#### Scenario: Listed identity provisioned

- **WHEN** `make worktree` runs with a model id that appears in `authors.yaml`
- **THEN** commits made in the new worktree carry that identity with no per-command environment exports

#### Scenario: Unlisted identity refused

- **WHEN** `make worktree` runs with a model id absent from `authors.yaml`
- **THEN** the target fails and no worktree is created
