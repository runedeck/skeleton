"""Pin the dcg command policy contract (SKEL-0009).

The template and the root carry the same packs, fixtures, runner, and
repository policy. Every pack id follows its file name. Every destructive
rule has a DENY fixture that names it. Every repository policy entry names
a rule that exists. When dcg is on PATH, the fixtures hold.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "templates" / "base"
PACKS = sorted((BASE / ".dcg" / "packs").glob("*.yaml"))
FIXTURES = (BASE / ".dcg" / "fixtures.txt").read_text(encoding="utf-8")
POLICY = (BASE / ".dcg.toml").read_text(encoding="utf-8")


def pack_id(path):
    return re.search(r"^id:\s*(\S+)", path.read_text(encoding="utf-8"), re.MULTILINE).group(1)


def rule_names(path):
    text = path.read_text(encoding="utf-8")
    body = text.split("destructive_patterns:", 1)[1]
    body = body.split("safe_patterns:", 1)[0]
    return re.findall(r"^\s+- name:\s*(\S+)", body, re.MULTILINE)


def fixture_rows():
    for line in FIXTURES.splitlines():
        if line.strip() and not line.startswith("#"):
            yield line.split(None, 2)


class ParityTests(unittest.TestCase):
    def test_root_mirrors_template(self):
        for relative in (".dcg.toml", "scripts/test-dcg-packs", *(f".dcg/{p.name}" for p in (BASE / ".dcg").iterdir() if p.is_file()), *(f".dcg/packs/{p.name}" for p in PACKS)):
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), (BASE / relative).read_bytes())


class PackLayoutTests(unittest.TestCase):
    def test_pack_id_follows_file_name(self):
        for pack in PACKS:
            with self.subTest(pack=pack.name):
                self.assertEqual(pack_id(pack), f"rune.{pack.stem}")

    def test_pack_header_names_the_record(self):
        for pack in PACKS:
            with self.subTest(pack=pack.name):
                self.assertIn("SKEL-0009", pack.read_text(encoding="utf-8").splitlines()[0])


class FixtureCoverageTests(unittest.TestCase):
    def test_every_destructive_rule_has_a_deny_fixture(self):
        denied = {rule for decision, rules, _ in fixture_rows() if decision == "DENY" for rule in rules.split("|")}
        for pack in PACKS:
            for name in rule_names(pack):
                with self.subTest(rule=f"{pack_id(pack)}:{name}"):
                    self.assertIn(f"{pack_id(pack)}:{name}", denied)

    def test_every_fixture_rule_exists(self):
        known = {f"{pack_id(p)}:{n}" for p in PACKS for n in rule_names(p)}
        for decision, rules, command in fixture_rows():
            if decision == "DENY":
                for rule in rules.split("|"):
                    with self.subTest(command=command):
                        self.assertIn(rule, known)

    def test_fixture_rows_are_well_formed(self):
        rows = list(fixture_rows())
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(len(row), 3, row)
            self.assertIn(row[0], ("DENY", "ALLOW"), row)


class RepositoryPolicyTests(unittest.TestCase):
    def test_policy_entries_name_existing_rules_and_only_deny(self):
        known = {f"{pack_id(p)}:{n}" for p in PACKS for n in rule_names(p)}
        entries = re.findall(r'^"([^"]+)"\s*=\s*"([^"]+)"', POLICY, re.MULTILINE)
        self.assertGreater(len(entries), 0)
        for rule, mode in entries:
            with self.subTest(rule=rule):
                self.assertIn(rule, known)
                self.assertEqual(mode, "deny")

    def test_tool_bound_packs_stay_relaxable(self):
        for prefix in ("rune.search:", "rune.parsers:"):
            with self.subTest(pack=prefix):
                self.assertNotIn(prefix, POLICY)


@unittest.skipUnless(shutil.which("dcg"), "dcg is not on PATH")
class LiveFixtureTests(unittest.TestCase):
    def test_fixtures_hold(self):
        run = subprocess.run(["python3", str(ROOT / "scripts" / "test-dcg-packs")], capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
