# Review Lanes Configuration

The dashboard state of the external review lanes is part of the ceremony: a wrong toggle reintroduces ambient reviewing, comment storms, or bot-driven merges no repository file can prevent. This guide records the required configuration for every lane and the reasoning behind each choice. It is destined for the provisioning deck; until that exists, it lives here beside the specs it serves.

The review funnel is the ordered workflow this configuration serves: it triggers cursor, then macroscope, then runeseer, and presents the pull request to the owner only after those lanes settle clean. Each stage spends only after the previous stage has settled clean.

## Cursor Bugbot (cursor.com/dashboard → Bugbot)

Bugbot settings resolve personal → repository → installation → team, where an installation is the GitHub App connection to one account or organization. Configure at the tiers named below and leave repository and personal dropdowns on "Use Installation Default": one source of truth, inherited by every current and future scaffolded repository. No behavioral toggle reads from the repository; repo files contribute review guidance only (`.cursor/BUGBOT.md`, root plus nested).

Preferences page (the team tier; on an individual plan this page is the top tier and "Use Team Default" resolves here):

| Setting | Required value | Reason |
| --- | --- | --- |
| Trigger Mode | Manual only | The cascade posts one standalone `@cursor review` comment per round; ambient pushes do not spend Cursor outside the ordered lanes. Cursor drops bot-authored trigger comments, so the cascade posts the comment with the owner-minted `RUNEWRIGHT_GITHUB_TOKEN` org secret (fine-grained, issues write only) |
| Incremental Review | On | Each round reviews only the delta since the last; without it every round re-flags the full backlog |
| Bugbot Effort Levels | Smart | Adequate; the adjudicating lane catches what a cheaper pass misses |

runedeck installation page:

| Setting | Required value | Reason |
| --- | --- | --- |
| Auto-Enable for New Repositories | On | Scaffolded repositories inherit the lane without a dashboard visit |
| Review Draft PRs | Off | Draft iteration is free by ceremony rule |
| Run Once Per PR | Off | It would ignore new commits entirely; incremental review is the right delta mechanism |
| Post PR Summary | Description mode if the dropdown offers one, else As Comment | The description is where a reader looks first, and it spares a comment |
| Post PR risk score | On | Cheap prioritization signal in the summary |
| Automatically Learn Rules | On | Suppressions accumulate across pull requests without re-teaching |
| Autofix Behavior | Off | Autofix in this org is suggestion-only through runewright; a bot pushing commits breaks commit attribution |

A terminal cursor failure adds `issue:cursor`, a terminal macroscope failure adds `issue:macroscope`, and a correctness round that produces no verdict adds `issue:rune`. The workflow token applies these labels without emitting another cascade event, and the cascade refuses to re-summon a blocked lane. Fix the provider or billing problem before removing a blocker; a successful current-head round clears its lane's blocker automatically.

Settled stages carry `stage:cursor` and `stage:macroscope`. Later rounds skip a settled stage while its findings stay resolved, so fix rounds spend only on the adjudicator. Remove a stage label to force that stage to re-run; the adjudicator's verdict does the same when a delta warrants it.

Bugbot reads `.cursor/BUGBOT.md` from the repository root. It supports no include syntax, so the file stays self-contained; nested `.cursor/BUGBOT.md` files scope guidance to subtrees.

## Macroscope, workspace level (macroscope.com → Settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Product Overview | Filled (text below) | Context improves every summary and review |
| Custom Agent Instructions | Empty | Slack agent unused |
| Excluded commit authors | Empty | Nearly all commits are agent-authored; excluding those identities would hollow out summaries and status reporting |
| Web search | On | Reviews may ground claims against upstream documentation |

Product Overview text:

> runedeck builds rune, a CLI that assembles and deploys agent skills, rules, and hooks ("runes") across AI coding harnesses. Repositories follow a review ceremony: model-authored commits, owner-authored pull requests, automatically ordered review lanes, and owner-signed release tags. The skeleton repository is the template every other repository is scaffolded from; changes to templates/ propagate to every scaffolded repository.

## Macroscope, per repository (Repos → select all → Edit settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Correctness | Off ambient; the `review:macroscope` label trigger only | The `review:macroscope` label triggers Macroscope after cursor settles clean; ambient runs would spend it ahead of the cheaper layer and outside the ordered workflow |
| Detection Mode | Prefer Precision | Ambient reviewing trades coverage for signal; runeseer still adjudicates whatever it reports |
| Check Run Agents | On | Enables in-repo `.macroscope/` agents as check runs; ceremony-specific checks can be authored there |
| Review Draft PRs | Off | Draft iteration is free |
| Automatically Merge Macroscope's PRs | Off | Nothing merges itself in this org; every merge is the owner's action |
| Auto-assign Reviewer | On | Routes a reviewer onto PRs opened without one |
| Skip Dependabot | Off | No Dependabot; revisit if it arrives |
| Review Cross-Repo PRs | On | Fork pull requests must pass stage 2 or their review stops after cursor |
| Skip PRs by Author | Empty | No exempt authors |
| Skip PRs by Labels | `review:skip` | The ceremony waiver label silences the lane |
| Approvability | On, medium threshold | Advisory beneath the required verdict checks: its approval cannot outrank a red `review/correctness`, and the owner's merge click stays the final gate |
| Release Ref Patterns | `v*` | Matches the signed-tag release ceremony |
| Status features | On | Commit summaries and digests cost nothing in review terms |

## PR description markers

Macroscope posts pull request summaries into the description instead of a comment when the body carries its markers. The pull request body template includes:

```text
<!-- Macroscope's pull request summary starts here -->
<!-- Macroscope's pull request summary ends here -->
```

One fewer comment per pull request, and the summary lands where a reader looks first. Authored Changes bullets follow the same register the summarizer uses: verb-first, factual, file-anchored, claims the diff upholds.

## Check names and secrets

Check contexts, identities, and the org secret roster live in the skeleton's [ARCHITECTURE.md](../../ARCHITECTURE.md); this guide carries only the dashboard state. The rule worth repeating here: `review / cascade` and `review/correctness` are required status checks in the owner-veto ruleset, and the verdict mirror fails closed, so a head with no verdict stays red until a funnel round completes; fork pull requests merge through the owner's admin bypass.

## Verification

After configuring, open a draft pull request in any scaffolded repository and push twice: no lane may comment while it is a draft. Mark it ready: the cascade starts by itself, posts `@cursor review`, waits for cursor to settle, summons macroscope, and lets runeseer adjudicate last. `review/correctness` must hold red until the verdict lands and the clean verdict must post the earned approval. Apply `review` only to re-summon after fixes.
