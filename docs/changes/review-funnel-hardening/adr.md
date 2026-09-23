---
title: "Review binds to the head, integration binds to the merge queue"
description: "The paid round, the ledger, and the seals bind to the commit the agent pushed. A merge-group run proves integration once, at merge. Consumers pin the controller by tag and both halves move in one sync."
type: adr
category: governance
tags:
    - ceremony
    - review
    - ci
status: proposed
created: 2026-09-21
updated: 2026-09-21
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0007 Base-Defined Checks and Failing Canaries"
    - "SKEL-0006 Fixture-Based Canary Testing"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1", "gpt-6-astra", "grok-4.6", "lumo-max"]
informed: []
upstream: []
change: review-funnel-hardening
---

# Review binds to the head, integration binds to the merge queue

## Context and Problem Statement

`runedeck/cli` #67 was the first pull request through the sealed funnel. Its code needed one fix. The ceremony needed nine hours, four owner interventions, and a hand merge. `main` moved four times during the review: an identity-test repair, a seer caller sync, a re-signed merge, and a hygiene sweep. Each move hit a different binding to the base. `quality`, a `pull_request` run on the merge commit, stayed red after main was repaired because GitHub does not re-run it on a base move and `gh run rerun` reuses the pinned merge commit. Only a new push refreshed it. The controller polls the green-head checks for five minutes after a push and then stands down for good, while `quality` on cli takes an hour, so no push reaches the paid *lane* (one reviewer job the controller runs, free or model-backed) without a label. The lane's staleness check compared `base.sha`, so a finished model run was discarded and a budgeted round lost. The next entry saw a ledger from another base, reset the stages, consumed the labels, and stopped. The seal verifier disagreed with the seal writer on a key name and a nonce length, and the controller expected a lane table no consumer had. Every consumer calls the controller at `@main`, so a seer change reaches them before their template does.

## Decision Drivers

- A reviewed head is a fact about that commit. A base move does not change what the reviewer read.
- Integration with `main` must be proven before merge, by a check the ruleset requires, in every consumer.
- The three-round budget must meter what the owner pays for: model calls, not workflow attempts.
- Two halves of one contract (cli writer, skeleton or seer verifier) drift unless one artifact binds them and both move together.

## Considered Options

1. Keep merge-commit checks and base-bound rounds, and add an operating rule that `main` never moves while a pull request is in the funnel.
2. Run `quality` twice per pull request, a `pull_request` run that checks out the head and a `merge_group` run on the merge.
3. Prove the head once in the `push` run, drop `quality` from `pull_request`, prove integration in a `merge_group` run the ruleset requires, pin the controller by tag, meter model calls, and publish the ceremony contract from the writer.

## Decision Outcome

Option 3.

- The paid round MUST bind to `(reviewed_sha, generation)`. A base move MUST NOT void a round. The ledger MUST record the base the round saw.
- `quality` MUST run on `push` to a branch, on the head commit, and MUST NOT run on `pull_request`. The `pull_request` run builds a merge commit that GitHub pins at first run and never refreshes on a base move, so its verdict is about a tree nobody can inspect. The `push` run is the green-head signal the controller waits for, and its check log is the receipt `rune sign submit` carries. A `merge_group` run of `quality` MUST prove the merge, and the ruleset MUST require it. A consumer without a merge queue MUST fail the configuration test.
- The controller MUST re-enter on a green head through the consumer's `workflow_run` event, not only through a bounded poll.
- The budget MUST count a round when the lane calls the model. An attempt that stops before the model call MUST NOT count. Attempts per work item MUST be capped at twice the round budget.
- A base-reset MUST reset the free-lane stages and continue into triage in the same run, and MUST NOT consume a review label it did not act on.
- Consumers MUST call the controller at a tag. The caller and the body MUST carry one protocol version, and a mismatch MUST fail closed with a message naming both.
- The cli MUST emit the ceremony contract as golden files: open-seal, merge-seal, `ledger` line, receipt, staleness input. Skeleton and seer tests MUST consume them, with negative cases. A change to the writer MUST regenerate them in the same pull request.
- `rune sign open` MUST write the body before the key touch, and a resume after a failed push MUST verify the remote head, the sealed tree, and an unused nonce before any push.
- Notices to the owner MUST name lanes, never money.

Option 1 was refuted by the day it describes: the rule broke four times in nine hours. Option 2 builds every push twice for one fact, and the `pull_request` half is the run that went stale on #67. It adds a build and keeps the defect. The first draft of this record chose it.

## Consequences

- One head build per push and one integration build per merge, in the queue, instead of one per base move. Pull requests that conflict with `main` bounce from the queue with a check, not from a skill.
- The agentic review does not wait for anything new. The controller re-enters on the `push` run's `workflow_run` event, the same run whose log becomes the receipt. Nothing in the funnel reads a `pull_request` build.
- A fork's push runs in the fork, not in the consumer. A fork pull request therefore has no green-head signal and no receipt in the consumer, and its head is proven only when the queue runs the merge. Fork lanes are owner-summoned already, so this narrows nothing the funnel gives forks today.
- Merge queues must be enabled on every consumer and required in every ruleset. The configuration test enforces it. Until a consumer has one, the old merge-commit `quality` stays required there.
- A verdict on a head whose base later moved is still a verdict on that diff. The merge-queue check decides whether the integration holds.
- Pinning the controller adds a tag step to every seer release and one line to every consumer sync. Controller fixes reach consumers with the sync, not before it.
- The attempt cap ends a runaway lane without the owner's help. A crashed attempt that called the model still counts, because the vendor still billed it.
- The contract files put the golden shape under the writer's control. Skeleton and seer stop guessing.
- The freeze of `main` is advisory for batches of ceremony changes only. The queue serializes integration.
