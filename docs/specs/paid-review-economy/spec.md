# Paid Review Economy Specification

## Purpose

How paid review spends: the controller invites the correctness lane after a deterministic triage, the triage stands it down on prose-only diffs and exhausted budgets, and each round binds to one head and generation. Split from `sealed-review-ceremony` on 2026-09-20.

## Requirements

### Requirement: Review Economy

Paid review MUST spend proportionally and within a bound. The correctness lane MUST be invited by the controller on the ready event and on each later green head, never by an agent, and only after a deterministic triage. A work item is the change identifier the pull request names, or the pull request itself when none.

#### Scenario: Controller invites the lane

- **WHEN** a pull request becomes ready with a valid open-seal, or a later green head appears
- **THEN** the controller runs the triage and invites the correctness lane only when the triage admits the head

### Requirement: Triage Stand-Down

The triage MUST stand the lane down on a diff since the last verdict that touches only prose outside the specifications, the runes, the harness instruction paths, and the workflows. It stops when the work item has spent three paid rounds. It stops when the comment or thread count on the head exceeds the lane configuration.

#### Scenario: Prose-only change

- **WHEN** the diff since the last verdict touches only markdown outside the specifications, the runes, the harness instruction paths, and the workflows
- **THEN** the correctness lane stands down without spend, the check reports `free lanes only`, and the head may still enter the signing queue

#### Scenario: Budget exhausted

- **WHEN** a work item has spent three paid rounds
- **THEN** the controller refuses a fourth, posts one owner-facing line, and the pull request waits for the owner

### Requirement: Round Binding and Re-review

A round MUST bind to `(reviewed_sha, generation)` and MUST be voided by a push during the round. Re-reviews MUST judge the range since the last recorded verdict without re-reporting its findings. Free lanes and Cursor Security MUST be accounted separately from this budget under their own caps. Low-severity notes MUST collect into a digest rather than inline threads.

#### Scenario: Push during a round

- **WHEN** a commit is pushed to the head while a round is running
- **THEN** the round is voided and its verdict, if any, is discarded

#### Scenario: Re-review after fixes

- **WHEN** a round already recorded a verdict for an ancestor of the head
- **THEN** the re-review judges the range since that ancestor and does not re-report the recorded findings
