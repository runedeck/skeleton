# Review Lanes Configuration

The dashboard state of the external review lanes is part of the ceremony: a wrong toggle reintroduces ambient reviewing, comment storms, or bot-driven merges no repository file can prevent. This guide records the required configuration for every lane and the reasoning behind each choice. It is destined for the provisioning deck; until that exists, it lives here beside the specs it serves.

The funnel this configuration serves: a pull request passes cursor, then macroscope, then runeseer, and only then reaches the owner. Each stage spends only after the previous stage has settled clean.

## Cursor Bugbot (cursor.com/dashboard → Bugbot)

Bugbot settings resolve personal → repository → installation → team, where an installation is the GitHub App connection to one account or organization. Configure at the tiers named below and leave repository and personal dropdowns on "Use Installation Default": one source of truth, inherited by every current and future scaffolded repository. No behavioral toggle reads from the repository; repo files contribute review guidance only (`.cursor/BUGBOT.md`, root plus nested).

Preferences page (the team tier; on an individual plan this page is the top tier and "Use Team Default" resolves here):

| Setting | Required value | Reason |
| --- | --- | --- |
| Trigger Mode | Only when mentioned | Stage 1 fires when the review cascade posts `bugbot run`; ambient per-push reviewing is the largest storm source |
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

Bugbot reads `.cursor/BUGBOT.md` from the repository root. It supports no include syntax, so the file stays self-contained; nested `.cursor/BUGBOT.md` files scope guidance to subtrees.

## Macroscope, workspace level (macroscope.com → Settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Product Overview | Filled (text below) | Context improves every summary and review |
| Custom Agent Instructions | Empty | Slack agent unused |
| Excluded commit authors | Empty | Nearly all commits are agent-authored; excluding those identities would hollow out summaries and status reporting |
| Web search | On | Reviews may ground claims against upstream documentation |

Product Overview text:

> runedeck builds rune, a CLI that assembles and deploys agent skills, rules, and hooks ("runes") across AI coding harnesses. Repositories follow a review ceremony: model-authored commits, owner-authored pull requests, label-summoned review lanes, and owner-signed release tags. The skeleton repository is the template every other repository is scaffolded from; changes to templates/ propagate to every scaffolded repository.

## Macroscope, per repository (Repos → select all → Edit settings)

| Setting | Required value | Reason |
| --- | --- | --- |
| Correctness | Off, with Always-Review label `review:macroscope` | Stage 2 fires only when summoned by the cascade or the owner |
| Detection Mode | Prefer Coverage | False positives cost adjudication time, not owner attention: runeseer judges every finding before anything reaches a human |
| Check Run Agents | On | Enables in-repo `.macroscope/` agents as check runs; ceremony-specific checks can be authored there |
| Review Draft PRs | Off | Draft iteration is free |
| Automatically Merge Macroscope's PRs | Off | Nothing merges itself in this org; every merge is the owner's action |
| Auto-assign Reviewer | Off | CODEOWNERS routes review |
| Skip Dependabot | Off | No Dependabot; revisit if it arrives |
| Review Cross-Repo PRs | On | Fork pull requests must pass stage 2 or the contributor funnel dead-ends after cursor |
| Skip PRs by Author | Empty | No exempt authors |
| Skip PRs by Labels | `review:skip` | The ceremony waiver label silences the lane |
| Approvability | Off | Earned approval is runeseer's alone; two approval authorities would blur the gate |
| Release Ref Patterns | `v*` | Matches the signed-tag release ceremony |
| Status features | On | Commit summaries and digests cost nothing in review terms |

## PR description markers

Macroscope posts pull request summaries into the description instead of a comment when the body carries its markers. The pull request body template includes:

```text
<!-- Macroscope's pull request summary starts here -->
<!-- Macroscope's pull request summary ends here -->
```

One fewer comment per pull request, and the summary lands where a reader looks first.

## Check names and secrets

The lanes run as reusable workflows called from `runedeck/seer`, so most check contexts compose as `caller job / called job` — the cascade's check is **`cascade / walk`**. The correctness lane is the exception: a caller-side mirror job reports under the stable name **`review/correctness`**, which is the context the canon names; never point a ruleset at its composed form. Never mark `review/correctness` as a *required* status check at all: summoned lanes cannot be universally required (an unsummoned pull request would block forever, and a skipped check would count as satisfied), so the merge gate is the earned approval under required reviews, and the check exists for visibility. The org secrets (`RUNESEER_APP_ID`, `RUNESEER_APP_KEY`, `RUNEWRIGHT_APP_ID`, `RUNEWRIGHT_APP_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`) must have **All repositories** visibility before any scaffolded repository summons a lane; a caller with unreadable secrets fails at first summon, not at scaffold time.

## Verification

After configuring, open a draft pull request in any scaffolded repository and push twice: no lane may comment. Mark it ready and apply `review`: cursor must answer the cascade's `bugbot run` comment, macroscope must answer its label, and runeseer must run only after both settle.
