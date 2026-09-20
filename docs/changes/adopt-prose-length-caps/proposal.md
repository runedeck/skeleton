---
adr: docs/changes/adopt-prose-length-caps/adr.md
status: proposed
decisions: ["Skeleton specifications follow the rune prose caps"]
---

# Adopt prose length caps

## Why

The cli change `prose-length-caps` gives `rune spec doctor` a 100-word requirement cap, a 30-word step cap, and a three-word floor for capability and change ids, and gives `rune docs check` the changelog shape. The skeleton's spec tree failed 40 of those checks: eleven two-word capabilities, two two-word changes, thirteen requirements up to 432 words, and three long steps. The base hook config runs both commands in every consumer, so the template's own tree has to pass them first.

## What Changes

- Rename eleven canonical capabilities and one delta-only capability to three-word ids, and the changes `review-tooling` and `skeleton-ceremony` to `review-tooling-lanes` and `skeleton-ceremony-adoption`. Every path reference follows.
- Split thirteen requirements into one requirement per MUST cluster, each scenario kept under the requirement it proves. The paid-review budget and triage leave `sealed-review-ceremony` for the new capability `paid-review-economy`, because the split file passed 150 lines.
- Retarget the draft change `review-tooling-lanes` at the split requirement names and move its PR-Agent lane into an ADDED requirement.
- Rewrite `CHANGELOG.md` to one verb-first line per change in the Keep a Changelog group order.

## Capabilities

### New Capabilities

- `adopt-prose-length-caps`: the skeleton's spec tree and changelog pass the rune caps.
- `paid-review-economy`: the paid-review budget, the triage stand-down, and round binding, moved out of `sealed-review-ceremony`.

### Modified Capabilities

- Every capability under `docs/specs/` changes its id. Requirement text is unchanged except where a sentence moved under a new heading or gained a MUST the parser requires.

## Impact

- The pi session's PR #50 retargets its three deltas at `attribution-check-enforcement`, `sealed-review-ceremony`, and `template-layer-composition`. `Trusted Attribution Inputs` lost its parser sentences to `Attribution Policy Parser`.
- Decision records that name the old ids keep their text. Accepted records stay as written.
