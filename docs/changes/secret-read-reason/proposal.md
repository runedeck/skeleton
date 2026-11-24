---
status: proposed
---

# Secret read reason

## Why

The comment at the top of `secretspec.toml` shows two reads: `secretspec run -- <command>` and `secretspec get <NAME>`. Neither gives `--reason`. SecretSpec 0.21.1 refuses both in an agent session, because its `require_reason` policy defaults to `agents` ([SecretSpec][SECRETSPEC]). An agent that copies the example gets "Accessing secrets requires a reason". A bare `secretspec get` also prints the value into the transcript.

## What Changes

- `templates/base/secretspec.toml.jinja` and the root `secretspec.toml` show one read, `secretspec run --reason "<why>" -- <command>`, and say that an agent session must give a reason.
- `CHANGELOG.md` gains one line.

## Capabilities

- secret-read-reason (new)

## Impact

- One template file, one root file, and `CHANGELOG.md`. `copier.yaml` seeds `secretspec.toml` once, so only new repositories get the new comment. An existing consumer edits its own copy: the deck does that in runedeck/deck#86.

[SECRETSPEC]: https://secretspec.dev/reference/configuration/
