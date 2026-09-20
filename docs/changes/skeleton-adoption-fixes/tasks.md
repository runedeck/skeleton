## 1. Implementation

- [x] 1.1 `scripts/check-authorship` judges a first adoption by the target's `authors.yaml` when `origin/main` has none, and prints it, in root and `templates/base`
- [x] 1.2 Remove `thread-resolver.yaml` from `templates/base` and from the skeleton's own workflows, with its zizmor entries
- [x] 1.3 Quote `description` as a basic string in `templates/rust/Cargo.toml` and `templates/python/pyproject.toml`

## 2. Verification

- [x] 2.1 `tests/test_authorship_integration.py` covers the first adoption, the target policy still binding, and a target without a policy
- [ ] 2.2 `prek run --all-files` and the pre-push stage pass in an isolated clone
- [ ] 2.3 seer deletes the no-op `thread-resolver.yaml` body once every consumer has dropped its caller (tracked in seer)
