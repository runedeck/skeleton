# Lane Configuration Specification

## Purpose

The dashboard state of externally hosted lanes is ceremony configuration. This capability records the required state per lane, so a misconfigured lane is a ceremony defect even when no repository file changes.

## Requirements

### Requirement: External Lane Configuration

The dashboard state of externally hosted lanes MUST form part of the ceremony configuration.
Optional Cursor reviews MUST use a standalone `@cursor review` comment.
Cursor MUST enable incremental review and disable draft reviews and autofix.
Optional CodeRabbit reviews MUST use the organization-defined `review:coderabbit` request label.
The repository MUST provision that label without applying it to pull requests.
The repository and base template MUST preserve inherited CodeRabbit review settings.
They MUST disable CodeRabbit review-status messages without suppressing findings.
The adjudicator MUST attribute requested CodeRabbit findings to their provider and source thread.
Macroscope MUST review only after a `review:macroscope` request.
Macroscope MUST disable draft reviews and auto-merge.
Its approvability approval MUST remain advisory beneath the required verdict checks.
Macroscope MUST honor `skip:macroscope`, which skips only that stage.
The cascade MUST retain Runeseer adjudication and the required verdict mirror.
The configuration guide MUST record the required state.
A misconfigured lane MUST remain a ceremony defect even when repository files do not change.

#### Scenario: Review products share an app identity

- **WHEN** Cursor Security Agent or Macroscope Approvability completes a check
- **THEN** the pipeline records that product without counting it as Bugbot or Macroscope correctness review

#### Scenario: Macroscope correctness identity is absent

- **WHEN** the repository variable `MACROSCOPE_CORRECTNESS_CHECK` is empty
- **THEN** the cascade reports a configuration error instead of accepting an arbitrary Macroscope check

#### Scenario: Optional review findings reach adjudication

- **WHEN** a requested CodeRabbit review reports findings
- **THEN** Runeseer receives the findings with their provider identity and source thread

#### Scenario: Ambient reviewer detected

- **WHEN** a lane reviews outside its sanctioned trigger or reviews a draft
- **THEN** the lane's dashboard configuration is corrected before the next round is summoned

#### Scenario: Adjudicated finding blocks a merge

- **WHEN** Runeseer records an unresolved finding in its current-head verdict
- **THEN** `review/correctness` blocks the merge until a clean verdict or the specified owner acceptance clears the finding

#### Scenario: Provider findings reach adjudication

- **WHEN** Macroscope correctness completes with `neutral` on the current head
- **THEN** Runeseer adjudicates its findings before the review check can approve the head

#### Scenario: Default reviewer unavailable

- **WHEN** Macroscope reports a terminal provider failure
- **THEN** the cascade stops immediately, preserves an undelivered request, applies its blocked label without another cascade event, and refuses requests until recovery

#### Scenario: Optional reviewer unavailable

- **WHEN** Cursor or CodeRabbit reports a terminal provider failure
- **THEN** its failure remains visible without blocking the default funnel or replacing Runeseer's required verdict

#### Scenario: CodeRabbit skips an unrequested review

- **WHEN** the inherited label policy excludes a pull request from CodeRabbit review
- **THEN** CodeRabbit posts no review-status message
- **AND** the configuration preserves the inherited request policy and finding reports

#### Scenario: Correctness lane scope

- **WHEN** the owner summons the correctness lane on any same-repository, non-draft pull request
- **THEN** the lane runs regardless of author. Spend is bounded to one round per cascade, and the owner must summon each further round deliberately

#### Scenario: Fork pull request

- **WHEN** a pull request comes from a fork
- **THEN** the correctness lane stands down because its caller and its body each refuse fork heads before any secret-bearing step, the ordered workflow stops after the free lanes, and the pull request merges through the owner's Repository-admin bypass once those lanes settle clean

#### Scenario: Instructions read from the base branch

- **WHEN** a pull request modifies reviewer instructions in its own head commit
- **THEN** the lanes still load the instructions from the base branch
