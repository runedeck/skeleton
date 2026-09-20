---
title: "Skeleton specifications follow the rune prose caps"
description: "The skeleton's spec tree uses three-word ids and requirements under 100 words, so the base hooks that run rune spec doctor and rune docs check pass on the template itself."
type: adr
category: documentation
tags:
    - skeleton
    - specifications
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
change: adopt-prose-length-caps
---

# Skeleton specifications follow the rune prose caps

## Context and Problem Statement

The base hook config runs `rune spec doctor` and `rune docs check` in every consumer. The rune 0.5.0 caps (100-word requirements, 30-word steps, three-word ids, one-line changelog entries) fail on the skeleton's own tree in 40 places. A template that fails its own hooks cannot ask a consumer to pass them.

## Considered Options

1. Exempt the skeleton through `spec.min_name_words: 0` and a larger word cap in `rune.yaml`.
2. Bring the tree under the caps: rename the ids, split the requirements, rewrite the changelog.
3. Drop the two hooks from the base config.

## Decision Outcome

Option 2. The caps exist because a 400-word requirement hides its MUST clauses, and the template is the one tree that must show the shape it asks for. The renames keep the old id in the decision records that cite it.

The tree MUST keep these rules:

- Every capability and change id MUST carry three or more hyphen-separated words.
- A requirement that outgrows 100 words MUST split into one requirement per MUST cluster, never shrink by dropping a clause.
- A canonical specification that outgrows 150 lines MUST split into a second capability with its own purpose.

## Consequences

- Eleven capability directories and two change directories change name. Open deltas that target them retarget on rebase, as PR #50 does.
- The paid-review economy has its own capability, `paid-review-economy`, which the review-ceremony purpose now points at.
