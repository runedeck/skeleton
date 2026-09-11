---
title: Verified Remote Execution
description: A downloaded tool or script runs only after its bytes match a digest committed to the repository
type: adr
category: security
tags:
    - security
    - ci
    - supply-chain
status: accepted
created: 2026-04-02
updated: 2026-09-10
author: "@N4M3Z"
project: runedeck/skeleton
related:
    - "SKEL-0004 Unified Module Validation"
    - "SKEL-0003 Shared Pinned Lint Tools"
responsible: ["@N4M3Z"]
accountable: ["@N4M3Z"]
consulted: ["claude-fable-5"]
informed: []
upstream:
    - "https://github.com/N4M3Z/forge-core/blob/132e0589eb87849973ab8ee984926f318af4d642/docs/decisions/CORE-0011%20Verified%20Remote%20Execution.md"
---

# Verified Remote Execution

## Context and Problem Statement

CI and the shared installer fetch binaries and scripts from the network. Blind `curl | bash` trusts the remote server at every run, so a compromised upstream silently changes what executes. Remote fetching itself is not the problem. Fetching content and running it is fine when the bytes are verified against a known-good digest before anything executes.

## Decision Drivers

- Remote artifacts are convenient: always current, zero local maintenance.
- The risk is unverified execution, not remote fetching.
- A committed digest is a trust anchor: the artifact can change, but execution requires an explicit digest update.
- Supply chain attacks target the gap between fetched and verified ([SLSA threat model][SLSA-THREATS]).

## Considered Options

1. Blind `curl | bash`: no verification, full trust in the upstream.
2. No remote execution: only committed local copies, manual updates.
3. Digest-verified remote execution: fetch, verify SHA-256 against a committed value, and execute only on a match.

## Decision Outcome

Chosen option: digest-verified remote execution.

The rule: any binary or script that CI or a hook fetches must match a SHA-256 digest committed to the repository before it runs. `templates/base/scripts/tool-versions` carries one version and one digest per tool and platform. `templates/base/scripts/install-tools` downloads each release archive into a scratch directory, checks the digest, and installs the binary only on a match. A mismatch fails the install and leaves nothing on the path.

Updating a digest is an explicit action: review the upstream release, change the committed value, push. Every change to executed code passes through the repository's review.

The upstream decision allowed a fallback to a committed local copy on mismatch. Skeleton has no local copy of a tool binary, so a mismatch is a hard failure. The check tools are then absent, and the guarded hooks report that under `REQUIRE_GATES` instead of skipping.

### Consequences

- [+] Remote content executes only when its bytes match the committed digest.
- [+] A compromised upstream is detected at install time, before anything runs.
- [+] Consistent with SLSA build integrity ([SLSA L2][SLSA-LEVELS]).
- [-] Every tool bump edits the digest table by hand. That friction is the point.

[SLSA-THREATS]: https://slsa.dev/spec/v1.0/threats
[SLSA-LEVELS]: https://slsa.dev/spec/v1.0/levels
