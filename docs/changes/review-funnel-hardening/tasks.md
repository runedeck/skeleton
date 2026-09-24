# Tasks

Owner review in small groups: group 1, key touch, group 2, key touch. Companion edits in seer and cli merge through their own funnels and are listed with their repository.

## 1. Integration in the queue, review on the head (skeleton)

- [x] 1.1 `quality.yaml`: `on: push` (head commit, `gh-readonly-queue/**` ignored) and `on: merge_group` (queue merge commit), `pull_request` removed, root and `templates/base`. The release-notes step finds the pull request by branch on push and by queue ref on `merge_group`. The pre-push range uses `merge_group.base_sha`
- [x] 1.1a root `quality.yaml` keeps the `test_dcg_policy.py` unittest step that `fable/dcg-command-policy` (skeleton `20fec5f8`) adds after the tool-installer test, in the job that runs the unittest block
- [ ] 1.2 (deferred to a follow-up, not on the merge path) `quality.yaml`: `Swatinem/rust-cache` pinned by digest, keyed on `Cargo.lock`, `save-if` off on `merge_group`, skipped without `Cargo.toml`
- [x] 1.3 rulesets: `merge_queue` rule (MERGE, ALLGREEN, 60 min check timeout, 5 entries) in `ceremony-base.json`, root and `templates/base`. The `quality` context stays required and both runs report it
- [ ] 1.4 `review-correctness.yaml` caller: `workflow_run` on `Quality` completed, `green-head` job maps `head_sha` to its open pull request and calls the body as a green-head event
- [ ] 1.5 `review-correctness.yaml` caller: `uses:` pins a seer tag and passes `protocol: 2`
- [x] 1.6 `draft-open.yaml`: `on: workflow_run` of `Quality` completed on `change/**`, `codex/**`, `fable/**`. Opens on a green same-repository push run, checks out the proven head for the body file only, no second build
- [x] 1.7 `tests/test_review_configuration.py`: quality on push and merge_group only, merge queue rule present, Draft Open on `workflow_run` (seer tag and controller `workflow_run` land with 1.4 and 1.5)

## 2. Specs (deltas in this change)

- [ ] 2.1 `paid-review-economy`: head-only binding, base recorded, model-call accounting with an attempt cap, base-reset continuation, green-head re-entry
- [ ] 2.2 `deterministic-merge-checks`: head proof and merge proof as two required contexts
- [ ] 2.3 `sealed-review-ceremony`: pinned controller with a protocol version, writer-published contract, lane-named notices, `rune sign open` body-before-touch and verified resume, freeze advisory

## 3. Ceremony contract (skeleton side)

- [ ] 3.1 `tests/fixtures/ceremony-contract/`: the five golden files and their `-bad-*` siblings, taken from `rune sign --emit-contract` (cli task 5.1)
- [ ] 3.2 `tests/test_ceremony_contract.py`: open-seal and merge-seal through `scripts/verify-seal`, ledger line through the `owner-seal.yaml` jq path, receipt through the receipt rule, staleness through the controller's check
- [ ] 3.3 fold the existing open-seal live-shape fixture and the lane-table fixture into 3.1

## 4. Companion: seer `review-correctness.yaml`

- [ ] 4.1 `live=` compares `head.sha` only, and the ledger records `base_sha` at round start
- [ ] 4.2 `PAID_ROUNDS` increments when the model is called, `ATTEMPTS` increments per entry and stops the lane at twice the round budget
- [ ] 4.3 base-reset resets the free-lane stages and continues into triage in the same run without consuming labels
- [ ] 4.4 green-head entry from the consumer's `workflow_run` event
- [ ] 4.5 `protocol` input, fail closed on mismatch with both versions named
- [ ] 4.6 `runeseer_summary.py standdown_notice`: "runeseer round" and lane names in the owner line, `free lanes only` kept as the machine key
- [ ] 4.7 seer release tag for the pinned caller
- [ ] 4.8 delete the no-op `thread-resolver.yaml` body once no consumer calls it

## 5. Companion: cli

- [ ] 5.1 `rune sign --emit-contract <dir>`: writes the five golden files and their negative siblings from the real writers, with a cli test that regenerates and diffs them
- [ ] 5.2 `rune sign submit`: `admit()` reports "no verdict on this head" ahead of an undisposed thread (`src/cli/sign/queue/ledger.rs`)
- [ ] 5.3 `rune sign open` writes the pull request body before the key touch
- [ ] 5.4 `rune sign open --resume`: verifies the remote head, the sealed tree, and an unused nonce, then pushes and flips
- [ ] 5.5 BabysitPR skill (deck): read every lane every tick, ledger in the change directory, `git merge-tree` before each push

## 6. Merge

- [ ] 6.1 Owner review of groups 1 to 3, one key touch on skeleton main
- [ ] 6.2 seer tag after group 4, one key touch on seer main
- [ ] 6.3 Consumer copier sync, once, after skeleton main carries this change, `fable/lane-table-in-template` (`4a97592d`), and `fable/seed-once-lint-config` (`fd00b59a`, direct-push signature rule), with merge queues enabled per repository before the sync. One session runs it.
- [ ] 6.4 Archive: `adr.md` moves to `docs/decisions/` with the next free SKEL number
