# Contributing

This repository is the template and archetype for every repository in the organization: `templates/` scaffold new repositories and `docs/specs/` carry the canonical ceremony specifications, so changes here propagate. Start with [ARCHITECTURE.md](ARCHITECTURE.md) for the structural overview.

## Getting Started

```sh
git clone https://github.com/runedeck/skeleton.git
cd skeleton
prek run --all-files    # the checks CI runs at commit stage
```

## Conventions

- 4-space indentation, no tab characters
- Every text file ends with a newline
- Keep portable ceremony files in `templates/base`; Copier release updates propagate them to consumers
- Shell scripts pass `shellcheck -S warning`

## Git

Conventional Commits: `type: description`. Lowercase, no trailing period, no scope.

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

## Pull Requests

1. Fork and create a branch
2. Make changes following the conventions above
3. Open a PR against `main` **as a draft**, and mark it ready when the tree is stable

The body carries `## Plan`, `## Changes`, `## Testing`, and `## Release Notes` sections (`- N/A` when nothing is user-facing); the template pre-fills the shape. Write PR text the way a diff summarizer would: verb-first, factual, file-anchored bullets, claims the diff upholds, no narrative.

## Review etiquette

Iterate in draft, collect fixes locally, push them as one batch, and request a fresh review round only when the tree is stable. A fix commit may name the review thread it answers with a `Resolves-Thread: <value>` trailer, where the value is the finding comment's URL, its numeric comment id, or the thread's GraphQL node id; the thread resolves automatically on push. Only threads on the same pull request resolve.

## Review bots

The funnel walks every ready same-repository pull request automatically: cursor, then macroscope, then the adjudicating correctness lane whose clean verdict earns the approving review. Bare `review` re-summons the funnel after fixes, while `review:runeseer`, `review:macroscope`, and `review:autofix` summon a single lane. A round consumes its labels when it ends. Every summon is visible in the pull request timeline, and [ARCHITECTURE.md](ARCHITECTURE.md) describes the lanes.
