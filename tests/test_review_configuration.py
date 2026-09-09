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
