---
adr: "docs/decisions/SKEL-0001 Version-Independent Model Attribution.md"
status: proposed
decisions: ["Version-Independent Model Attribution"]
---

# Derived display name

## Why

Nine heads of the 2026-09-21 landing round were authored `Claude Fable 5 (claude-fable-5)` by a Claude Fable 5.1 session. The policy accepts `claude-fable-5-1` without a roster line (SKEL-0001), but `author-identity.py resolve` spelled a new model as `Claude (claude-fable-5-1)`, so nobody used it and agents copied the nearest roster line instead. The version is part of the record. A display name that drops it loses which model wrote the change.

## What Changes

- `scripts/author-identity.py` (root and `templates/base`): `resolve` derives the display name from the model ID the way the roster spells it. `claude-fable-5-1` under `claude` is `Claude Fable 5.1`, `gpt-6-astra` under `codex` is `Codex GPT 6 Astra`. Words title-case, a run of version segments joins with dots, the harness leads unless the model names it.
- `tests/test_author_identity.py`, `tests/test_authorship_integration.py`: the generated names carry the version. Every existing roster line reproduces from its model ID.

## Capabilities

### Modified Capabilities

- `commit-author-attribution`: a generated identity keeps the model version in its display name.

## Impact

- `make worktree IDENTITY=<model-id>` now prints and sets the full name. Consumers take the script through the next copier sync. Commits already on `main` as `claude-fable-5` stay: published history is not rewritten.
