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

Reviews are billed and re-run on every push, so batch your responses: collect fixes locally while reviewers are working and push them together once the lanes settle, rather than one push per finding. A fix commit may name the review thread it answers with a `Resolves-Thread: <value>` trailer, where the value is the finding comment's URL, its numeric comment id, or the thread's GraphQL node id; the thread resolves automatically on push. Only threads on the same pull request resolve.

Billed reviewers are summoned, never ambient: the maintainer applies review labels to invoke them — bare `review` for the full cascade, `review:runeseer`, `review:macroscope`, or `review:autofix` for a single lane — and each summon is visible in the pull request timeline.
