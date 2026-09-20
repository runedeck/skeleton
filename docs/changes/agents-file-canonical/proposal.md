---
adr: docs/changes/agents-file-canonical/adr.md
status: proposed
decisions: ["AGENTS.md is the only instruction file, and the ignore baseline is audited"]
---

# Agents file canonical

## Why

Every runedeck consumer carried a `CLAUDE.md` that said `@AGENTS.md`, rendered from the template, and the cli carried a `GEMINI.md` twin. Claude Code reads `AGENTS.md` directly, so the stubs were dead weight that a consumer could let drift (purge40k's copy disagreed with its `AGENTS.md` in two numbers). The template's `.gitignore` was seeded once and never audited, so seer, bench, site, homebrew-tap, and pi lacked most of the runtime paths the stack must not track, and the cli had lost `build/` and `dist/`.

## What Changes

- `templates/base/CLAUDE.md` is gone. The parity audit already reports a file the template removed, so a consumer's leftover stub is drift until deleted.
- `templates/base/.gitignore` becomes the stack baseline: rune output, spec runtime state, workspaces and worktrees, quarantine, Entire and SpecStory data, tool caches, secrets. It stays seed-once, and `consumer-parity.py` gains `missing_ignore_lines`, which reports a consumer whose file lacks a baseline pattern and ignores what it adds.
- The skeleton's own `.gitignore` is the baseline plus its Copier answers.

## Capabilities

### Modified Capabilities

- `consumer-template-parity`: two requirements added, the ignore baseline and the single instruction file.

## Impact

- Each consumer deletes its `CLAUDE.md` (and the cli its `GEMINI.md`) and merges the baseline into its `.gitignore` in its own commit. The audit reports them until they do.
- Gemini CLI reads `AGENTS.md` only when `context.fileName` names it in its settings.
