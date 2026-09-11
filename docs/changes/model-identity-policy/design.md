# Model Identity Policy Design

## Approach

Use the [selected policy](../../decisions/SKEL-0001%20Version-Independent%20Model%20Attribution.md).
The [delta specification](specs/commit-attribution/spec.md) defines its observable behavior.

## Structure

`scripts/author-identity.py` parses policy, validates identities, creates comparison keys, and resolves provisioning identities.
The helper uses the Python standard library.
Its parser accepts plain block lists with four-space entries.
It supports `authors`, `trailers`, and optional `model_domains`.
An absent domain list derives approved harness domains from model authors in the trusted legacy policy.
Trailer aliases grant no harness permissions.
An explicit domain list replaces this inference.
An empty domain list permits only exact author entries.

`scripts/check-authorship` selects the commit range and reads commit metadata.
The workflow checks out the base SHA and calls that script.
The local hook reads policy from `origin/main`.
The template Makefile calls the resolver before workspace creation.

Root and template implementations remain byte-identical.
Regression tests exercise identity cases and isolated commit histories.

## Compatibility

Existing explicit identities remain available.
Historical context aliases remain narrowly defined.
The change retains the current attribution error severity.
It adds no new instruction lint gate.

## Rollout

Release Skeleton first.
Adopt its template through Copier.
Update the CLI's embedded Skeleton release through its existing update path.

The new local checker accepts future versions under harness domains already recorded on the trusted base.
The current CI checker still requires exact model entries until this change merges.
The owner must decide the initial CI policy transition.
The pull request cannot change the trusted CI checker for its own run.

## Risks

A syntactically valid identity can still name the wrong runtime model.
This validator checks attribution declarations, not execution evidence.

Existing consumers have separate validators and different template revisions.
Consumer rollout stays explicit so this source change does not imply estate-wide deployment.
