"""Pin the machinery canary's contract with the tools it drives.

Ruff reads ``RUFF_NO_CACHE`` as a boolean: ``true`` and ``false`` pass,
``1`` fails with ``invalid value '1' for '--no-cache'``. The canary broke
on 2026-09-09 (skeleton#45) the first time the ruff hook fired inside the
rendered consumer, because the test exported ``RUFF_NO_CACHE=1``. These
tests keep both tracked assignments on an accepted value and verify the
canary workflow reports before it fails.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENTS = (
    (ROOT / "tests" / "copier-update-canary", re.compile(r"^RUFF_NO_CACHE=(\S+)", re.MULTILINE)),
    (
        ROOT / "templates" / "base" / ".github" / "workflows" / "template-update.yaml",
        re.compile(r'RUFF_NO_CACHE:\s*"?([^"\s]+)"?'),
    ),
)


class RuffCacheEnvironmentTests(unittest.TestCase):
    def test_tracked_assignments_use_true(self):
        for path, pattern in ASSIGNMENTS:
            with self.subTest(path=path.relative_to(ROOT)):
                values = pattern.findall(path.read_text(encoding="utf-8"))
                self.assertTrue(values, f"no RUFF_NO_CACHE assignment in {path}")
                self.assertEqual(set(values), {"true"})

    @unittest.skipUnless(shutil.which("ruff"), "ruff is not installed")
    def test_ruff_accepts_only_boolean_values(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "probe.py").write_text("x = 1\n", encoding="utf-8")
            ruff = shutil.which("ruff")
            for value, accepted in (("true", True), ("false", True), ("1", False), ("yes", False)):
                with self.subTest(value=value):
                    result = subprocess.run(
                        [ruff, "check", "."],
                        cwd=directory,
                        env={"PATH": os.environ.get("PATH", ""), "RUFF_NO_CACHE": value},
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode == 0, accepted, result.stderr)


class CanaryWorkflowTests(unittest.TestCase):
    workflow = (ROOT / ".github" / "workflows" / "canary.yaml").read_text(encoding="utf-8")

    def test_probe_steps_keep_running_after_failure(self):
        self.assertEqual(self.workflow.count("continue-on-error: true"), 2)

    def test_report_names_the_failed_steps(self):
        self.assertIn("steps.run.outcome", self.workflow)
        self.assertIn("steps.copier.outcome", self.workflow)
        self.assertIn("failed step", self.workflow)

    def test_run_fails_after_the_report(self):
        report_at = self.workflow.index("name: Report breakage")
        fail_at = self.workflow.index("name: Fail the run")
        self.assertLess(report_at, fail_at)
        tail = self.workflow[fail_at:]
        self.assertIn("if: always()", tail)
        self.assertIn("exit 1", tail)

    def test_canary_requires_the_pinned_tools(self):
        self.assertIn("REQUIRE_GATES: \"1\"", self.workflow)


class QualityWorkflowTests(unittest.TestCase):
    workflow = (ROOT / ".github" / "workflows" / "quality.yaml").read_text(encoding="utf-8")

    def test_quality_runs_the_copier_canary_on_template_paths(self):
        self.assertIn("bash tests/copier-update-canary", self.workflow)
        self.assertIn("templates/", self.workflow)
        self.assertIn("copier.yaml", self.workflow)

    def test_quality_runs_these_regressions(self):
        self.assertIn("python3 -m unittest discover -s tests -p 'test_canary_contract.py' -v", self.workflow)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_jj_push.py' -v", self.workflow)


if __name__ == "__main__":
    unittest.main()
