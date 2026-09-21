"""Check the optional review configuration and its template copy."""

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COPIES = (ROOT, ROOT / "templates" / "base")


def label_job(root):
    return read_yaml(root / ".github/workflows/pr-lint.yaml")["jobs"]["labels"]


def read_yaml(path):
    return yaml.safe_load(path.read_text())


def read_json(path):
    return json.loads(path.read_text())


def triggers(workflow):
    # YAML 1.1 reads a bare `on` key as the boolean True.
    return workflow.get("on", workflow.get(True))


def rule(ruleset, kind):
    return next(entry for entry in ruleset["rules"] if entry["type"] == kind)


def label_script(root):
    return label_job(root)["steps"][0]["with"]["script"]


def provisioned_labels(root):
    script = label_script(root)
    array = script.split("const wanted = [", 1)[1].split("];", 1)[0]
    array = re.sub(r"^\s*//.*$", "", array, flags=re.MULTILINE)
    array = re.sub(r",\s*$", "", array)
    return json.loads("[" + array + "]")


class OptionalReviewConfigurationTests(unittest.TestCase):
    def test_status_suppression_preserves_inherited_review_policy(self):
        expected = {"inheritance": True, "reviews": {"review_status": False}}
        for root in COPIES:
            with self.subTest(root=root):
                self.assertEqual(read_yaml(root / ".coderabbit.yaml"), expected)

    def test_coderabbit_request_label_is_provisioned_once(self):
        for root in COPIES:
            with self.subTest(root=root):
                labels = provisioned_labels(root)
                self.assertEqual(
                    [entry for entry in labels if entry[0] == "review:coderabbit"],
                    [["review:coderabbit", "5319e7", "Summons a standalone CodeRabbit round"]],
                )
                self.assertEqual(len(labels), len({entry[0] for entry in labels}))

    def test_label_provisioning_preserves_other_lane_requests(self):
        for root in COPIES:
            with self.subTest(root=root):
                names = {entry[0] for entry in provisioned_labels(root)}
                self.assertTrue(
                    {
                        "review",
                        "review:cursor",
                        "review:macroscope",
                        "review:runeseer",
                    }.issubset(names)
                )

    def test_label_provisioning_does_not_apply_review_requests(self):
        for root in COPIES:
            with self.subTest(root=root):
                job = label_script(root)
                self.assertIn("github.rest.issues.updateLabel(", job)
                self.assertIn("github.rest.issues.createLabel(", job)
                self.assertNotRegex(job, r"\b(?:addLabels|setLabels|issue_number)\b")

    def test_repository_and_template_provision_the_same_labels(self):
        self.assertEqual(provisioned_labels(COPIES[0]), provisioned_labels(COPIES[1]))

    def test_quality_runs_these_regressions(self):
        workflow = read_yaml(ROOT / ".github/workflows/quality.yaml")
        commands = [step.get("run", "") for step in workflow["jobs"]["quality"]["steps"]]
        self.assertIn(
            "python3 -m unittest discover -s tests -p 'test_review_configuration.py' -v",
            commands,
        )

    def test_cascade_preserves_label_permissions_and_optional_token_independence(self):
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/review-cascade.yaml")
                self.assertEqual(workflow["permissions"]["pull-requests"], "write")
                self.assertEqual(workflow["permissions"]["issues"], "write")
                self.assertEqual(workflow["permissions"]["checks"], "read")
                job = next(job for job in workflow["jobs"].values() if "uses" in job)
                self.assertNotIn("RUNEWRIGHT_GITHUB_TOKEN", job["secrets"])
                self.assertEqual(
                    workflow["concurrency"]["cancel-in-progress"],
                    "${{ github.event.action == 'labeled' && github.event.label.name == 'review' }}",
                )
                self.assertEqual(
                    job["with"]["macroscope_correctness_check"],
                    "${{ vars.MACROSCOPE_CORRECTNESS_CHECK }}",
                )

    def test_optional_cursor_caller_has_no_head_checkout(self):
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/review-cursor.yaml")
                self.assertEqual(workflow["permissions"]["pull-requests"], "write")
                self.assertEqual(workflow["permissions"]["issues"], "write")
                self.assertIs(workflow["concurrency"]["cancel-in-progress"], False)
                self.assertEqual(list(workflow["jobs"]), ["summon"])
                job = workflow["jobs"]["summon"]
                self.assertEqual(
                    job["uses"],
                    "runedeck/seer/.github/workflows/review-cursor.yaml@main",
                )
                self.assertIn("review:cursor", job["if"])
                self.assertIn("skip:cursor", job["if"])
                self.assertNotIn("steps", job)

    def test_cascade_reaches_the_controller_on_ready_and_green_heads(self):
        # docs/specs/review-round-requests, Ready Starts the Funnel: the ready
        # event and each later head reach the controller without a label.
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/review-cascade.yaml")
                types = triggers(workflow)["pull_request_target"]["types"]
                self.assertTrue({"ready_for_review", "synchronize", "reopened", "labeled"}.issubset(types))
                jobs = workflow["jobs"]
                self.assertEqual(len(jobs), 1)
                job = next(iter(jobs.values()))
                self.assertIn("uses", job)
                self.assertNotIn("contains(github.event.pull_request.labels.*.name, 'review')", job["if"])
                self.assertIn("ready_for_review", job["if"])
                self.assertIn("synchronize", job["if"])
                self.assertIn("github.event.pull_request.draft == false", job["if"])

    def test_correctness_caller_reaches_the_controller_without_a_label(self):
        # docs/specs/review-round-requests, Ready Starts the Funnel: the
        # correctness caller, not only the cascade, forwards the ready event
        # and every later push to the controller, whose triage decides the
        # spend. A label-gated caller here left the controller unreachable
        # on every consumer while the seer body carried it (cli #67).
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/review-correctness.yaml")
                types = triggers(workflow)["pull_request_target"]["types"]
                self.assertTrue(
                    {"ready_for_review", "synchronize", "reopened", "edited", "labeled"}.issubset(types)
                )
                review = workflow["jobs"]["review"]
                self.assertIn("uses", review)
                self.assertIn("synchronize", review["if"])
                self.assertIn("reopened", review["if"])
                self.assertIn("ready_for_review", review["if"])
                self.assertNotIn("contains(github.event.pull_request.labels.*.name, 'review:runeseer')", review["if"])
                release = workflow["jobs"]["release"]
                self.assertNotIn("review:runeseer", release["if"])

    def test_required_checks_bind_everyone(self):
        # docs/specs/sealed-review-ceremony, Owner Veto and Lane Independence: the
        # three required checks sit where no actor bypasses them, and the
        # owner bypass covers the review rule alone.
        required = {"quality", "owner-seal", "review/correctness"}
        for root in COPIES:
            with self.subTest(root=root):
                base = read_json(root / ".github/rulesets/ceremony-base.json")
                veto = read_json(root / ".github/rulesets/owner-veto.json")
                self.assertEqual(base["bypass_actors"], [])
                checks = rule(base, "required_status_checks")["parameters"]["required_status_checks"]
                self.assertEqual({check["context"] for check in checks}, required)
                self.assertTrue(all(check["integration_id"] == 15368 for check in checks))
                self.assertEqual([r["type"] for r in veto["rules"]], ["pull_request"])
                self.assertIs(rule(veto, "pull_request")["parameters"]["require_code_owner_review"], True)
                self.assertEqual(
                    veto["bypass_actors"],
                    [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}],
                )
        for name in ("ceremony-base.json", "owner-veto.json"):
            with self.subTest(name=name):
                self.assertEqual(
                    read_json(COPIES[0] / ".github/rulesets" / name),
                    read_json(COPIES[1] / ".github/rulesets" / name),
                )

    def test_owner_seal_runs_from_the_default_branch(self):
        # The check never runs the candidate tree: pull_request_target, a
        # default-branch checkout, and two check runs the ruleset and the
        # controller read by name.
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/owner-seal.yaml")
                events = triggers(workflow)
                self.assertEqual(list(events), ["pull_request_target"])
                self.assertTrue({"ready_for_review", "synchronize", "edited"}.issubset(events["pull_request_target"]["types"]))
                self.assertEqual(workflow["permissions"], {})
                jobs = workflow["jobs"]
                self.assertEqual({job["name"] for job in jobs.values()}, {"owner-seal/open", "owner-seal"})
                seal = next(job for job in jobs.values() if job["name"] == "owner-seal")
                self.assertEqual(seal["needs"], "open")
                self.assertEqual(seal["if"], "always()")
                for job in jobs.values():
                    for step in job["steps"]:
                        if "uses" in step and step["uses"].startswith("actions/checkout@"):
                            self.assertEqual(step["with"]["ref"], "${{ github.event.repository.default_branch }}")
                            self.assertIs(step["with"]["persist-credentials"], False)
                merge = next(step for step in seal["steps"] if step.get("name") == "Verify the merge-seal")
                self.assertIn("--ledger", merge["run"])
                self.assertNotIn("--no-ledger", merge["run"])
        self.assertEqual(
            read_yaml(COPIES[0] / ".github/workflows/owner-seal.yaml"),
            read_yaml(COPIES[1] / ".github/workflows/owner-seal.yaml"),
        )

    def test_draft_opens_after_the_deterministic_checks(self):
        # docs/specs/sealed-review-ceremony, First push opens a draft: the draft
        # waits for quality on the pushed head.
        for root in COPIES:
            with self.subTest(root=root):
                workflow = read_yaml(root / ".github/workflows/draft-open.yaml")
                quality = read_yaml(root / ".github/workflows/quality.yaml")
                self.assertIn("workflow_call", triggers(quality))
                jobs = workflow["jobs"]
                self.assertEqual(jobs["checks"]["uses"], "./.github/workflows/quality.yaml")
                self.assertEqual(jobs["checks"]["needs"], "existing")
                self.assertEqual(jobs["open"]["needs"], ["existing", "checks"])
                self.assertIn("needs.checks.result == 'success'", jobs["open"]["if"])
                create = next(step for step in jobs["open"]["steps"] if step.get("name") == "Open the draft")
                self.assertIn("--draft", create["run"])
                self.assertEqual(create["env"]["GH_TOKEN"], "${{ steps.runewright.outputs.token }}")
        self.assertEqual(
            read_yaml(COPIES[0] / ".github/workflows/draft-open.yaml"),
            read_yaml(COPIES[1] / ".github/workflows/draft-open.yaml"),
        )

    def test_repository_and_template_share_caller_contracts(self):
        for name in ("review-cursor.yaml", "review-cascade.yaml"):
            with self.subTest(name=name):
                workflows = [read_yaml(root / ".github/workflows" / name) for root in COPIES]
                for workflow in workflows:
                    # The root preserves its existing required-check job name.
                    # Compare the reusable caller contract independent of that name.
                    jobs = workflow["jobs"]
                    for key, job in list(jobs.items()):
                        if "uses" in job:
                            jobs["reusable-caller"] = jobs.pop(key)
                self.assertEqual(
                    workflows[0],
                    workflows[1],
                )


if __name__ == "__main__":
    unittest.main()
