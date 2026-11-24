## ADDED Requirements

### Requirement: Declaration shows a read with a reason

The secret declaration that the generator writes MUST show its example read with a reason for the access. The secret manager refuses a read from an agent session that gives no reason, so an agent that copies a read without one fails.

#### Scenario: Agent copies the example read

- **WHEN** an agent copies the read that the generated declaration shows
- **THEN** the read gives a reason
- **AND** the secret manager accepts the read from an agent session
