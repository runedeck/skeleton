"""Exercise explicit-bookmark push gates with local, isolated JJ fixtures.

The fixtures have a bare Git backend and a separate JJ workspace. The only
remote is a temporary local directory. Fixture hooks do not run project code.
"""

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Skeleton keeps the hooks in its template payload and byte-identical
# copies at its own root; the tests drive both.
HOOK_DIRECTORIES = (ROOT / ".githooks", ROOT / "templates" / "base" / ".githooks")
HOOKS = HOOK_DIRECTORIES[1]
BOOKMARK = "codex/fixture-policy"
ZERO = "0" * 40
HOOK = r"""
import json
import os
import subprocess
import sys
from pathlib import Path

def git(*arguments):
    return subprocess.check_output(["git", *arguments], text=True).strip()

record = {
    "cwd": str(Path.cwd()),
    "head": git("rev-parse", "HEAD"),
    "trusted_main": git("rev-parse", "refs/remotes/origin/main"),
    "bare": git("rev-parse", "--is-bare-repository"),
    "status": git("status", "--porcelain"),
    "updates": sys.stdin.read().splitlines(),
    "arguments": sys.argv[1:],
    "files": git("ls-files").splitlines(),
}
Path(os.environ["JJ_PUSH_TEST_RECORD"]).write_text(json.dumps(record))
mode = os.environ.get("JJ_PUSH_TEST_MODE", "pass")
if mode == "fail":
    sys.exit(23)
if mode == "dirty":
    Path("payload.txt").write_text("Hook changed the target.\n")
if mode == "move":
    subprocess.run(
        [os.environ["JJ_PUSH_TEST_REAL_JJ"], "bookmark", "set",
         os.environ["JJ_PUSH_TEST_BOOKMARK"], "-r", "main", "--allow-backwards"],
        cwd=os.environ["JJ_PUSH_TEST_WORKSPACE"], check=True,
    )
if mode == "remote-move":
    subprocess.run(
        ["git", "--git-dir", os.environ["JJ_PUSH_TEST_REMOTE"], "update-ref",
         "refs/heads/" + os.environ["JJ_PUSH_TEST_BOOKMARK"], record["trusted_main"]],
        check=True,
    )
"""


class HookParityTests(unittest.TestCase):
    """The root hooks are byte-identical copies of the template payload.

    The bookmark tests below drive the template copy; equality makes the
    root copy covered by the same run.
    """

    def test_root_hooks_match_the_template(self):
        root, template = HOOK_DIRECTORIES
        for name in ("pre-commit", "pre-push", "jj-push", "jj-push-bookmark.py"):
            with self.subTest(hook=name):
                self.assertEqual((root / name).read_bytes(), (template / name).read_bytes())
                self.assertEqual(
                    os.access(root / name, os.X_OK),
                    os.access(template / name, os.X_OK),
                    f"{name}: executable bit differs",
                )


class BookmarkFixture(unittest.TestCase):
    """The repository, workspace, remote, hooks, and recording jj the push tests share."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jj-push-integration-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.repository = self.directory / "repository"
        self.workspace = self.directory / "workspace"
        self.remote = self.directory / "remote.git"
        self.record = self.directory / "hook.json"
        self.command_log = self.directory / "jj-commands.jsonl"
        self.git_binary = shutil.which("git")
        self.jj_binary = shutil.which("jj")
        self.assertIsNotNone(self.git_binary, "Git is required for fixture tests")
        self.assertIsNotNone(self.jj_binary, "JJ is required for fixture tests")
        self.config = self.directory / "jj-config.toml"
        self.config.write_text(
            '[user]\nname = "Fixture Owner"\nemail = "owner@example.invalid"\n'
            '[signing]\nbehavior = "drop"\n'
            "[git]\nsign-on-push = false\ncolocate = false\n"
            '[ui]\ncolor = "never"\npager = ":builtin"\n',
            encoding="utf-8",
        )
        self.environment = {
            "PATH": os.environ.get("PATH", os.defpath),
            "LC_ALL": "C",
            "TMPDIR": str(self.directory),
            "JJ_CONFIG": str(self.config),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "file",
            "JJ_PUSH_TEST_RECORD": str(self.record),
            "JJ_PUSH_TEST_REAL_JJ": self.jj_binary,
            "JJ_PUSH_TEST_WORKSPACE": str(self.workspace),
            "JJ_PUSH_TEST_REMOTE": str(self.remote),
            "JJ_PUSH_TEST_BOOKMARK": BOOKMARK,
            "JJ_PUSH_TEST_LOG": str(self.command_log),
        }
        self.checked([self.git_binary, "init", "--bare", "--quiet", str(self.remote)])
        self.jj("git", "init", "--no-colocate", str(self.repository))
        hooks = self.repository / ".githooks"
        hooks.mkdir()
        for name in ("jj-push", "jj-push-bookmark.py"):
            source = HOOKS / name
            self.assertTrue(source.is_file(), f"Missing implementation: {source}")
            shutil.copy2(source, hooks / name)
        (hooks / "pre-push").write_text(
            "#!/usr/bin/env bash\nexec "
            + shlex.quote(sys.executable)
            + " -c "
            + shlex.quote(HOOK)
            + ' "$@"\n',
            encoding="utf-8",
        )
        (hooks / "pre-push").chmod(0o755)
        (self.repository / "payload.txt").write_text("Base fixture.\n")
        (self.repository / "authors.yaml").write_text("authors: []\n")
        self.jj("describe", "-m", "Fixture base", cwd=self.repository)
        self.jj("bookmark", "create", "main", "-r", "@", cwd=self.repository)
        self.jj("git", "remote", "add", "origin", str(self.remote), cwd=self.repository)
        self.jj("git", "push", "--bookmark", "main", cwd=self.repository)
        self.base = self.jj(
            "log", "--no-graph", "-r", "main", "-T", "commit_id", cwd=self.repository
        )
        self.jj("workspace", "add", str(self.workspace), cwd=self.repository)
        self.jj("new", "main", cwd=self.workspace)
        (self.workspace / "payload.txt").write_text("Approved target.\n")
        self.jj("describe", "-m", "Fixture target", cwd=self.workspace)
        self.jj("bookmark", "create", BOOKMARK, "-r", "@", cwd=self.workspace)
        self.target = self.jj(
            "log", "--no-graph", "-r", BOOKMARK, "-T", "commit_id", cwd=self.workspace
        )
        self.jj("new", cwd=self.workspace)
        self.install_recording_jj()

    def command(self, arguments, *, cwd=None, environment=None):
        command_environment = self.environment.copy()
        command_environment.update(environment or {})
        return subprocess.run(
            arguments,
            cwd=cwd or self.directory,
            env=command_environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )

    def checked(self, arguments, *, cwd=None, environment=None):
        result = self.command(arguments, cwd=cwd, environment=environment)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def jj(self, *arguments, cwd=None):
        return self.checked([self.jj_binary, *arguments], cwd=cwd)

    def install_recording_jj(self):
        directory = self.directory / "bin"
        directory.mkdir()
        shim = directory / "jj"
        shim.write_text(
            f"#!{sys.executable}\n"
            "import json, os, subprocess, sys\n"
            'with open(os.environ["JJ_PUSH_TEST_LOG"], "a") as log:\n'
            '    log.write(json.dumps(sys.argv[1:]) + "\\n")\n'
            'real = os.environ["JJ_PUSH_TEST_REAL_JJ"]\n'
            'if os.environ.get("JJ_PUSH_TEST_FINAL_MOVE") and "push" in sys.argv[1:]:\n'
            '    subprocess.run([real, "bookmark", "set", os.environ["JJ_PUSH_TEST_BOOKMARK"],\n'
            '                    "-r", "main", "--allow-backwards"],\n'
            '                   cwd=os.environ["JJ_PUSH_TEST_WORKSPACE"], check=True)\n'
            "os.execv(real, [real, *sys.argv[1:]])\n",
            encoding="utf-8",
        )
        shim.chmod(0o755)
        self.environment["PATH"] = (
            str(directory) + os.pathsep + self.environment["PATH"]
        )

    def push(self, *arguments, mode="pass"):
        return self.command(
            ["bash", str(self.workspace / ".githooks" / "jj-push"), *arguments],
            cwd=self.workspace,
            environment={"JJ_PUSH_TEST_MODE": mode},
        )

    def remote_target(self, name=BOOKMARK, *, remote=None):
        result = self.command(
            [
                self.git_binary,
                "--git-dir",
                str(remote or self.remote),
                "rev-parse",
                "--verify",
                f"refs/heads/{name}",
            ]
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def assert_hook(self, *, previous, bookmark=BOOKMARK):
        self.assertTrue(self.record.is_file(), "The pre-push hook did not run")
        record = json.loads(self.record.read_text())
        self.assertEqual(record["head"], self.target)
        self.assertEqual(record["trusted_main"], self.base)
        self.assertEqual(record["bare"], "false")
        self.assertEqual(record["status"], "")
        self.assertNotEqual(record["cwd"], str(self.workspace))
        self.assertIn("payload.txt", record["files"])
        self.assertEqual(
            record["updates"],
            [f"refs/heads/{bookmark} {self.target} refs/heads/{bookmark} {previous}"],
        )
        return record


class BookmarkPushTests(BookmarkFixture):
    def test_new_bookmark_without_git_head_uses_exact_workspace_snapshot(self):
        self.assertFalse((self.workspace / ".git").exists())
        backend = self.jj("git", "root", cwd=self.workspace)
        result = self.command(
            [
                self.git_binary,
                "--git-dir",
                backend,
                "show-ref",
                "--verify",
                f"refs/heads/{BOOKMARK}",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO)
        self.assertEqual(self.remote_target(), self.target)

    def test_unrelated_bookmark_does_not_enter_update_range(self):
        self.jj("bookmark", "create", "unrelated", "-r", "main", cwd=self.workspace)
        result = self.push("-b", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO)
        self.assertIsNone(self.remote_target("unrelated"))

    def test_existing_remote_target_sets_exact_previous_sha(self):
        self.jj("git", "push", "--bookmark", BOOKMARK, cwd=self.workspace)
        previous = self.target
        (self.workspace / "payload.txt").write_text("Second approved target.\n")
        self.jj("describe", "-m", "Fixture follow-up", cwd=self.workspace)
        self.jj("bookmark", "set", BOOKMARK, "-r", "@", cwd=self.workspace)
        self.target = self.jj(
            "log", "--no-graph", "-r", BOOKMARK, "-T", "commit_id", cwd=self.workspace
        )
        self.jj("new", cwd=self.workspace)
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=previous)
        self.assertEqual(self.remote_target(), self.target)

    def test_hook_failure_prevents_publication(self):
        result = self.push("--bookmark", BOOKMARK, mode="fail")
        self.assertNotEqual(result.returncode, 0)
        self.assert_hook(previous=ZERO)
        self.assertIsNone(self.remote_target())

    def test_hook_modification_prevents_publication(self):
        result = self.push("--bookmark", BOOKMARK, mode="dirty")
        self.assertNotEqual(result.returncode, 0)
        self.assert_hook(previous=ZERO)
        self.assertIsNone(self.remote_target())

    def test_bookmark_movement_during_hook_prevents_publication(self):
        result = self.push("--bookmark", BOOKMARK, mode="move")
        self.assertNotEqual(result.returncode, 0)
        self.assert_hook(previous=ZERO)
        self.assertIsNone(self.remote_target())

    def test_bookmark_movement_at_publication_keeps_validated_target(self):
        self.environment["JJ_PUSH_TEST_FINAL_MOVE"] = "1"
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO)
        self.assertEqual(self.remote_target(), self.target)

    def test_remote_movement_during_hook_prevents_publication(self):
        result = self.push("--bookmark", BOOKMARK, mode="remote-move")
        self.assertNotEqual(result.returncode, 0)
        self.assert_hook(previous=ZERO)
        self.assertEqual(self.remote_target(), self.base)

    def test_remote_movement_before_hook_requires_reconciliation(self):
        self.checked(
            [
                self.git_binary,
                "--git-dir",
                str(self.remote),
                "update-ref",
                f"refs/heads/{BOOKMARK}",
                self.base,
            ]
        )
        result = self.push("--bookmark", BOOKMARK)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())
        self.assertEqual(self.remote_target(), self.base)

    def test_push_binds_resolved_selection_and_keeps_signing_configuration(self):
        configuration = self.config.read_bytes()
        arguments = ["--bookmark", BOOKMARK, "--dry-run"]
        expected_arguments = [
            "--remote",
            "origin",
            "--bookmark",
            f"exact:{json.dumps(BOOKMARK)}",
            "--dry-run",
        ]
        result = self.push(*arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = [json.loads(line) for line in self.command_log.read_text().splitlines()]
        self.assertEqual(calls[-1][0], "--at-operation")
        self.assertEqual(calls[-1][2:], ["git", "push", *expected_arguments])
        self.assertEqual(self.config.read_bytes(), configuration)
        self.assertEqual(
            self.jj("config", "get", "git.sign-on-push", cwd=self.workspace), "false"
        )
        self.assertIsNone(self.remote_target())

    def test_brace_named_bookmark_is_published_as_one_literal(self):
        literal = "codex/{fixture-a,fixture-b}"
        self.jj(
            "bookmark",
            "create",
            json.dumps(literal),
            "-r",
            BOOKMARK,
            cwd=self.workspace,
        )
        for name in ("codex/fixture-a", "codex/fixture-b"):
            self.jj("bookmark", "create", name, "-r", "main", cwd=self.workspace)
        result = self.push("--bookmark", literal)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO, bookmark=literal)
        self.assertEqual(self.remote_target(literal), self.target)
        self.assertIsNone(self.remote_target("codex/fixture-a"))
        self.assertIsNone(self.remote_target("codex/fixture-b"))

    def test_git_push_configuration_cannot_change_validated_remote(self):
        other_remote = self.directory / "other.git"
        self.checked([self.git_binary, "init", "--bare", "--quiet", str(other_remote)])
        self.jj("git", "remote", "add", "other", str(other_remote), cwd=self.workspace)
        self.config.write_text(
            self.config.read_text().replace("[git]\n", '[git]\npush = "other"\n')
        )
        self.assertEqual(
            self.jj("config", "get", "git.push", cwd=self.workspace), "other"
        )
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO)
        self.assertEqual(self.remote_target(), self.target)
        self.assertIsNone(self.remote_target(remote=other_remote))

    def test_mixed_selection_is_rejected_before_hook(self):
        result = self.push("--bookmark", BOOKMARK, "--all")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())
        self.assertIsNone(self.remote_target())

    def test_equals_bookmark_syntax_routes_through_the_gate(self):
        result = self.push(f"--bookmark={BOOKMARK}")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_hook(previous=ZERO)
        self.assertEqual(self.remote_target(), self.target)


if __name__ == "__main__":
    unittest.main()


FAKE_GPG = """#!/bin/sh
key=${FAKE_GPG_KEY:-29DD2145CE7A818929459B2649F08103D3DA399E}
case " $* " in
  *" --import "*) cat >/dev/null 2>&1; exit 0 ;;
  *" --export "*) printf 'fake-key-bytes\\n' ;;
  *" --fingerprint "*) printf '%s:::::::::%s:\\n' "fpr" "$key" ;;
  *" -bsau "*)
    cat >/dev/null
    printf '[GNUPG:] SIG_CREATED D 1 8 00 1789482678 %s\\n' "$key" >&2
    printf -- '-----BEGIN PGP SIGNATURE-----\\nfake %s\\n-----END PGP SIGNATURE-----\\n' "$key" ;;
  *" --verify "*)
    cat >/dev/null
    printf '[GNUPG:] NEWSIG\\n[GNUPG:] GOODSIG %s Owner <o@example.com>\\n[GNUPG:] VALIDSIG %s 2026-09-15 1789482678 0 4 0 1 10 00 %s\\n' "$key" "$key" "$key" ;;
  *) exit 3 ;;
esac
"""
OWNER_FINGERPRINT = "29DD2145CE7A818929459B2649F08103D3DA399E"


class ProtectedBranchSignatureTests(BookmarkFixture):
    """A direct push to main signs every commit it adds (owner direct push).

    The fixture's main gains KEYS and the two verifier scripts from the
    template, so the hook reads them from the trusted base, and a fake gpg
    signs and verifies without an agent.
    """

    def setUp(self):
        super().setUp()
        fake_gpg = self.directory / "gpg"
        fake_gpg.write_text(FAKE_GPG, encoding="utf-8")
        fake_gpg.chmod(0o755)
        cache = self.directory / "keycache"
        cache.mkdir()
        (cache / f"{OWNER_FINGERPRINT}.asc").write_text("fake armor\n", encoding="utf-8")
        self.environment.update(
            VERIFY_SEAL_GPG=str(fake_gpg),
            TRUSTED_KEYS_OFFLINE="1",
            TRUSTED_KEYS_CACHE=str(cache),
        )
        self.fake_gpg = fake_gpg
        # Seed main with KEYS and the verifier scripts, then push it so the
        # trusted base the hook reads carries them. The bootstrap variant
        # puts them in the pushed head instead: the first push of the rule.
        carrier = self.repository if self.verifier_on_base else self.workspace
        if self.verifier_on_base:
            self.seed_verifier(self.repository)
            self.jj("describe", "-m", "Fixture base with KEYS", cwd=self.repository)
            self.jj("bookmark", "set", "main", "-r", "@", cwd=self.repository)
            self.jj("git", "push", "--bookmark", "main", cwd=self.repository)
        self.base = self.jj("log", "--no-graph", "-r", "main", "-T", "commit_id", cwd=self.repository)
        self.jj("git", "fetch", cwd=self.workspace)
        self.jj("new", "main", cwd=self.workspace)
        if carrier is self.workspace:
            self.seed_verifier(self.workspace)
        (self.workspace / "payload.txt").write_text("Owner direct change.\n")
        self.jj("describe", "-m", "Owner direct change", cwd=self.workspace)
        self.head_change = self.jj("log", "--no-graph", "-r", "@", "-T", "change_id", cwd=self.workspace)
        self.jj("new", cwd=self.workspace)

    verifier_on_base = True

    def seed_verifier(self, root):
        scripts = root / "scripts"
        scripts.mkdir()
        for name in ("verify-range-signatures", "trusted-keys"):
            shutil.copy2(ROOT / "templates" / "base" / "scripts" / name, scripts / name)
        (root / "KEYS").write_text((ROOT / "KEYS").read_text(encoding="utf-8"), encoding="utf-8")

    def sign_head(self):
        # Sign through git so the fake gpg is what verifies it: jj sign would
        # need the owner's signing configuration this fixture does not carry.
        backend = self.jj("git", "root", cwd=self.workspace)
        commit = self.jj("log", "--no-graph", "-r", self.head_change, "-T", "commit_id", cwd=self.workspace)
        env = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_COMMITTER_NAME": "Owner", "GIT_COMMITTER_EMAIL": "o@example.com"}
        tree = self.checked([self.git_binary, "--git-dir", backend, "rev-parse", f"{commit}^{{tree}}"], environment=env)
        parent = self.checked([self.git_binary, "--git-dir", backend, "rev-parse", f"{commit}^"], environment=env)
        signed = self.checked(
            [self.git_binary, "--git-dir", backend, "-c", f"gpg.program={self.fake_gpg}",
             "-c", f"user.signingkey={OWNER_FINGERPRINT}", "commit-tree", "-S", "-p", parent, "-m", "Owner direct change", tree],
            environment=env,
        )
        self.checked([self.git_binary, "--git-dir", backend, "update-ref", "refs/heads/signed-fixture", signed], environment=env)
        self.jj("git", "import", cwd=self.workspace)
        self.jj("bookmark", "set", "main", "-r", "signed-fixture", "--allow-backwards", cwd=self.workspace)
        return signed

    def test_signed_direct_push_to_main_passes(self):
        signed = self.sign_head()
        result = self.push("--bookmark", "main")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("owner signatures ok: 1 commit(s)", result.stdout)
        self.assertEqual(self.remote_target("main"), signed)

    def test_unsigned_direct_push_to_main_is_refused(self):
        self.jj("bookmark", "set", "main", "-r", self.head_change, "--allow-backwards", cwd=self.workspace)
        result = self.push("--bookmark", "main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no valid signature", result.stdout + result.stderr)
        self.assertIn("jj sign -r <rev>", result.stdout + result.stderr)
        self.assertEqual(self.remote_target("main"), self.base)

    def test_feature_bookmark_is_not_signature_checked(self):
        self.jj("bookmark", "set", BOOKMARK, "-r", self.head_change, "--allow-backwards", cwd=self.workspace)
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("owner signatures", result.stdout)

    def test_harness_git_config_is_stripped_before_the_checks(self):
        self.jj("bookmark", "set", BOOKMARK, "-r", self.head_change, "--allow-backwards", cwd=self.workspace)
        self.environment["GIT_CONFIG_PARAMETERS"] = "'http.proxyAuthMethod=basic'"
        self.environment["GIT_CONFIG_COUNT"] = "1"
        self.environment["GIT_CONFIG_KEY_0"] = "core.hooksPath"
        self.environment["GIT_CONFIG_VALUE_0"] = "/nonexistent"
        result = self.push("--bookmark", BOOKMARK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)



class BootstrapSignatureTests(ProtectedBranchSignatureTests):
    """The push that first carries the verifier is judged by its own copy.

    origin/main has no scripts/verify-range-signatures yet, so the hook
    falls back to the pushed head and still demands the signature.
    """

    verifier_on_base = False

    def test_signed_direct_push_to_main_passes(self):
        signed = self.sign_head()
        result = self.push("--bookmark", "main")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("carries no scripts/verify-range-signatures; using the pushed head's copy", result.stdout)
        self.assertIn("owner signatures ok: 1 commit(s)", result.stdout)
        self.assertEqual(self.remote_target("main"), signed)
