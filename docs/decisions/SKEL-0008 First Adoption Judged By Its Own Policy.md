---
title: "First Adoption Judged By Its Own Policy"
description: "When the trusted base carries no attribution policy, the authorship check judges the pushed range by the policy that range adds, and says so; every later push is judged by the base"
type: adr
category: governance
tags:
    - ceremony
    - attribution
    - adoption
status: proposed
created: 2026-09-20
updated: 2026-09-20
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0007 Base-Defined Checks and Failing Canaries"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream: []
---

# First Adoption Judged By Its Own Policy

## Context and Problem Statement

The authorship check reads its policy from `origin/main:authors.yaml`, so a pull request cannot weaken the rules that judge it (SKEL-0007). A repository that adopts the template for the first time has no `authors.yaml` on `origin/main`: the adoption range is what adds it. The check then fails before it reads a commit, and the owner skips it. Three consumers adopted the template on 2026-09-20 and each needed the skip. A check that is skipped on every first use teaches everyone to skip it.

## Decision Drivers

- The base-ref rule of SKEL-0007 must hold for every push after the first.
- A first adoption must pass a real check, not a skipped one.
- The check must never judge a range by a policy it did not announce.

## Considered Options

1. When `origin/main` has no `authors.yaml`, judge the range by the target's `authors.yaml` and print which policy was used. A target without one fails.
2. Keep the failure and document the skip.
3. Bootstrap every repository with an `authors.yaml` commit by hand before adoption.

## Decision Outcome

Chosen option: judge a first adoption by its own policy, aloud.

`scripts/check-authorship` keeps `origin/main:authors.yaml` as the trusted policy. When that path does not exist and `origin/main` resolves, it reads `<target>:authors.yaml` instead and prints `first adoption is judged by <target>:authors.yaml`. A target without the file fails as before. The fallback applies only while the base has no policy at all: a base with any `authors.yaml`, valid or not, is still the trusted policy, so a head can never replace an existing one.

Option 2 keeps a check nobody runs. Option 3 puts an unchecked commit on `main` to make the check pass.

## Consequences

- [+] A first adoption passes the same identity rules as every later push, and the log names the policy that judged it.
- [+] The SKEL-0007 boundary stays intact after the first push.
- [-] The first push of a repository is judged by a policy the owner has not merged yet. The owner reviews that push as they review the policy file in it.
