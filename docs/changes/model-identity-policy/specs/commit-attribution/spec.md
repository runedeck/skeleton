## MODIFIED Requirements

### Requirement: Allowlisted Model Identities

Every commit reaching `main` MUST carry an author identity that the trusted `authors.yaml` policy accepts.

The policy MUST accept exact `authors:` entries and formatted model identities under exact `model_domains:` entries.
When `model_domains:` is absent, the policy MUST derive approved harness domains from valid model entries in trusted `authors:`.
Trailer-only aliases MUST NOT grant harness permissions.
An explicit `model_domains:` list MUST replace inference, including an empty list.

A formatted identity MUST use `Display Name (model-id) <model-id@domain>`.
Both model IDs MUST match after context normalization.
A model ID MUST use lowercase ASCII alphanumeric segments separated by dots or hyphens.
A model domain MUST use `<harness>.noreply.nexus.local`, where the harness is a lowercase ASCII slug.
The identity MUST contain printable text with no surrounding whitespace.

New model versions under an approved domain MUST require no policy entry.
Human identities MUST remain exact policy entries.
Listed identities under internal model domains MUST also satisfy the model format and ID-matching rules.

#### Scenario: New model version

- **WHEN** a commit uses a valid identity for an unlisted model version under an approved domain
- **THEN** the attribution check accepts that identity

#### Scenario: Model IDs differ

- **WHEN** the display name and address contain different normalized model IDs
- **THEN** the check fails and identifies the commit

#### Scenario: Legacy policy permits a future model version

- **WHEN** trusted legacy policy lists a Claude model author and omits `model_domains:`
- **THEN** the new checker accepts a valid `claude-fable-5.2` identity under that same domain

#### Scenario: Explicit empty domain list

- **WHEN** trusted policy sets `model_domains: []`
- **THEN** the new checker accepts only exact author entries

#### Scenario: Unapproved address domain

- **WHEN** an unlisted identity uses a domain absent from the explicit or inferred approved domains
- **THEN** the check fails, including when that domain adds a suffix to an approved domain

#### Scenario: Existing exact identity

- **WHEN** an identity appears in the trusted `authors:` list
- **THEN** the check retains its existing author and contributor permissions

#### Scenario: Missing model ID

- **WHEN** an unlisted model identity omits the parenthesized model ID
- **THEN** the check fails and states the required format

#### Scenario: Malformed listed model

- **WHEN** an explicit internal model entry contains mismatched model IDs
- **THEN** policy validation fails before the commit range is examined

### Requirement: Contributor Trailers

A commit produced by several models MUST name the orchestrator as author.
It MUST name each other model contributor in a `Co-Authored-By` trailer using an accepted identity.
The check MUST accept exact `trailers:` aliases only in contributor trailers.
It MUST NOT accept a trailer-only alias as the author.

The check MUST compare model contributors by normalized model ID and harness domain, independent of display-name wording.
It MUST remove an explicit trailing `[1m]` context annotation before comparison.
It MUST treat the historical IDs `claude-fable-51m` and `claude-opus-51m` as `claude-fable-5` and `claude-opus-5`, respectively.
Other IDs ending in `1m` MUST retain their identity.

#### Scenario: Distinct contributors

- **WHEN** an accepted model author names two other accepted models as contributors
- **THEN** the attribution check accepts those contributors

#### Scenario: Author repeated through an alias

- **WHEN** a contributor has the author's normalized model ID and domain but a different display name or context annotation
- **THEN** the check rejects the repeated author

#### Scenario: Vendor trailer alias

- **WHEN** an exact vendor alias appears in `trailers:`
- **THEN** the check accepts it as a contributor and rejects it as the author

#### Scenario: Future ID ends in context-like text

- **WHEN** an ID ends in `1m` and differs from both historical aliases
- **THEN** normalization preserves that ID

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

## ADDED Requirements

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
