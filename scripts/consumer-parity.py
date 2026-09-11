#!/usr/bin/env python3
"""Compare consumer repositories with the skeleton ceremony template.

For each consumer the script renders ``templates/base`` at the consumer's
recorded ``_commit`` and at skeleton main, compares every rendered file
with the consumer's copy, and compares the consumer's labels with the set
``pr-lint.yaml`` provisions. Differences that the central divergence
register approves pass; everything else is drift. A file the template
removed between the pin and main is drift while the consumer keeps it.

The script runs with three kinds of input:

- ``--skeleton DIR``: a checkout of skeleton at main.
- ``--consumer NAME=DIR``: a checkout of one consumer, repeatable.
- ``--labels NAME=FILE``: a JSON array of that consumer's live labels
  (``[{"name", "color", "description"}]``), repeatable. A name that has
  labels but no checkout is audited for labels only.
- ``--error NAME=TEXT``: a fetch failure the caller wants in the report,
  repeatable. It counts as a failed audit.

It writes a Markdown report to stdout and exits 1 when any consumer shows
drift, when a consumer's pin does not resolve, or when a fetch error was
passed in. Consumer code never executes: Copier renders with
``--skip-tasks`` and ``--defaults``, and the comparison reads bytes and
modes only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".jj", "answers.yaml"}
REGISTER = ".ceremony-divergences.yaml"
COPIER_CONFIG = "copier.yaml"
STE_RECORD = Path(".vale", "ste-source.yaml")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_flat(path: Path) -> dict[str, str]:
    """Read ``key: value`` lines from a flat YAML file without a parser."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.startswith("#") and not line.startswith(" "):
            key, _, value = line.partition(":")
            values[key.strip()] = value.strip().strip("'\"")
    return values


def read_divergences(path: Path) -> tuple[list[dict], dict[str, str]]:
    """Parse the block-list register: entries and the extensions map."""
    entries: list[dict] = []
    extensions: dict[str, str] = {}
    if not path.is_file():
        return entries, extensions
    current: dict | None = None
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if not line.startswith(" "):
            key, _, value = stripped.partition(":")
            section = key.strip()
            current = None
            continue
        if section == "entries" and stripped.startswith("- "):
            current = {}
            key, _, value = stripped[2:].partition(":")
            current[key.strip()] = value.strip()
            entries.append(current)
        elif section == "entries" and current is not None and ":" in stripped:
            key, _, value = stripped.partition(":")
            current[key.strip()] = value.strip()
        elif section == "extensions" and ":" in stripped:
            key, _, value = stripped.partition(":")
            extensions[key.strip()] = value.strip().strip("'\"")
    return entries, extensions


def approved(entries: list[dict], repository: str, path: str, template_digest: str, consumer_digest: str) -> bool:
    for entry in entries:
        if entry.get("repository") != repository or entry.get("path") != path:
            continue
        if entry.get("template_sha256") == template_digest and entry.get("consumer_sha256") == consumer_digest:
            return True
    return False


def consumer_entries(name: str, consumer: Path, extensions: dict[str, str]) -> tuple[list[dict], str | None]:
    """Return the consumer's own entries when the central file approves its register by digest."""
    register = consumer / REGISTER
    if not register.is_file():
        return [], None
    digest = sha256(register)
    if extensions.get(name) != digest:
        return [], f"`{REGISTER}`: consumer register digest `{digest[:12]}` is not approved centrally"
    entries, _ = read_divergences(register)
    for entry in entries:
        entry.setdefault("repository", name)
    if not entries:
        return [], None
    return entries, None


def resolve(skeleton: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(skeleton), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


def render(skeleton: Path, ref: str, answers: dict[str, str], destination: Path) -> None:
    data = [f"--data={key}={value}" for key, value in answers.items() if not key.startswith("_")]
    subprocess.run(
        ["copier", "copy", "--quiet", "--defaults", "--skip-tasks", "--vcs-ref", ref, *data, str(skeleton), str(destination)],
        check=True,
        capture_output=True,
        text=True,
    )


def seeded_paths(skeleton: Path) -> set[str]:
    """Paths under ``_skip_if_exists`` in copier.yaml: seeded once, owned by the consumer."""
    seeded: set[str] = set()
    config = skeleton / COPIER_CONFIG
    if not config.is_file():
        return seeded
    inside = False
    for raw in config.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            inside = line.startswith("_skip_if_exists:")
            continue
        if inside and line.strip().startswith("- "):
            seeded.add(line.strip()[2:].strip().strip("'\""))
    return seeded


def walk(root: Path, seeded: set[str] = frozenset()) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(root)
        if relative.parts[0] in SKIP or relative.name in SKIP:
            continue
        if relative.as_posix() in seeded:
            continue
        files[relative.as_posix()] = path
    return files


def executable(path: Path) -> bool:
    return bool(path.stat().st_mode & stat.S_IXUSR)


def symlink_in_path(root: Path, relative: str) -> bool:
    """True when the file or any directory above it under root is a symlink."""
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def compare_files(
    name: str,
    consumer: Path,
    rendered: Path,
    baseline: Path | None,
    entries: list[dict],
    seeded: set[str] = frozenset(),
) -> tuple[list[str], list[str]]:
    drift: list[str] = []
    declared: list[str] = []
    template_files = walk(rendered, seeded)
    for relative, template_path in sorted(template_files.items()):
        consumer_path = consumer / relative
        if symlink_in_path(consumer, relative) or template_path.is_symlink():
            drift.append(f"`{relative}`: symlink on one side")
            continue
        if not consumer_path.is_file():
            drift.append(f"`{relative}`: missing in consumer")
            continue
        template_digest = sha256(template_path)
        consumer_digest = sha256(consumer_path)
        if executable(template_path) != executable(consumer_path):
            drift.append(f"`{relative}`: executable bit differs")
            continue
        if template_digest == consumer_digest:
            continue
        if approved(entries, name, relative, template_digest, consumer_digest):
            declared.append(f"`{relative}`")
        else:
            drift.append(f"`{relative}`: differs")
    if baseline is not None:
        for relative in sorted(set(walk(baseline, seeded)) - set(template_files)):
            if (consumer / relative).exists():
                drift.append(f"`{relative}`: removed from the template, still present")
    return drift, declared


def provisioned_labels(skeleton: Path) -> tuple[list[list[str]], list[str]]:
    script = (skeleton / ".github" / "workflows" / "pr-lint.yaml").read_text(encoding="utf-8")
    array = script.split("const wanted = [", 1)[1].split("];", 1)[0]
    array = re.sub(r"^\s*//.*$", "", array, flags=re.MULTILINE)
    array = re.sub(r",\s*$", "", array)
    wanted = json.loads("[" + array + "]")
    retired = json.loads(script.split("const retired = ", 1)[1].split(";", 1)[0])
    return wanted, retired


def compare_labels(live: list[dict], wanted: list[list[str]], retired: list[str]) -> list[str]:
    drift: list[str] = []
    by_name = {label["name"]: label for label in live}
    for name, color, description in wanted:
        label = by_name.get(name)
        if label is None:
            drift.append(f"label `{name}`: missing")
            continue
        if label.get("color", "").lower() != color.lower():
            drift.append(f"label `{name}`: color `{label.get('color')}`, expected `{color}`")
        if (label.get("description") or "") != description:
            drift.append(f"label `{name}`: description differs")
    for name in retired:
        if name in by_name:
            drift.append(f"label `{name}`: retired name still present")
    return drift


def ste_source_status(skeleton: Path, name: str, consumer: Path) -> str | None:
    """Report when the consumer that hosts the STE rule source has moved past the frozen snapshot."""
    record = read_flat(skeleton / STE_RECORD)
    repository = record.get("repository", "").rstrip("/").rsplit("/", 1)[-1]
    if repository != name or not record.get("path"):
        return None
    source = consumer / record["path"]
    if not source.is_file():
        return f"- STE rule source `{record['path']}` is missing in {name}"
    actual = sha256(source)
    if actual == record.get("sha256"):
        return f"- STE rule source matches the frozen snapshot (`{actual[:12]}`)"
    return f"- STE rule source moved: `{actual[:12]}` in {name}, snapshot records `{record.get('sha256', '')[:12]}`; refresh `.vale/ste-source.json`"


def audit_files(skeleton: Path, name: str, consumer: Path, central: list[dict], extensions: dict[str, str]) -> tuple[list[str], bool]:
    lines: list[str] = []
    failed = False
    answers = read_flat(consumer / "answers.yaml")
    pin = answers.get("_commit", "")
    resolved_pin = resolve(skeleton, pin) if pin else None
    main = resolve(skeleton, "HEAD")
    if resolved_pin is None:
        lines.append(f"- pin `{pin or '(none)'}`: does not resolve on skeleton, comparing against main only")
        failed = True
    else:
        lines.append(f"- pin `{pin}` resolves to `{resolved_pin[:12]}`; skeleton main is `{main[:12]}`")
    entries = list(central)
    own, problem = consumer_entries(name, consumer, extensions)
    if problem:
        lines.append(f"- {problem}")
        failed = True
    entries.extend(own)
    with tempfile.TemporaryDirectory(prefix="consumer-parity-") as directory:
        rendered = Path(directory, "main")
        render(skeleton, "HEAD", answers, rendered)
        if own and (rendered / REGISTER).is_file():
            # An approved consumer register differs from the empty template
            # copy by design; the approval covers that difference.
            entries.append({
                "repository": name,
                "path": REGISTER,
                "template_sha256": sha256(rendered / REGISTER),
                "consumer_sha256": sha256(consumer / REGISTER),
            })
        baseline = None
        if resolved_pin is not None and resolved_pin != main:
            baseline = Path(directory, "pin")
            render(skeleton, resolved_pin, answers, baseline)
        drift, declared = compare_files(name, consumer, rendered, baseline, entries, seeded_paths(skeleton))
    if declared:
        lines.append("- declared divergences: " + ", ".join(declared))
    if drift:
        failed = True
        lines.append("- drift against skeleton main:")
        lines.extend(f"    - {item}" for item in drift)
    else:
        lines.append("- files match skeleton main")
    status = ste_source_status(skeleton, name, consumer)
    if status:
        lines.append(status)
        failed = failed or "moved" in status or "missing" in status
    return lines, failed


def audit_labels(skeleton: Path, labels: list[dict]) -> tuple[list[str], bool]:
    wanted, retired = provisioned_labels(skeleton)
    label_drift = compare_labels(labels, wanted, retired)
    if label_drift:
        return ["- label drift:", *(f"    - {item}" for item in label_drift)], True
    return ["- labels match the provisioned set"], False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("--skeleton", type=Path, default=ROOT)
    parser.add_argument("--consumer", action="append", default=[], metavar="NAME=DIR")
    parser.add_argument("--labels", action="append", default=[], metavar="NAME=FILE")
    parser.add_argument("--error", action="append", default=[], metavar="NAME=TEXT")
    args = parser.parse_args(argv)

    central, extensions = read_divergences(args.skeleton / REGISTER)
    checkouts = dict(item.split("=", 1) for item in args.consumer)
    label_files = dict(item.split("=", 1) for item in args.labels)
    errors = dict(item.split("=", 1) for item in args.error)
    names = sorted(set(checkouts) | set(label_files) | set(errors))
    report: list[str] = ["## Consumer parity"]
    any_failed = False
    for name in names:
        lines: list[str] = [f"### {name}"]
        failed = False
        if name in errors:
            lines.append(f"- fetch failed: {errors[name]}")
            failed = True
        if name in checkouts:
            file_lines, file_failed = audit_files(args.skeleton, name, Path(checkouts[name]), central, extensions)
            lines.extend(file_lines)
            failed = failed or file_failed
        elif name not in errors:
            lines.append("- no template checkout; labels only")
        if name in label_files:
            labels = json.loads(Path(label_files[name]).read_text(encoding="utf-8"))
            label_lines, label_failed = audit_labels(args.skeleton, labels)
            lines.extend(label_lines)
            failed = failed or label_failed
        report.extend(lines)
        report.append("")
        any_failed = any_failed or failed
    report.append("Result: " + ("drift found" if any_failed else "all consumers match"))
    print("\n".join(report))
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
