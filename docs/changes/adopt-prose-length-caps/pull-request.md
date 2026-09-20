Bring the skeleton's spec tree and changelog under the rune 0.5.0 prose caps.

## Plan

The base hooks run `rune spec doctor` and `rune docs check` in every consumer, and the skeleton's own tree failed them in 40 places: eleven two-word capabilities, two two-word changes, thirteen requirements up to 432 words, three long steps, and a changelog of paragraphs. Rename, split, and rewrite until both commands pass, with the requirement text kept.

## Changes

- Rename eleven capabilities and two changes to three-word ids, and every path reference, workflow comment, and test comment follows.
- Split thirteen requirements into one per MUST cluster, scenarios kept with the requirement they prove.
- Add `paid-review-economy`, the budget and triage requirements moved out of `sealed-review-ceremony`.
- Retarget the draft change `review-tooling-lanes` at the split names, and its PR-Agent lane becomes an ADDED requirement.
- Rewrite `CHANGELOG.md` to one verb-first line per change.
- Add `docs/changes/adopt-prose-length-caps/` with proposal, delta, tasks, and `adr.md`.

## Testing

- [x] `rune spec doctor`, `rune spec validate`, `rune docs check`: no error with rune 0.5.0 (2a4666f6).
- [x] `pytest tests` (134 passed) and `tests/spec-presence` (24 checks) in the workspace.
- [ ] Both prek stages in an isolated clone.

## Release Notes

- Change every capability and change id to three hyphenated words and split every requirement over 100 words.
