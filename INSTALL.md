# Install Skeleton

> Configure the archetype repository and verify the portable Copier template.

I want you to prepare this checkout for template development and run its checks autonomously.

## OBJECTIVE

Repository hooks active, validation tools installed, and the Copier base template rendered successfully.

## DONE WHEN

`prek run --all-files` exits 0 and Copier renders `templates/base` into a temporary repository.

## TODO

- [ ] Install the repository tools
- [ ] Activate the git hooks
- [ ] Run the repository checks
- [ ] Render a Copier smoke-test repository

## Steps

```sh
bash scripts/install-tools
git config core.hooksPath .githooks
prek run --all-files
scratch=$(mktemp -d)
copier copy --defaults . "$scratch/skeleton-smoke"
```

The installer supports macOS with Homebrew and Linux with Homebrew, apt, dnf, or pacman. Downloaded release archives are checked against their upstream checksum manifests. Copier renders a git template from its last commit, so the smoke test covers committed template state; commit (or `jj` snapshot and describe) working-tree edits before smoke-testing them.

EXECUTE NOW: Complete the TODO list to achieve: hooks active, checks green, and the portable template rendered.
