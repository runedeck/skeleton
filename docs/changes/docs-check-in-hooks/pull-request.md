Run `rune docs check` in every consumer's commit stage when `docs/` or `CHANGELOG.md` changes.

## Plan

The cli change `prose-length-caps` teaches `rune docs check` the changelog shape. The base hook config runs `rune spec doctor` and never `rune docs check`, so a consumer's changelog is checked only where a repository added the hook by hand, and never on a changelog-only commit. One hook in the base config, with the same skip rule as spec doctor, closes that.

## Changes

- Add a `rune-docs-check` hook after `rune-spec-doctor` in `.pre-commit-config.yaml`, on `^(docs/|CHANGELOG\.md$)`, skipping when `rune` is absent.
- Add the same hook to `templates/base/.pre-commit-config.yaml`.
- Add `docs/changes/docs-check-in-hooks/` with proposal, delta spec, tasks, and `adr.md`.

## Testing

- [x] `prek run --all-files` and `prek run --stage pre-push --all-files` with `REQUIRE_GATES=1` in an isolated clone of `42bc1fc3`, both exit 0.

## Release Notes

- Add a `rune docs check` hook to the base pre-commit config, on `docs/` and `CHANGELOG.md`.
