Shows the example read in `secretspec.toml` with `--reason`, which secretspec requires from an agent session.

## Plan

Change `secret-read-reason`: proposal, one ADDED delta (`secret-read-reason`), and tasks under `docs/changes/secret-read-reason/`.

## Changes

- Changes the comment in `templates/base/secretspec.toml.jinja` and the root `secretspec.toml`: the read is `secretspec run --reason "<why>" -- <command>`, and the bare `secretspec get <NAME>` example is gone, because it prints the value.
- Adds one `CHANGELOG.md` line.

## Testing

- With secretspec 0.21.1 in an agent session, a read without `--reason` exits 1 with "Accessing secrets requires a reason", and the same read with `--reason` succeeds. The probe used a scratch manifest with a synthetic value.
- `rune spec validate secret-read-reason` passes. The guarded push pipeline passed on this head.

## Release Notes

- The `secretspec.toml` comment shows a read that works in an agent session.
