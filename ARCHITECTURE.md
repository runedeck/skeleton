# Architecture

This repository is the template and archetype for every repository in the organization. Three repositories divide the machinery:

| Repository | Role                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| `skeleton` | The archetype: `templates/` scaffold new repositories, `docs/specs/` carry the canonical ceremony specifications |
| `seer`     | The review machinery: every lane body as a reusable workflow, the org dashboard |
| `.github`  | The organization's face: profile and community defaults                        |

## Review funnel

Same-repository pull requests walk four stages, each spending only after the previous settles clean:

1. **cursor** — summoned by a `bugbot run` comment the cascade posts
2. **macroscope** — summoned by the `review:macroscope` label
3. **runeseer** — summoned by the `review:runeseer` label; adjudicates the free lanes' findings and earns the approving review on an explicit clean verdict for the live head
4. **the owner** — reviews only work carrying that approval; merging is always the owner's action

The funnel walks every ready same-repository pull request automatically, and the bare `review` label re-summons it after fixes. Labels are one-round tokens, consumed when the round ends. Fork pull requests run the free lanes and merge through the owner's Repository-admin bypass, since the paid lane's secrets never reach fork-triggered runs.

## Subscription model

A repository subscribes through its own workflow files: each carries a thin caller per lane that owns the triggers, concurrency, and permissions, and delegates the logic with `uses: runedeck/seer/.github/workflows/<lane>.yaml@main`. The `.ceremony-manifest` drift-checks the callers against this repository's baseline. Repo-local workflows stay local: quality, pr-lint, canary, and spec-drift review this repository's own content.

## Identities

`runewright` acts (labels, comments, patches, greetings; contents and workflows write). `runeseer` reviews (contents read only; its APPROVE is the earned approval). The identity that writes content holds no approval role, and the identity that approves cannot write content.

## Check names

Most lane checks compose as `caller job / called job`; the cascade reports as `cascade / walk`. The correctness lane is mirrored by a caller-side job under the stable name `review/correctness`, and the mirror fails closed: a head with no verdict reports failure, never a satisfiable skip. Both contexts are required status checks in the owner-veto ruleset, which the funnel satisfies by walking every ready same-repository pull request automatically; the merge gate is that verdict plus the earned approval under required reviews. Fork pull requests, where the paid lane cannot run, merge through the owner's Repository-admin bypass after the free lanes settle.

## Secrets

Org secrets with All-repositories visibility: `RUNESEER_APP_ID`, `RUNESEER_APP_KEY`, `RUNEWRIGHT_APP_ID`, `RUNEWRIGHT_APP_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`. Callers pass them to seer's bodies explicitly; a repository without access fails at first summon, not at scaffold time.
