# Review Lanes Configuration

The dashboard state of the external review lanes is part of the ceremony: a wrong toggle reintroduces ambient reviewing, comment storms, or bot-driven merges no repository file can prevent. This guide records the required configuration for every lane and the reasoning behind each choice. It is destined for the provisioning deck. Until that exists, it lives here beside the specs it serves.

The default review funnel runs Macroscope, then Runeseer. Cursor and CodeRabbit provide optional standalone reviews. Their absence does not block the default funnel or approve a pull request. Runeseer still requires a verdict on the current head.

## Cursor Bugbot (cursor.com/dashboard → Bugbot)

Bugbot settings resolve personal → repository → installation → team, where an installation is the GitHub App connection to one account or organization. Configure at the tiers named below and leave repository and personal dropdowns on "Use Installation Default": one source of truth, inherited by every current and future generated repository. No behavioral toggle reads from the repository. Repo files contribute review guidance only (`.cursor/BUGBOT.md`, root plus nested).

Preferences page (the team tier, and on an individual plan the top tier, where "Use Team Default" resolves):

| Setting | Required value | Reason |
| --- | --- | --- |
| Trigger Mode | Manual only | `review:cursor` requests one standalone `@cursor review` comment. This optional summon uses the owner-minted `RUNEWRIGHT_GITHUB_TOKEN` secret because Cursor ignores bot-authored comments. The default cascade does not need this token. |
| Incremental Review | On | Each round reviews only the delta since the last. Without it every round re-flags the full backlog |
| Bugbot Effort Levels | Smart | Adequate. The adjudicating lane catches what a cheaper pass misses |

runedeck installation page:

| Setting | Required value | Reason |
| --- | --- | --- |
| Auto-Enable for New Repositories | On | Scaffolded repositories inherit the lane without a dashboard visit |
| Review Draft PRs | Off | Draft iteration is free by ceremony rule |
| Run Once Per PR | Off | It would ignore new commits entirely. Incremental review is the right delta mechanism |
| Post PR Summary | Description mode if the dropdown offers one, else As Comment | The description is where a reader looks first, and it spares a comment |
| Post PR risk score | On | Cheap prioritization signal in the summary |
| Automatically Learn Rules | On | Suppressions accumulate across pull requests without re-teaching |
| Autofix Behavior | Off | Autofix in this org is suggestion-only through runewright. A bot pushing commits breaks commit attribution |

A terminal Macroscope failure adds `issue:macroscope`. A correctness round without a verdict adds `issue:rune`. The workflow token applies these labels without starting another cascade. The cascade refuses another request for a blocked default lane. Correct the provider or billing problem before removing its blocker.

A completed current-head Macroscope correctness check clears `issue:macroscope` when its conclusion is `success` or `neutral`.
A successful current-head correctness round clears `issue:rune`.
An existing `issue:cursor` label does not block the default cascade.

The cascade verifies the exact Macroscope correctness check on the current head in every round.
It reuses a completed `success` or `neutral` check and sends its findings to Runeseer.
An informational `stage:macroscope` label records completion.
Removing that label does not force another review while reusable current-head evidence remains.
Cursor stage records do not create a required default stage.

Bugbot reads `.cursor/BUGBOT.md` from the repository root. It supports no include syntax, so the file stays self-contained. Nested `.cursor/BUGBOT.md` files scope guidance to subtrees.

## CodeRabbit

CodeRabbit remains optional. The organization requires `review:coderabbit` before CodeRabbit reviews a pull request.
The PR Lint workflow provisions this label without applying it.
Apply the label only when you want a standalone CodeRabbit round.

The root and base template contain `.coderabbit.yaml`.
The configuration enables inheritance to preserve organization settings.
It sets `reviews.review_status: false` to suppress review-status messages, including skipped-review messages.
It preserves findings and the inherited opt-in policy.
A skipped review is not an approval.
The owner must resolve genuine CodeRabbit findings before merge or explicitly accept them.
Runeseer collects requested CodeRabbit findings with their provider identity and source thread.

See the CodeRabbit [auto-review settings](https://docs.coderabbit.ai/configuration/auto-review)
and [configuration inheritance](https://docs.coderabbit.ai/configuration/configuration-inheritance).
The [configuration schema](https://coderabbit.ai/integrations/schema.v2.json) defines `review_status` and inherited settings.

## Macroscope, workspace level (macroscope.com → Settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Product Overview | Filled (text below) | Context improves every summary and review |
| Custom Agent Instructions | Empty | Slack agent unused |
| Excluded commit authors | Empty | Nearly all commits are agent-authored. Excluding those identities would hollow out summaries and status reporting |
| Web search | On | Reviews may ground claims against upstream documentation |

Product Overview text:

> runedeck builds rune, a CLI that assembles and deploys agent skills, rules, and hooks ("runes") across AI coding harnesses. Repositories follow a review ceremony: model-authored commits, owner-authored pull requests, automatically ordered review lanes, and owner-signed release tags. The skeleton repository is the template every other repository is generated from. Changes to templates/ propagate to every generated repository.

## Macroscope, per repository (Repos → select all → Edit settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Correctness | Off ambient, `review:macroscope` label trigger only | Macroscope starts the default cascade. The label also requests a standalone round. |
| Always Review PR Labels | `review:macroscope` | The app starts the requested correctness review. |
| Detection Mode | Prefer Precision | Ambient reviewing trades coverage for signal. Runeseer still adjudicates whatever it reports |
| Check Run Agents | On | Enables in-repo `.macroscope/` agents as check runs. Ceremony-specific checks can be authored there |
| Review Draft PRs | Off | Draft iteration is free |
| Automatically Merge Macroscope's PRs | Off | Nothing merges itself in this org. Every merge is the owner's action |
| Auto-assign Reviewer | On | Routes a reviewer onto PRs opened without one |
| Skip Dependabot | Off | No Dependabot. Revisit if it arrives |
| Review Cross-Repo PRs | On | Macroscope reviews fork pull requests before the owner considers an admin bypass. |
| Skip PRs by Author | Empty | No exempt authors |
| Skip PRs by Labels | `skip:macroscope` | The owner override that stands this lane down |
| Approvability | On, medium threshold | Advisory beneath the required verdict checks: its approval cannot outrank a red `review/correctness`, and the owner's merge click stays the final gate |
| Release Ref Patterns | `v*` | Matches the signed-tag release ceremony |
| Status features | On | Commit summaries and digests cost nothing in review terms |

Set the repository variable `MACROSCOPE_CORRECTNESS_CHECK` to an observed correctness check name.
Use the exact name from a real Macroscope correctness run on the current head.
Approvability and custom-agent checks do not establish correctness review.
An empty variable stops the default cascade with a configuration error.
The caller passes this value to Seer as `macroscope_correctness_check`.
See the Macroscope [label configuration](https://docs.macroscope.com/bug-detection-and-fixes.md).

## Owner overrides

Default lanes support `skip:` and `ignore:` overrides. The optional Cursor summon retains `skip:cursor`.

| Label | Effect | Reads it |
| --- | --- | --- |
| `skip:cursor` | The optional Cursor summon does not run | Cursor caller and body |
| `skip:macroscope` | The default Macroscope stage does not run | Cascade body, Macroscope dashboard |
| `skip:runeseer` | The correctness lane is never summoned or invoked, and its required mirror clears | Cascade body, correctness caller and body |
| `ignore:macroscope` | Macroscope runs and reports. Its unresolved findings stop holding the funnel | Cascade body |
| `ignore:runeseer` | The correctness lane runs and records its verdict. The findings stop holding the merge | Correctness body and caller |

A terminal default-lane failure still fails under `ignore:`. A failed provider is not a completed review. Optional Cursor and CodeRabbit failures do not block the default cascade. Their genuine findings still require resolution or explicit owner acceptance. For Runeseer, a verdict on the current head remains necessary. Use `skip:` when a lane should not run.

## PR description markers

Macroscope posts pull request summaries into the description instead of a comment when the body carries its markers. The pull request body template includes:

```text
<!-- Macroscope's pull request summary starts here -->
<!-- Macroscope's pull request summary ends here -->
```

One fewer comment per pull request, and the summary lands where a reader looks first. Authored Changes bullets follow the same register the summarizer uses: verb-first, factual, file-anchored, claims the diff upholds.

## Check names and secrets

The skeleton's [ARCHITECTURE.md](../../ARCHITECTURE.md#check-names) defines check contexts, identities, and the organization secret list.
Use its authoritative review-gate description when you configure branch rules.

## Verification

1. Open a draft pull request in a scaffolded repository.
2. Push twice and verify that no review lane starts.
3. Apply `review` while the pull request remains a draft.
4. Mark it ready and verify that Macroscope runs before Runeseer.
5. Verify that neither optional lane starts from the bare `review` label.
6. Verify that `review/correctness` remains red until Runeseer records a clean current-head verdict.
7. Verify that the clean verdict posts an approval.
8. Apply `review:cursor` or `review:coderabbit` only when you want that optional review.

A pull request without `review:coderabbit` must produce no CodeRabbit skipped-review message.
An optional review failure must not replace the Runeseer verdict or suppress genuine findings.

Check review evidence by provider, exact check name, and current head.
Keep `not requested`, `running`, `reviewed`, `findings`, and `provider failure` states distinct.
Cursor Security Agent does not establish Bugbot coverage.
Macroscope Approvability does not establish correctness coverage.

## Caller permissions and deployment

The cascade needs `contents: read`, `checks: read`, `issues: write`, and `pull-requests: write`.
The optional Cursor caller needs the same permissions except `checks: read`.
Both callers use the workflow token for label removal after successful dispatch.
Label removal does not cancel a dispatched round.
A failed dispatch retains its request label.
The owner token is necessary only for the optional Bugbot summon.

Deploy Seer's reusable workflows before the updated callers.
Propagate caller and configuration changes to existing repositories and CLI embedded templates.
Repositories without PR Lint need the owner to create `review:coderabbit` as a repository label.
Creating the label does not request a review.
