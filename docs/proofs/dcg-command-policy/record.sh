#!/usr/bin/env bash
# Driver for a recorded acceptance proof of the dcg-command-policy
# specification. docs/proofs/cast.py records this script. The grammar
# lives in ../driver.sh; edit only the scenes at the end.
#
# Every scene asks dcg for a decision with `dcg test` or `dcg explain`;
# no denied command is ever executed. The repository under test is a
# scratch git root that carries this repository's .dcg/, .dcg.toml, and
# scripts/test-dcg-packs, because dcg discovers .dcg.toml at the nearest
# .git, and a jj workspace has none.
# shellcheck source=../driver.sh
. "$(dirname "$0")/../driver.sh"

printf '\033[2J\033[H'

ROOT=$(cd "$(dirname "$0")/../../.." && pwd) || exit 1
RUNE=${RUNE:-rune}
export RUNE
PROOF_HOME=$(mktemp -d "${TMPDIR:-/tmp}/dcg-command-policy.XXXXXX")
trap 'command rm -rf "$PROOF_HOME"' EXIT
cd "$PROOF_HOME" || exit 1
git init -q .
rsync -a "$ROOT/.dcg/" .dcg/
rsync -a "$ROOT/.dcg.toml" .dcg.toml
mkdir -p scripts
rsync -a "$ROOT/scripts/test-dcg-packs" scripts/test-dcg-packs

# Host configs for the policy scenes. `host.toml` is the isolated test
# config plus one relaxation; dcg still discovers the repository .dcg.toml.
host_config() {
    { cat .dcg/test-config.toml; printf '\n[policy.rules]\n'; printf '"%s" = "warn"\n' "$@"; } > host.toml
}
host_pack_config() {
    { cat .dcg/test-config.toml; printf '\n[policy.packs]\n'; printf '"%s" = "warn"\n' "$@"; } > host.toml
}
export DCG_CONFIG=$PWD/.dcg/test-config.toml
export TYPE_DELAY=0 PAUSE_AFTER_COMMENT=0 PAUSE_AFTER_OUTPUT=0

scenario "Pack validates"
comment "Seven packs, one per rule family. Each id is rune.<file name>."
run "for p in .dcg/packs/*.yaml; do printf '%s ' \"\$p\"; dcg pack validate \"\$p\" | grep -o 'Pack ID: .*'; done"
expect "^.dcg/packs/homebrew.yaml .*Pack ID: rune.homebrew$"
expect "^.dcg/packs/search.yaml .*Pack ID: rune.search$"
expect "^.dcg/packs/secrets.yaml .*Pack ID: rune.secrets$"

scenario "Denial states the replacement"
comment "The rule names itself and the denial text names rg."
run "dcg test 'grep -r pattern .'"
expect "rune.search:grep-use-rg"
expect "Use rg \(ripgrep\) instead of grep"

scenario "Pack edit admits a denied command"
comment "Break the secret-read rule so it matches nothing. The fixtures name every line that moved."
run "python3 scripts/test-dcg-packs | tail -n 1"
expect "^[0-9]+ cases, 0 wrong$"
run "sed -i.bak 's/^    pattern: .*Keychains.*/    pattern: never-matches-anything-zzz/' .dcg/packs/secrets.yaml; python3 scripts/test-dcg-packs | tail -n 3; mv -f .dcg/packs/secrets.yaml.bak .dcg/packs/secrets.yaml"
expect "cat .env.template.production  <-- expected DENY rune.secrets:casual-secret-read"
expect "^64 cases, 8 wrong$"

scenario "Exemption removed"
comment "Drop the example-file exemption; the ALLOW fixture for .env.example turns into a denial."
run "sed -i.bak '/^safe_patterns:/,\$d' .dcg/packs/secrets.yaml; python3 scripts/test-dcg-packs | tail -n 3; mv -f .dcg/packs/secrets.yaml.bak .dcg/packs/secrets.yaml"
expect "cat .env.example  <-- expected ALLOW -"
expect_not " 0 wrong$"

scenario "Host without dcg"
comment "The hook prints its skip and exits 0 when dcg is absent and REQUIRE_GATES is unset."
run "PATH=/usr/bin:/bin sh -c 'if command -v dcg >/dev/null 2>&1; then echo has-dcg; elif [ -n \"\${REQUIRE_GATES:-}\" ]; then echo \"REQUIRE_GATES set and dcg is absent\"; exit 1; else echo \"dcg is absent, pack fixtures not replayed\"; fi'; echo \"exit=\$?\""
expect "^dcg is absent, pack fixtures not replayed$"
expect "^exit=0$"

scenario "Continuous integration without dcg"
comment "The same hook fails under REQUIRE_GATES."
run "REQUIRE_GATES=1 PATH=/usr/bin:/bin sh -c 'if command -v dcg >/dev/null 2>&1; then echo has-dcg; elif [ -n \"\${REQUIRE_GATES:-}\" ]; then echo \"REQUIRE_GATES set and dcg is absent\"; exit 1; fi'; echo \"exit=\$?\""
expect "^REQUIRE_GATES set and dcg is absent$"
expect "^exit=1$"

scenario "Host relaxes a tool-free pack"
comment "The host relaxes the whole push pack to warn. The repository .dcg.toml pins the rule to deny. The more specific entry wins."
host_pack_config "rune.push"
run "DCG_CONFIG=host.toml dcg explain --format json 'git push origin main' | jq -c '{decision, mode, outcome}'"
expect '"outcome":"deny"'
comment "A host entry for the same rule key is not overridden by the repository on dcg 0.14.4. The host guard is the host's."
host_config "rune.push:git-push-skips-checks"
run "DCG_CONFIG=host.toml dcg explain --format json 'git push origin main' | jq -c '{decision, mode, outcome}'"
expect '"outcome":"warn"'

scenario "Host without rg"
comment "The host relaxes the grep rule; no repository entry pins it; the command runs with a warning."
host_config "rune.search:grep-use-rg"
run "DCG_CONFIG=host.toml dcg explain --format json 'grep -r pattern .' | jq -c '{decision, mode, outcome}'"
expect '"decision":"deny","mode":"warn","outcome":"warn"'

scenario "Host without fd but with rg"
comment "Only the find rules relax; grep stays denied."
host_config "rune.search:find-use-fd" "rune.search:find-alt-forms"
run "DCG_CONFIG=host.toml dcg explain --format json 'grep -r pattern .' | jq -c .outcome; DCG_CONFIG=host.toml dcg explain --format json 'find . -name x' | jq -c .outcome"
expect '^"deny"$'
expect '^"warn"$'

scenario "Fresh machine"
comment "The installer refuses an archive whose digest differs; the pinned versions live in tool-versions."
run "grep -E '^(RG|FD|YQ|JQ|DCG)_VERSION=' scripts/tool-versions" "grep -E '^(RG|FD|YQ|JQ|DCG)_VERSION=' '$ROOT/templates/base/scripts/tool-versions'"
expect '^DCG_VERSION="0.14.4"$'
expect '^RG_VERSION="15.2.0"$'
run "python3 -m unittest tests.test_tool_install 2>&1 | tail -n 1" "(cd '$ROOT' && python3 -m unittest tests.test_tool_install 2>&1 | tail -n 1)"
expect "OK"
expect_not "FAILED"

scenario "Continuous integration"
comment "quality.yaml installs the tools first, then runs the hooks under REQUIRE_GATES."
run "grep -n -E 'install-tools|REQUIRE_GATES: \"1\"|test_dcg_policy' .github/workflows/quality.yaml" "grep -n -E 'install-tools|REQUIRE_GATES: \"1\"|test_dcg_policy' '$ROOT/.github/workflows/quality.yaml'"
expect "bash scripts/install-tools"
expect "test_dcg_policy"
expect 'REQUIRE_GATES: "1"'
