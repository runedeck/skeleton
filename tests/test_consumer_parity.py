"""Pin the consumer-parity audit's pure logic.

The rendering path needs Copier and a git checkout, so these tests drive
the register parser, the file comparison, the label comparison, and the
report assembly with fixtures on disk. The weekly workflow is the only
caller of the rendering path.
"""

import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("consumer_parity", ROOT / "scripts" / "consumer-parity.py")
parity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parity)

REGISTER = """# comment
version: 1
entries:
    - repository: cli
      path: .gitleaks.toml
      reason: fixtures
      template_sha256: aaa
      consumer_sha256: bbb
    - repository: deck
      path: README.md
      reason: prose
      template_sha256: ccc
      consumer_sha256: ddd
extensions:
    cli: "1234"
"""


def write(path: Path, text: str, executable: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class RegisterTests(unittest.TestCase):
    def test_entries_and_extensions_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            entries, extensions = parity.read_divergences(write(Path(directory, "r.yaml"), REGISTER))
        self.assertEqual([entry["path"] for entry in entries], [".gitleaks.toml", "README.md"])
        self.assertEqual(entries[0]["consumer_sha256"], "bbb")
        self.assertEqual(extensions, {"cli": "1234"})

    def test_empty_register_parses(self):
        with tempfile.TemporaryDirectory() as directory:
            entries, extensions = parity.read_divergences(write(Path(directory, "r.yaml"), "version: 1\nentries: []\nextensions: {}\n"))
        self.assertEqual((entries, extensions), ([], {}))

    def test_approval_needs_both_digests(self):
        entries = [{"repository": "cli", "path": "a", "template_sha256": "t", "consumer_sha256": "c"}]
        self.assertTrue(parity.approved(entries, "cli", "a", "t", "c"))
        self.assertFalse(parity.approved(entries, "cli", "a", "t", "other"))
        self.assertFalse(parity.approved(entries, "deck", "a", "t", "c"))

    def test_consumer_register_counts_only_when_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory, "cli")
            register = write(consumer / parity.REGISTER, "version: 1\nentries:\n    - path: own.txt\n      reason: local\n      template_sha256: t\n      consumer_sha256: c\nextensions: {}\n")
            digest = parity.sha256(register)
            own, problem = parity.consumer_entries("cli", consumer, {"cli": digest})
            self.assertIsNone(problem)
            self.assertEqual(own[0]["repository"], "cli")
            self.assertEqual(own[0]["path"], "own.txt")
            own, problem = parity.consumer_entries("cli", consumer, {"cli": "stale"})
            self.assertEqual(own, [])
            self.assertIn("not approved centrally", problem)


class SeededPathTests(unittest.TestCase):
    def test_copier_skip_list_is_read(self):
        seeded = parity.seeded_paths(ROOT)
        self.assertIn("CHANGELOG.md", seeded)
        self.assertIn(".gitignore", seeded)
        self.assertNotIn(".pre-commit-config.yaml", seeded)

    def test_seeded_files_are_not_compared(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory, "main")
            consumer = Path(directory, "consumer")
            write(rendered / "CHANGELOG.md", "template\n")
            write(consumer / "CHANGELOG.md", "downstream\n")
            write(rendered / "managed.txt", "x\n")
            write(consumer / "managed.txt", "x\n")
            drift, _ = parity.compare_files("cli", consumer, rendered, None, [], {"CHANGELOG.md"})
        self.assertEqual(drift, [])


class FileComparisonTests(unittest.TestCase):
    def test_modes_removals_and_declarations(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory, "main")
            baseline = Path(directory, "pin")
            consumer = Path(directory, "consumer")
            write(rendered / "same.txt", "same\n")
            write(consumer / "same.txt", "same\n")
            write(rendered / "hook", "#!/bin/sh\n", executable=True)
            write(consumer / "hook", "#!/bin/sh\n")
            write(rendered / "declared.txt", "template\n")
            write(consumer / "declared.txt", "consumer\n")
            write(rendered / "drifted.txt", "template\n")
            write(consumer / "drifted.txt", "consumer\n")
            write(rendered / "missing.txt", "template\n")
            write(baseline / "gone.txt", "old\n")
            write(consumer / "gone.txt", "old\n")
            write(baseline / "same.txt", "same\n")
            entries = [{
                "repository": "cli",
                "path": "declared.txt",
                "template_sha256": parity.sha256(rendered / "declared.txt"),
                "consumer_sha256": parity.sha256(consumer / "declared.txt"),
            }]
            drift, declared = parity.compare_files("cli", consumer, rendered, baseline, entries)
        self.assertEqual(declared, ["`declared.txt`"])
        self.assertEqual(
            drift,
            [
                "`drifted.txt`: differs",
                "`hook`: executable bit differs",
                "`missing.txt`: missing in consumer",
                "`gone.txt`: removed from the template, still present",
            ],
        )

    def test_symlink_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory, "main")
            consumer = Path(directory, "consumer")
            write(rendered / "real.txt", "x\n")
            write(consumer / "target.txt", "x\n")
            os.symlink("target.txt", consumer / "real.txt")
            drift, _ = parity.compare_files("cli", consumer, rendered, None, [])
        self.assertEqual(drift, ["`real.txt`: symlink on one side"])

    def test_symlinked_directory_is_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            rendered = Path(directory, "main")
            consumer = Path(directory, "consumer")
            write(rendered / ".github" / "workflows" / "quality.yaml", "on: push\n")
            write(consumer / "elsewhere" / "workflows" / "quality.yaml", "on: push\n")
            (consumer / ".github").mkdir()
            os.symlink("../elsewhere/workflows", consumer / ".github" / "workflows")
            drift, _ = parity.compare_files("cli", consumer, rendered, None, [])
        self.assertEqual(drift, ["`.github/workflows/quality.yaml`: symlink on one side"])


class LabelTests(unittest.TestCase):
    def test_provisioned_labels_parse_from_pr_lint(self):
        wanted, retired = parity.provisioned_labels(ROOT)
        self.assertTrue(wanted)
        self.assertTrue(all(len(row) == 3 for row in wanted))
        self.assertIsInstance(retired, list)

    def test_label_drift(self):
        wanted = [["review:runeseer", "0E8A16", "Summon a review"]]
        live = [{"name": "review:runeseer", "color": "0e8a16", "description": "Summon a review"}, {"name": "old", "color": "000000", "description": ""}]
        self.assertEqual(parity.compare_labels(live, wanted, ["old"]), ["label `old`: retired name still present"])
        self.assertEqual(parity.compare_labels([], wanted, []), ["label `review:runeseer`: missing"])


class ReportTests(unittest.TestCase):
    def run_main(self, *arguments):
        stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            code = parity.main(["--skeleton", str(ROOT), *arguments])
            return code, sys.stdout.getvalue()
        finally:
            sys.stdout = stdout

    def test_labels_only_consumer_is_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            labels = write(Path(directory, "seer.json"), json.dumps([]))
            code, report = self.run_main(f"--labels=seer={labels}")
        self.assertEqual(code, 1)
        self.assertIn("### seer", report)
        self.assertIn("labels only", report)
        self.assertIn("label drift", report)
        self.assertIn("Result: drift found", report)

    def test_fetch_error_fails_the_run_and_stays_in_the_report(self):
        code, report = self.run_main("--error=bench=clone failed: not found")
        self.assertEqual(code, 1)
        self.assertIn("- fetch failed: clone failed: not found", report)

    def test_nothing_to_audit_passes(self):
        code, report = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("Result: all consumers match", report)


class SourceFreshnessTests(unittest.TestCase):
    def test_snapshot_status_names_the_hosting_consumer(self):
        record = parity.read_flat(ROOT / parity.STE_RECORD)
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory, "deck")
            source = write(consumer / record["path"], "{}\n")
            self.assertIn("moved", parity.ste_source_status(ROOT, "deck", consumer))
            source.write_bytes((ROOT / ".vale" / "ste-source.json").read_bytes())
            self.assertIn("matches", parity.ste_source_status(ROOT, "deck", consumer))
            self.assertIsNone(parity.ste_source_status(ROOT, "cli", consumer))


if __name__ == "__main__":
    unittest.main()
