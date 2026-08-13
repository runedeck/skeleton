## RENAMED Requirements

- FROM: `### Requirement: Three Review Lanes`
- TO: `### Requirement: Review Lanes`

## MODIFIED Requirements

### Requirement: Review Lanes

A lane that bills per run MUST run only inside a review funnel round. A review lane MUST NOT start from pull request lifecycle events alone; every round MUST start only when a maintainer applies a review label that requests the round. Bare `review` MUST run the full funnel, cursor, then macroscope, then pr-agent, then the adjudicating correctness lane, while each `review:` label MUST summon its single lane. A review label handled by this repository's workflows and applied while the pull request is draft MUST remain pending and MUST release when the pull request is marked ready. Removing such a label MUST cancel the in-flight round it requested. Each stage spends only after the previous stage settles clean, so paid stages run only on work every cheaper stage has passed. Cursor runs manually from the cascade's standalone `@cursor review` comment. PR-Agent runs one `review` call in command mode from a pinned image. Stages settle once per pull request: a settled stage is recorded as a `stage:` label and later rounds skip it, verifying only that its findings stay resolved, so fix rounds return straight to the adjudicator. The adjudicator's verdict MAY request a restart of an earlier stage when the accumulated delta is structurally large, and the owner restarts one by removing its stage label. Re-rounds judge only the range since the previous verdict. A terminal provider failure in any lane MUST stop immediately, clear the active review label, apply a persistent `issue:` blocked label, and refuse later review requests until the blocker is cleared or a successful current-head round proves recovery. The cascade (`review / cascade`) and the verdict mirror (`review/correctness`) MUST be required status checks, and the mirror MUST fail closed: a head with no verdict reports failure until a round completes. Fork pull requests, where the correctness lane cannot run, merge through the owner's Repository-admin bypass after the free lanes settle.

#### Scenario: Full cascade from one label

- **WHEN** the owner applies `review`
- **THEN** the lanes run in escalation order and `review/correctness` adjudicates last, after the other lanes settle clean on the head

#### Scenario: Fix round skips settled stages

- **WHEN** the owner re-summons after fixes and earlier stages carry their `stage:` labels with all their findings resolved
- **THEN** the cascade skips those stages without respending them and the adjudicator judges the delta since its previous verdict

#### Scenario: Restart of an earlier stage

- **WHEN** the adjudicator's verdict requests a restart, or the owner removes a `stage:` label
- **THEN** the next round re-runs that stage onward

#### Scenario: Push between rounds

- **WHEN** a pull request is pushed carrying no `review` or `review:` label
- **THEN** no paid lane runs for that push; the previous head's verdict remains behind, and the current head's required checks stay unsatisfied until a maintainer applies a review label, holding the merge closed

#### Scenario: PR-Agent lane summoned alone

- **WHEN** the owner applies `review:pr-agent`
- **THEN** the lane runs one review call, posts its findings under the workflow token, consumes the label, and records `stage:pr-agent` when the findings resolve

## ADDED Requirements

### Requirement: Lane Table

Every lane MUST be one row of the lane table: its summon, its settle signal, its finding source, and its labels. The cascade MUST iterate the table, and a new lane MUST add a row, never lane-specific shell.

#### Scenario: New lane joins

- **WHEN** a reviewer joins the funnel
- **THEN** its row provisions its labels, its summon, and its settle check without a change to the cascade logic

### Requirement: Status Comment Upsert

A workflow-authored status comment MUST carry a header marker and MUST update in place on later rounds. A lane MUST NOT post a second status comment while one with the same marker exists on the pull request.

#### Scenario: Owner reminder repeats

- **WHEN** the dashboard sweep finds a pull request still waiting on the owner
- **THEN** the existing reminder updates its age instead of a second reminder appearing

#### Scenario: Autofix patch changes

- **WHEN** a later suggest run produces a different patch
- **THEN** the suggestion comment updates to the new patch
