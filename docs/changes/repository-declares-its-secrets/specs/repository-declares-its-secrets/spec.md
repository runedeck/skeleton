## ADDED Requirements

### Requirement: Generated repository declares its secrets

The generator MUST write a secret declaration at the root of every new repository. The declaration MUST name the repository, MUST give every secret a description, and MUST include a profile for continuous integration that reads secrets only from the job environment.

#### Scenario: New repository from the template

- **WHEN** the generator creates a repository
- **THEN** the repository root holds a secret declaration named after the repository
- **AND** its continuous integration profile reads only the job environment

### Requirement: Consumer owns its declaration

After the first copy, a template update MUST NOT change a consumer's secret declaration, because each consumer lists its own secrets.

#### Scenario: Template update over an edited declaration

- **WHEN** a consumer added a secret to its declaration and then takes a template update
- **THEN** the declaration keeps the consumer's secret

### Requirement: Commit stage checks the declaration

The validator MUST check the secret declaration in the commit stage whenever the declaration changes, and MUST reject a declaration that does not parse or that has a secret without a description. The check MUST NOT read a secret value, and it MUST skip when the secret manager is not installed.

#### Scenario: Secret without a description

- **WHEN** a commit adds a secret without a description to the declaration
- **THEN** the commit stage fails and names the secret

#### Scenario: Workstation without the secret manager

- **WHEN** a contributor commits a declaration change without the secret manager installed
- **THEN** the check skips and the commit proceeds
