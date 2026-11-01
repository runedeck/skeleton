Seeds a `secretspec.toml` at every repository root and checks it in the commit stage without reading a value.

## Plan

Change `repository-declares-its-secrets`: proposal, one ADDED delta (`repository-declares-its-secrets`), and tasks under `docs/changes/repository-declares-its-secrets/`.

## Changes

- Adds `templates/base/secretspec.toml.jinja` and the root `secretspec.toml`: an optional `GH_TOKEN` and a `ci` profile whose provider chain is `env://` only.
- Adds `secretspec.toml` to `_skip_if_exists` in `copier.yaml`, so a consumer owns its list after the first copy.
- Adds the `secretspec-manifest` hook to `.pre-commit-config.yaml` and `templates/base/.pre-commit-config.yaml`. It runs `secretspec schema --file secretspec.toml` when the file changes and skips when `secretspec` is absent.
- Exempts `secretspec` from the pin check in `tests/test_tool_install.py`, because the owner installs it from the Brewfile.
- Adds two `CHANGELOG.md` lines.

## Testing

- `python3 -m unittest discover tests`: 148 pass. `test_review_configuration` needs PyYAML, which the system Python lacks, and passes under `uv run --with pyyaml`.
- `tests/copier-update-canary`: the rendered template passes every hook, `secretspec manifest` included.
- `secretspec schema` rejects a declaration with a secret that has no description and accepts the committed one.
- `rune spec validate repository-declares-its-secrets` passes. The guarded push pipeline passed on this head.

## Release Notes

- New repositories get a `secretspec.toml` that lists the secrets they read, and the commit stage checks it.
