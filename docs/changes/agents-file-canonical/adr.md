---
title: "AGENTS.md is the only instruction file, and the ignore baseline is audited"
description: "The template renders AGENTS.md alone, never CLAUDE.md or GEMINI.md, and the parity audit checks that every consumer keeps the template's .gitignore patterns."
type: adr
category: infrastructure
tags:
    - skeleton
    - template
    - hygiene
status: proposed
created: 2026-09-21
updated: 2026-09-21
author: "@N4M3Z"
project: skeleton
related:
    - "SKEL-0002 Central Ceremony Divergence Manifest"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1"]
informed: []
upstream: []
change: agents-file-canonical
---

# AGENTS.md is the only instruction file, and the ignore baseline is audited

## Context and Problem Statement

Harness-specific instruction files (`CLAUDE.md`, `GEMINI.md`) were stubs that pointed at `AGENTS.md`, and one consumer let its copy diverge. The seeded `.gitignore` had no check after seeding, so most consumers lacked the runtime paths the stack agrees not to track.

## Considered Options

1. Keep the stubs and add a parity rule that they equal `@AGENTS.md`.
2. Render `AGENTS.md` alone and let the audit report a leftover stub as a removed file.
3. Make `.gitignore` a managed file that Copier rewrites on update.
4. Keep `.gitignore` seed-once and audit the baseline patterns.

## Decision Outcome

Options 2 and 4. A stub that only redirects is a second place for drift. A managed `.gitignore` would erase each repository's own patterns on update, so the baseline is checked line by line instead.

The template MUST keep these rules:

- `AGENTS.md` MUST be the only instruction file the template renders.
- Every pattern in `templates/base/.gitignore` MUST be present in each consumer's file.

## Consequences

- A harness that reads only its own file needs configuration (`context.fileName` for Gemini CLI).
- A consumer's extra ignore patterns never trigger drift.
