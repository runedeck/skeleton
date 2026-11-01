---
status: proposed
---

# Repository declares its secrets

## Why

A consumer repository reads secrets in its scripts and checks, for example a GitHub token for `gh`, and nothing lists them. A new contributor learns which ones exist from a failure. SecretSpec declares the secrets a project needs in one `secretspec.toml` and reads them from a provider the user chooses: the Keychain, Proton Pass, `pass`, a dotenv file, or the CI environment ([SecretSpec][SECRETSPEC]). The owner chose one declaration file at each repository root.

## What Changes

- `templates/base/secretspec.toml.jinja` seeds a declaration named after the repository. It declares an optional `GH_TOKEN` and a `ci` profile that reads only the job environment.
- `copier.yaml` lists `secretspec.toml` under `_skip_if_exists`, so each consumer owns its list after the first copy.
- The root and template hook configs gain `secretspec-manifest`, which checks that the declaration parses and that every secret has a description. It reads no value and skips when `secretspec` is absent.
- `tests/test_tool_install.py` exempts `secretspec` from the pin check, because the owner installs it from Homebrew.
- The skeleton carries the same declaration at its own root.

## Capabilities

- repository-declares-its-secrets (new)

## Impact

- Two hook configs, one new template file, one root file, `copier.yaml`, one test, and `CHANGELOG.md`. Consumers receive the file and the hook through `copier update`. The cli's embedded skeleton copy picks it up at the next consumer sync.

[SECRETSPEC]: https://github.com/cachix/secretspec
