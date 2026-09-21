## ADDED Requirements

### Requirement: KEYS names signers by fingerprint

The root `KEYS` file MUST hold one line per trusted signer: the keyword `signer`, a 40-character hexadecimal OpenPGP fingerprint, and one or more addresses that name where the key bytes come from. Comments start with `#`. The file MUST hold no key material. A seal or tag signature MUST verify against a fingerprint the file lists, as a primary or a subkey.

#### Scenario: Line shape

- **WHEN** `KEYS` holds `signer 29DD2145CE7A818929459B2649F08103D3DA399E git@martinzeman.net N4M3Z@users.noreply.github.com`
- **THEN** the resolver pins `29DD2145…` and fetches its bytes from the WKD of `git@martinzeman.net`, then from `github.com/N4M3Z.gpg`

#### Scenario: Malformed line

- **WHEN** a line has another keyword, a fingerprint that is not 40 hexadecimal characters, or no address
- **THEN** `scripts/trusted-keys` exits nonzero naming the line and imports nothing for it

### Requirement: Key bytes come from a pinned fetch

`scripts/trusted-keys` MUST resolve each address in order: the advanced Web Key Directory `openpgpkey.<domain>`, then the direct one on `<domain>`, and for a GitHub address `https://github.com/<user>.gpg`. It MUST import the bytes into a scratch keyring, MUST admit them only when the pinned fingerprint appears there as a primary or subkey, and MUST discard bytes that do not. After every address, a cache directory `TRUSTED_KEYS_CACHE/<fingerprint>.asc` MUST be tried, and `--offline` MUST skip the network.

#### Scenario: Fetched key does not carry the pin

- **WHEN** a source returns a key whose fingerprints do not include the pinned one
- **THEN** the key is not imported, the next source is tried, and the line fails when none carries the pin

#### Scenario: WKD unreachable

- **WHEN** `openpgpkey.<domain>` does not answer and the line names a GitHub address second
- **THEN** the key resolves from `github.com/<user>.gpg` and the pin still decides

### Requirement: One resolver for every signature check

`scripts/verify-seal`, `scripts/verify-release-tag`, and `rune sign` MUST build their keyring through `scripts/trusted-keys` from the `KEYS` of the protected branch, never from a keyring on the machine.

#### Scenario: Seal check in CI

- **WHEN** `owner-seal` runs `verify-seal`
- **THEN** the keyring holds exactly the keys `KEYS` pins, resolved at run time
