---
title: Unified Module Validation
description: One validation path through prek, with the git hook as its runner and make validate as its front door
type: adr
category: process
tags:
    - validation
    - ci
    - prek
status: accepted
created: 2026-04-02
updated: 2026-09-10
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0005 Verified Remote Execution"
    - "SKEL-0006 Fixture-Based Canary Testing"
    - "SKEL-0003 Shared Pinned Lint Tools"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream:
    - "https://github.com/N4M3Z/forge-core/blob/132e0589eb87849973ab8ee984926f318af4d642/docs/decisions/CORE-0010%20Unified%20Module%20Validation.md"
---

# Unified Module Validation

## Context and Problem Statement

Validation logic must be identical across CI, the commit hook, and a contributor's shell. A consumer repository must not reimplement checks. The skeleton template defines what a valid repository looks like through the shared `.pre-commit-config.yaml`, and rune supplies deck and module validation through `rune validate`.

## Decision Drivers

- One validation path. No duplicate logic across Makefile, CI, and hook scripts.
- CI and a fresh clone must run the same checks with the same pinned tools.
- No consumer-specific validator scripts beside the shared configuration.

## Considered Options

1. Inline CI and hook scripts: each repository maintains its own validation commands.
2. prek as the primary runner: one declarative hook configuration that CI, the git hook, and `make validate` all execute.
3. A hash-verified remote validation script downloaded at hook time.

## Decision Outcome

Chosen option: prek as the primary runner.

`.pre-commit-config.yaml` declares every check: shellcheck, ruff, gitleaks, semgrep, the prose and workflow linters, and `rune validate`. The git `pre-commit` hook runs `prek run`, and `make validate` delegates to that hook with `--all-files`. CI calls the prek binary directly with `REQUIRE_GATES=1`, so a linter that the installer failed to place fails the run instead of skipping.

The upstream decision kept a remote validation script as a fallback for hosts without prek. Skeleton drops that fallback: `scripts/install-tools` installs every pinned tool from a digest-verified archive ([SKEL-0005](SKEL-0005%20Verified%20Remote%20Execution.md)), so prek is always present after `make install`. A hook that finds no prek prints the install command and fails.

Canary fixtures under `tests/fixtures/` ([SKEL-0006](SKEL-0006%20Fixture-Based%20Canary%20Testing.md)) prove the configured checks catch the failures they exist for.

### Consequences

- [+] One source of truth: the prek configuration is the check list.
- [+] CI and a contributor's shell run identical checks against identical tool versions.
- [+] No per-repository validator to maintain beside the template.
- [-] A repository with no `make install` has no checks until the tools arrive. The guarded hooks report that instead of skipping silently under `REQUIRE_GATES`.
