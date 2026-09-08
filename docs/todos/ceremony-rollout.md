# Ceremony rollout

- [x] Transfer the runewright app registration from the owner's personal account to the runedeck org, where runeseer already lives (app settings → Advanced → Transfer ownership; installations and org secrets survive)

- [ ] Org operations belong to `runedeck/seer`, the org's review and observation center: the org-wide veto monitor with its "Awaiting owner review" queue issue, and the reusable lane workflows (review-correctness, review-cascade, autofix pair, congrats, issue-dedup) with their scripts. `runedeck/.github` keeps only the org profile and community defaults. The skeleton is the archetype only: its workflows — and `templates/base` pr-lint, quality, congrats — are thin callers pinned at `runedeck/seer/...@main`, later at seer's signed tags, and the manifest guards only callers and genuinely local files
- [ ] After the first signed skeleton release tag: publish `.pre-commit-hooks.yaml` at the skeleton root and shrink the scaffolded `.pre-commit-config.yaml` to builtins plus `repo: https://github.com/runedeck/skeleton` pinned to that tag
- [ ] Author `.macroscope/` check-run agents for ceremony-specific checks
- [ ] Verify Bugbot answers a runewright-posted `bugbot run` comment; if it ignores bot comments, the cascade's stage 1 needs the owner's own comment and the guide changes accordingly
- [ ] Promote the drafts-provenance machinery into rune or retire the `.provenance/drafts/` convention entirely (deck todo 2026-07-19 tracks the rune side)
- [ ] Move the review-lanes configuration guide into the provisioning deck once it exists
- [ ] Workflow linting in seer's quality job (actionlint, hash-verified install) so expression and embedded-shell mistakes surface before review
- [x] Release workflow verifies the `v*` tag signature against root `KEYS` before publication and compiles merged Release Notes sections into the release body
- [ ] rune mdschema enforces the declared word_count and lists constraints; today only heading presence is checked, so the schemas' constraints are documentation
