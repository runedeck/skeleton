## MODIFIED Requirements

### Requirement: Worktree Identity Provisioning

`make worktree BRANCH=<branch> IDENTITY=<model-id> [HARNESS=<harness>]` MUST resolve identity before it creates a worktree or workspace.

For an existing model, the resolver MUST select a unique matching author entry.
For a new model, the resolver MUST generate a formatted identity under the supplied approved harness domain.
An absent harness MUST resolve only when one existing identity matches the model.
An ambiguous identity or unapproved harness MUST fail before workspace creation.

In a jj colocated repository the target MUST create a jj workspace under `.workspaces/` and print the `JJ_USER` and `JJ_EMAIL` exports for the selected identity, because jj reads the author from the environment of each command.
In a git-only repository the target MUST create a git worktree under `.worktrees/` and write the selected `user.name` and `user.email` into that worktree's configuration.

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

#### Scenario: Colocated repository provisions a workspace

- **WHEN** the repository carries a `.jj` directory
- **THEN** the target creates a jj workspace and prints the `JJ_USER` and `JJ_EMAIL` exports instead of writing git configuration

#### Scenario: Git-only repository provisions a worktree

- **WHEN** the repository carries no `.jj` directory
- **THEN** the target creates a git worktree with the selected identity in its worktree configuration
