---
adr: "docs/decisions/SKEL-0002 Central Ceremony Divergence Manifest.md"
status: proposed
---

# Skeleton Ceremony

## Why

The nightly canary reported green while a probe failed (skeleton#45). The byte-comparison drift guard was retired without recording the invariant it enforced (skeleton#10, skeleton#18). The spec drift log carried four open items (skeleton#22). The deck's lint row and jj push check lived only in the deck, so consumers and the template disagreed (deck#18, deck#45). Skeleton had no tags, so Copier propagation had never fired.

[SKEL-0002](../../decisions/SKEL-0002%20Central%20Ceremony%20Divergence%20Manifest.md) records the divergence register. [SKEL-0003](../../decisions/SKEL-0003%20Shared%20Pinned%20Lint%20Tools.md) records the lint row promotion.

## What Changes

- The canary uses `RUFF_NO_CACHE=true`, names failed steps in its issue, and ends the run as failed. Quality runs the Copier probe on template changes.
- The cascade callers no longer trigger on `opened`.
- `templates/base` gains the six-linter row with digests, the generated Vale STE style, the deck's jj push check and its tests, and a divergence register.
- A weekly consumer-parity workflow compares every consumer with the template and posts to the deck audit issue.
- `template-update.yaml` targets skeleton main when no newer tag exists and publishes a patch instead of a pull request.
- The commit-attribution and template-composition specs describe the jj workspace path and the install-versus-validate Copier split.
- `DECK-0001` becomes `SKEL-0001`. Three forge-core decisions enter as SKEL-0004 to SKEL-0006 through reviewed adoption.

## Capabilities

- review-ceremony (modified)
- template-composition (modified)

## Impact

- Root and template workflows, hooks, prek configuration, tool pins, and tests.
- Consumers receive the changes through the next `copier update`. The consumers-copier change carries that.
