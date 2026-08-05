# Changelog

All notable changes to Skeleton are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Portable Copier generation with release metadata for downstream template updates.
- Per-lane owner overrides: `skip:<lane>` stands a lane down, and `ignore:<lane>` lets it report without holding the merge.

### Changed

- Review rounds begin only from explicit review labels.
- The single `review:skip` waiver becomes the per-lane `skip:` and `ignore:` families, covering the adjudicating lane as well as the external ones.
- Tracked-file secret scans use one repository-relative snapshot.

### Removed

- Consumer byte comparisons against the moving skeleton branch.
