# Behavior proof: trusted-key-anchor

`record.sh` holds one scene per requirement of the `trusted-key-anchor` specification, in the grammar of
`docs/proofs/driver.sh`. `proof.cast` is its recording on 2026-09-21, exit 0. `proof.txt` is the transcript
`asciinema convert -f txt` wrote from it, and `proof.gif` the render.

Transcript digest (`shasum -a 256 proof.txt`): `044ce9761172e5c85433caad5888ec21361836069f0dd7699d464722e1c2316c`

The proof is offline: `TRUSTED_KEYS_OFFLINE` skips WKD and GitHub, and `TRUSTED_KEYS_CACHE` holds the owner's
public key (`tests/fixtures/owner-public-key.asc`) under the pinned fingerprint, under the primary, and under a
wrong pin, so the same bytes are admitted or dropped by the pin alone.

Re-record after a change to the scenes or the resolver:

```sh
asciinema rec --command "bash docs/proofs/trusted-key-anchor/record.sh" \
    --headless --window-size 100x30 --idle-time-limit 2 --overwrite --return proof.cast
agg --theme github-dark --font-size 11 --fps-cap 3 --last-frame-duration 3 proof.cast proof.gif
asciinema convert -f txt --overwrite proof.cast proof.txt
```

Where asciinema cannot open a pseudo terminal, `docs/proofs/cast.py` writes the same cast from the script's
output stream: `python3 docs/proofs/cast.py docs/proofs/trusted-key-anchor/record.sh proof.cast`.
