# Review Ceremony Specification

## Purpose

Nothing reaches `main` on one opinion. An application opens every pull request so the sole human's approval counts. The default review funnel runs Macroscope, then Runeseer. Cursor and CodeRabbit provide optional standalone reviews. A skipped optional review does not approve the pull request. Runeseer still requires a verdict on the current head. Deterministic checks stay independent of them, secret scanning is scoped to what a push introduces, specifications bind to protected paths, and releases are sealed by an owner-signed tag. After code merges, the drift review compares the canonical documents under `docs/specs/` with the merged tree and reports any requirement that now describes behavior the tree no longer has.

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

### Requirement: Default and Optional Review Lanes

A lane that bills per run MUST run only inside a requested review round.
A review lane MUST NOT start from pull request lifecycle events alone.
A maintainer MUST apply a review label to request each round.
Bare `review` MUST request Macroscope, then the adjudicating correctness lane.
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
- **THEN** the cascade verifies completed Macroscope correctness evidence on the current head before Runeseer adjudicates

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

#### Scenario: Push between rounds

- **WHEN** a pull request is pushed carrying no `review` or `review:` label
- **THEN** no paid lane runs for that push; the previous head's verdict remains behind, and the current head's required checks stay unsatisfied until a maintainer applies a review label, holding the merge closed

### Requirement: External Lane Configuration

The dashboard state of externally hosted lanes SHALL form part of the ceremony configuration.
Optional Cursor reviews MUST use a standalone `@cursor review` comment.
Cursor MUST enable incremental review and disable draft reviews and autofix.
Optional CodeRabbit reviews MUST use the organization-defined `review:coderabbit` request label.
The repository MUST provision that label without applying it to pull requests.
The repository and base template MUST preserve inherited CodeRabbit review settings.
They MUST disable CodeRabbit review-status messages without suppressing findings.
The adjudicator MUST attribute requested CodeRabbit findings to their provider and source thread.
Macroscope MUST review only after a `review:macroscope` request.
Macroscope MUST disable draft reviews and auto-merge.
Its approvability approval SHALL remain advisory beneath the required verdict checks.
Macroscope MUST honor `skip:macroscope`, which skips only that stage.
The cascade MUST retain Runeseer adjudication and the required verdict mirror.
The configuration guide SHALL record the required state.
A misconfigured lane SHALL remain a ceremony defect even when repository files do not change.

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
- **THEN** Runeseer adjudicates its findings before the review gate can approve the head

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
- **THEN** the lane runs regardless of author; spend is bounded to one round per cascade, and the owner must summon each further round deliberately

#### Scenario: Fork pull request

- **WHEN** a pull request comes from a fork
- **THEN** the correctness lane stands down because its caller and its body each refuse fork heads before any secret-bearing step, the ordered workflow stops after the free lanes, and the pull request merges through the owner's Repository-admin bypass once those lanes settle clean

#### Scenario: Instructions read from the base branch

- **WHEN** a pull request modifies reviewer instructions in its own head commit
- **THEN** the lanes still load the instructions from the base branch

### Requirement: Draft Exemption

A review lane SHALL NOT run on drafts.
Draft iteration and unlabeled pushes SHALL remain free.
The repository handles `review`, `review:runeseer`, `review:cursor`, and `review:autofix` request labels.
These requests SHALL wait while the pull request remains a draft.
They SHALL start when the pull request becomes ready.
Removing a pending request SHALL prevent dispatch.
Removing a dispatched `review` or `review:cursor` label SHALL preserve the active round.
The Cursor workflow SHALL consume `review:cursor` after the summon succeeds.
Cursor SHALL control the posted review through its app trigger.
The Macroscope app SHALL control `review:macroscope` through its own trigger.
The cascade SHALL apply that label only to a ready pull request.
Readiness without a request label MUST NOT start a lane.

The `skip:<lane>` and `ignore:<lane>` labels SHALL act as overrides, not round requests.
An override SHALL neither start nor cancel a round.
The `skip:<lane>` label MUST prevent that lane from running, reporting findings, or spending money.
The `ignore:<lane>` label MUST preserve the lane's full report while releasing its findings from the merge gate.
Both overrides MUST clear the lane's required mirror check.
The correctness mirror MUST record owner acceptance through an approving review when `ignore:runeseer` accompanies a verdict on the judged head.
This acceptance SHALL satisfy the review requirement without a ruleset bypass.
The mirror MUST NOT approve a head the lane never judged.
A terminal default-lane failure MUST still fail the cascade under `ignore:<lane>`.
A failed provider does not establish a completed review.
A round SHALL consist of one cascade.
The cascade SHALL consume `review` after it dispatches the correctness round.
The correctness lane SHALL consume its own request label when its round ends.
The next round SHALL require a fresh `review` label.

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

A pull request touching protected paths SHALL either carry a specification change or an `ignore:spec` label with a stated reason in the body. `ignore:spec` belongs to the ignore family of allowed defects: the change lands unspecified, and the label records that the owner accepted that.

#### Scenario: Protected path with a specification

- **WHEN** a pull request modifies a protected path and includes a specification change
- **THEN** the specification check passes

#### Scenario: Protected path without either

- **WHEN** a pull request modifies a protected path with no specification change and no `ignore:spec` label
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

The owner's hardware key MUST enter the ceremony at tags, not merges: release and checkpoint tags are annotated and owner-signed, a signed tag vouches for every commit reachable beneath it, and the root `KEYS` file plus the tag ruleset carry the trust anchor. The release workflow MUST verify the tag against `KEYS` before publication. Merging MUST NOT demand any additional signature ritual beyond the platform's own; the merge action is the owner's sign-off at credential strength, and the signed tag is the sign-off at hardware strength.

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

Every pull request body MUST carry a Release Notes section with at least one entry, `- N/A` legal for work with no user-facing effect, and the release workflow MUST compile the sections of merged pull requests into the release body the owner signs over. A pull request body MUST NOT change at or after merge; if it does, release compilation MUST fail because the public API cannot attest the merge-time body.

#### Scenario: Missing section

- **WHEN** a pull request body has no Release Notes section
- **THEN** the quality check fails naming the requirement

### Requirement: Merge and Release Ceremony

Approved work MUST enter `main` as a GitHub merge commit, and release tags MUST be annotated, signed by the owner, and verified before any release publishes.

#### Scenario: Merge preserves authorship

- **WHEN** the owner merges an approved pull request
- **THEN** every commit keeps its model author and contributor trailers on `main`

#### Scenario: Release verification

- **WHEN** the release workflow runs for a `v*` tag
- **THEN** it verifies the tag signature against the committed `KEYS` file before building, and fails on an unsigned or unknown signature

#### Scenario: Tag creation restricted

- **WHEN** an identity other than the owner attempts to create a `v*` tag
- **THEN** the tag rule refuses it
