## MODIFIED Requirements

### Requirement: Deterministic Checks Independent of Review

The tests, lint, secret scan, schema validation, authorship, and specification checks MUST be required independently of the review lanes, and a passing review MUST NOT substitute for any of them. The head MUST be proven by a `push` run on the head commit, and `quality` MUST NOT run on `pull_request`, because that run's merge commit is pinned at first run and never refreshed. A `merge_group` run MUST prove the merge, and the ruleset MUST require it with the merge queue on. A base move MUST NOT change the result of the head run.

#### Scenario: Review passes while a test fails

- **WHEN** every review lane passes and a test job fails
- **THEN** `main` refuses the merge

#### Scenario: Base moves under a green head

- **WHEN** `main` advances after the head run passed
- **THEN** the head run stays green, no `pull_request` run is rebuilt, the merge queue runs the `merge_group` job on the real merge, and a failure there refuses the merge

#### Scenario: Pull request opens on a proven head

- **WHEN** the push run on the head passed and the app opens the draft
- **THEN** no second `quality` build starts, the push run's check is the green-head signal, and its log is the receipt

#### Scenario: Consumer without a merge queue

- **WHEN** a consumer's ruleset does not enable the merge queue
- **THEN** the configuration test fails and names the repository, and the merge-commit `quality` stays required there until the queue is on
