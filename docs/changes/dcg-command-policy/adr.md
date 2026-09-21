---
title: "dcg enforces the shell policy, one pack per rule, and the repository only tightens"
description: "Every runedeck repository carries dcg packs under .dcg/packs/, one per rule it enforces, with fixtures that pin each decision, a tighten-only .dcg.toml at the root, and the host config as the only place a pack relaxes."
type: adr
category: architecture
tags:
    - skeleton
    - dcg
    - shell-policy
status: proposed
created: 2026-09-22
updated: 2026-09-22
author: "@N4M3Z"
project: skeleton
related:
    - "SKEL-0003 Shared Pinned Lint Tools"
    - "SKEL-0007 Base-Defined Checks and Failing Canaries"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5-1"]
informed: []
upstream:
    - "https://github.com/Dicklesworthstone/destructive_command_guard"
change: dcg-command-policy
---

# dcg enforces the shell policy, one pack per rule, and the repository only tightens

## Context and Problem Statement

Rules such as UseEfficientCLI and VersionControl tell an agent which shell commands to use. A rule is text, and an agent that skims it runs `grep`, `git push`, or `sed -i` on a provenance sidecar anyway. dcg (Destructive Command Guard) evaluates every agent shell command before it runs, across Claude Code, Codex, Gemini, Cursor, and pi, from one binary and one set of YAML packs. The deck adopted it in DECK-0010 with two packs that each mixed several rules. The owner's dotfiles carried four more. A denial named a pack that said nothing about the rule, a rule change touched unrelated rules, the packs demanded tools no installer installed, and nothing checked that a pack edit kept its decisions. The policy is the same in every runedeck repository, so the deck was the wrong home.

## Considered Options

1. Keep the rules as prose only and rely on review to catch a wrong command.
2. Harness-specific hooks (a Claude Code PreToolUse script, a Codex equivalent), one implementation per harness.
3. dcg packs in the skeleton, one pack per rule, decisions pinned by fixtures, the repository able to tighten and only the host able to relax.

## Decision Outcome

Option 3. A denial with the replacement in its text corrects an agent in one turn, which is the strongest repair short of removing the command. One pack per rule means a denial names the rule (`rune.search:grep-use-rg`), a rule change is one file, and a host can relax one rule by one policy line. Fixtures make a pack edit a tested change: `scripts/test-dcg-packs` replays every rule and every exemption under an isolated config and fails when a decision or its rule moves.

The policy has two layers. The host config (`~/.config/dcg/config.toml`) loads the packs through `custom_paths` and may relax one rule per missing tool to a warning: the `grep` rules without `rg`, the `find` rules without `fd`, the YAML rule without `yq`, the JSON rule without `jq`. The command then runs and the denial text still teaches. The repository `.dcg.toml` pins every tool-free rule to `deny`. dcg applies a discovered repository file as enforcement only, so the repository can never relax what the host denies. Checked on dcg 0.14.4: a host pack-wide `warn` on `rune.push` with the repository per-rule `deny` gives `outcome` `deny`, so the pin holds against a broad relaxation. A host entry for the same rule key wins over the repository, so the pin does not hold against a host that names the rule. That is dcg's model: the host guard belongs to the host. A per-pack `deny` for an external pack in the repository file is ignored, so the entries are per rule.

The layout MUST keep these rules:

- Packs live in `.dcg/packs/<segment>.yaml` with id `rune.<segment>`, one rule family per file, the header stating the record it enforces.
- `.dcg/fixtures.txt` holds a denied command for every rule and a permitted command for every exemption, each with its decision and rule. The `check-dcg-packs` hook replays it on every pack edit.
- `.dcg.toml` carries a per-rule `deny` for every rule that needs no external tool and no entry for a rule that redirects to one.
- Pack loading stays in the host config. A discovered repository file cannot add pack paths.
- A host that duplicates a repository pack under `~/.config/dcg/packs/` defeats the relaxation, because the user copy fires first. The owner's dotfiles keep only host packs (`aliases`, `dotguard`).

## Consequences

- Every consumer takes the packs, fixtures, runner, hook, and `.dcg.toml` through the copier sync. The deck's `toolpolicy.yaml` and `repo.yaml` are deleted in that sync by hand, because the template never carried them.
- A contributor without a host config that lists `.dcg/packs/*.yaml` loads no rune pack and gets no rune denial. `install-tools` puts dcg on `PATH`, and the hook installer is dcg's own. Pack loading for such a host is documented, not automated.
- `.dcg.toml` and `[policy]` need dcg 0.14 or newer. On dcg 0.5.x the packs load and deny at every severity, and the relaxation is ignored, so a host without `rg` is blocked there until it updates.
- dcg 0.14 blocks a redirect to a path with a variable (`> "$TMPDIR/x"`) under `core.filesystem`. Scratch output goes to a literal `/tmp/claude/...` path.
- dcg scans heredoc bodies, so a quoted `grep -r` inside a Python string blocks the command. Write such text with the harness file tools.
- `lookPath` is read at `chezmoi apply`. A tool installed or removed later leaves the rendered policy stale until the next apply.
- The split moved the `git push --dry-run` exemption out of the pack that holds the provenance rules. `git push --dry-run origin main > .provenance/x.yaml` was allowed before and is denied now. That is a tightening, recorded in the fixtures.
- On dcg 0.14 a `find` through a path or `busybox` normalizes to `find`, so `find-alt-forms` and `find-use-fd` overlap. The fixture accepts either attribution.

## Proof

Recorded proof `docs/proofs/dcg-command-policy/`, scenes for pack validation, the denial text, the fixture failure, the exemption removal, the hook without dcg, and the two policy layers on dcg 0.14.4.
