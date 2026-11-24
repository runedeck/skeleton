# Tasks

## 1. Implementation

- [x] 1.1 The example read in `templates/base/secretspec.toml.jinja` and the root `secretspec.toml` gives `--reason`
- [x] 1.2 One `CHANGELOG.md` line

## 2. Verification

- [x] 2.1 SecretSpec 0.21.1 refuses a read without `--reason` in an agent session and accepts the same read with one
- [x] 2.2 `rune spec validate secret-read-reason` and the guarded push pipeline

## 3. Record

- [ ] 3.1 Archive merges the delta into `docs/specs/`
