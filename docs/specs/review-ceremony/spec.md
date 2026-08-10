# Review Ceremony Specification

## Purpose

Nothing reaches `main` on one opinion. An application opens every pull request so the sole human's approval counts. Three vendor-diverse automated reviewers, called review lanes, examine each pull request in an ordered workflow called the review funnel; each lane reports a blocking check run, and later lanes start only after earlier lanes settle clean. Deterministic checks stay independent of them, secret scanning is scoped to what a push introduces, specifications bind to protected paths, and releases are sealed by an owner-signed tag. After code merges, the drift review compares the canonical documents under `docs/specs/` with the merged tree and reports any requirement that now describes behavior the tree no longer has.

## Requirements

### Requirement: Owner-Opened Pull Requests

The owner MUST author every ceremony pull request, ghostwritten by the orchestrating agent with a short summary and pushed under the owner's credentials, and the `runewright` app SHALL post the full ceremony body as the first comment. The app acts only server-side, from workflow-minted tokens; no local key ceremony is required to move work.

*Rationale:* owner authorship is currently the only way to summon the hosted review bots without a Cursor team subscription; individual-tier Bugbot reviews only the account owner's pull requests.

#### Scenario: Ghostwritten pull request

- **WHEN** an agent finishes a ceremony branch
- **THEN** the pull request opens under the owner's authorship with a short summary, and the app comments the plan, changes, and testing record

#### Scenario: Application privileges

- **WHEN** the app authenticates
- **THEN** it holds contents, pull-request, and issue write only, and it bypasses no branch rule

### Requirement: Owner Veto

Work authored by anyone other than the owner SHALL require the owner's code-owner review before merging, while the owner's own pull requests SHALL merge on the owner's action alone, with every required check binding both cases.

#### Scenario: Another contributor's pull request

- **WHEN** a pull request is authored by anyone other than the owner
- **THEN** `CODEOWNERS` routes required review to the owner and the merge waits for the owner's approval

#### Scenario: The owner's own pull request

- **WHEN** the owner authors a pull request
- **THEN** it merges on the owner's action without an approval object, through a bypass scoped to the review rules only

#### Scenario: Checks bind everyone

- **WHEN** any same-repository pull request fails a required check
- **THEN** the merge is refused regardless of who authored it; the review ruleset grants its admin bypass to the owner as an actor, and the ceremony reserves its use for fork pull requests, where the correctness lane stands down on the same-repository guard and produces no verdict

### Requirement: Three Review Lanes

A lane that bills per run MUST run only inside a review funnel round. A review lane MUST NOT start from pull request lifecycle events alone; every round MUST start only when a maintainer applies a review label that requests the round. Bare `review` MUST run the full funnel, cursor, then macroscope, then the adjudicating correctness lane, while each `review:` label MUST summon its single lane. A review label handled by this repository's workflows and applied while the pull request is draft MUST remain pending and MUST release when the pull request is marked ready. Removing such a label MUST cancel the in-flight round it requested. Each stage spends only after the previous stage settles clean, so paid stages run only on work every cheaper stage has passed. Cursor runs manually from the cascade's standalone `@cursor review` comment. Stages settle once per pull request: a settled stage is recorded as a `stage:` label and later rounds skip it, verifying only that its findings stay resolved, so fix rounds return straight to the adjudicator. The adjudicator's verdict MAY request a restart of an earlier stage when the accumulated delta is structurally large, and the owner restarts one by removing its stage label. Re-rounds judge only the range since the previous verdict. A terminal provider failure in any lane MUST stop immediately, clear the active review label, apply a persistent `issue:` blocked label, and refuse later review requests until the blocker is cleared or a successful current-head round proves recovery. The cascade (`review / cascade`) and the verdict mirror (`review/correctness`) SHALL be required status checks, and the mirror SHALL fail closed: a head with no verdict reports failure until a round completes. Fork pull requests, where the correctness lane cannot run, merge through the owner's Repository-admin bypass after the free lanes settle.

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

### Requirement: External Lane Configuration

The dashboard state of externally hosted lanes is ceremony configuration: Cursor MUST run manually from a standalone `@cursor review` comment with incremental review enabled, draft reviews off, and autofix off; Macroscope MUST review only by its stage label with draft review and auto-merge off, its approvability approval advisory beneath the required verdict checks, and honoring `skip:macroscope`, which stands down only that stage. The cascade still delivers the adjudication, so the required verdict mirror clears normally. The configuration guide records the full required state, and a misconfigured lane is a ceremony defect even though no repository file changes.

#### Scenario: Ambient reviewer detected

- **WHEN** a lane reviews outside its sanctioned trigger or reviews a draft
- **THEN** the lane's dashboard configuration is corrected before the next round is summoned

#### Scenario: Lane blocks a merge

- **WHEN** a lane reports a blocking finding
- **THEN** its check fails and `main` refuses the merge until the finding is resolved

#### Scenario: Reviewer unavailable

- **WHEN** cursor or macroscope reports a terminal provider failure
- **THEN** the cascade stops immediately, clears that lane's review label, applies its blocked label without triggering another cascade, and refuses later review requests until recovery

#### Scenario: Correctness lane scope

- **WHEN** the owner summons the correctness lane on any same-repository, non-draft pull request
- **THEN** the lane runs regardless of author; spend is bounded to one round per cascade, and the owner must summon each further round deliberately

#### Scenario: Fork pull request

- **WHEN** a pull request comes from a fork
- **THEN** the correctness lane stands down because its caller and its body each refuse fork heads before any secret-bearing step, the ordered workflow stops after the free lanes, and the pull request merges through the owner's Repository-admin bypass once those lanes settle clean

#### Scenario: Instructions read from the base branch

- **WHEN** a pull request modifies reviewer instructions in its own head commit
- **THEN** the lanes still load the instructions from the base branch

### Requirement: Draft Exemption

A review lane SHALL NOT run on drafts; draft iteration and unlabeled pushes are free. The lane-request labels this repository's own workflows answer, `review`, `review:runeseer`, and `review:autofix`, SHALL all wait when applied to a draft, release when the pull request becomes ready, and cancel their requested in-flight round when removed. The Macroscope app answers `review:macroscope` on its own trigger, which no workflow here controls; the cascade applies that label only to a ready pull request, and that is what keeps drafts free of it. Readiness without one of those labels MUST NOT start a lane. The owner override labels `skip:<lane>` and `ignore:<lane>` are overrides rather than lane requests, so they neither start nor cancel a round. `skip:<lane>` MUST prevent that lane from running at all, so it produces no finding and spends nothing. `ignore:<lane>` MUST let the lane run and report in full, and MUST withdraw only the power of its findings to hold the merge, so its record stays on the pull request. Both MUST clear that lane's required mirror check, and a terminal provider failure MUST still fail the cascade under `ignore:<lane>`, since a broken lane is not a judged one. A round is one cascade: the correctness lane consumes the lane-request labels when its round ends, and the next round starts with a fresh `review` label.

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

#### Scenario: Review request removed

- **WHEN** the maintainer removes a review label during the round it requested
- **THEN** that round is canceled and the removal starts no lane

#### Scenario: Review request consumed

- **WHEN** the correctness lane's round ends
- **THEN** the review labels are removed, and a later push summons nothing until a fresh label lands

### Requirement: Deterministic Checks Independent of Review

The tests, lint, secret scan, schema validation, authorship, and specification checks SHALL be required independently of the review lanes, and a passing review SHALL NOT substitute for any of them.

#### Scenario: Review passes while a test fails

- **WHEN** every review lane passes and a test job fails
- **THEN** `main` refuses the merge

### Requirement: Range-Scoped Secret Scanning

Secret scanning SHALL examine only the commits a push or pull request introduces, resolved as an explicit commit range; a full-history scan SHALL run on a schedule, not per push or pull request.

#### Scenario: Pull-request scan

- **WHEN** the secret scan runs on a pull request
- **THEN** it scans from the merge base to the head commit and no earlier history

#### Scenario: Pre-push scan

- **WHEN** the pre-push hook receives a ref update for an existing remote branch
- **THEN** it scans from the remote commit to the local commit

#### Scenario: New branch push

- **WHEN** the pushed ref does not exist on the remote
- **THEN** the hook scans from the merge base with the default branch to the local commit

#### Scenario: Scheduled full scan

- **WHEN** the scheduled scan fires
- **THEN** it scans the full history, and no per-push or per-pull-request scan does

### Requirement: Specification Presence on Protected Paths

A pull request touching protected paths SHALL either carry a specification change or a `spec:none` label with a stated reason in the body.

#### Scenario: Protected path with a specification

- **WHEN** a pull request modifies a protected path and includes a specification change
- **THEN** the specification check passes

#### Scenario: Protected path without either

- **WHEN** a pull request modifies a protected path with no specification change and no `spec:none` label
- **THEN** the specification check fails

#### Scenario: Unprotected path

- **WHEN** a pull request touches only files outside the protected paths
- **THEN** the specification check passes without requiring a specification change

### Requirement: Earned Approval

A clean correctness verdict on a pull request whose review was requested SHALL become the reviewer identity's approving review, and any later push SHALL dismiss it until a clean re-review re-grants it. The verdict SHALL be recorded machine-readably with a finding count of zero, bound to the commit id it judged, and approval SHALL fire only when the bound id is the live current head.

#### Scenario: Clean verdict approves

- **WHEN** `review/correctness` posts a verdict of clean after a review label requests a round
- **THEN** the reviewer identity submits an approving review satisfying the required approval

#### Scenario: Push dismisses

- **WHEN** any commit lands after the approval
- **THEN** the approval is dismissed and returns only after a clean re-review

### Requirement: Owner Attestation on Tags

The owner's hardware key SHALL enter the ceremony at tags, not merges: release and checkpoint tags are annotated and owner-signed, a signed tag vouches for every commit reachable beneath it, and the root `KEYS` file plus the tag ruleset carry the trust anchor today. The release workflow, when releases begin, SHALL verify the tag against `KEYS` before anything publishes; until it exists, verification is the operator's `git verify-tag`. Merging SHALL demand no signature ritual beyond the platform's own; the merge action is the owner's sign-off at credential strength, and the signed tag is the sign-off at hardware strength.

#### Scenario: Signed tag vouches for merged history

- **WHEN** the owner signs a release or checkpoint tag over `main`
- **THEN** every merge since the previous signed tag is attested by that signature

#### Scenario: Merge needs no ritual

- **WHEN** an approved, green pull request is merged from the platform interface
- **THEN** no additional signature is demanded at merge time

### Requirement: Review Economy

Reviews SHALL spend proportionally to what changed: the correctness lane stands down on prose-only diffs, re-reviews judge only the range since the last recorded verdict without re-reporting its findings, low-severity notes collect into a digest rather than inline threads, and pull requests open as drafts until the tree is stable.

#### Scenario: Prose-only change

- **WHEN** a pull request touches only markdown outside the specifications and the machinery
- **THEN** the correctness lane stands down without spend and its check reports green

#### Scenario: Re-review after fixes

- **WHEN** a round already recorded a verdict for an ancestor of the head
- **THEN** the re-review judges the range since that ancestor and does not re-report the recorded findings

### Requirement: Finding Resolution

A fix commit MAY name the review thread it answers with a `Resolves-Thread:` trailer whose value is the finding comment's URL, its numeric comment id, or the thread's node id, and the named threads SHALL resolve automatically when the commit is pushed. A trailer SHALL resolve only threads on its own pull request.

#### Scenario: Trailer resolves thread

- **WHEN** a pushed commit carries `Resolves-Thread:` naming a thread on its pull request
- **THEN** that thread is resolved and the resolution traces to the commit

### Requirement: Release Notes Attestation

Every pull request body SHALL carry a Release Notes section with at least one entry, `- N/A` legal for work with no user-facing effect, and the release workflow SHALL compile the sections of merged pull requests into the release body the owner signs over.

#### Scenario: Missing section

- **WHEN** a pull request body has no Release Notes section
- **THEN** the quality check fails naming the requirement

### Requirement: Merge and Release Ceremony

Approved work SHALL enter `main` as a GitHub merge commit, and release tags SHALL be annotated, signed by the owner, and verified before any release publishes.

#### Scenario: Merge preserves authorship

- **WHEN** the owner merges an approved pull request
- **THEN** every commit keeps its model author and contributor trailers on `main`

#### Scenario: Release verification

- **WHEN** the release workflow runs for a `v*` tag
- **THEN** it verifies the tag signature against the committed `KEYS` file before building, and fails on an unsigned or unknown signature

#### Scenario: Tag creation restricted

- **WHEN** an identity other than the owner attempts to create a `v*` tag
- **THEN** the tag rule refuses it
