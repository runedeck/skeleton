"""Pin the shared tool installer's contract.

Every tool the prek hooks call by name must have a version in
``tool-versions``. Every archive install must carry a reviewed digest for
each supported platform. The installer must refuse an archive whose bytes
do not match the pinned digest.
"""

import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "templates" / "base"
VERSIONS = (BASE / "scripts" / "tool-versions").read_text(encoding="utf-8")
INSTALLER = (BASE / "scripts" / "install-tools").read_text(encoding="utf-8")
ARCHIVE_TOOLS = ("gitleaks", "mdschema", "rumdl", "typos", "vale", "lychee", "zizmor", "actionlint")
PLATFORMS = ("DARWIN_AMD64", "DARWIN_ARM64", "LINUX_AMD64", "LINUX_ARM64")


def variables():
    return dict(re.findall(r'^([A-Z0-9_]+)="([^"]*)"', VERSIONS, re.MULTILINE))


class PinCoverageTests(unittest.TestCase):
    def test_every_archive_tool_has_four_platform_digests(self):
        pins = variables()
        for tool in ARCHIVE_TOOLS:
            for platform in PLATFORMS:
                key = f"{tool.upper()}_{platform}_SHA256"
                with self.subTest(key=key):
                    self.assertRegex(pins.get(key, ""), r"^[0-9a-f]{64}$")

    def test_every_hook_binary_is_pinned(self):
        config = (BASE / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        guarded = set(re.findall(r"command -v ([a-z]+) >/dev/null", config))
        pins = variables()
        for tool in sorted(guarded - {"rune"}):
            with self.subTest(tool=tool):
                self.assertIn(f"{tool.upper()}_VERSION", pins)

    def test_installer_verifies_every_pinned_tool(self):
        for tool in ARCHIVE_TOOLS:
            with self.subTest(tool=tool):
                self.assertIn(f'tool_matches_version {tool} "${tool.upper()}_VERSION"', INSTALLER)

    def test_root_and_template_installers_match(self):
        self.assertIn("templates/base/scripts/install-tools", (ROOT / "scripts" / "install-tools").read_text())
        self.assertEqual(
            (ROOT / "templates" / "base" / "scripts" / "tool-versions").read_bytes(),
            (BASE / "scripts" / "tool-versions").read_bytes(),
        )


class DigestVerificationTests(unittest.TestCase):
    """Drive verified_archive and its digest helper with a local archive."""

    def run_installer(self, directory, digest):
        home = Path(directory, "home")
        home.mkdir(exist_ok=True)
        archive = Path(directory, "tool.tar.gz")
        payload = Path(directory, "tool")
        payload.write_text("#!/bin/sh\necho tool\n", encoding="utf-8")
        payload.chmod(0o755)
        subprocess.run(["tar", "-czf", str(archive), "-C", directory, "tool"], check=True)
        if digest is None:
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        script = f"""
set -euo pipefail
source {BASE / 'scripts' / 'tool-versions'}
INSTALL_DIRECTORY="{home}/.local/bin"
command_exists() {{ command -v "$1" >/dev/null 2>&1; }}
log() {{ :; }}
fail() {{ printf 'fatal: %s\\n' "$*" >&2; exit 1; }}
{extract_function("digest_matches")}
{extract_function("verified_archive")}
verified_archive "file://{archive}" tool.tar.gz {digest} tool
"""
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "HOME": str(home), "TMPDIR": directory},
        )
        return result, home / ".local" / "bin" / "tool"

    def test_mismatched_archive_is_refused_before_install(self):
        with tempfile.TemporaryDirectory() as directory:
            result, installed = self.run_installer(directory, "0" * 64)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("could not install verified archive", result.stderr)
            self.assertNotIn("command not found", result.stderr)
            self.assertFalse(installed.exists())

    def test_matching_archive_installs_the_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            result, installed = self.run_installer(directory, None)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(installed.is_file())
            self.assertTrue(os.access(installed, os.X_OK))


def extract_function(name):
    match = re.search(rf"^{name}\(\) \{{\n.*?^\}}\n", INSTALLER, re.MULTILINE | re.DOTALL)
    assert match, name
    return match.group(0)


if __name__ == "__main__":
    unittest.main()
