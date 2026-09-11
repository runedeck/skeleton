# Architecture

This repository is the template and archetype for every repository in the organization. Three repositories divide the machinery:

| Repository | Role                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| `skeleton` | The portable archetype: Copier installs `templates/base`, Rune composes optional layers, and `docs/specs/` carry the canonical ceremony specifications |
| `seer`     | The review machinery: every lane body as a reusable workflow, the org dashboard |
| `.github`  | The organization's face: profile and community defaults                        |

## Review funnel

The default review funnel serves same-repository pull requests.

1. Macroscope provides correctness evidence on the current head, including any findings.
2. Runeseer adjudicates the findings and records a current-head verdict.
3. The owner reviews the result and decides whether to merge.

Cursor Bugbot and CodeRabbit provide optional standalone reviews.
Their absence does not prevent the default funnel from running.
Their absence also does not establish approval.
The [review ceremony specification](docs/specs/review-ceremony/spec.md#requirement-default-and-optional-review-lanes) defines request handling and current-head evidence reuse.
The [configuration guide](docs/guides/review-lanes-configuration.md) defines provider settings and exact check identification.
Fork pull requests use the available free lanes and the owner's Repository-admin bypass.
The correctness caller and body refuse fork heads before any secret-bearing step.

## Subscription model

A repository subscribes through its own workflow files: each carries a thin caller per lane that owns the triggers, concurrency, and permissions, and delegates the logic with `uses: runedeck/seer/.github/workflows/<lane>.yaml@main`. Copier records the skeleton reference in `answers.yaml`, and the weekly template-update run publishes the next update as a patch the owner applies and pushes. Repo-local workflows stay local: quality, pr-lint, canary, and spec-drift review this repository's own content. Rune is optional. Direct Copier consumers run the same ceremony.

## Identities

`runewright` acts (labels, comments, patches, greetings, and contents and workflows write). `runeseer` reviews (contents read only, and its APPROVE is the earned approval). The identity that writes content holds no approval role, and the identity that approves cannot write content.

## Check names

Most lane checks compose as `caller job / called job`.
Their display names can vary with the caller job name.
The stable `review/correctness` mirror is the single required review status check.
The separate required `quality` check enforces deterministic validation.
The cascade reports orchestration progress, not a second merge decision.
A head without a verdict fails the review gate.
A clean, no-restart verdict on the current head earns Runeseer's approval.
The specification defines owner acceptance and fork exceptions.
Branch review requirements remain separate from these status checks.

## Secrets

Organization secrets: `RUNESEER_APP_ID`, `RUNESEER_APP_KEY`, `RUNEWRIGHT_APP_ID`, `RUNEWRIGHT_APP_KEY`, `RUNEWRIGHT_GITHUB_TOKEN`, and `CLAUDE_CODE_OAUTH_TOKEN`.
The optional Bugbot summon uses the owner-minted `RUNEWRIGHT_GITHUB_TOKEN` because Cursor ignores bot-authored review requests.
The default cascade does not need that token.
Callers pass the secrets their reusable workflows need.
Repository access to those secrets remains a deployment prerequisite.
