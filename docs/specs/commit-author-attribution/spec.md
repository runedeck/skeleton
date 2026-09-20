# Commit Attribution Specification

## Purpose

Every commit in a runedeck repository says who authored it from the commit object alone: a human, or an AI model, and for a model, which harness and which model. Author identities are allowlisted, work by several models is attributed through *trailers*, and a required check applies the same rules to every pull request without a model-version catalog.

## Requirements

### Requirement: Allowlisted Model Identities

Every commit reaching `main` MUST carry an author identity that the trusted `authors.yaml` policy accepts.

The policy MUST accept exact `authors:` entries and formatted model identities under exact `model_domains:` entries.
When `model_domains:` is absent, the policy MUST derive approved harness domains from valid model entries in trusted `authors:`.
Trailer-only aliases MUST NOT grant harness permissions.
An explicit `model_domains:` list MUST replace inference, including an empty list.

New model versions under an approved domain MUST require no policy entry.
Human identities MUST remain exact policy entries.

#### Scenario: New model version

- **WHEN** a commit uses a valid identity for an unlisted model version under an approved domain
- **THEN** the attribution check accepts that identity

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

### Requirement: Model Identity Format

A formatted identity MUST use `Display Name (model-id) <model-id@domain>`.
Both model IDs MUST match after context normalization.
A model ID MUST use lowercase ASCII alphanumeric segments separated by dots or hyphens.
A model domain MUST use `<harness>.noreply.nexus.local`, where the harness is a lowercase ASCII slug.
The identity MUST contain printable text with no surrounding whitespace.
Listed identities under internal model domains MUST also satisfy the model format and ID-matching rules.

#### Scenario: Model IDs differ

- **WHEN** the display name and address contain different normalized model IDs
- **THEN** the check fails and identifies the commit

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

### Requirement: Unsigned Model Commits

Commits authored by models MUST be unsigned, and no branch rule MUST require commit signatures on `main`.

#### Scenario: Unsigned commit accepted

- **WHEN** an allowlisted model pushes an unsigned commit to a pull request branch
- **THEN** no check rejects the commit for lacking a signature
