# Review Lanes Configuration

The dashboard state of the external review lanes is part of the ceremony: a wrong toggle reintroduces ambient reviewing, comment storms, or bot-driven merges no repository file can prevent. This guide records the required configuration for every lane and the reasoning behind each choice. It is destined for the provisioning deck; until that exists, it lives here beside the specs it serves.

The funnel this configuration serves: a pull request passes cursor, then macroscope, then runeseer, and only then reaches the owner. Each stage spends only after the previous stage has settled clean.

## Cursor Bugbot (cursor.com/dashboard → Bugbot)

| Setting | Required value | Reason |
| --- | --- | --- |
| Trigger Mode | Only when mentioned | Stage 1 fires when the review cascade posts `bugbot run`; ambient per-push reviewing is the largest storm source |
| Incremental Review | On | Each round reviews only the delta since the last; without it every round re-flags the full backlog |
| Review Draft PRs | Off | Draft iteration is free by ceremony rule |
| Autofix Mode | Off | Autofix in this org is suggestion-only through runewright; a bot pushing commits breaks commit attribution |
| PR Summaries | On | One self-editing comment; the risk score block rides along |
| Post PR risk score | On | Cheap prioritization signal in the summary |
| Bugbot Effort Levels | Smart | Adequate; the adjudicating lane catches what a cheaper pass misses |
| Repository Rules | Seed from `.cursor/BUGBOT.md` learnings | Dashboard rules persist across pull requests; the in-repo `BUGBOT.md` carries the same suppressions for transparency |

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

## Verification

After configuring, open a draft pull request in any scaffolded repository and push twice: no lane may comment. Mark it ready and apply `review`: cursor must answer the cascade's `bugbot run` comment, macroscope must answer its label, and runeseer must run only after both settle.
