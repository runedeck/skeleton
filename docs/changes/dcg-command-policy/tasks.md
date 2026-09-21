## 1. Packs

- [x] 1.1 Seven packs under `templates/base/.dcg/packs/` and the root, ids `rune.<segment>`, headers naming SKEL-0009, prose through Vale
- [x] 1.2 Six pattern repairs from the adversarial review, each with a fixture in both directions
- [x] 1.3 `.dcg/fixtures.txt` (64 cases, rule attribution), `.dcg/test-config.toml`, `scripts/test-dcg-packs` on `dcg test --format json`, exit 0 under dcg 0.14.4
- [x] 1.4 `check-dcg-packs` hook in both prek configs, template paths in the skeleton trigger, skip printed, fails under `REQUIRE_GATES`
- [x] 1.5 `.dcg.toml` in template and root with per-rule `deny` for the six tool-free rules
- [x] 1.6 `tests/test_dcg_policy.py`: parity, ids, coverage, policy entries, live fixtures, wired into `quality.yaml`

## 2. Host

- [x] 2.1 Chezmoi `dot_config/dcg/config.toml.tmpl` renders `[policy.rules]` warnings per missing tool from `lookPath` (checked both ways with `chezmoi execute-template`)
- [x] 2.2 Chezmoi drops `toolpolicy.yaml`, `rtk.yaml`, `homebrew.yaml` (`.chezmoiremove`), `tests/test-dcg-packs.sh` keeps the host packs only
- [x] 2.3 Owner updated dcg to 0.14.4
- [ ] 2.4 Owner runs `chezmoi apply`, then `dcg config` lists no `rune.toolpolicy`, `rtk.passthrough`, or user `rune.homebrew`
- [x] 2.5 Live on 0.14.4 from a scratch git root: host pack-wide `warn` plus repository per-rule `deny` gives `outcome` `deny`. A host per-rule `warn` on the same key gives `warn` and the repository does not override it. A per-pack repository entry for an external pack is ignored

## 3. Installer

- [x] 3.1 `scripts/tool-versions` pins `rg` 15.2.0, `fd` 10.5.0, `yq` 4.53.6, `jq` 1.8.2, `dcg` 0.14.4 with digests for darwin and linux, amd64 and arm64 (publisher checksums for rg, yq, jq, dcg, computed for fd)
- [x] 3.2 `install-tools` gains `verified_binary`, `install_rg`, `install_fd`, `install_yq`, `install_jq`, `install_dcg`. `all_tools_match` and `verify_tools` know them. `tests/test_tool_install.py` covers them
- [ ] 3.3 A fresh-machine run of `install-tools` (CI quality job on the first push)

## 4. Proof

- [x] 4.1 `docs/proofs/dcg-command-policy/record.sh`, eleven scenes, recorded through `docs/proofs/cast.py` under dcg 0.14.4, exit 0, GIF and transcript filed (digest `d32ac416`), page `docs/specs/2026-09-22-dcg-policy-proof.html` in the workshop

## 5. Consumers

- [ ] 5.1 Copier sync of every consumer. In the deck delete `.dcg/packs/toolpolicy.yaml` and `repo.yaml` by hand and drop the deck commits `dcg-packs` and `dcg-split`
