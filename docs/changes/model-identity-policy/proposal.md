---
adr: "docs/decisions/DECK-0001.md"
status: proposed
---
# Model Identity Policy

## Why

Accept new model versions without editing a model catalog for every release.

Pushback outcome: **Survivor**.
The existing commit-attribution capability requires exact model entries.
No active change in this workspace covers version-independent attribution.
This change modifies that capability rather than creating a second validator.

The [decision record](../../decisions/DECK-0001.md) compares the alternatives.

## What Changes

- Replace per-version membership with a stable model identity format and approved harness domains.
- Preserve exact human identities and vendor trailer aliases.
- Share identity validation between local checks, CI, and workspace provisioning.
- Preserve the trusted-base review boundary.

## Capabilities

- `commit-attribution` (modified)

## Impact

- Skeleton root and base template attribution scripts, workflows, policy files, and tests.
- Base template workspace identity resolution.
- Consumer updates through Copier after the Skeleton release.
- CLI embedded templates require a later release update.
