# Worktree Identity Specification

## Purpose

How `make worktree` gives a workspace its model identity before any commit exists, and how `make worktree-done` removes only a clean, merged workspace.

## Requirements

### Requirement: Worktree Identity Provisioning

`make worktree BRANCH=<branch> IDENTITY=<model-id> [HARNESS=<harness>]` MUST resolve identity before it creates a worktree or workspace.

For an existing model, the resolver MUST select a unique matching author entry.
For a new model, the resolver MUST generate a formatted identity under the supplied approved harness domain.
An absent harness MUST resolve only when one existing identity matches the model.
An ambiguous identity or unapproved harness MUST fail before workspace creation.

Git worktrees MUST receive the selected `user.name` and `user.email`.
Jujutsu workspaces MUST report the selected `JJ_USER` and `JJ_EMAIL` values.

#### Scenario: Unique existing identity

- **WHEN** one author entry matches the model and the harness is absent
- **THEN** the resolver returns that entry

#### Scenario: New model provisioned

- **WHEN** an unlisted valid model ID and an approved harness are supplied
- **THEN** the resolver generates an identity that the attribution validator accepts

#### Scenario: Ambiguous existing identity

- **WHEN** several author entries match the model and the harness is absent
- **THEN** the target fails before it creates a workspace or branch

#### Scenario: New model needs a harness

- **WHEN** an unlisted model has no supplied harness
- **THEN** the target requests a harness before it creates a workspace or branch

#### Scenario: Unknown harness

- **WHEN** the supplied harness selects no approved domain or existing identity
- **THEN** the target fails before it creates a workspace or branch

### Requirement: Worktree Cleanup

`make worktree-done BRANCH=<branch>` MUST remove only a clean worktree or workspace whose work is merged.

The target MUST preserve tracked, untracked, and ignored files when it cannot verify safe removal.

#### Scenario: Git branch merged by ancestry

- **WHEN** the worktree and branch heads are reachable from the default branch
- **THEN** the target removes the worktree and deletes the local branch

#### Scenario: Git branch squash merged

- **WHEN** GitHub reports a merged pull request whose head equals the worktree and branch head
- **THEN** the target removes the worktree and deletes the local branch

#### Scenario: Git merge state is not safe

- **WHEN** the matching pull request is open, stale, absent, or unavailable
- **THEN** the target fails and preserves the worktree and branch

#### Scenario: Jujutsu workspace contains unmerged work

- **WHEN** the workspace or its local bookmark contains nonempty work that is not on trunk
- **THEN** the target fails and preserves the workspace and bookmark

#### Scenario: Workspace contains ignored data

- **WHEN** the worktree or workspace contains ignored files
- **THEN** the target fails and identifies the data that requires preservation

#### Scenario: Jujutsu workspace is safe

- **WHEN** the workspace is clean and its local bookmark has no work outside trunk
- **THEN** the target removes the workspace directory before it forgets the workspace and bookmark
