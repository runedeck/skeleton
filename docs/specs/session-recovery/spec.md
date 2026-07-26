# Session Recovery Specification

## Purpose

A commit on `main` leads back to the session that wrote it. The recovery key is a trailer on the commit object, checkpoint attachment adds the richer walk, capture runs without per-clone setup, and session output never enters a repository.

## Requirements

### Requirement: Session Trailer on Ceremonial Commits

Every ceremonial commit SHALL carry a `Session: <harness>:<session-id>` trailer naming the session that produced it, stamped by the committing agent and checked at staged review.

#### Scenario: Trailer present

- **WHEN** the owner approves the staged diff and the orchestrating model commits
- **THEN** the commit message carries a `Session:` trailer resolving to a synced transcript

#### Scenario: Several sessions in one commit

- **WHEN** work from more than one session lands in a single ceremonial commit
- **THEN** the commit carries one `Session:` trailer per session

### Requirement: Checkpoint Attachment at the Review Boundary

Immediately after a ceremonial commit, and before any further commit in that repository, the session SHALL be attached in each repository that received a commit, linking a checkpoint to that commit.

#### Scenario: Attachment after commit

- **WHEN** a ceremonial commit lands in a repository
- **THEN** `entire session attach` runs in that repository and the checkpoint links to that commit

#### Scenario: Session spanning repositories

- **WHEN** one session commits to more than one repository
- **THEN** attachment runs once in each repository committed

### Requirement: Walk from Commit to Session

A commit on `main` SHALL resolve to the session that produced it from its trailer alone, with checkpoint explanation available where attachment ran.

#### Scenario: Recovering from a bisected defect

- **WHEN** `git bisect` identifies the commit that introduced a defect
- **THEN** the `Session:` trailer names the session, the harness can resume it, and `entire checkpoint explain <sha>` explains it where a checkpoint was attached

#### Scenario: Attachment absent

- **WHEN** a commit carries a trailer but no attached checkpoint
- **THEN** recovery proceeds from the trailer and transcript, and no check or merge rule is affected

### Requirement: Capture Enabled Everywhere

Every repository SHALL capture sessions without per-clone setup: agents start through the wrapper that syncs sessions when they end, and `rune init` scaffolds the tracked project binding.

#### Scenario: Agent started through rune

- **WHEN** an agent starts through `rune launch` or `rune run`
- **THEN** its session is synced when the session ends

#### Scenario: Freshly scaffolded repository

- **WHEN** `rune init` scaffolds a repository
- **THEN** the SpecStory project binding is present and tracked, and the ignore rules cover transcript output

### Requirement: Transcripts Outside the Repository

Transcripts and debug output SHALL be written to the working layer rather than any repository, while the project binding that identifies their source stays tracked.

#### Scenario: Transcript destination

- **WHEN** a session is synced
- **THEN** its transcript is written under the harness working layer and no repository path

#### Scenario: Transcript never staged

- **WHEN** transcript or debug output appears under `.specstory/`
- **THEN** those files are ignored and never reach a pull request

### Requirement: Stable Commit Identifiers

Merge strategies that rewrite commit ids SHALL NOT be used on `main`, since a rewritten id orphans its checkpoint.

#### Scenario: Merge preserves ids

- **WHEN** an approved pull request merges
- **THEN** every commit keeps the id its checkpoint was bound to
