# Contributing

## Getting Started

```sh
git clone https://github.com/${OWNER}/${NAME}.git
cd ${NAME}
make install
```

## Conventions

See [README.md](README.md) for project-specific conventions.

## Git

Conventional Commits: `type: description`. Lowercase, no trailing period, no scope.

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## Pull Requests

1. Fork and create a branch
2. Make changes following the conventions above
3. `make validate`
4. Open a PR against `main` **as a draft**, and mark it ready when the tree is stable

CI runs validation on every PR. The `main` branch requires passing CI before merge. The body carries a `## Release Notes` section (`- N/A` when nothing is user-facing).

## Review etiquette

No reviewer runs ambiently: every lane answers a maintainer-applied label, and pushes to an unlabeled pull request summon nothing. Bare `review` runs the full funnel — cursor, then macroscope, then the adjudicating correctness lane, each stage only after the previous settles clean — while `review:runeseer`, `review:macroscope`, and `review:autofix` summon a single lane. Every summon is visible in the pull request timeline.

Batch your responses: iterate in draft, collect fixes locally, push them as one batch, and summon a fresh round only when the tree is stable. A fix commit may name the review thread it answers with a `Resolves-Thread: <value>` trailer, where the value is the finding comment's URL, its numeric comment id, or the thread's GraphQL node id; the thread resolves automatically on push. Only threads on the same pull request resolve.
