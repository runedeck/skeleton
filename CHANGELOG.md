# Changelog

All notable changes to Skeleton are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Add `scripts/trash` to the template and the root: a recoverable delete on macOS and Linux through the FreeDesktop trash layout, no Finder, with `tests/test_trash.py`.
- Add seven dcg packs under `.dcg/packs/`, one per rule (`search`, `parsers`, `secrets`, `push`, `provenance`, `rtk`, `homebrew`), ids `rune.<segment>`, in the template and the root (SKEL-0009).
- Add `.dcg/fixtures.txt`, `.dcg/test-config.toml`, and `scripts/test-dcg-packs`: a denied command per rule and a permitted one per exemption, replayed through `dcg test` under an isolated config.
- Add the `check-dcg-packs` hook, which validates every pack and replays the fixtures on each pack edit, and `tests/test_dcg_policy.py` for parity, ids, coverage, and policy entries.
- Add `.dcg.toml` at the repository root: a per-rule `deny` for every rule that needs no external tool, applied by dcg as enforcement only.
- Add pinned `rg`, `fd`, `yq`, `jq`, and `dcg` to `install-tools` and `tool-versions`, with reviewed digests for darwin and linux on amd64 and arm64.
- Add `scripts/verify-range-signatures`: the guarded push requires a `KEYS` signature on every commit a direct push adds to `main` (Owner Direct Push spec).
- Add `scripts/trusted-keys`, which resolves the signers `KEYS` pins through the owner's Web Key Directory, then GitHub, then a cache, admitting only bytes that carry the pin.
- Add `tests/trusted-keys` and the owner's public key as its fixture, a recorded proof under `docs/proofs/trusted-key-anchor/`, and a gitleaks allowance for bare OpenPGP fingerprints.
- Add the `.gitignore` baseline check to the parity audit, which reports a consumer whose file lacks a template pattern.
- Add SKEL-0007: the checks that judge a pull request run from the base ref, and the machinery canary runs every probe and ends as failed.
- Add the six-linter row from the deck (rumdl, typos, Vale, lychee, zizmor, actionlint), pinned with four digests each and run through guarded prek hooks.
- Add `REQUIRE_GATES=1`, which turns a missing linter binary into a failure.
- Add `scripts/install-tools.local` support, so consumer-only validators install through Quality, the canary, and template updates alike.
- Add the authorship hook to every push, including empty commits.
- Add the `review:pr-agent` and `skip:pr-agent` labels that the PR-Agent caller reads.
- Add connect and total timeouts with three retries to `install-tools` downloads.
- Add a `trash` guard to `worktree-done`: it moves a workspace to the trash only when `trash` is installed and names a missing git store.
- Add every standalone review label to CONTRIBUTING.
- Add the Vale STE style, generated from a frozen snapshot of the deck's Simplified Technical English rule source by `scripts/generate-vale-style.py`, with a staleness check.
- Add the jj push check (`jj-push-bookmark.py`) and its tests, upstreamed from the deck.
- Add `.ceremony-divergences.yaml`, the central register of declared consumer divergences (SKEL-0002).
- Add `consumer-parity.yaml`, a weekly file and label parity audit of every consumer in `TEMPLATE_CONSUMERS`, reported on the deck audit issue.
- Add `LABELS_ONLY_CONSUMERS` for a consumer that never adopted the template.
- Add the root `Makefile` and `.githooks/` as byte-identical copies of the template payload, so `make install` and `make validate` work here too.
- Add run-time workspace resolution to the `jj push` alias, so a jj workspace runs its own hooks.
- Add `module.yaml`, so `rune adr adopt` and `rune adopt doctor` work in this repository.
- Add decision records SKEL-0002 to SKEL-0006, three of them reviewed adoptions of forge-core decisions.
- Add the `worktree` and `worktree-done` Makefile targets: jj workspaces in a colocated repo, git worktrees otherwise, and a merge-state check before removal.
- Add portable Copier generation with release metadata for downstream template updates.
- Add portable repository setup that installs the complete check toolchain on macOS and supported Linux distributions.
- Add signed release publication that verifies tags against root `KEYS` and compiles pull request Release Notes.
- Add per-lane owner overrides: `skip:<lane>` stands a lane down, and `ignore:<lane>` lets it report without holding the merge.
- Add the `review:cursor` label, which summons a standalone Cursor round through the seer lane.
- Add the full ceremony label taxonomy: the `stage:` round records and the `issue:` provider blockers the cascade applies.

### Changed

- Spell the GPT acronym in upper case in derived display names and the roster: `Codex GPT 5.6 Sol`, not `Codex Gpt 5.6 Sol`.
- Change the ruleset bypass from the owner's user id to the repository admin role, mode always, so the owner's direct push is the one path around the review rules.
- Change `typos.toml` and `.rumdl.toml` to seeded-once files: consumers own their excluded fixtures and accepted words, and the parity audit no longer compares them.
- Change `author-identity.py resolve` to derive the display name from the model ID, so `claude-fable-5-1` is `Claude Fable 5.1` and not `Claude` (derived-display-name).
- Change `KEYS` from an armored key block to `signer <fingerprint> <address>...` lines, and `verify-seal` and `verify-release-tag` to build their keyring through `scripts/trusted-keys`.
- Change every capability and change id to three hyphenated words, and split every requirement over 100 words, as the rune prose caps require.
- Change every specification to MUST wording under 150 lines, with terms defined in `docs/specs/glossary.md`.
- Change the review-ceremony capability into review-lanes, review-requests, lane-configuration, merge-checks, and release-ceremony.
- Change commit-attribution by splitting off attribution-check and worktree-identity, and the active deltas follow their requirements.
- Change CONTRIBUTING: no generation footer, tool badge, or session link in pull request bodies and commit messages.
- Change the machinery canary to name each failed step in its issue and end the run as failed.
- Change Quality to run the Copier update probe when templates, `copier.yaml`, or tests change.
- Change the cascade callers to trigger on labels and readiness only, so nothing starts on open.
- Change `template-update.yaml` to target skeleton main when no newer tag exists and to publish the update as a patch artifact and run summary, never a pull request.
- Change `make install` to require the full pinned toolchain, Copier included, while `make validate` and the review lanes run without Copier.
- Change `template-update.yaml` to compare skeleton main by hand when the recorded pin is a commit, because Copier only compares tags.
- Change the attestation spec-presence check to protect the lint configs, `scripts/`, `.vale/`, and the divergence register.
- Change `copier.yaml` to seed `CHANGELOG.md`, `AGENTS.md`, `CONTRIBUTING.md`, `INSTALL.md`, `CODEOWNERS`, and `.gitignore` once, and updates never rewrite them.
- Change the cursor caller to pass the app secrets the seer body requires.
- Change the attestations checkout to drop persisted credentials.
- Change the pre-push hook to unset inherited git environment.
- Change the Vale hook to skip archived changes.
- Change the worktree target's jj path to the specified behavior: a jj workspace plus `JJ_USER` and `JJ_EMAIL` exports.
- Change the skeleton-local decision record `DECK-0001` to `SKEL-0001`.
- Change review rounds to start only from explicit review labels.
- Change the single `review:skip` waiver into the per-lane `skip:` and `ignore:` families, covering the adjudicating lane as well as the external ones.
- Change tracked-file secret scans to one repository-relative snapshot.
- Change the specification waiver to the allowed defect `ignore:spec`, in the ignore family with a mandatory body reason.
- Change the authorship check to read separate author and trailer lists from `authors.yaml`, so a trailer attribution no longer validates an author field.
- Change the hardcoded tooling-attribution exception into a `trailers:` list entry.
- Change the template payload to carry the same two-list authorship check as the repository root.

### Removed

- Remove `CLAUDE.md` from the template payload, so `AGENTS.md` is the only instruction file a consumer receives.
- Remove consumer byte comparisons against the moving skeleton branch.
- Remove the `spec:none` label from every repository through the label synchronization.
