---
title: "Shared Pinned Lint Tools"
description: "The prose and workflow linters the deck adopted move into the template payload as digest-pinned installs with guarded prek hooks, and the Vale STE style is generated from the deck rule source"
type: adr
category: process
tags:
    - lint
    - template
    - prose
status: proposed
created: 2026-09-10
updated: 2026-09-10
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0004 Unified Module Validation"
    - "SKEL-0005 Verified Remote Execution"
    - "SKEL-0006 Fixture-Based Canary Testing"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream: []
---

# Shared Pinned Lint Tools

## Context and Problem Statement

The deck adopted six linters under its DECK-0010 decision: rumdl for Markdown, typos for spelling, Vale for prose style, lychee for links, actionlint and zizmor for workflows. It installs them inline in its quality workflow with linux digests and runs them through guarded prek hooks. The skeleton template carried none of them, so a fresh consumer had no prose checks, the deck's local and CI installs did not share one path, and deck#18 stayed open on that gap. The Vale STE rules were also hand-copied from the Simplified Technical English skill's `rules.json` and had already diverged from it.

## Decision Drivers

- Local and CI must run the same pinned binary, installed by the same script ([SKEL-0004](SKEL-0004%20Unified%20Module%20Validation.md)).
- Every download must be digest-verified on every supported platform ([SKEL-0005](SKEL-0005%20Verified%20Remote%20Execution.md)).
- One rule source for Simplified Technical English, owned by the deck skill.

## Considered Options

1. Promote the whole DECK-0010 row into `templates/base`: pins, installer, hooks, and a generated Vale style.
2. Promote Vale only and leave the other five linters deck-local.
3. Keep every linter deck-local and let each consumer install its own.

## Decision Outcome

Chosen option: the whole row.

`templates/base/scripts/tool-versions` pins each linter with darwin and linux digests for amd64 and arm64. `install-tools` installs them from verified release archives. `templates/base/.pre-commit-config.yaml` carries one guarded hook per linter: the hook skips when the binary is absent so a fresh clone stays usable, and fails under `REQUIRE_GATES=1`, which CI sets. `scripts/generate-vale-style.py` compiles `.vale/styles/STE/` from a frozen snapshot of the deck skill's `rules.json`. The snapshot's source commit and digest live in `.vale/ste-source.yaml`, and a hook fails when a generated file is stale. Every generated rule carries `scope: sentence`, so YAML front matter is metadata and never lints. Blockquotes lint as prose, so captured output belongs in a fence.

Option 2 leaves the deck's local and CI paths split for five tools. Option 3 is the state that produced deck#18.

## Consequences

- [+] Every consumer gets the same lint row through one `make install`.
- [+] The Vale style cannot drift from its rule source without a failing check.
- [-] The template carries a frozen copy of the deck rule source. The parity audit reports when the deck moves past it.
- [-] Six more version bumps to review by hand, each with four digests.
