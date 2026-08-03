# Architecture

This repository is the template and archetype for every repository in the organization. Three repositories divide the machinery:

| Repository | Role                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| `skeleton` | The portable archetype: Copier installs `templates/base`, Rune composes optional layers, and `docs/specs/` carry the canonical ceremony specifications |
| `seer`     | The review machinery: every lane body as a reusable workflow, the org dashboard |
| `.github`  | The organization's face: profile and community defaults                        |

## Review funnel

Same-repository pull requests run four stages, each spending only after the previous settles clean:

1. **cursor** — summoned by an `@cursor review` comment the cascade posts
2. **macroscope** — summoned by the `review:macroscope` label
3. **runeseer** — summoned by the `review:runeseer` label; adjudicates the free lanes' findings and earns the approving review on an explicit clean verdict for the live head
4. **the owner** — reviews only work carrying that approval; merging is always the owner's action

The review cascade runs automatically for every ready same-repository pull request, and the bare `review` label re-summons it after fixes. Summon labels are one-round tokens, consumed when the round ends. Stages settle once: a settled stage carries a `stage:` label and later rounds skip it while its findings stay resolved, so fix rounds go straight to the adjudicator, which judges only the delta since its previous verdict. The adjudicator's verdict can send the pull request back to an earlier stage, and the owner does the same by removing a `stage:` label. Fork pull requests run the free lanes and merge through the owner's Repository-admin bypass, since the paid lane's secrets never reach fork-triggered runs.

## Subscription model

A repository subscribes through its own workflow files: each carries a thin caller per lane that owns the triggers, concurrency, and permissions, and delegates the logic with `uses: runedeck/seer/.github/workflows/<lane>.yaml@main`. Copier records the skeleton release in `answers.yaml` and proposes later releases through ordinary pull requests. Repo-local workflows stay local: quality, pr-lint, canary, and spec-drift review this repository's own content. Rune is optional; direct Copier consumers run the same ceremony.

## Identities

`runewright` acts (labels, comments, patches, greetings; contents and workflows write). `runeseer` reviews (contents read only; its APPROVE is the earned approval). The identity that writes content holds no approval role, and the identity that approves cannot write content.

## Check names

Most lane checks compose as `caller job / called job`; the cascade reports as `review / cascade`. The correctness lane is mirrored by a caller-side job under the stable name `review/correctness`, and the mirror fails closed: a head with no verdict reports failure, never a satisfiable skip. Both contexts are required status checks in the owner-veto ruleset, which the automatic review cascade satisfies for every ready same-repository pull request; the merge gate is that verdict plus the earned approval under required reviews. Fork pull requests, where the paid lane cannot run, merge through the owner's Repository-admin bypass after the free lanes settle.

## Secrets

Org secrets with All-repositories visibility: `RUNESEER_APP_ID`, `RUNESEER_APP_KEY`, `RUNEWRIGHT_APP_ID`, `RUNEWRIGHT_APP_KEY`, `RUNEWRIGHT_GITHUB_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`. The `RUNEWRIGHT_GITHUB_TOKEN` is an owner-minted fine-grained token (issues write only) the cascade uses to post Cursor summons, because Cursor drops bot-authored trigger comments. Callers pass them to seer's bodies explicitly; a repository without access fails at first summon, not at scaffold time.
