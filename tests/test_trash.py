"""Pin scripts/trash: a recoverable delete into the system Trash.

macOS hands every path to /usr/bin/trash (Finder's Trash, with Put Back) and
falls back to a move into ~/.Trash. Linux hands them to `gio trash` and falls
back to the FreeDesktop layout under $XDG_DATA_HOME/Trash. TRASH_PLATFORM,
TRASH_MACOS_TOOL, and TRASH_GIO point the script at fakes, so no test touches
a real Trash. The root copy and the template copy are the same bytes.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trash"
TEMPLATE = ROOT / "templates" / "base" / "scripts" / "trash"


class TrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="trash-test-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.xdg = self.tmp / "xdg"
        self.work = self.tmp / "work"
        self.work.mkdir()
        self.log = self.tmp / "calls.log"
        self.missing = str(self.tmp / "absent-tool")

    def fake(self, name, code=0):
        """A stand-in tool that records its arguments, one per line."""
        tool = self.tmp / name
        tool.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" >> "{self.log}"\nexit {code}\n')
        tool.chmod(0o755)
        return str(tool)

    def run_trash(self, *paths, platform, macos_tool=None, gio=None):
        env = dict(
            os.environ,
            HOME=str(self.home),
            XDG_DATA_HOME=str(self.xdg),
            TRASH_PLATFORM=platform,
            TRASH_MACOS_TOOL=macos_tool or self.missing,
            TRASH_GIO=gio or self.missing,
        )
        return subprocess.run(
            ["sh", str(SCRIPT), *paths], cwd=self.work, env=env, capture_output=True, text=True, check=False
        )

    def test_root_and_template_copies_match(self):
        self.assertEqual(SCRIPT.read_bytes(), TEMPLATE.read_bytes())

    def test_macos_hands_paths_to_the_system_tool(self):
        tool = self.fake("macos-trash")
        result = self.run_trash("a.txt", "dir", platform="Darwin", macos_tool=tool)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["a.txt", "dir"])

    def test_macos_passes_the_tool_exit_code_through(self):
        tool = self.fake("macos-trash", code=5)
        self.assertEqual(self.run_trash("a.txt", platform="Darwin", macos_tool=tool).returncode, 5)

    def test_macos_without_the_tool_moves_into_dot_trash(self):
        (self.work / "a.txt").write_text("a")
        for _ in range(2):
            (self.work / "same").write_text("x")
            self.assertEqual(self.run_trash("same", platform="Darwin").returncode, 0)
        result = self.run_trash("a.txt", platform="Darwin")
        self.assertEqual(result.returncode, 0, result.stderr)
        trash = self.home / ".Trash"
        self.assertEqual(sorted(p.name for p in trash.iterdir()), ["a.txt", "same", "same.2"])
        self.assertFalse((self.work / "a.txt").exists())
        self.assertFalse((self.xdg / "Trash").exists())

    def test_linux_hands_paths_to_gio(self):
        gio = self.fake("gio")
        result = self.run_trash("a.txt", platform="Linux", gio=gio)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), ["trash", "--", "a.txt"])

    def test_linux_without_gio_writes_the_freedesktop_layout(self):
        (self.work / "a.txt").write_text("a")
        (self.work / "dir").mkdir()
        (self.work / "dir" / "b").write_text("b")
        result = self.run_trash("a.txt", str(self.work / "dir"), platform="Linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        trash = self.xdg / "Trash"
        self.assertTrue((trash / "files" / "a.txt").is_file())
        self.assertTrue((trash / "files" / "dir" / "b").is_file())
        info = (trash / "info" / "a.txt.trashinfo").read_text()
        self.assertIn("[Trash Info]\n", info)
        self.assertIn(f"Path={(self.work / 'a.txt').resolve()}\n", info)
        self.assertIn("DeletionDate=", info)
        self.assertFalse((self.work / "a.txt").exists())

    def test_linux_name_collision_gets_a_counter(self):
        for _ in range(2):
            (self.work / "same").write_text("x")
            self.assertEqual(self.run_trash("same", platform="Linux").returncode, 0)
        names = sorted(p.name for p in (self.xdg / "Trash" / "files").iterdir())
        self.assertEqual(names, ["same", "same.2"])
        self.assertTrue((self.xdg / "Trash" / "info" / "same.2.trashinfo").exists())

    def test_missing_path_exits_1_and_the_rest_still_moves(self):
        (self.work / "present").write_text("x")
        for platform, trash in (("Linux", self.xdg / "Trash" / "files"), ("Darwin", self.home / ".Trash")):
            (self.work / "present").write_text("x")
            result = self.run_trash("absent", "present", platform=platform)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no such file or directory: absent", result.stderr)
            self.assertTrue((trash / "present").exists())

    def test_no_argument_exits_64(self):
        self.assertEqual(self.run_trash(platform="Darwin").returncode, 64)


if __name__ == "__main__":
    unittest.main()
