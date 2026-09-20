---
adr: docs/changes/docs-check-in-hooks/adr.md
status: proposed
decisions: ["Every consumer runs rune docs check on its changelog"]
---

# Docs check in hooks

## Why

The cli's `prose-length-caps` change teaches `rune docs check` the changelog shape (one line per change, Keep a Changelog groups) and `rune spec doctor` the three-word name floor. The skeleton's hook config runs `rune spec doctor` and never `rune docs check`, so a consumer's changelog is checked only where a repository added the hook by hand, and never on a changelog-only commit.

## What Changes

- `.pre-commit-config.yaml` at the root and in `templates/base/` gain a `rune-docs-check` hook after `rune-spec-doctor`, with the same skip rule when `rune` is absent, on `^(docs/|CHANGELOG\.md$)`.

## Capabilities

### New Capabilities

- `docs-check-in-hooks`: every consumer's commit stage runs `rune docs check` when `docs/` or `CHANGELOG.md` changes.

## Impact

- Two hook config files. Consumers receive it through `copier update`. The deck and the cli carry the hook already and gain only the `CHANGELOG.md` trigger.
