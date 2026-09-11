# Changelog

All notable changes to Skeleton are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- CONTRIBUTING: no generation footer, tool badge, or session link in pull request bodies and commit messages.
- The machinery canary names each failed step in its issue and ends the run as failed. Quality runs the Copier update probe when templates, `copier.yaml`, or tests change.
- The cascade callers trigger on labels and readiness only. Nothing starts on open.
- `template-update.yaml` targets skeleton main when no newer tag exists and publishes the update as a patch artifact and run summary. It no longer opens pull requests.
- `make install` requires the full pinned toolchain, Copier included. `make validate` and the review lanes run without Copier.
- `template-update.yaml` compares skeleton main by hand when the recorded pin is a commit, because Copier only compares tags.
- The attestation spec-presence check protects the lint configs, `scripts/`, `.vale/`, and the divergence register.
- `copier.yaml` seeds `CHANGELOG.md`, `AGENTS.md`, `CONTRIBUTING.md`, `INSTALL.md`, `CODEOWNERS`, and `.gitignore` once. Updates never rewrite them and the parity audit skips them.
- The cursor caller passes the app secrets the seer body requires. The attestations checkout drops persisted credentials. The pre-push hook unsets inherited git environment. The Vale hook skips archived changes.
- The worktree target's jj path is the specified behavior: a jj workspace plus `JJ_USER` and `JJ_EMAIL` exports.
- The skeleton-local decision record `DECK-0001` is `SKEL-0001`.
- Review rounds begin only from explicit review labels.
- The single `review:skip` waiver becomes the per-lane `skip:` and `ignore:` families, covering the adjudicating lane as well as the external ones.
- Tracked-file secret scans use one repository-relative snapshot.
- The specification waiver is the allowed defect `ignore:spec`, in the ignore family with a mandatory body reason.
- The authorship check reads separate author and trailer lists from `authors.yaml`. A trailer attribution can no longer validate an author field. The hardcoded tooling-attribution exception moved into the `trailers:` list.
- The template payload carries the same two-list authorship check as the repository root, so generated and Copier-updated consumers receive it.

### Added

- The six-linter row from the deck (rumdl, typos, Vale, lychee, zizmor, actionlint) pinned with four digests each, installed by `install-tools`, and run through guarded prek hooks. `REQUIRE_GATES=1` turns a missing binary into a failure.
- `install-tools` runs `scripts/install-tools.local` when a consumer has one, so consumer-only validators install through Quality, the canary, and template updates alike.
- The authorship hook runs on every push, including empty commits.
- The Vale STE style is generated from a frozen snapshot of the deck's Simplified Technical English rule source by `scripts/generate-vale-style.py`, with a staleness check. The strict-mode words render as suggestions, so every list in the snapshot reaches the style.
- The jj push check (`jj-push-bookmark.py`) and its tests, upstreamed from the deck.
- `.ceremony-divergences.yaml`: the central register of declared consumer divergences (SKEL-0002).
- `consumer-parity.yaml`: weekly file and label parity audit of every consumer in `TEMPLATE_CONSUMERS`, reported on the deck audit issue. A consumer that never adopted the template is named in `LABELS_ONLY_CONSUMERS`.
- Root `Makefile` and `.githooks/`, byte-identical copies of the template payload, so `make install` and `make validate` work in this repository too.
- The `jj push` alias resolves the active workspace root at run time, so a jj workspace runs its own hooks.
- `module.yaml`, so `rune adr adopt` and `rune adopt doctor` work in this repository.
- Decision records SKEL-0002 to SKEL-0006, three of them reviewed adoptions of forge-core decisions.
- The worktree and worktree-done Makefile targets: create and remove an agent work tree. In a jj colocated repo the targets use jj workspaces. In a git-only repo they use git worktrees. Removal verifies the merge state first.
- Portable Copier generation with release metadata for downstream template updates.
- Portable repository setup installs the complete check toolchain on macOS and supported Linux distributions.
- Signed release publication verifies tags against root `KEYS` and compiles pull request Release Notes.
- Per-lane owner overrides: `skip:<lane>` stands a lane down, and `ignore:<lane>` lets it report without holding the merge.
- The `review:cursor` label summons a standalone Cursor round through the seer lane.
- The provisioned label set carries the full ceremony taxonomy: the `stage:` round records and the `issue:` provider blockers the cascade applies.

### Removed

- Consumer byte comparisons against the moving skeleton branch.
- The `spec:none` label, retired from every repository by the label synchronization.
