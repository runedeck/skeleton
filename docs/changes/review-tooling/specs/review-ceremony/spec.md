## MODIFIED Requirements

### Requirement: Default and Optional Review Lanes

A lane that bills per run MUST run only inside a requested review round.
A review lane MUST NOT start from pull request lifecycle events alone.
A maintainer MUST apply a review label to request each round.
Bare `review` MUST request Macroscope, then PR-Agent, then the adjudicating correctness lane.
Each `review:` label MUST request its single lane.
Cursor and CodeRabbit SHALL remain optional standalone lanes outside the default funnel.
The default funnel MUST proceed without an optional lane request or an optional provider credential.
An unavailable or skipped optional lane MUST NOT count as a clean review.
The owner MUST resolve genuine findings from optional lanes before merge or explicitly accept them.

A review label handled by this repository's workflows MUST remain pending while the pull request is a draft.
The pending request MUST start when the pull request becomes ready.
Removing a pending request label MUST prevent dispatch.
Consuming a dispatched request label MUST preserve the active round.
An infrastructure failure before dispatch MUST preserve the request label.
The cascade MUST verify the configured Macroscope correctness check on the current head in every round.
A completed `success` or `neutral` check MUST permit Runeseer to adjudicate the reported findings.
The cascade MAY reuse that completed check without requesting another Macroscope review.
The `stage:macroscope` label SHALL record completion without replacing current-head evidence.
Removing that label SHALL NOT require another review when the current head already has a qualifying completed check.
Further rounds MUST judge only the range since the previous verdict.

PR-Agent MUST run one `review` call in command mode from a pinned image.
The default cascade MUST run PR-Agent after it verifies the Macroscope check.
Runeseer MUST adjudicate the findings after PR-Agent completes its current-head review.
The cascade MAY reuse a completed PR-Agent review on the same head when its findings are resolved.
The `stage:pr-agent` label SHALL record completion without replacing current-head evidence.

A terminal provider failure in a default lane MUST stop the cascade immediately.
The failure handler MUST preserve an undelivered review request and apply a persistent `issue:` label.
It MUST refuse another request for that lane until the blocker clears or a qualifying current-head round proves recovery.
The verdict mirror (`review/correctness`) SHALL remain the single required review status check.
The `quality` check SHALL enforce deterministic validation independently.
The cascade SHALL report orchestration progress without acting as a second required review status check.
The mirror MUST report failure for a head without a verdict until a round completes.
Fork pull requests SHALL use the owner's Repository-admin bypass after the available free default lanes settle clean.

#### Scenario: Full cascade from one label

- **WHEN** the owner applies `review`
- **THEN** the cascade verifies completed Macroscope correctness evidence on the current head before it runs PR-Agent
- **AND** Runeseer adjudicates after PR-Agent completes its current-head review

#### Scenario: Optional lane does not participate

- **WHEN** Cursor or CodeRabbit does not review the pull request
- **THEN** the default funnel proceeds without treating that absence as approval
- **AND** `review/correctness` still requires a verdict on the current head

#### Scenario: Optional lane reports a finding

- **WHEN** a requested Cursor or CodeRabbit round reports a genuine finding
- **THEN** a fix or an explicit owner acceptance resolves the finding before merge

#### Scenario: Review round reuses current-head evidence

- **WHEN** the configured Macroscope correctness check completed with `success` or `neutral` on the current head
- **THEN** the cascade reuses that check and sends its findings to Runeseer without another Macroscope request

#### Scenario: Stage label removal preserves valid evidence

- **WHEN** the owner removes `stage:macroscope` while a qualifying completed check remains on the current head
- **THEN** the next cascade verifies and reuses that check

#### Scenario: Stage label cannot approve a changed head

- **WHEN** `stage:macroscope` remains after a head change without a qualifying completed check on the new head
- **THEN** the cascade waits for an existing current-head run or requests a new Macroscope review

#### Scenario: PR-Agent stage requires current-head evidence

- **WHEN** `stage:pr-agent` remains after a head change without a completed PR-Agent review on the new head
- **THEN** the cascade requests a PR-Agent review before Runeseer adjudicates

#### Scenario: PR-Agent round reuses current-head evidence

- **WHEN** PR-Agent completed its review on the current head and its findings are resolved
- **THEN** the cascade reuses that review without another PR-Agent request

#### Scenario: Push between rounds

- **WHEN** a pull request is pushed carrying no `review` or `review:` label
- **THEN** no paid lane runs for that push
- **AND** the previous head's verdict does not approve the new head
- **AND** the current head requires a fresh review request and a clean verdict before merge

#### Scenario: PR-Agent lane summoned alone

- **WHEN** the owner applies `review:pr-agent`
- **THEN** the lane runs one review call and posts its findings under the workflow token
- **AND** the lane consumes the request label
- **AND** the lane records `stage:pr-agent` when the findings resolve

## ADDED Requirements

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

### Requirement: Status Comment Upsert

A workflow-authored status comment MUST carry a header marker.
Later rounds MUST update the comment with that marker.
A lane MUST NOT post another status comment with the same marker on the pull request.

#### Scenario: Owner reminder repeats

- **WHEN** the dashboard sweep finds a pull request still waiting on the owner
- **THEN** the existing reminder updates its age instead of a second reminder appearing

#### Scenario: Autofix patch changes

- **WHEN** a later suggest run produces a different patch
- **THEN** the suggestion comment updates to the new patch
