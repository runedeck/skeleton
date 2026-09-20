# Review Lanes Specification

## Purpose

Which *agentic review lanes* exist, which of them the default *review funnel* runs, in what order, and what evidence each round reuses. A lane that bills per run spends only inside a requested round.

## Requirements

### Requirement: Paid Lane Admission

A lane that bills per run MUST run only inside a requested review round.
A paid lane MUST start only from the controller after its triage admits a ready or green head, or from an owner-applied review label.
An agent MUST NOT request a round.
Bare `review` MUST request Macroscope, then the adjudicating correctness lane.
Each `review:` label MUST request its single lane.

#### Scenario: Full cascade from one label

- **WHEN** the owner applies `review`
- **THEN** the cascade verifies completed Macroscope correctness evidence on the current head before Runeseer adjudicates

### Requirement: Free and Optional Lanes

Codex and Cursor Security MUST run on every push as free lanes and record into the ledger. Cursor Security MUST run under its own spend cap and only for trusted actors. CodeRabbit and Macroscope MUST remain optional summoned lanes outside the default funnel.
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

Every finding from every lane MUST receive a disposition in the correctness verdict, and the owner MUST clear or reject the ones disposed as `owner` before the head can be queued for the seal.

### Requirement: Pending Review Requests

A review label handled by this repository's workflows MUST remain pending while the pull request is a draft.
The pending request MUST start when the pull request becomes ready.
Removing a pending request label MUST prevent dispatch.
Consuming a dispatched request label MUST preserve the active round.
An infrastructure failure before dispatch MUST preserve the request label.

### Requirement: Current-Head Evidence Reuse

The cascade MUST verify the configured Macroscope correctness check on the current head in every round.
A completed `success` or `neutral` check MUST permit Runeseer to adjudicate the reported findings.
The cascade MAY reuse that completed check without requesting another Macroscope review.
The `stage:macroscope` label MUST record completion without replacing current-head evidence.
Removing that label MUST NOT require another review when the current head already has a qualifying completed check.
Further rounds MUST judge only the range since the previous verdict.

#### Scenario: Review round reuses current-head evidence

- **WHEN** the configured Macroscope correctness check completed with `success` or `neutral` on the current head
- **THEN** the cascade reuses that check and sends its findings to Runeseer without another Macroscope request

#### Scenario: Stage label removal preserves valid evidence

- **WHEN** the owner removes `stage:macroscope` while a qualifying completed check remains on the current head
- **THEN** the next cascade verifies and reuses that check

#### Scenario: Stage label cannot approve a changed head

- **WHEN** `stage:macroscope` remains after a head change without a qualifying completed check on the new head
- **THEN** the cascade waits for an existing current-head run or requests a new Macroscope review

### Requirement: Lane Failure Handling

A terminal provider failure in a default lane MUST stop the cascade immediately.
The failure handler MUST preserve an undelivered review request and apply a persistent `issue:` label.
It MUST refuse another request for that lane until the blocker clears or a qualifying current-head round proves recovery.

### Requirement: Required Review Checks

The verdict mirror (`review/correctness`) MUST remain the single required review status check, and it MUST be the controller's check, reporting the ledger's coverage state when the paid lane does not run.
The `quality` check MUST enforce deterministic validation independently.
The cascade MUST report orchestration progress without acting as a second required review status check.
The mirror MUST report failure for a head without a verdict until a round completes.
Fork pull requests MUST use the owner's Repository-admin bypass after the available free default lanes settle clean.

#### Scenario: Push between rounds

- **WHEN** a pull request is pushed carrying no `review` or `review:` label
- **THEN** no paid lane runs for that push
- **AND** the previous head's verdict remains behind
- **AND** the current head's required checks stay unsatisfied until a maintainer applies a review label, holding the merge closed
