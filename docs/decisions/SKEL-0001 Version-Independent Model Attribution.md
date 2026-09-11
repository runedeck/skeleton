---
title: Version-Independent Model Attribution
description: Accept future model versions through a stable identity format and approved harness domains.
type: adr
category: governance
tags:
    - attribution
    - models
status: proposed
created: "2026-09-08"
updated: "2026-09-08"
author: "Codex (gpt-6-astra)"
project: runedeck/skeleton
responsible: ["Codex (gpt-6-astra)"]
accountable: ["@N4M3Z"]
consulted: []
informed: ["@N4M3Z"]
upstream: []
---

# SKEL-0001: Version-Independent Model Attribution

## Context and Problem Statement

The current author policy requires an entry for each model release.
The same list also drives workspace identity selection.
A new model can therefore fail publication despite following the existing address format.

## Considered Options

- Add each release to the catalog.
- Accept any email address.
- Query provider catalogs.
- Validate identity structure under approved harness domains.

## Decision Outcome

Use identity structure and approved domains.
This option avoids per-release maintenance and network dependencies.
It preserves the harness-domain boundary.
Keep human identities and vendor trailer aliases explicit.
Use one implementation for validation and identity provisioning.
Derive legacy harness domains from the trusted author list when the domain list is absent.
An explicit domain list controls the policy after migration.

## Consequences

- New versions need no policy entry under an approved harness.
- New harness domains still need owner review.
- Attribution remains a declaration rather than proof of model execution.

## More Information

[Model identity policy](../changes/model-identity-policy/proposal.md)
