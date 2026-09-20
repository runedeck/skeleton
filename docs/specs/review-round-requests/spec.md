# Review Requests Specification

## Purpose

How a review round starts and how a maintainer stands a lane down: the ready event as the automatic request, the controller's triage, the request labels the owner may still apply to force a round, and the `skip:` and `ignore:` overrides that stand a lane down or withdraw its hold on the merge.

## Requirements

### Requirement: Ready Starts the Funnel

A review lane MUST NOT run on drafts.
Draft iteration MUST remain free of paid review.
The free lanes and the deterministic checks MUST run on every push to a draft and record their results in the ledger.
The ready event MUST be the automatic review request.
The controller MUST start the funnel when a pull request becomes ready with a valid open-seal, and on each later green head, after its triage admits the head.
An agent MUST NOT apply a review label.

#### Scenario: Draft iteration

- **WHEN** an agent pushes repeatedly to a draft pull request
- **THEN** the free lanes and deterministic checks run and fill the ledger, and no paid lane runs

#### Scenario: Marked ready with a seal

- **WHEN** `rune sign open` flips a draft ready with a valid open-seal
- **THEN** the controller triages the head and, when admitted, runs the cascade once in escalation order

#### Scenario: Marked ready without a seal

- **WHEN** a draft is marked ready by any path other than `rune sign open`
- **THEN** no paid lane starts and `owner-seal` fails on the head

#### Scenario: Reopened pull request

- **WHEN** a pull request reopens
- **THEN** the controller treats the current head as a green head and applies the triage before any paid lane starts

### Requirement: Owner Review Labels

The owner MAY apply `review`, `review:runeseer`, `review:cursor`, or `review:autofix` to force a round the triage would have stood down.
A forced round MUST still count against the work item's paid budget.
These labels MUST wait while the pull request remains a draft and MUST start when it becomes ready.
Removing a pending request MUST prevent dispatch.
Removing a dispatched `review` or `review:cursor` label MUST preserve the active round.

#### Scenario: Pending review request removed

- **WHEN** the maintainer removes `review` or `review:cursor` before dispatch
- **THEN** the workflow prevents the pending dispatch and starts no new lane

#### Scenario: Dispatched review request removed

- **WHEN** `review` or `review:cursor` is removed after successful dispatch
- **THEN** the active round continues and the removal starts no new lane

#### Scenario: Owner forces a round

- **WHEN** the owner applies `review:runeseer` to a ready head the triage stood down
- **THEN** the lane runs on that head and the work item's paid budget decreases by one

### Requirement: App-Controlled Lane Labels

The Cursor workflow MUST consume `review:cursor` after the summon succeeds.
Cursor MUST control the posted review through its app trigger.
The Macroscope app MUST control `review:macroscope` through its own trigger.
The cascade MUST apply that label only to a ready pull request.

#### Scenario: Cursor request consumed by its summon

- **WHEN** the Cursor summon succeeds
- **THEN** the workflow removes `review:cursor` and Cursor's app trigger controls the posted review

### Requirement: Lane Override Labels

The `skip:<lane>` and `ignore:<lane>` labels MUST act as overrides, not round requests.
An override MUST neither start nor cancel a round.
The `skip:<lane>` label MUST prevent that lane from running, reporting findings, or spending money, and the ledger MUST record the lane as `skipped`.
The `ignore:<lane>` label MUST preserve the lane's full report while releasing its findings from the merge hold, and MUST NOT apply to a finding the verdict rates critical.
Both overrides MUST clear the lane's required mirror check.

#### Scenario: Lane skipped by override

- **WHEN** the owner applies `skip:<lane>` to a pull request
- **THEN** that lane does not run, reports nothing, spends nothing, and the ledger records it as `skipped`

### Requirement: Owner Acceptance Through Ignore

The correctness mirror MUST record owner acceptance through an approving review when `ignore:runeseer` accompanies a verdict on the judged head and generation.
This acceptance MUST satisfy the review requirement without a ruleset bypass.
The mirror MUST NOT approve a head the lane never judged.
A terminal default-lane failure MUST still fail the cascade under `ignore:<lane>`.
A failed provider does not establish a completed review.

#### Scenario: Ignored finding released from the hold

- **WHEN** `ignore:runeseer` accompanies a verdict on the judged head and generation
- **THEN** the mirror records an approving review and the non-critical findings no longer hold the merge

### Requirement: Round Consumption

A round MUST consist of one cascade.
The cascade MUST consume `review` after it dispatches the correctness round.
The correctness lane MUST consume its own request label when its round ends.

#### Scenario: Review request consumed

- **WHEN** the correctness lane's round ends
- **THEN** the review labels are removed, and the next green head goes through the triage again
