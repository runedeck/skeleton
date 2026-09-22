"""Pin scripts/trash: a recoverable delete on macOS and Linux with no Finder.

The script writes the FreeDesktop trash layout under $XDG_DATA_HOME/Trash:
files/<name> holds the item and info/<name>.trashinfo its original path and
deletion time. The root copy and the template copy are the same bytes.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "trash"
TEMPLATE = ROOT / "templates" / "base" / "scripts" / "trash"


def run(*paths, cwd, xdg):
    env = dict(os.environ, XDG_DATA_HOME=str(xdg))
    return subprocess.run(["sh", str(SCRIPT), *paths], cwd=cwd, env=env, capture_output=True, text=True, check=False)


class TrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="trash-test-"))
        self.xdg = self.tmp / "xdg"
        self.work = self.tmp / "work"
        self.work.mkdir()

    def test_root_and_template_copies_match(self):
        self.assertEqual(SCRIPT.read_bytes(), TEMPLATE.read_bytes())

    def test_file_and_directory_move_to_files_with_info(self):
        (self.work / "a.txt").write_text("a")
        (self.work / "dir").mkdir()
        (self.work / "dir" / "b").write_text("b")
        result = run("a.txt", str(self.work / "dir"), cwd=self.work, xdg=self.xdg)
        self.assertEqual(result.returncode, 0, result.stderr)
        trash = self.xdg / "Trash"
        self.assertTrue((trash / "files" / "a.txt").is_file())
        self.assertTrue((trash / "files" / "dir" / "b").is_file())
        info = (trash / "info" / "a.txt.trashinfo").read_text()
        self.assertIn("[Trash Info]\n", info)
        self.assertIn(f"Path={(self.work / 'a.txt').resolve()}\n", info)
        self.assertIn("DeletionDate=", info)
        self.assertFalse((self.work / "a.txt").exists())

    def test_name_collision_gets_a_counter(self):
        for _ in range(2):
            (self.work / "same").write_text("x")
            self.assertEqual(run("same", cwd=self.work, xdg=self.xdg).returncode, 0)
        names = sorted(p.name for p in (self.xdg / "Trash" / "files").iterdir())
        self.assertEqual(names, ["same", "same.2"])
        self.assertTrue((self.xdg / "Trash" / "info" / "same.2.trashinfo").exists())

    def test_missing_path_exits_1_and_the_rest_still_moves(self):
        (self.work / "present").write_text("x")
        result = run("absent", "present", cwd=self.work, xdg=self.xdg)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no such file or directory: absent", result.stderr)
        self.assertTrue((self.xdg / "Trash" / "files" / "present").exists())

    def test_no_argument_exits_64(self):
        self.assertEqual(run(cwd=self.work, xdg=self.xdg).returncode, 64)


if __name__ == "__main__":
    unittest.main()
