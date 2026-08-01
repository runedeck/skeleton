# Contributing

The skeleton is the runedeck archetype: its `templates/` scaffold every
repository in the org, and its `docs/specs/` carry the canonical ceremony
specifications. Changes here propagate, so review runs deeper than usual.

## Git

Conventional Commits: `type: description`. Lowercase, no trailing period, no scope.

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## Pull Requests

1. Fork and create a branch
2. Make changes; keep `templates/base` copies and their root counterparts in step where the `.ceremony-manifest` pairs them
3. Open a PR against `main` **as a draft**, and mark it ready when the tree is stable

The body carries `## Plan`, `## Changes`, `## Testing`, and `## Release Notes` sections (`- N/A` when nothing is user-facing); the template pre-fills the shape.

## Review etiquette

No reviewer runs ambiently: every lane answers a maintainer-applied label, and pushes to an unlabeled pull request summon nothing. Bare `review` runs the full funnel — cursor, then macroscope, then the adjudicating correctness lane, each stage only after the previous settles clean — while `review:runeseer`, `review:macroscope`, and `review:autofix` summon a single lane. A summon is one round: the labels are consumed when the round ends.

Batch your responses: iterate in draft, collect fixes locally, push them as one batch, and summon a fresh round only when the tree is stable. A fix commit may name the review thread it answers with a `Resolves-Thread: <value>` trailer, where the value is the finding comment's URL, its numeric comment id, or the thread's GraphQL node id; the thread resolves automatically on push. Only threads on the same pull request resolve.
