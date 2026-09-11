---
title: Fixture-Based Canary Testing
description: Validators test against real fixture files in valid and invalid directories to prove they catch errors
type: adr
category: process
tags:
    - testing
    - validation
    - fixtures
status: accepted
created: 2026-04-05
updated: 2026-09-10
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0004 Unified Module Validation"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream:
    - "https://github.com/N4M3Z/forge-core/blob/132e0589eb87849973ab8ee984926f318af4d642/docs/decisions/CORE-0012%20Fixture-Based%20Canary%20Testing.md"
    - "https://github.com/json-schema-org/JSON-Schema-Test-Suite"
---

# Fixture-Based Canary Testing

## Context and Problem Statement

A validator can regress silently. A broken validator that accepts everything still exits 0 in CI. Unit tests verify single check functions, but nothing proves the full pipeline, from file read through frontmatter extraction to schema validation, catches real errors. The machinery canary exists for the same reason at the workflow level: skeleton#45 showed a green run hiding a failed step for a full day.

## Decision Drivers

- A validator that accepts everything is as broken as one that rejects everything.
- Adding a test case must mean adding a file, not writing code.
- The pattern must serve every validator: ADR schema, mdschema, prose style, tool installer.

## Considered Options

1. `valid/` and `invalid/` directories: fixtures organized by expected result, the runner globs and asserts from the parent directory.
2. An inline annotation manifest: one JSON file with a valid flag per fixture, the JSON Schema Test Suite pattern.
3. Filename prefixes: `pass-` and `fail-` in one flat directory.

## Decision Outcome

Chosen option: `valid/` and `invalid/` directories. The directory name is the assertion and the layout is self-documenting without a manifest or convention document.

Skeleton keeps its fixtures under `tests/fixtures/<validator>/{valid,invalid}/`. The first set covers the generated Vale style: `tests/fixtures/vale/valid/` holds prose the style must accept, including fenced and inline code with semicolons, and `tests/fixtures/vale/invalid/` holds a blockquote, a contraction, and a semicolon the style must reject. `tests/test_vale_style.py` asserts every valid fixture passes and every invalid fixture fails.

### Consequences

- [+] Adding a canary test is creating a file in the right directory.
- [+] A directory listing shows the coverage at a glance.
- [-] Two directories per validator instead of one flat directory.
