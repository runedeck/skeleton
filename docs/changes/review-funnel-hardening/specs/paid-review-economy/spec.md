## MODIFIED Requirements

### Requirement: Review Economy

Paid review MUST spend proportionally and within a bound. The correctness lane MUST be invited by the controller on a green head, never by an agent, and only after a deterministic triage. A green head reaches the controller through the consumer's `workflow_run` event when the required checks complete, and through a bounded poll after a push. A work item is the change identifier the pull request names, or the pull request itself when none.

#### Scenario: Controller invites the lane

- **WHEN** a pull request becomes ready with a valid open-seal, or a later green head appears
- **THEN** the controller runs the triage and invites the correctness lane only when the triage admits the head

#### Scenario: Green head after the poll window

- **WHEN** a head's required checks turn green after the controller's poll window closed
- **THEN** the consumer's `workflow_run` event re-enters the controller and the triage runs on that head

### Requirement: Round Binding and Re-review

A round MUST bind to `(reviewed_sha, generation)` and MUST be voided by a push to the head during the round. A move of the base MUST NOT void a round. The ledger MUST record the base the round saw. Re-reviews MUST judge the range after the last recorded verdict without re-reporting its findings. Free lanes and Cursor Security MUST be accounted separately from this budget under their own caps. Low-severity notes MUST collect into a digest rather than inline threads.

#### Scenario: Push during a round

- **WHEN** a commit is pushed to the head while a round is running
- **THEN** the round is voided and its verdict, if any, is discarded

#### Scenario: Re-review after fixes

- **WHEN** a round already recorded a verdict for an ancestor of the head
- **THEN** the re-review judges the range after that ancestor and does not re-report the recorded findings

#### Scenario: Base moves during a round

- **WHEN** `main` advances while a round is running and the head is unchanged
- **THEN** the round completes, its verdict posts against `(reviewed_sha, generation)`, and the ledger records the new base

## ADDED Requirements

### Requirement: Attempt Accounting

The budget MUST count a round when the lane calls the model. An attempt that stops before the model call MUST NOT count against the round budget. Attempts per work item MUST stop at twice the round budget. A base-reset MUST reset the free-lane stages and continue into triage in the same run, and MUST NOT consume a review label it did not act on.

#### Scenario: Attempt stops before the model

- **WHEN** an attempt stops in triage or on a configuration fault before the model is called
- **THEN** the round budget is unchanged and the attempt counter increments

#### Scenario: Attempt cap reached

- **WHEN** a work item reaches twice its round budget in attempts
- **THEN** the controller stops the lane, posts one owner-facing line, and waits for the owner

#### Scenario: Base-reset on entry

- **WHEN** the controller enters on a head whose newest ledger records another base
- **THEN** it resets the free-lane stages, keeps the labels, and runs the triage in the same run
