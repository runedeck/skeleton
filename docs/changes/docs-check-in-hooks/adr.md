---
title: "Every consumer runs rune docs check on its changelog"
description: "The base hook config runs rune docs check on docs/ and CHANGELOG.md changes, so the changelog shape and the docs links hold in every consumer's commit stage."
type: adr
category: infrastructure
tags:
    - skeleton
    - hooks
    - changelog
status: proposed
created: 2026-09-20
updated: 2026-09-20
author: "@N4M3Z"
project: skeleton
related:
    - "SKEL-0007 Base-Defined Checks and Failing Canaries"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1"]
informed: []
upstream: []
change: docs-check-in-hooks
---

# Every consumer runs rune docs check on its changelog

## Context and Problem Statement

A rule that lives in the rune binary reaches a repository only through a hook that runs the binary. `rune spec doctor` has such a hook in the base config. `rune docs check`, which now carries the changelog shape, does not, and the repositories that added it by hand trigger it on `docs/` alone.

## Considered Options

1. Leave each consumer to add the hook.
2. Add the hook to the base config with `CHANGELOG.md` in its trigger.
3. Fold the changelog check into `rune spec doctor` so the existing hook covers it.

## Decision Outcome

Option 2. The base config is where a check for every consumer belongs (SKEL-0007). The changelog is not a specification artifact, so option 3 would blur `spec doctor`.

The base config MUST keep these rules:

- The hook MUST trigger on `CHANGELOG.md` as well as `docs/`.
- The hook MUST skip when `rune` is absent, until a pinned release makes it a required tool.

## Consequences

- Consumers gain the check on their next `copier update`. The deck and the cli already run it and gain the changelog trigger.
- A consumer whose changelog does not fit the shape sees the failure on its first changelog commit after the update, not before.
