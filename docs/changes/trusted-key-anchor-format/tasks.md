# Tasks

## 1. Format and resolver

- [x] 1.1 `KEYS` as `signer <fingerprint> <address>...` in `templates/base` and the root
- [x] 1.2 `scripts/trusted-keys`: WKD advanced, WKD direct, GitHub, cache, pin check per fetch, `--offline`
- [x] 1.3 `verify-seal` and `verify-release-tag` build their keyring through it

## 2. Verification

- [x] 2.1 `tests/trusted-keys`: subkey pin, primary pin, wrong pin refused, malformed lines refused, two signers
- [x] 2.2 `tests/verify-seal` passes with the new format (40 checks)
- [x] 2.3 Live: the real `KEYS` resolves `29DD2145…` from `github.com/N4M3Z.gpg` while WKD is undeployed
- [x] 2.4 Both prek stages in an isolated clone
- [x] 2.5 Recorded proof under `docs/proofs/trusted-key-anchor/`, one scene per requirement

## 3. Follow-through

- [ ] 3.1 cli `rune sign` reads `KEYS` through `scripts/trusted-keys`
- [ ] 3.2 Consumers take the format through `copier update`
- [ ] 3.3 Archive moves `adr.md` to `docs/decisions/` as SKEL-0009
