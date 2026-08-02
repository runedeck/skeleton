# Contributing

## Getting Started

```sh
git clone https://github.com/${OWNER}/${NAME}.git
cd ${NAME}
make install    # activates the git hooks and the jj push alias
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

CI runs validation on every PR. The `main` branch requires passing CI before merge. The body carries a `## Release Notes` section (`- N/A` when nothing is user-facing). Write PR text the way a diff summarizer would: verb-first, factual, file-anchored bullets, claims the diff upholds, no narrative.

## Review etiquette

Iterate in draft, collect fixes locally, push them as one batch, and request a fresh review round only when the tree is stable. A fix commit may name the review thread it answers with a `Resolves-Thread: <value>` trailer, where the value is the finding comment's URL, its numeric comment id, or the thread's GraphQL node id; the thread resolves automatically on push. Only threads on the same pull request resolve.

## Review bots

The review cascade runs automatically for every ready same-repository pull request: cursor, then macroscope, then the adjudicating correctness lane. Bare `review` re-summons the cascade after fixes, while `review:runeseer`, `review:macroscope`, and `review:autofix` summon a single lane. A round consumes its labels when it ends, and every round is visible in the pull request timeline.
