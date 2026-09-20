Make `AGENTS.md` the only instruction file the template renders and audit the `.gitignore` baseline in every consumer.

## Plan

Drop `templates/base/CLAUDE.md`, turn the template's `.gitignore` into the stack baseline, and teach the parity audit to report a consumer whose `.gitignore` lacks any baseline pattern.

## Changes

- Remove `templates/base/CLAUDE.md`.
- Rewrite `templates/base/.gitignore` as the baseline (rune output, spec runtime state, workspaces and worktrees, quarantine, Entire and SpecStory data, caches, secrets), and sync the skeleton's own file.
- Add `missing_ignore_lines` to `scripts/consumer-parity.py` with a test.
- Add `docs/changes/agents-file-canonical/`.

## Testing

- [x] `pytest tests`: 135 passed.
- [ ] Both prek stages in an isolated clone.

## Release Notes

- Remove `CLAUDE.md` from the template and audit the `.gitignore` baseline in every consumer.
