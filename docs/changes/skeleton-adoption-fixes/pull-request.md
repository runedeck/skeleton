Three defects the 2026-09-20 adoptions found in the template.

## Plan

Fix the three at their source so the next consumer adopts without a skipped hook, a dead workflow caller, or an invalid manifest. The authorship rule gets a decision record because it moves a trust boundary for one push.

## Changes

- Read the target commit's `authors.yaml` in `scripts/check-authorship` when `origin/main` resolves and carries none, and print which policy judged the range. A base with any `authors.yaml` stays the trusted policy. Root and `templates/base`.
- Record the rule in `docs/decisions/SKEL-0008 First Adoption Judged By Its Own Policy.md`.
- Delete `thread-resolver.yaml` from `templates/base/.github/workflows` and from the skeleton's own workflows, and drop its two entries from each `zizmor.yml`.
- Quote `description` as a basic string in `templates/rust/Cargo.toml` and `templates/python/pyproject.toml`, because `rune init` escapes the brief for one.
- Add the change directory `docs/changes/skeleton-adoption-fixes` with deltas for `attribution-check-enforcement`, `sealed-review-ceremony`, and `template-layer-composition`.
- Add three cases to `tests/test_authorship_integration.py`: a first adoption passes and says so, its target policy still rejects an unknown author, and a target without a policy fails.

## Testing

- `uv run --with pyyaml python3 -m unittest tests.test_authorship_integration`: 32 tests pass.
- `prek run --all-files` and `prek run --all-files --hook-stage pre-push` pass in a fresh clone of the branch head.
- `rune spec validate skeleton-adoption-fixes` and `rune spec doctor` pass on the swept tree (`334361d0`).

## Release Notes

- A repository's first template adoption passes the authorship check by its own `authors.yaml`, and the log says so.
- The template no longer carries a `thread-resolver` workflow caller.
- `rune init` writes a valid manifest for a brief with an apostrophe.
