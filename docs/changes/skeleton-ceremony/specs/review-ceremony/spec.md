## ADDED Requirements

### Requirement: Trusted Check State

A pull request MUST NOT select or weaken the checks that judge it. The specification-presence check, the authorship policy, and the protected-path list SHALL execute from the base ref. The head `.pre-commit-config.yaml` MAY run, because every change to it is itself a protected path that needs a specification or an `ignore:spec` waiver.

#### Scenario: Head edits the check policy

- **WHEN** a pull request changes `.pre-commit-config.yaml`, `authors.yaml`, or a workflow under `.github/workflows/`
- **THEN** the specification-presence check runs from the base ref and requires a specification change or an `ignore:spec` label

#### Scenario: Head removes a hook

- **WHEN** a pull request deletes a hook from `.pre-commit-config.yaml` without a specification change
- **THEN** the specification-presence check fails before the weakened configuration can pass the merge

### Requirement: Declared Ceremony Divergence

A consumer that keeps a deliberate difference from the skeleton template SHALL declare it in `.ceremony-divergences.yaml` with the path, the reason, and the SHA-256 of both sides at approval time. The central register in skeleton SHALL approve each consumer's divergence file by digest. An undeclared or expired difference SHALL report as drift.

#### Scenario: Consumer declares a divergence

- **WHEN** a consumer file differs from the rendered template and a central entry names that path with matching digests
- **THEN** the parity audit passes the file as declared

#### Scenario: Declared file changes on either side

- **WHEN** the template or the consumer file no longer matches the digest recorded in the entry
- **THEN** the parity audit reports the path as drift until the entry is re-approved

#### Scenario: Consumer appends without approval

- **WHEN** a consumer adds an entry to its own divergence file and the central register does not approve that file's digest
- **THEN** the parity audit ignores the appended entry and reports the path as drift

#### Scenario: Consumer appends with approval

- **WHEN** the central `extensions` map records the digest of the consumer's divergence file
- **THEN** the parity audit merges the consumer's entries with the central ones before comparing

### Requirement: Machinery Canary Result

The nightly machinery canary SHALL run every probe step to completion, name each failed step in the issue it files, and end the run as failed when any probe failed.

#### Scenario: Probe fails

- **WHEN** the Copier update probe exits nonzero
- **THEN** the machinery step still runs, the filed issue names `Exercise Copier updates`, and the run conclusion is failure

#### Scenario: Template change reaches a pull request

- **WHEN** a pull request changes `templates/`, `copier.yaml`, or `tests/`
- **THEN** the Quality workflow runs the Copier update probe before the nightly canary can find it broken

### Requirement: Consumer Parity Audit

Skeleton SHALL run a scheduled parity audit that renders `templates/base` at each consumer's recorded release and at skeleton main, compares every rendered file with the consumer's copy, compares the consumer's labels with the provisioned set, and posts one report per run on the standing audit issue.

#### Scenario: Consumer lags the template

- **WHEN** a consumer file differs from the template rendered at skeleton main and no divergence entry covers it
- **THEN** the report lists the path under drift and the run fails after posting

#### Scenario: Consumer label differs

- **WHEN** a consumer label's name, color, or description differs from the provisioned set, or a retired label is still present
- **THEN** the report lists the label under drift

#### Scenario: Consumer pin does not resolve

- **WHEN** a consumer's recorded `_commit` is not a skeleton ref
- **THEN** the report names the invalid pin and the comparison continues against skeleton main

#### Scenario: Template removed a file since the pin

- **WHEN** the template rendered at the consumer's pin has a file that the template at main no longer renders, and the consumer still has it
- **THEN** the report lists the path as drift

#### Scenario: Consumer cannot be fetched

- **WHEN** one consumer clone or label listing fails
- **THEN** the report names the failure for that consumer, the other consumers are still compared, and the run fails after posting

#### Scenario: Consumer has no answers file

- **WHEN** a consumer clone has no `answers.yaml` and the `LABELS_ONLY_CONSUMERS` variable does not name it
- **THEN** the report lists the missing file as a failure instead of auditing labels alone

#### Scenario: Rule source moves past the snapshot

- **WHEN** the consumer that hosts the Simplified Technical English rule source has a `rules.json` whose digest differs from `.vale/ste-source.yaml`
- **THEN** the report names the new digest and asks for a snapshot refresh
