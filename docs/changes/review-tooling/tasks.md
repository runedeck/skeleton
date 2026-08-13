## 1. Implementation

- [ ] 1.1 Add the lane table to the shared definitions file and make the cascade iterate it
- [ ] 1.2 Add the `review-pragent` lane body with the image pinned by digest and the model key secret named
- [ ] 1.3 Provision the five pr-agent labels through labeler
- [ ] 1.4 Admit PR-Agent comments as trusted lane inputs in the correctness lane
- [ ] 1.5 Upsert the autofix suggestion through create-or-update-comment
- [ ] 1.6 Upsert the owner reminder in the dashboard sweep
- [ ] 1.7 Add the caller stub to the template root and `templates/base`

## 2. Verification

- [ ] 2.1 `rune spec validate review-tooling` passes
- [ ] 2.2 actionlint and zizmor pass on every changed workflow
- [ ] 2.3 One live pr-agent round on a fixture pull request settles and consumes its label
- [ ] 2.4 A second dashboard sweep updates the reminder instead of posting a second one
