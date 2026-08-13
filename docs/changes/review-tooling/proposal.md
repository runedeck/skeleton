---
decisions:
  - "DECK-0011 Review Tooling Adoption"
status: proposed
---

# Review Tooling

## Why

The review funnel carries every review semantic in hand-written shell and Python: lane order, settle detection, comment posting, and the summon of each external reviewer. Three tools it needs are already adopted: reviewdog posts findings, github-script drives the API, and labeler provisions labels. Two gaps remain. Every bot status comment is a bespoke API post, so a status that changes over time (the owner-review reminder, the autofix suggestion) accumulates duplicates instead of updating in place. And the funnel has no open-source reviewer lane: every finding comes from a hosted vendor or from the paid correctness lane itself.

## What Changes

- A fourth external lane, pr-agent, summoned by `review:pr-agent` and settled like the others. It runs the open-source PR-Agent `review` tool once per round against a model the org configures, so the funnel keeps a vendor-independent reviewer.
- Bot status comments update in place. A workflow-authored status carries a header marker, and the lane upserts it through create-or-update-comment, so a pull request shows one current status instead of a history of posts.
- Reviewdog, github-script, and labeler stay the adopted tools for findings, API scripting, and label provisioning. The decision record names all five, so no lane reimplements them.
- Lane definitions become data: a lane row names its summon, its settle signal, its finding source, and its labels, and the cascade iterates the rows.

## Capabilities

- review-ceremony (modified): the lane roster and the status-comment requirements.

## Impact

- runedeck/seer workflows: a new `review-pragent` lane, the autofix and dashboard comment paths, the cascade lane table, and label provisioning for `review:pr-agent`, `skip:pr-agent`, `ignore:pr-agent`, `issue:pr-agent`, and `stage:pr-agent`.
- Consumer stubs from this template: one caller stub for the new lane, delivered through `copier update`.
- Org secrets: one model credential for pr-agent.
