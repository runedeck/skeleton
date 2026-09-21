---
adr: docs/changes/trusted-key-anchor-format/adr.md
status: proposed
decisions: ["KEYS pins fingerprints and resolves bytes through WKD"]
---

# Trusted key anchor format

## Why

`KEYS` held a 2.8 KB armored key block in every repository. The block is the same bytes fifteen times, no reviewer reads an armor diff, and a key rotation is a fifteen-file change. The Apache convention the file copies keeps blocks because Apache releases verify offline for years, while the ceremony verifies in CI with network and signs locally with a cache. The owner now publishes keys through a Web Key Directory on `openpgpkey.martinzeman.net` (`N4M3Z/openpgpkey`), which every OpenPGP client resolves by address.

## What Changes

- `KEYS` becomes fingerprint lines: `signer <fingerprint> <address>...`. The first line pins the YubiKey signing subkey `29DD2145CE7A818929459B2649F08103D3DA399E` with `git@martinzeman.net` and `N4M3Z@users.noreply.github.com` as sources.
- `scripts/trusted-keys` (template and root) resolves a `KEYS` file into a gpg homedir: WKD advanced, WKD direct, GitHub, then a cache, each fetch admitted only when it carries the pin.
- `verify-seal` and `verify-release-tag` build their keyring through it. `tests/trusted-keys` covers the pin logic offline with the owner's public key as the fixture.

## Capabilities

### New Capabilities

- `trusted-key-anchor`: the `KEYS` format, the pinned fetch, and the single resolver.

### Modified Capabilities

- `owner-release-ceremony`: the trust anchor is the fingerprint list, not a key block.

## Impact

- Consumers receive the new `KEYS`, `scripts/trusted-keys`, and `verify-seal` through `copier update`. Until then their old `KEYS` blocks still work with their old verifiers.
- `rune sign` (cli) reads `KEYS` through `gpg --import`, so it needs the same resolver, a cli change.
- CI gains network fetches to `openpgpkey.martinzeman.net` and `github.com`, and the pin makes both untrusted byte sources.
