# Model Identity Policy Validation

Validated locally on 2026-09-09.
The comparison base is Skeleton commit `55e67abc7a2edf2045ee6b85235718ddbc655407`.
This record does not claim a commit, push, release, or consumer deployment.

## Results

- The identity suite passes 31 unit tests and 28 integration tests.
- Integration tests exercise both root and template checkers with isolated Git fixtures.
- The existing worktree cleanup suite passes.
- Ruff, ShellCheck, actionlint, and YAML parsing pass for the changed implementation.
- `rune spec validate model-identity-policy` passes.
- The ADR passes `mdschema` with the CLI decision schema.
- Independent review found a malformed explicit model-row bypass and a workflow quoting error.
- Both defects are fixed and covered by policy tests or workflow validation.
- Legacy policy tests accept Fable 5.2 under its recorded harness domain.
- Tests reject domain registration from the head and permission inference from trailer aliases.
- An explicit empty domain list disables inference.
- The new checker accepts the prepared Skeleton conflict fix against the unchanged trusted base policy.
- Semgrep scans 122 files with 183 applicable rules when Git ignore filtering is disabled for this isolated workspace.
- Its three checkout findings target the two trusted-base attestation checkouts and the guarded main-push specification workflow.
- Review confirmed that these checkouts execute trusted base or main code, not pull-request head code.
- Push hooks disable Semgrep's optional version notification, which attempted a sandbox-denied cache write after scanning.

## Baseline Limits

Skeleton is a template repository, not a rune source.
Plain `rune validate` rejects its missing source marker.
The documented `--force` mode reports two errors on both the unchanged base and this workspace.
Both lack `module.yaml` and `defaults.yaml`.
Both also report the existing missing-manifest warning.
This change adds no `rune validate --force` errors.

Skeleton has no default `mdschema` configuration.
An explicit check against the sibling Docs specification schemas reports heading-structure violations.
Those schema checks reject the specification's nested and repeated sections.
The independent rune specification validator passes.
The specification schema mismatch remains outside this attribution change.

## Delivery

The source change is local.
The owner approved the code change and publication.
The old CI checker still rejects new model versions until the policy change merges.
The new local checker preserves the trusted base policy as its domain source.
The sandbox retains its file restrictions, and Semgrep scanning remains enabled.
Skeleton release, Copier adoption, and CLI embedded-template updates remain pending.
