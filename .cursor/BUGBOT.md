# Review guidance for this repository

This repository is the runedeck skeleton: empty-repo archetypes under
`templates/`, canonical ceremony specifications under `docs/specs/`, and the
org's review machinery under `.github/workflows/`. Template files contain
`${VARIABLE}` placeholders resolved at render time. Unresolved placeholders
are not bugs.

Suppressions, learned from past rounds:

- Pagination on deliberately bounded sets (a repo's own workflows, a
  manifest's file list) is not a finding. Flag pagination only where the set
  genuinely grows without bound.
- Do not re-report a finding another reviewer already posted on this pull
  request, and do not re-report a finding already addressed by a later
  commit. Check the commit history first.
- Severity floor: report medium and above inline. Fold nits into one
  comment.
- `language: system` prek hooks assume the tool is installed by INSTALL.md
  or CI. A missing-binary scenario is a finding only when no install path
  documents the tool.
