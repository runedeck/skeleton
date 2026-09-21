---
title: "KEYS pins fingerprints and resolves bytes through WKD"
description: "The root KEYS file names trusted signers by fingerprint and the addresses their bytes come from, and scripts/trusted-keys fetches and admits only bytes that carry the pin."
type: adr
category: security
tags:
    - skeleton
    - signing
    - openpgp
status: proposed
created: 2026-09-21
updated: 2026-09-21
author: "@N4M3Z"
project: skeleton
related:
    - "SKEL-0005 Verified Remote Execution"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1"]
informed: []
upstream:
    - "https://github.com/N4M3Z/openpgpkey"
    - "https://www.apache.org/info/verification.html"
change: trusted-key-anchor-format
---

# KEYS pins fingerprints and resolves bytes through WKD

## Context and Problem Statement

The ceremony trusts a signature only when its fingerprint is in the repository's `KEYS`, read from the protected branch, so the trusted set is itself under review. The file followed the Apache convention and held the armored public key block. Fifteen repositories carried the same 2.8 KB, no diff of it was readable, and rotation meant fifteen sealed changes of opaque bytes.

## Considered Options

1. Keep the armored blocks (Apache `KEYS`).
2. Fingerprints in `KEYS`, bytes bundled beside it under `.keys/`.
3. Fingerprints in `KEYS`, bytes fetched from a keyserver.
4. Fingerprints in `KEYS`, bytes fetched from the owner's Web Key Directory with GitHub as fallback, every fetch checked against the pin.

## Decision Outcome

Option 4. The pin stays under review, which is the property the file exists for. The bytes come from a source the owner controls (`openpgpkey.martinzeman.net`, itself rendered from a reviewed fingerprint list), with `github.com/<user>.gpg` behind it and a local cache for offline signing. A fetch that does not carry the pin is discarded, so no source is trusted, only the fingerprint. Keyservers are gone or strip identities (option 3). Bundled blocks (option 2) keep the fifteen-copy problem for the bytes.

The format MUST keep these rules:

- `signer <fingerprint> <address>...`, one per line, comments with `#`, no key material.
- Every fetched key is admitted only when the pinned fingerprint is one of its primary or subkey fingerprints.
- `verify-seal`, `verify-release-tag`, and `rune sign` build their keyring through the one resolver.

## Consequences

- A key rotation is one line per repository, and the line is readable in review.
- CI depends on the WKD host or GitHub answering. The pin makes an outage a failed check, never a wrong acceptance.
- The 2016 RSA key `7206934F96D69695261387EA52D89102B83379DB` is not a signer: it is still used on an older machine but never sealed a change, so it does not appear in any `KEYS`.
