---
title: "Base-Defined Checks and Failing Canaries"
description: "The checks that judge a pull request execute from the base ref, and the machinery canary runs every probe to completion and ends as failed when any probe failed"
type: adr
category: governance
tags:
    - ceremony
    - ci
    - canary
status: proposed
created: 2026-09-13
updated: 2026-09-13
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0002 Central Ceremony Divergence Manifest"
    - "SKEL-0006 Fixture-Based Canary Testing"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1"]
informed: []
upstream: []
---

# Base-Defined Checks and Failing Canaries

## Context and Problem Statement

Two requirements of the skeleton-ceremony change had an implementation and no decision record. The spec-presence check, the authorship policy, and the protected-path list run from the base ref through `pull_request_target`, because a pull request that could edit the policy that judges it could waive its own review. The nightly machinery canary reported green while a probe failed (skeleton#45), because a failed step did not fail the run and the filed issue did not name it. Both behaviors are now in `.github/workflows/attestations.yaml` and `.github/workflows/canary.yaml`, and the merge-checks and consumer-parity deltas describe them, but nothing recorded why.

## Decision Drivers

- A pull request must not select or weaken the checks that judge it.
- A canary that hides a failed probe is worse than no canary.
- The head may still run its own hooks, because every hook edit is itself a protected path.

## Considered Options

1. Base-ref execution of the judging checks through `pull_request_target`, with the head allowed to run its own hooks. The canary runs every probe under `continue-on-error`, names each failed step, and ends as failed.
2. Head-ref execution of every check, with a review requirement on policy files.
3. A canary that stops at the first failed probe.

## Decision Outcome

Chosen option: base-ref execution of the judging checks and a canary that runs every probe and fails.

The spec-presence check, the authorship policy, and the protected-path list execute from `github.event.pull_request.base.sha`, and the workflow verifies the checkout matches that commit before it judges anything. A change to `.pre-commit-config.yaml`, `authors.yaml`, or a workflow is a protected path and needs a specification change or an `ignore:spec` waiver. The machinery canary runs each probe step with `continue-on-error`, so a failed probe never hides the ones after it, names every failed step in the issue it files, and ends the run as failed when any probe failed. Quality runs the Copier update probe when a pull request changes `templates/`, `copier.yaml`, or `tests/`, so a broken template is visible in the pull request that broke it.

Option 2 lets the head redefine the reviewer. Option 3 reports the first failure and hides the rest.

## Consequences

- [+] The trusted base decides what a pull request must carry, and the head cannot change that in the same change.
- [+] A red canary names what broke.
- [-] A policy change lands in two steps: the pull request that proposes it is judged by the old policy.
- [-] Every probe runs to completion even after an early failure, so a broken nightly takes longer to finish.
