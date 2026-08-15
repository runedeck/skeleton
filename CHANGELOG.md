# Changelog

All notable changes to Skeleton are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Portable Copier generation with release metadata for downstream template updates.
- Portable repository setup installs the complete check toolchain on macOS and supported Linux distributions.
- Signed release publication verifies tags against root `KEYS` and compiles pull request Release Notes.
- Per-lane owner overrides: `skip:<lane>` stands a lane down, and `ignore:<lane>` lets it report without holding the merge.
- The `review:cursor` label summons a standalone Cursor round through the seer lane.
- The provisioned label set carries the full ceremony taxonomy: the `stage:` round records and the `issue:` provider blockers the cascade applies.

### Changed

- Review rounds begin only from explicit review labels.
- The single `review:skip` waiver becomes the per-lane `skip:` and `ignore:` families, covering the adjudicating lane as well as the external ones.
- Tracked-file secret scans use one repository-relative snapshot.
- The specification waiver is the allowed defect `ignore:spec`, in the ignore family with a mandatory body reason.
- The authorship check reads separate author and trailer lists from `authors.yaml`. A trailer attribution can no longer validate an author field. The hardcoded tooling-attribution exception moved into the `trailers:` list.

### Removed

- Consumer byte comparisons against the moving skeleton branch.
- The `spec:none` label, retired from every repository by the label synchronization.
