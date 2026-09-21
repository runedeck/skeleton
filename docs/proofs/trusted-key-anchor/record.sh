#!/usr/bin/env bash
# Driver for a recorded acceptance proof of the trusted-key-anchor
# specification. asciinema (or docs/proofs/cast.py) records this script.
# The grammar lives in ../driver.sh; edit only the scenes at the end.
# shellcheck source=../driver.sh
. "$(dirname "$0")/../driver.sh"

printf '\033[2J\033[H'

ROOT=$(cd "$(dirname "$0")/../../.." && pwd) || exit 1
RUNE=${RUNE:-rune}
export RUNE
PROOF_HOME=$(mktemp -d "${TMPDIR:-/tmp}/trusted-key-anchor.XXXXXX")
trap 'command rm -rf "$PROOF_HOME"' EXIT
cd "$PROOF_HOME" || exit 1

# The proof is offline: the owner's public key sits in a cache directory, the
# way rune sign keeps it for signing without a network. The resolver is the
# template's own script, and the KEYS files are written here scene by scene.
export TRUSTED_KEYS_OFFLINE=1
export TRUSTED_KEYS_CACHE=$PROOF_HOME/cache
mkdir -p "$TRUSTED_KEYS_CACHE"
for pin in 29DD2145CE7A818929459B2649F08103D3DA399E 786F851F8AE345F5A98B822EC92F47D08BCD9F72 0000000000000000000000000000000000000000; do
    rsync -a "$ROOT/tests/fixtures/owner-public-key.asc" "$TRUSTED_KEYS_CACHE/$pin.asc"
done
# The viewer sees repository-relative paths, as the owner would type them.
mkdir -p scripts
rsync -a "$ROOT/scripts/trusted-keys" "$ROOT/scripts/verify-seal" scripts/
rsync -a "$ROOT/KEYS" KEYS.repo
resolver="scripts/trusted-keys"

scenario "KEYS names signers by fingerprint"
comment "The trust anchor is one readable line: a pin and the addresses the bytes come from. No key block."
run "cat KEYS" "cat KEYS.repo"
expect "^signer 29DD2145CE7A818929459B2649F08103D3DA399E git@martinzeman.net"
expect_not "BEGIN PGP"

scenario "The pin admits the key that carries it"
comment "The pinned fingerprint is a signing subkey; the resolver imports its primary and reports the source."
printf 'signer 29DD2145CE7A818929459B2649F08103D3DA399E git@martinzeman.net\n' > KEYS
run "$resolver --keys KEYS --homedir home1"
expect "^29DD2145CE7A818929459B2649F08103D3DA399E cache:"
run "gpg --homedir home1 --no-autostart --with-colons --fingerprint --list-keys | awk -F: '\$1==\"fpr\"{print \$10}'"
expect "786F851F8AE345F5A98B822EC92F47D08BCD9F72"

scenario "Fetched bytes that do not carry the pin are dropped"
comment "The cache answers with a real key, but not the pinned one: nothing is imported and the line fails."
printf 'signer 0000000000000000000000000000000000000000 git@martinzeman.net\n' > KEYS
run "$resolver --keys KEYS --homedir home2 || echo \"exit \$?\""
expect "could not resolve 0000000000000000000000000000000000000000"
expect "exit 1"
run "gpg --homedir home2 --no-autostart --with-colons --fingerprint --list-keys 2>/dev/null | grep -c '^fpr:' || true"
expect "^0$"

scenario "Malformed lines fail closed"
comment "A keyword typo, a short fingerprint, or a missing address is an error, never an empty trusted set."
printf 'trusted 29DD2145CE7A818929459B2649F08103D3DA399E git@martinzeman.net\n' > KEYS
run "$resolver --keys KEYS --homedir home3 || echo \"exit \$?\""
expect 'found trusted'
expect "exit 1"
printf 'signer 29DD2145CE7A818929459B2649F08103D3DA399E\n' > KEYS
run "$resolver --keys KEYS --homedir home3 || echo \"exit \$?\""
expect "has no address"

scenario "verify-seal builds its keyring through the resolver"
comment "The seal verifier no longer imports KEYS itself: one resolver, one rule, for seals, tags, and rune sign."
run "grep -n 'trusted-keys' scripts/verify-seal"
expect "trusted-keys"
