# Review Requests Specification

## Purpose

How a maintainer asks for a review round and takes one back: the request labels, their behavior on drafts, and the `skip:` and `ignore:` overrides that stand a lane down or withdraw its hold on the merge.

## Requirements

### Requirement: Draft Exemption

A review lane MUST NOT run on drafts.
Draft iteration and unlabeled pushes MUST remain free.
The repository handles `review`, `review:runeseer`, `review:cursor`, and `review:autofix` request labels.
These requests MUST wait while the pull request remains a draft.
They MUST start when the pull request becomes ready.
Removing a pending request MUST prevent dispatch.
Removing a dispatched `review` or `review:cursor` label MUST preserve the active round.
The Cursor workflow MUST consume `review:cursor` after the summon succeeds.
Cursor MUST control the posted review through its app trigger.
The Macroscope app MUST control `review:macroscope` through its own trigger.
The cascade MUST apply that label only to a ready pull request.
Readiness without a request label MUST NOT start a lane.

The `skip:<lane>` and `ignore:<lane>` labels MUST act as overrides, not round requests.
An override MUST neither start nor cancel a round.
The `skip:<lane>` label MUST prevent that lane from running, reporting findings, or spending money.
The `ignore:<lane>` label MUST preserve the lane's full report while releasing its findings from the merge hold.
Both overrides MUST clear the lane's required mirror check.
The correctness mirror MUST record owner acceptance through an approving review when `ignore:runeseer` accompanies a verdict on the judged head.
This acceptance MUST satisfy the review requirement without a ruleset bypass.
The mirror MUST NOT approve a head the lane never judged.
A terminal default-lane failure MUST still fail the cascade under `ignore:<lane>`.
A failed provider does not establish a completed review.
A round MUST consist of one cascade.
The cascade MUST consume `review` after it dispatches the correctness round.
The correctness lane MUST consume its own request label when its round ends.
The next round MUST require a fresh `review` label.

#### Scenario: Draft iteration

- **WHEN** an agent pushes repeatedly to a draft pull request
- **THEN** no review lane runs for those pushes

#### Scenario: Marked ready with a pending review request

- **WHEN** a draft pull request carrying `review` is marked ready for review
- **THEN** the cascade runs once in escalation order, answering the maintainer-applied label

#### Scenario: Marked ready without a review request

- **WHEN** a draft pull request carrying no `review` or `review:` label is marked ready for review
- **THEN** no review lane starts

#### Scenario: Reopened pull request

- **WHEN** a pull request reopens without a fresh maintainer-applied review label
- **THEN** no review lane starts on the current head

#### Scenario: Pending review request removed

- **WHEN** the maintainer removes `review` or `review:cursor` before dispatch
- **THEN** the workflow prevents the pending dispatch and starts no new lane

#### Scenario: Dispatched review request removed

- **WHEN** `review` or `review:cursor` is removed after successful dispatch
- **THEN** the active round continues and the removal starts no new lane

#### Scenario: Review request consumed

- **WHEN** the correctness lane's round ends
- **THEN** the review labels are removed, and a later push summons nothing until a fresh label lands
