## MODIFIED Requirements

### Requirement: Paid Lane Admission

A lane that bills per run MUST run only inside a requested review round.
A review lane MUST NOT start from pull request lifecycle events alone.
A maintainer MUST apply a review label to request each round.
Bare `review` MUST request Macroscope, then PR-Agent, then the adjudicating correctness lane.
Each `review:` label MUST request its single lane.

#### Scenario: Full cascade from one label

- **WHEN** the owner applies `review`
- **THEN** the cascade verifies completed Macroscope correctness evidence on the current head before it runs PR-Agent
- **AND** Runeseer adjudicates after PR-Agent completes its current-head review

### Requirement: Free and Optional Lanes

Cursor and CodeRabbit MUST remain optional standalone lanes outside the default funnel.
The default funnel MUST proceed without an optional lane request or an optional provider credential.
An unavailable or skipped optional lane MUST NOT count as a clean review.

#### Scenario: Optional lane does not participate

- **WHEN** Cursor or CodeRabbit does not review the pull request
- **THEN** the default funnel proceeds without treating that absence as approval
- **AND** `review/correctness` still requires a verdict on the current head

#### Scenario: Optional lane reports a finding

- **WHEN** a requested Cursor or CodeRabbit round reports a genuine finding
- **THEN** a fix or an explicit owner acceptance resolves the finding before merge

### Requirement: Finding Disposition Before Seal

The owner MUST resolve genuine findings from optional lanes before merge or explicitly accept them.

#### Scenario: Optional finding accepted by the owner

- **WHEN** the owner explicitly accepts a genuine finding from an optional lane
- **THEN** the finding no longer holds the merge closed

### Requirement: Required Review Checks

The verdict mirror (`review/correctness`) MUST remain the single required review status check.
The `quality` check MUST enforce deterministic validation independently.
The cascade MUST report orchestration progress without acting as a second required review status check.
The mirror MUST report failure for a head without a verdict until a round completes.
Fork pull requests MUST use the owner's Repository-admin bypass after the available free default lanes settle clean.

#### Scenario: Push between rounds

- **WHEN** a pull request is pushed carrying no `review` or `review:` label
- **THEN** no paid lane runs for that push
- **AND** the previous head's verdict does not approve the new head
- **AND** the current head requires a fresh review request and a clean verdict before merge

## ADDED Requirements

### Requirement: PR-Agent Review Lane

PR-Agent MUST run one `review` call in command mode from a pinned image.
The default cascade MUST run PR-Agent after it verifies the Macroscope check.
Runeseer MUST adjudicate the findings after PR-Agent completes its current-head review.
The cascade MAY reuse a completed PR-Agent review on the same head when its findings are resolved.
The `stage:pr-agent` label MUST record completion without replacing current-head evidence.

#### Scenario: PR-Agent stage requires current-head evidence

- **WHEN** `stage:pr-agent` remains after a head change without a completed PR-Agent review on the new head
- **THEN** the cascade requests a PR-Agent review before Runeseer adjudicates

#### Scenario: PR-Agent round reuses current-head evidence

- **WHEN** PR-Agent completed its review on the current head and its findings are resolved
- **THEN** the cascade reuses that review without another PR-Agent request

#### Scenario: PR-Agent lane summoned alone

- **WHEN** the owner applies `review:pr-agent`
- **THEN** the lane runs one review call and posts its findings under the workflow token
- **AND** the lane consumes the request label
- **AND** the lane records `stage:pr-agent` when the findings resolve

### Requirement: Lane Table

Every lane MUST have one table row that names its request scope, summon, settle signal, finding source, and labels.
The request scope MUST identify a default lane or a standalone lane.
The cascade MUST select only default rows for bare `review`.
A single-lane request MUST select only its matching row.
The cascade MUST iterate the selected rows.
A new lane MUST add a row instead of lane-specific shell.

#### Scenario: New lane joins

- **WHEN** a reviewer joins the funnel
- **THEN** its row provisions its labels, its summon, and its settle check without a change to the cascade logic

#### Scenario: Optional rows stay outside the default request

- **WHEN** the lane table includes standalone Cursor and CodeRabbit rows and the owner applies bare `review`
- **THEN** the cascade selects Macroscope, PR-Agent, and Runeseer without selecting either standalone row
