---
title: "Central Ceremony Divergence Manifest"
description: "Deliberate consumer differences from the skeleton template are declared by path and digest in one central register that consumers may extend but not self-approve"
type: adr
category: governance
tags:
    - ceremony
    - template
    - drift
status: proposed
created: 2026-09-10
updated: 2026-09-10
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0003 Shared Pinned Lint Tools"
    - "SKEL-0004 Unified Module Validation"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream: []
---

# Central Ceremony Divergence Manifest

## Context and Problem Statement

Consumers of the skeleton template keep deliberate differences: cli keeps an allowlist in its gitleaks config for benchmark fixtures, and the skeleton root names its cascade job differently from the template so the required check composes. The retired byte-comparison guard (skeleton#10, skeleton#18) let a pull request edit the manifest that judged it. Copier propagation replaced the guard, but nothing records which differences are deliberate, so the weekly audit reports the same intentional rows every week and a consumer could quietly diverge further.

## Decision Drivers

- A consumer must not be able to waive its own drift in the same change that introduces it.
- The record must expire when either side moves, so an approval never outlives the bytes it approved.
- The audit must run without executing consumer code.

## Considered Options

1. Exact paths with paired digests in a central register, with consumer extension files approved centrally by digest.
2. Free-form per-consumer exclusion lists that the audit honours as written.
3. Structured field-level patches with approved patch digests.

## Decision Outcome

Chosen option: exact paths with paired digests.

`.ceremony-divergences.yaml` at the skeleton root lists each approved divergence as `repository`, `path`, `reason`, `template_sha256`, and `consumer_sha256`. The template carries an empty copy so every consumer has a place to append its own entries. The central `extensions` map approves a consumer's copy by digest, so an appended entry counts only after skeleton has reviewed the consumer's file. The consumer-parity audit passes a differing path only when an entry matches both digests exactly. A change on either side expires the entry and the path reports as drift until re-approved.

Option 2 lets a consumer suppress its own findings. Option 3 costs a patch format and a merge engine for what is, in practice, a handful of whole-file differences.

## Consequences

- [+] Every intentional difference has a reason and an approval in one reviewable file.
- [+] A drifted file cannot hide behind an old approval.
- [-] Refreshing a consumer's template copy means re-approving every declared path it touches.
- [-] The register carries digests by hand until a helper computes them.
