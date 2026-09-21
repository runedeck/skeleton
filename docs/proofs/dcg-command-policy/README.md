# Behavior proof: dcg-command-policy

`record.sh` contains one scene per scenario of the `dcg-command-policy` delta specification, in the grammar
of `docs/proofs/driver.sh`. The candidate is this repository's `.dcg/packs/`, `.dcg.toml`, `.dcg/fixtures.txt`,
and `scripts/test-dcg-packs`, copied into a scratch git root, because dcg discovers `.dcg.toml` at the nearest
`.git` and a jj workspace has none. `proof.cast` is its recording on 2026-09-22 under dcg 0.14.4 through
`docs/proofs/cast.py`, exit 0. `proof.txt` is the transcript `asciinema convert -f txt` wrote from it, and
`proof.gif` the render.

Transcript digest (`shasum -a 256 proof.txt`): `d32ac416fcd1a105d5bc4a092c09e7b581f7ca325266d725a2ac5a2845dc345c`

Every scene asks dcg for a decision with `dcg test` or `dcg explain`. No denied command is executed. The policy
scenes select a host config with `DCG_CONFIG`, built from `.dcg/test-config.toml` plus one relaxation, so the
host packs of the recording machine never take part.

Scenes, in the order the specification lists them:

- Pack validates
- Denial states the replacement
- Pack edit admits a denied command
- Exemption removed
- Host without dcg
- Continuous integration without dcg
- Host relaxes a tool-free pack
- Host without rg
- Host without fd but with rg
- Fresh machine
- Continuous integration

Limits. "Fresh machine" shows the pinned versions and the digest-refusal test, not a download: the recording
machine has no network, and the first CI run of the quality job is the live install. "Continuous integration"
shows the workflow text, not a run. "Host relaxes a tool-free pack" also records that a host entry for the same
rule key is not overridden by the repository on dcg 0.14.4.

Re-record after a change to the scenes or the candidate:

```sh
python3 docs/proofs/cast.py docs/proofs/dcg-command-policy/record.sh docs/proofs/dcg-command-policy/proof.cast
agg --theme github-dark --font-size 11 --fps-cap 3 --last-frame-duration 3 proof.cast proof.gif
asciinema convert -f txt --overwrite proof.cast proof.txt
```
