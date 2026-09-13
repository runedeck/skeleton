# Review Ceremony Specification

## Purpose

Nothing reaches `main` on one model's opinion. At least three vendor-diverse *agentic review lanes* examine each pull request in an ordered *review funnel*, so cross-harness and cross-model checks agree before a human enters the loop, last, when the change is demonstrably ready. The default funnel runs Macroscope, then Runeseer as the adjudicator. Cursor and CodeRabbit provide optional standalone reviews. A skipped optional review does not approve the pull request, and Runeseer still requires a verdict on the current head. An application opens every pull request so the sole human's approval counts.

This capability holds the ceremony's shape: who opens and who vetoes, how a verdict earns approval, and how review spend stays proportional. The lanes themselves are in `review-lanes`, their request labels in `review-requests`, their dashboard state in `lane-configuration`, the deterministic checks in `merge-checks`, and the signed release path in `release-ceremony`. After code merges, the drift review compares the canonical documents under `docs/specs/` with the merged tree and reports any requirement that now describes behavior the tree no longer has.

## Requirements

### Requirement: Owner-Opened Pull Requests

The owner MUST author every ceremony pull request, ghostwritten by the orchestrating agent with a short summary and pushed under the owner's credentials, and the `runewright` app MUST post the full ceremony body as the first comment. The app acts only server-side, from workflow-minted tokens. No local key ceremony is required to move work.

*Rationale:* owner authorship is currently the only way to summon the hosted review bots without a Cursor team subscription. Individual-tier Bugbot reviews only the account owner's pull requests.

#### Scenario: Ghostwritten pull request

- **WHEN** an agent finishes a ceremony branch
- **THEN** the pull request opens under the owner's authorship with a short summary, and the app comments the plan, changes, and testing record

#### Scenario: Application privileges

- **WHEN** the app authenticates
- **THEN** it holds contents, pull-request, and issue write only, and it bypasses no branch rule

### Requirement: Owner Veto

Work authored by anyone other than the owner MUST require the owner's code-owner review before merging, while the owner's own pull requests MUST merge on the owner's action alone, with every required check binding both cases.

#### Scenario: Another contributor's pull request

- **WHEN** a pull request is authored by anyone other than the owner
- **THEN** `CODEOWNERS` routes required review to the owner and the merge waits for the owner's approval

#### Scenario: The owner's own pull request

- **WHEN** the owner authors a pull request
- **THEN** it merges on the owner's action without an approval object, through a bypass scoped to the review rules only

#### Scenario: Checks bind everyone

- **WHEN** any same-repository pull request fails a required check
- **THEN** the merge is refused regardless of who authored it. The review ruleset grants its admin bypass to the owner as an actor, and the ceremony reserves its use for fork pull requests, where the correctness lane stands down on the same-repository guard and produces no verdict

### Requirement: Earned Approval

A clean correctness verdict on a pull request whose review was requested MUST become the reviewer identity's approving review, and any later push MUST dismiss it until a clean re-review re-grants it. The verdict MUST be recorded machine-readably with a finding count of zero, bound to the commit id it judged, and approval MUST fire only when the bound id is the live current head.

#### Scenario: Clean verdict approves

- **WHEN** `review/correctness` posts a verdict of clean after a review label requests a round
- **THEN** the reviewer identity submits an approving review satisfying the required approval

#### Scenario: Push dismisses

- **WHEN** any commit lands after the approval
- **THEN** the approval is dismissed and returns only after a clean re-review

### Requirement: Review Economy

Reviews MUST spend proportionally to what changed: the correctness lane stands down on prose-only diffs, re-reviews judge only the range since the last recorded verdict without re-reporting its findings, low-severity notes collect into a digest rather than inline threads, and pull requests open as drafts until the tree is stable.

#### Scenario: Prose-only change

- **WHEN** a pull request touches only markdown outside the specifications and the machinery
- **THEN** the correctness lane stands down without spend and its check reports green

#### Scenario: Re-review after fixes

- **WHEN** a round already recorded a verdict for an ancestor of the head
- **THEN** the re-review judges the range since that ancestor and does not re-report the recorded findings

### Requirement: Finding Resolution

A fix commit MAY name the review thread it answers with a `Resolves-Thread:` trailer whose value is the finding comment's URL, its numeric comment id, or the thread's node id, and the named threads MUST resolve automatically when the commit is pushed. A trailer MUST resolve only threads on its own pull request.

#### Scenario: Trailer resolves thread

- **WHEN** a pushed commit carries `Resolves-Thread:` naming a thread on its pull request
- **THEN** that thread is resolved and the resolution traces to the commit
