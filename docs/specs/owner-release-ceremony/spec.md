# Release Ceremony Specification

## Purpose

How the owner's hardware key enters the ceremony and how approved work enters `main`: the open-seal that readies a pull request, the merge-seal that permits its merge, the owner-signed tags that vouch for `main`, and release notes compiled from merged pull requests. The key touches three times: open, merge, tag.

## Requirements

### Requirement: Owner Attestation on Seals and Tags

The owner's hardware key MUST enter the ceremony at three points. The *open-seal* is an empty signed commit beneath the pull request head whose subject line carries the repository, the base ref, the pull request number, the head tree, and a single-use nonce of 64 lowercase hex characters, 32 random bytes. `rune sign open` MUST write that nonce into the pull request body when it flips the draft ready. The session agent MAY invoke `rune sign open`, `submit`, and `next`. The touch is the owner's, and nothing signs without it.

#### Scenario: Open-seal binds one pull request

- **WHEN** `owner-seal` verifies a ready pull request
- **THEN** the seal names this pull request's number and this pull request's body carries the seal's nonce
- **AND** the sealed tree is an ancestor of the head and the signature verifies against `KEYS`
- **AND** another body that carries the nonce is reported and does not fail this pull request

#### Scenario: Inherited seal

- **WHEN** a branch forked from a sealed branch opens its own pull request
- **THEN** the nonce belongs to the original pull request, `owner-seal` fails, and the new pull request needs its own open-seal

### Requirement: Merge-Seal Shape

The *merge-seal* is an empty signed commit whose sole parent is the ledger's `reviewed_sha` and whose tree equals that parent's tree. It MUST name `reviewed_sha`, the ledger generation, and the sha256 digest of the ledger artifact in its subject line.

#### Scenario: Merge-seal is an empty child

- **WHEN** `owner-seal` verifies a merge-seal
- **THEN** the seal's sole parent equals the ledger's `reviewed_sha`, its tree equals the parent tree, its generation matches the ledger, and its signature verifies against `KEYS`

#### Scenario: Push after the merge-seal

- **WHEN** any commit is pushed above the merge-seal
- **THEN** `owner-seal` fails until the owner seals the new head

#### Scenario: Generation bump after the merge-seal

- **WHEN** the ledger generation increments after a merge-seal was signed
- **THEN** `owner-seal` fails, the queue entry is stale, and the owner seals again after re-adjudication

### Requirement: Signed Tags and Trust Anchor

Release and checkpoint tags MUST be annotated and owner-signed, and a signed tag vouches for every commit reachable beneath it. The root `KEYS` file, read from the protected default branch and resolved as `trusted-key-anchor` specifies, and the tag ruleset carry the trust anchor.

#### Scenario: Signed tag vouches for merged history

- **WHEN** the owner signs a release or checkpoint tag over `main`
- **THEN** every merge since the previous signed tag is attested by that signature

### Requirement: Owner-Seal Merge Check

Merging a same-repository pull request MUST require both seals through the `owner-seal` check. The check MUST read the ledger from a record that only the controller's app identity can write, never from a comment, and MUST fail when `reviewed_sha` has no ledger.

#### Scenario: Ledger read from the check run

- **WHEN** `owner-seal` verifies a merge-seal
- **THEN** it reads the `ledger` check run on `reviewed_sha` under the reviewing identity, never a comment
- **AND** it fails when `reviewed_sha` has no ledger or the artifact digest does not match

### Requirement: Ledger Record Binding

The ledger record is a check run named `ledger` on `reviewed_sha` under the reviewing identity, whose first output line names the ledger artifact, its digest, the generation, and the pull request. A reader that needs the threads fetches the artifact and MUST prove it by the digest. The check's workflow file runs from the default branch, and a head branch can still post a check run of the same name from a `pull_request` workflow, so the binding boundary is an organization ruleset `workflows` rule pinned to the check's file on the default branch.

#### Scenario: Head branch posts a ledger check run

- **WHEN** a `pull_request` workflow on the head branch posts a check run named `ledger`
- **THEN** the organization `workflows` rule keeps the binding on the default-branch file and the head's record does not count

### Requirement: Signing Queue Admission

`rune sign submit` MUST refuse a head unless the ledger at its current generation shows a paid clean verdict or the coverage state `free lanes only` with its reason, every expected lane in a terminal status, zero open or `owner` threads, every required check green, and the proof the receipt names present. It MUST record the coverage state on the request. `rune sign next` MUST show the diff stat against base, the disposition table or the coverage state, the proof, and the request fields being authorized, and MUST take one acknowledgment before the key.

#### Scenario: Free lanes only

- **WHEN** the ledger shows `free lanes only` and every other condition holds
- **THEN** the head is queued with `free lanes only` and its reason on the request, and `rune sign next` shows that state before the touch

#### Scenario: Owner thread open

- **WHEN** the ledger holds a thread disposed as `owner`
- **THEN** `rune sign submit` refuses until the owner clears or rejects it

### Requirement: Release Notes Attestation

Every pull request body MUST carry a Release Notes section with at least one entry, `- N/A` legal for work with no user-facing effect, and the release workflow MUST compile the sections of merged pull requests into the release body the owner signs over. A pull request body MUST NOT change after the open-seal. A body edit MUST increment the ledger generation. If the body changes at or after merge, release compilation MUST fail because the public API cannot attest the merge-time body.

#### Scenario: Missing section

- **WHEN** a pull request body has no Release Notes section
- **THEN** the quality check fails naming the requirement

#### Scenario: Body edited after ready

- **WHEN** the body changes after `rune sign open`
- **THEN** the ledger generation increments and the standing approval and queue entry become stale

### Requirement: Merge and Release Ceremony

Approved work MUST enter `main` as a GitHub merge commit, and release tags MUST be annotated, signed by the owner, and verified before any release publishes.

#### Scenario: Merge preserves authorship

- **WHEN** the owner merges a sealed pull request
- **THEN** every commit keeps its model author and contributor trailers on `main`, and the two seals are part of the merged history

#### Scenario: Release verification

- **WHEN** the release workflow runs for a `v*` tag
- **THEN** it verifies the tag signature against the signers the committed `KEYS` file pins before building, and fails on an unsigned or unknown signature

#### Scenario: Tag creation restricted

- **WHEN** an identity other than the owner attempts to create a `v*` tag
- **THEN** the tag rule refuses it

### Requirement: Owner Direct Push

The owner MAY push to the protected branch outside a pull request, as a fast-forward or a force push, through the repository admin bypass on both branch rulesets.
Every commit such a push adds to the branch MUST carry a signature that verifies against `KEYS`.
Commits the branch already reaches are outside the range: work that entered through a pull request stays unsigned.

#### Scenario: Signed direct push

- **WHEN** the owner pushes `main` directly and every added commit is signed by a `KEYS` key
- **THEN** the guarded push publishes it

#### Scenario: Unsigned commit in a direct push

- **WHEN** a direct push to `main` adds a commit without a `KEYS` signature
- **THEN** the guarded push refuses, names the commit, and points to `jj sign` or a pull request

#### Scenario: Feature branch push

- **WHEN** a push targets a branch other than the protected one
- **THEN** no signature is required and the pushed commits stay as authored

### Requirement: Direct Push Enforcement

The guarded push MUST refuse a direct push when any added commit is unsigned or signed by a key `KEYS` does not name, and MUST name the first such commit.
The platform MUST NOT require signatures on the branch, because model commits are unsigned by design.
The guarded push is the enforcement point, and a push that goes around it is the owner's own act.

#### Scenario: Stranger's signature

- **WHEN** a direct push adds a commit signed by a key `KEYS` does not name
- **THEN** the guarded push refuses and names the fingerprint
