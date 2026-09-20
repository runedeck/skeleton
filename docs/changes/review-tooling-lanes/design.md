# Review Tooling Design

## Approach

PR-Agent runs in command mode from a pinned container image, not as its GitHub Action. The Action mode reviews on pull request events, which the ceremony forbids: a lane runs only when a maintainer applies its label. Command mode runs one `review` call per summon and posts through the workflow token, so the lane fits the existing summon, settle, and blocker mechanics unchanged.

Status comments use the peter-evans pair, find-comment and create-or-update-comment, keyed by a header marker. The sticky-comment action was the alternative. The pair won because find-comment also serves the lanes that only read a marker, and both actions carry the lowest open-issue counts in the candidate set.

## Structure

- `review-pragent.yaml` (seer): the reusable lane body. Scope check, one PR-Agent run, label consumption, blocker on provider failure.
- `review-entry-pragent.yaml` (template, root and `templates/base`): the caller stub.
- `review-cascade.yaml` (seer): the lane table gains a pr-agent row between macroscope and the adjudicator.
- `review-correctness.yaml` (seer): the trusted lane inputs admit PR-Agent comments, identified by the workflow token identity plus the PR-Agent review header.
- `autofix-comment.yaml` and `dashboard.sh` (seer): the suggestion and the owner reminder upsert instead of posting anew.

## Risks

- PR-Agent needs an API-key credential, which the Claude Code subscription token is not. The org must provision one model key. The tasks name the secret and stop the lane with a clear fault when it is absent.
- The container image must be pinned by digest, or the lane trusts a mutable tag. The task pins the digest and the canary round proves it.
- PR-Agent posts under the workflow token identity, which other lanes also use. The correctness lane admits those comments only with the PR-Agent header, so a stray workflow comment never counts as a finding.
- A fourth lane lengthens the funnel. PR-Agent's review is one model call, so the budget is seconds, and `skip:pr-agent` stands it down.
