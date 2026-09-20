# Review Ceremony Specification

## Purpose

Nothing reaches `main` on one model's opinion, and nothing carries the owner's name without the owner's key. Free *agentic review lanes* examine every push and fill a *ledger* the ceremony owns. The paid adjudicator, Runeseer, runs only after the owner marks the pull request ready with an *open-seal*, and only when a deterministic triage says a second opinion is worth its cost. Every thread from every lane ends in a recorded disposition. The owner's second key touch, the *merge-seal*, is what the ruleset requires before merge. Every lane is a vendor product that can be switched off on any day. The ledger, the seals, and the ruleset are not.

This capability holds the ceremony's shape: who opens and who readies, how a verdict earns approval, and how the ledger tracks coverage. The paid-review budget and triage are in `paid-review-economy`, the lanes in `agentic-review-lanes`, their request labels and the triage in `review-round-requests`, their dashboard state in `external-lane-configuration`, the deterministic checks in `deterministic-merge-checks`, and the seals and the signed release path in `owner-release-ceremony`. After code merges, the drift review compares the canonical documents under `docs/specs/` with the merged tree and reports any requirement that now describes behavior the tree no longer has.

## Requirements

### Requirement: Draft by the App, Ready by the Owner

A ceremony pull request MUST open as a draft under the `runewright` app identity on the first push of a branch that passes the deterministic checks, with the ceremony body the session agent wrote. It MUST become ready, and enter the owner's name, only through `rune sign open`, which signs an open-seal with the owner's hardware key and flips the draft.

#### Scenario: First push opens a draft

- **WHEN** an agent pushes a ceremony branch and the deterministic checks pass
- **THEN** the app opens a draft pull request with the agent's ceremony body, and no review lane runs

#### Scenario: Owner readies with a seal

- **WHEN** the owner runs `rune sign open` on the branch and touches the key
- **THEN** an open-seal commit is written beneath the head, the draft becomes ready, and the pull request enters the owner's name

### Requirement: No Ready Without a Seal

No other identity MUST flip a draft to ready. A ready pull request whose head has no valid open-seal beneath it MUST fail the `owner-seal` check regardless of which account the platform records as the author.

#### Scenario: Ready without a seal

- **WHEN** a pull request is marked ready by any path other than `rune sign open`
- **THEN** `owner-seal` fails and the merge is refused until a valid open-seal exists

#### Scenario: Agent may not ready

- **WHEN** an agent attempts to mark a draft ready, close a pull request, or merge one
- **THEN** the action is refused by the rule the agent carries and, for ready, by the missing seal

### Requirement: App Identity Scope

The app MUST act only server-side, from workflow-minted tokens, and holds contents, pull-request, and issue write only. It bypasses no branch rule.

*Rationale:* a pull request in the owner's name is an attestation, and an attestation needs the key. Opening the draft under the app lets the free lanes and the deterministic checks run from the first push without a touch. The individual-tier Cursor restriction to owner-authored pull requests is a lane-configuration fact the canary MUST prove or disprove, not a reason to put the owner's name on an unsealed draft.

#### Scenario: App token scope

- **WHEN** a workflow mints the app token to open or update a draft
- **THEN** the token carries contents, pull-request, and issue write only, and no branch rule is bypassed

### Requirement: Owner Veto

Work authored by anyone other than the owner MUST require the owner's code-owner review before merging, while the owner's own pull requests MUST merge on the owner's action alone, with every required check binding both cases. An outside pull request MUST be admitted to the ceremony only through `rune sign adopt`, which seals a copy of its head onto an owner-controlled branch.

#### Scenario: Another contributor's pull request

- **WHEN** a pull request is authored by anyone other than the owner
- **THEN** `CODEOWNERS` routes required review to the owner, no metered lane runs on it, and the merge waits for adoption and the owner's approval

#### Scenario: The owner's own pull request

- **WHEN** the owner authors or readies a pull request
- **THEN** it merges on the owner's action without an approval object, through a bypass scoped to the review rules only

#### Scenario: Checks bind everyone

- **WHEN** any same-repository pull request fails a required check
- **THEN** the merge is refused regardless of who authored it

### Requirement: Ledger

The ceremony MUST keep one ledger per pull request, owned by the controller workflow and never by a vendor lane. For each head the ledger MUST record `reviewed_sha`, a `generation` counter, a status for every lane the configuration expects (`completed`, `completed-no-findings`, `skipped`, `ineligible`, `failed`, `rate-limited`, or `pending`), and every review thread on the head with its disposition.

#### Scenario: Lane reports without findings

- **WHEN** a lane's check run completes on the head and posts no thread
- **THEN** the ledger records `completed-no-findings` for that lane, distinct from `skipped`

### Requirement: Ledger Thread Sources

Threads MUST be read from the platform API by lane login. The platform's resolved flag MUST NOT be a source. A thread from a login the lane table does not name MUST be kept for disposition and MUST grant no approval authority. Any new thread or lane status change MUST increment the generation. The lane table, `KEYS`, and the verifier MUST be read from the protected default branch, never from the candidate tree.

#### Scenario: Late thread

- **WHEN** a lane posts a thread after a verdict was recorded for the head
- **THEN** the generation increments, the standing approval and any queue entry for the previous generation become stale, and one more adjudication is permitted on the same head

#### Scenario: Unknown reviewer

- **WHEN** a review thread arrives from a login absent from the lane table
- **THEN** the thread enters the ledger for disposition and the ledger records no lane status for it

### Requirement: Earned Approval

A clean correctness verdict MUST become the reviewer identity's approving review, bound to `(reviewed_sha, generation)`. The verdict MUST list every open thread the ledger holds for that head with a disposition of `fixed`, `rejected` with a stated reason, or `owner`. A verdict that reports clean while any ledger thread lacks a disposition MUST fail the `review/correctness` check as a lane fault. Any later push, and any generation increment, MUST dismiss the approval until a clean re-adjudication re-grants it.

#### Scenario: Clean verdict approves

- **WHEN** `review/correctness` records a clean verdict with every ledger thread disposed
- **THEN** the reviewer identity submits an approving review bound to the head and generation

#### Scenario: Clean with an undisposed thread

- **WHEN** the verdict reports clean and the ledger holds a thread with no disposition
- **THEN** the check fails, naming the thread

#### Scenario: Push dismisses

- **WHEN** any commit is pushed after the approval
- **THEN** the approval is dismissed and returns only after a clean re-adjudication

### Requirement: Coverage Without the Paid Lane

When Runeseer is off or stands down, the check MUST report the ledger's coverage state, `free lanes only` with the reason, and MUST NOT report clean.

#### Scenario: Paid lane off

- **WHEN** Runeseer is disabled or the triage stands it down
- **THEN** the check reports green with the coverage state `free lanes only` and its reason, and the ledger records the lane as `skipped`

### Requirement: Finding Resolution

Only the reviewer identity MUST resolve review threads, acting on the verdict's disposition list through the resolver workflow. Threads listed `fixed` are resolved. Threads listed `rejected` or `owner` stay open. The owner MAY resolve by hand. An agent MUST NOT resolve a thread or comment on a pull request. A fix commit MAY name the thread it answers with a `Resolves-Thread:` trailer. The trailer MUST be bookkeeping for the verdict and MUST NOT narrow the range a review judges.

#### Scenario: Verdict lists fixed

- **WHEN** the verdict lists a thread as `fixed` and the resolver runs
- **THEN** that thread is resolved and the resolution traces to the verdict

#### Scenario: Trailer names a thread

- **WHEN** a pushed commit carries `Resolves-Thread:` naming a thread on its pull request
- **THEN** the verdict may cite the commit as the fix, and the review still judges the full range since the last verdict

### Requirement: Lane Independence

No vendor lane MUST be named as required in the ruleset. The required checks are the deterministic checks, `owner-seal`, and the controller's `review/correctness`. The ledger, the seals, and the ruleset MUST function with any lane off, and every expected lane MUST have a recorded status on every head. Adding or removing a lane MUST be one row in the lane table on the protected branch.

#### Scenario: Every lane off

- **WHEN** no vendor lane reports on a head
- **THEN** the ledger records each expected lane as `skipped` or `ineligible`, the check reports `free lanes only`, and the merge still requires both seals

#### Scenario: Lane removed

- **WHEN** a lane's row is removed from the lane table
- **THEN** the ledger stops expecting it and no requirement elsewhere changes
