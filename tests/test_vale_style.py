"""Pin the generated Vale STE style and its behavior on prose.

The style is compiled from the frozen rule snapshot by
``scripts/generate-vale-style.py``. Generation is deterministic, the
check mode reports a stale or foreign file, fenced and inline code never
lint, and blockquotes lint as prose because captured output belongs in a
fence.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "templates" / "base"
GENERATOR = BASE / "scripts" / "generate-vale-style.py"
FIXTURES = ROOT / "tests" / "fixtures" / "vale"


def run_generator(*arguments, cwd):
    return subprocess.run(
        ["python3", str(GENERATOR), *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def copy_style_tree(directory):
    """Copy the generator, snapshot, and record into a scratch tree."""
    scratch = Path(directory, "repo")
    (scratch / "scripts").mkdir(parents=True)
    (scratch / ".vale").mkdir()
    shutil.copy2(GENERATOR, scratch / "scripts" / GENERATOR.name)
    shutil.copy2(BASE / ".vale" / "ste-source.json", scratch / ".vale" / "ste-source.json")
    shutil.copy2(BASE / ".vale" / "ste-source.yaml", scratch / ".vale" / "ste-source.yaml")
    shutil.copy2(BASE / ".vale.ini", scratch / ".vale.ini")
    return scratch


class GenerationTests(unittest.TestCase):
    def test_committed_style_matches_the_snapshot(self):
        self.assertEqual(run_generator("--check", cwd=BASE).returncode, 0)
        self.assertEqual(run_generator("--check", cwd=ROOT).returncode, 0)

    def test_generation_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            scratch = copy_style_tree(directory)
            script = scratch / "scripts" / GENERATOR.name
            self.assertEqual(subprocess.run(["python3", str(script)], cwd=scratch, check=False).returncode, 0)
            first = {p.name: p.read_bytes() for p in (scratch / ".vale" / "styles" / "STE").glob("*.yml")}
            subprocess.run(["python3", str(script)], cwd=scratch, check=True)
            second = {p.name: p.read_bytes() for p in (scratch / ".vale" / "styles" / "STE").glob("*.yml")}
            self.assertEqual(first, second)
            self.assertEqual(first, {p.name: p.read_bytes() for p in (BASE / ".vale" / "styles" / "STE").glob("*.yml")})

    def test_changed_source_is_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            scratch = copy_style_tree(directory)
            script = scratch / "scripts" / GENERATOR.name
            subprocess.run(["python3", str(script)], cwd=scratch, check=True)
            source = scratch / ".vale" / "ste-source.json"
            rules = json.loads(source.read_text())
            rules["marketing"].append("frictionless")
            source.write_text(json.dumps(rules, indent=2))
            result = subprocess.run(["python3", str(script), "--check"], cwd=scratch, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not match the recorded", result.stderr)
            self.assertIn("is stale", result.stderr)

    def test_extra_style_file_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            scratch = copy_style_tree(directory)
            script = scratch / "scripts" / GENERATOR.name
            subprocess.run(["python3", str(script)], cwd=scratch, check=True)
            (scratch / ".vale" / "styles" / "STE" / "Handmade.yml").write_text("extends: existence\n")
            result = subprocess.run(["python3", str(script), "--check"], cwd=scratch, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Handmade.yml is not generated", result.stderr)


@unittest.skipUnless(shutil.which("vale"), "vale is not installed")
class ProseBehaviorTests(unittest.TestCase):
    def lint(self, name):
        result = subprocess.run(
            ["vale", "--no-wrap", "--output=line", "--config", str(BASE / ".vale.ini"), str(FIXTURES / name)],
            cwd=BASE,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout

    def test_valid_fixtures_pass(self):
        for fixture in sorted((FIXTURES / "valid").glob("*.md")):
            with self.subTest(fixture=fixture.name):
                code, output = self.lint(f"valid/{fixture.name}")
                self.assertEqual(code, 0, output)

    def test_invalid_fixtures_fail(self):
        for fixture in sorted((FIXTURES / "invalid").glob("*.md")):
            with self.subTest(fixture=fixture.name):
                code, output = self.lint(f"invalid/{fixture.name}")
                self.assertNotEqual(code, 0, output)

    def test_blockquote_is_prose(self):
        _code, output = self.lint("invalid/blockquote-semicolon.md")
        self.assertIn("STE.Semicolons", output)

    def test_fenced_and_inline_code_are_not_linted(self):
        code, output = self.lint("valid/code-only.md")
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
