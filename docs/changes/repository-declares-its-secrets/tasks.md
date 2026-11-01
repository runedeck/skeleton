# Tasks

## 1. Implementation

- [x] 1.1 `templates/base/secretspec.toml.jinja` and the root `secretspec.toml`
- [x] 1.2 `secretspec.toml` under `_skip_if_exists` in `copier.yaml`
- [x] 1.3 `secretspec-manifest` hook in both hook configs, and the pin-check exemption in `tests/test_tool_install.py`

## 2. Verification

- [x] 2.1 The hook rejects a declaration with a secret that has no description, and passes the committed one
- [x] 2.2 `tests/copier-update-canary` and `python3 -m unittest discover tests`
- [ ] 2.3 `copier update` in the consumers at the next batched sync

## 3. Record

- [ ] 3.1 Archive merges the delta into `docs/specs/`
