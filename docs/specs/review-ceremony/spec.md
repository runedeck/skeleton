# Review Ceremony Specification

## Purpose

Nothing reaches `main` on one opinion. An application opens every pull request so the sole human's approval counts, three vendor-diverse review lanes block as check runs, deterministic checks stay independent of them, secret scanning is scoped to what a push introduces, specifications bind to protected paths, and releases are sealed by an owner-signed tag.

## Requirements

### Requirement: Owner-Opened Pull Requests

The owner SHALL author every ceremony pull request, ghostwritten by the orchestrating agent with a short summary, and the `runewright` app SHALL push the branch over HTTPS and post the full ceremony body as the first comment.

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

- **WHEN** any pull request fails a required check
- **THEN** the merge is refused regardless of who authored it, since the checks rules admit no bypass

### Requirement: Three Review Lanes

Every pull request SHALL run `review/conventions` and `review/defects`, and the owner's pull requests SHALL additionally run `review/correctness`, each lane a separate check run backed by a different vendor. The correctness lane spends the owner's subscription, so it is scoped to the owner's pull requests and SHALL NOT be required of anyone else's.

#### Scenario: Lane blocks a merge

- **WHEN** a lane reports a blocking finding
- **THEN** its check fails and `main` refuses the merge until the finding is resolved

#### Scenario: Reviewer unavailable

- **WHEN** a review lane that applies to the pull request cannot produce a verdict
- **THEN** its check remains pending rather than passing

#### Scenario: Correctness lane scope

- **WHEN** a pull request is authored by anyone other than the owner
- **THEN** `review/correctness` does not run and its absence blocks nothing

#### Scenario: Instructions read from the base branch

- **WHEN** a pull request modifies reviewer instructions in its own head commit
- **THEN** the lanes still load the instructions from the base branch

### Requirement: Draft Exemption

Review lanes SHALL run when a pull request is opened, reopened, marked ready for review, or synchronized while not a draft, and SHALL NOT run on synchronization of a draft.

#### Scenario: Draft iteration

- **WHEN** an agent pushes repeatedly to a draft pull request
- **THEN** no review lane runs for those pushes

#### Scenario: Marked ready

- **WHEN** the pull request is marked ready for review
- **THEN** every review lane runs against the current head commit

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

A clean correctness verdict on the owner's pull request SHALL become the reviewer identity's approving review, and any later push SHALL dismiss it until a clean re-review re-grants it.

#### Scenario: Clean verdict approves

- **WHEN** `review/correctness` posts a verdict of clean on the owner's pull request
- **THEN** the reviewer identity submits an approving review satisfying the required approval

#### Scenario: Push dismisses

- **WHEN** any commit lands after the approval
- **THEN** the approval is dismissed and returns only after a clean re-review

### Requirement: Owner Seal

Merging SHALL require the branch head to be an owner seal: an empty, signature-verified commit by the owner with a `seal:` subject. A push after the seal SHALL unseal the branch, and a valid seal SHALL restore the earned approval its own push dismissed.

#### Scenario: Sealed branch merges

- **WHEN** the head commit is an empty verified owner commit with a `seal:` subject
- **THEN** the `owner-seal` check passes and the merge may proceed

#### Scenario: Push unseals

- **WHEN** any commit lands after a seal
- **THEN** the `owner-seal` check fails until the owner seals again

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
