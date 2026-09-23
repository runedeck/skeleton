---
adr: docs/changes/review-funnel-hardening/adr.md
status: proposed
decisions: ["Review binds to the head, integration binds to the merge queue"]
---

# Review funnel bound to the head

## Why

The first pull request through the sealed funnel, `runedeck/cli` #67 on 2026-09-21, needed one code fix from review and about nine hours of ceremony. `main` moved four times while the pull request was in the funnel. Each move re-reddened the required `quality` check (a merge-commit run GitHub never refreshes), voided one of three paid rounds (the lane compares `base.sha`), or turned a push into a base-reset run that consumed the labels without judging. The controller's five-minute poll never saw cli's hour-long `quality` turn green, so no push reached the paid lane without a label. Four more defects were writer/verifier mismatches that a shared contract would have caught. The owner merged by hand. This change binds the review to the head the agent pushed, proves integration once in the merge queue, meters model calls instead of workflow attempts, pins the controller, and publishes the ceremony contract from the writer. Three adversarial reviews (astra, grok, lumo) of the first draft shaped it: the first draft bound `quality` to the head alone and counted only verdicts, and both were refuted.

## What Changes

- `quality.yaml` runs on `push` to a branch, on the head commit, and on `merge_group`, on the queue's merge. It does not run on `pull_request`. The push run is the green-head signal and the receipt source, the merge-group run proves the merge. The ruleset requires both contexts and enables the merge queue. A consumer without a merge queue fails `test_review_configuration.py`.
- The review-correctness caller gains a `workflow_run` trigger on `Quality` completing green, maps the head to its open pull request, and enters the controller as a green-head event. The five-minute poll stays as the fast path.
- Consumers call the controller at a seer tag, not `@main`. Caller and body carry one protocol version and fail closed on a mismatch.
- The paid-review economy binds a round to `(reviewed_sha, generation)`, records the base it saw, counts a round when the model is called, caps attempts at twice the round budget, and continues a base-reset into triage without consuming labels.
- The cli emits the ceremony contract as golden files (open-seal, merge-seal, `ledger` line, receipt, staleness input). Skeleton and seer tests consume them with negative cases. Two ad-hoc fixtures (open-seal, lane table) fold into the contract.
- `quality.yaml` caches the Rust build keyed on `Cargo.lock`, read-only for forks, off on the `main` run. The push run is the one CI build per push.
- Notices name lanes ("runeseer round", "Codex and Cursor only"), never money. The owner read "paid round" as GitHub billing.
- `rune sign open` writes the body before the key touch and resumes after a failed push only when the remote head, the sealed tree, and an unused nonce still match.
- The freeze of `main` during a funnel pass becomes advisory guidance for batches of ceremony changes, not a rule the design depends on.

## Capabilities

- paid-review-economy (modified)
- deterministic-merge-checks (modified)
- sealed-review-ceremony (modified)

## Impact

- `templates/base/.github/workflows/quality.yaml`, `review-correctness.yaml`, `draft-open.yaml`, `templates/base/.github/rulesets/*.json`, and the root copies.
- `docs/specs/paid-review-economy`, `docs/specs/deterministic-merge-checks`, `docs/specs/sealed-review-ceremony`.
- `tests/fixtures/ceremony-contract/` and the tests that read it.
- Companion work outside this repository, listed in `tasks.md`: seer `review-correctness.yaml` (staleness, budget, base-reset, `workflow_run` entry, notice wording, protocol version, release tag), cli (`rune sign --emit-contract`, `sign open` body and resume, `sign submit` message order).
- Consumers receive the template through one copier sync after skeleton and seer both carry this change. Until a consumer has a merge queue, its old merge-commit `quality` stays required.
