## ADDED Requirements

### Requirement: One pack per rule it enforces

The repository MUST keep its dcg packs under `.dcg/packs/`, one file per rule or skill the pack enforces, with the id `rune.<segment>` and a file name equal to the segment. Each pack header MUST state the record it enforces. The segments are `search` (rg for grep, fd for find), `parsers` (yq for YAML, jq for JSON, one rule each), `secrets` (no casual read of key or environment files), `push` (no bare `git push` in a jj-colocated repository), `provenance` (no shell write into `.provenance/`), `rtk` (no `rtk` in front of a harness it cannot filter), and `homebrew` (no pipe after `brew`).

#### Scenario: Pack validates

- **WHEN** `dcg pack validate` runs on each file under `.dcg/packs/`
- **THEN** every pack is valid and its id is `rune.<file name without extension>`

#### Scenario: Denial states the replacement

- **WHEN** an agent runs a recursive grep from the repository root under the default policy
- **THEN** dcg denies the command with the rule `rune.search:grep-use-rg` and the denial text states `rg`

### Requirement: Fixtures pin every decision

`.dcg/fixtures.txt` MUST hold, for every destructive rule, at least one command that the rule denies, and for every exemption a command that the rule would deny without it. Each line MUST state the decision and, for a denial, the rule that matches. `scripts/test-dcg-packs` MUST replay each line through `dcg test --format json` from the repository root under `.dcg/test-config.toml`, which loads only the core packs and the repository packs. It MUST exit nonzero when a decision or a rule differs, when dcg answers with another schema, or when the file has no case.

#### Scenario: Pack edit admits a denied command

- **WHEN** a pack edit turns a `DENY` fixture into an allow
- **THEN** `scripts/test-dcg-packs` prints the line with the expected decision and rule and exits 1

#### Scenario: Exemption removed

- **WHEN** a safe pattern or a lookahead exemption is deleted from a pack
- **THEN** at least one `ALLOW` fixture turns into a denial and the runner exits 1

### Requirement: The hook replays the fixtures on every pack edit

The `check-dcg-packs` prek hook MUST validate every pack and run `scripts/test-dcg-packs` on each edit under `.dcg/`, `.dcg.toml`, the runner, or `scripts/tool-versions`. It MUST fail under `REQUIRE_GATES` when dcg is absent and MUST print the skip otherwise.

#### Scenario: Host without dcg

- **WHEN** the hook runs where `dcg` is not on `PATH` and `REQUIRE_GATES` is unset
- **THEN** the hook prints that the fixtures were not replayed and exits 0

#### Scenario: Continuous integration without dcg

- **WHEN** the hook runs with `REQUIRE_GATES` set and `dcg` is not on `PATH`
- **THEN** the hook exits 1

### Requirement: Repository policy only tightens

The repository MUST have `.dcg.toml` at its root with a per-rule `deny` entry for each rule that needs no external tool: `rune.secrets:casual-secret-read`, `rune.push:git-push-skips-checks`, the three `rune.provenance` rules, `rune.rtk:rtk-wraps-harness`, and `rune.homebrew:brew-no-pipe`. It MUST NOT set an entry for a `rune.search` or `rune.parsers` rule, so a host without `rg`, `fd`, `yq`, or `jq` may relax the rule for that one tool to a warning. Entries MUST be per rule: dcg 0.14 honors a per-rule deny for an external pack from a discovered repository file and ignores a per-pack one. Pack loading MUST stay in the host config, which dcg reads for custom pack paths.

#### Scenario: Host relaxes a tool-free pack

- **WHEN** the host config sets `[policy.packs] "rune.push" = "warn"` and the repository `.dcg.toml` sets `"rune.push:git-push-skips-checks" = "deny"`
- **THEN** `dcg explain --format json` on a bare git push from the repository root reports `outcome` `deny`, and a host entry for that same rule key still reports `outcome` `warn`

#### Scenario: Host without rg

- **WHEN** the host config sets `"rune.search:grep-use-rg" = "warn"` and the agent runs a recursive grep from the repository root
- **THEN** `dcg explain --format json` reports `decision` `deny`, `mode` `warn`, and `outcome` `warn`, and the command runs

#### Scenario: Host without fd but with rg

- **WHEN** the host config sets only the two `find` rules of `rune.search` to `warn`
- **THEN** a recursive grep from the repository root reports `outcome` `deny` and a `find` reports `outcome` `warn`

### Requirement: Install what the packs demand

`scripts/install-tools` MUST install pinned versions of `rg`, `fd`, `yq`, `jq`, and `dcg` with reviewed digests in `scripts/tool-versions` for darwin and linux on amd64 and arm64, through the same digest check as the other tools. `all_tools_match` and `verify_tools` MUST know the five.

#### Scenario: Fresh machine

- **WHEN** `scripts/install-tools` runs on a machine without those five tools
- **THEN** each tool is on `PATH` at the pinned version, and the installer exits nonzero when a digest differs

#### Scenario: Continuous integration

- **WHEN** the quality workflow runs `install-tools` and then the hooks with `REQUIRE_GATES` set
- **THEN** dcg is on `PATH` and `check-dcg-packs` replays the fixtures
