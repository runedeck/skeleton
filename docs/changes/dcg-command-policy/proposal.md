---
adr: docs/changes/dcg-command-policy/adr.md
status: proposed
decisions: ["dcg enforces the shell policy, one pack per rule, and the repository only tightens"]
---

# dcg command policy

## Why

The deck has carried two repo-local dcg packs from DECK-0010 on (`toolpolicy.yaml`, `repo.yaml`), and the owner's dotfiles carry four more. Each mixed several rules, so a denial named a pack that said nothing about which rule fired, and a rule change touched a file with unrelated rules. The packs redirected to `rg`, `fd`, `yq`, and `jq` without any installer providing them, so a host without `rg` got a hard block that told it to run a tool it did not have. Nothing tested that a pack edit kept its decisions. And every runedeck repository needs the same policy, which makes the skeleton the home, not the deck.

## What Changes

- `templates/base/.dcg/packs/` and the skeleton root gain seven packs, one per rule: `search`, `parsers`, `secrets`, `push`, `provenance`, `rtk`, `homebrew`, ids `rune.<segment>`. Severities come from the deck packs. Six patterns are repaired on the way: the example-file exemption admitted an example file beside a real `.env`, the dry-run exemption matched a branch named `fix--dry-run`, a `--no-pager` or quoted `-C` global option escaped the push rule, the brew rule denied `||` and missed a path-qualified `brew`, the provenance rule denied a copy out of `.provenance/` and allowed `touch` into it, and the parser rule is split into a YAML and a JSON rule.
- `.dcg/fixtures.txt` pins a denied command per rule and a permitted command per exemption, each with its rule. `scripts/test-dcg-packs` replays them through `dcg test --format json` under the isolated `.dcg/test-config.toml`. The `check-dcg-packs` prek hook validates each pack and runs the fixtures on every pack edit. `tests/test_dcg_policy.py` pins root and template parity, ids, fixture coverage, and the policy entries.
- `.dcg.toml` at the repository root pins each tool-free rule to `deny`. The host config may relax the rules of one missing tool to a warning. The owner's chezmoi template renders that relaxation per tool from `lookPath` and drops the three user packs that duplicated repository packs.
- `scripts/install-tools` and `scripts/tool-versions` gain pinned `rg`, `fd`, `yq`, `jq`, and `dcg`.

## Capabilities

### New Capabilities

- `dcg-command-policy`: the pack layout, the fixtures, the repository policy file, and the installer additions.

### Modified Capabilities

None.

## Impact

Every consumer takes the seven packs, the fixtures, the script, the hook, and `.dcg.toml` through `copier update`. The deck drops `toolpolicy.yaml` and `repo.yaml` in that sync. A consumer with a local pack keeps it beside the template packs. `.dcg.toml` and `[policy]` need dcg 0.14 or newer. dcg 0.5.x loads the packs and ignores both. There the packs deny at every severity.
