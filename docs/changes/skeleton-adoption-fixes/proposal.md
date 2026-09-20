---
adr: "docs/decisions/SKEL-0008 First Adoption Judged By Its Own Policy.md"
status: proposed
---

# Skeleton Adoption Fixes

## Why

Three consumers adopted the template on 2026-09-20 (seer, site, bench). Each first push failed the authorship hook, because the hook reads its policy from `origin/main:authors.yaml` and the pushed range is what adds that file. The owner skipped the hook three times. A check that must be skipped on every first use is not a check.

The template still carries a `thread-resolver` caller, although seer retired the body: resolution moved into the correctness round. seer keeps a no-op body alive so the callers stay green.

The Rust and Python manifests quote `description` as a TOML literal string. `rune init`, the only renderer of those layers, escapes the brief for a basic string, so a brief with an apostrophe produced an invalid manifest. The cli's own test found it against the embedded copy.

[SKEL-0008](../../decisions/SKEL-0008%20First%20Adoption%20Judged%20By%20Its%20Own%20Policy.md) records the first-adoption rule.

## What Changes

- `scripts/check-authorship`, root and template, judges a first adoption by the target's own `authors.yaml` when `origin/main` has none, and says so in its output. Every later push is judged by `origin/main` as before.
- `thread-resolver.yaml` leaves `templates/base` and the skeleton's own workflows, with its zizmor entries. seer deletes the no-op body after the consumers update.
- `templates/rust/Cargo.toml` and `templates/python/pyproject.toml` quote `description` as a basic string.

## Capabilities

- attribution-check-enforcement (modified)
- sealed-review-ceremony (modified)
- template-layer-composition (modified)

## Impact

- Consumers pick the changes up on their next `copier update`. The manifests are `rune init` layers and reach no existing consumer.
- seer keeps the no-op `thread-resolver.yaml` body until every consumer has dropped its caller.
