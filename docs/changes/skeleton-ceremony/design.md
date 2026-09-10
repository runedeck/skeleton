# Skeleton Ceremony Design

## Approach

Fix the fixer first, then unify. The canary and Quality changes make template breakage visible in the pull request that causes it. The lint row, the jj push check, and the divergence register move into `templates/base` so the template is the single source and the deck stops carrying private copies. The parity workflow then measures the gap deterministically, and the LLM audit routine only reads its output.

The alternative was to fix each consumer in place and keep the template thin. That leaves the deck and cli diverging again by the next audit.

## Structure

- `tests/copier-update-canary`, `.github/workflows/canary.yaml`, `.github/workflows/quality.yaml`: the canary contract.
- `templates/base/scripts/{tool-versions,install-tools,generate-vale-style.py}`, `templates/base/.pre-commit-config.yaml`, `templates/base/.vale/`: the lint row.
- `templates/base/.githooks/{jj-push,jj-push-bookmark.py}`, `tests/test_jj_push.py`: the push check.
- `.ceremony-divergences.yaml`, `scripts/consumer-parity.py`, `.github/workflows/consumer-parity.yaml`: the audit.
- `templates/base/.github/workflows/template-update.yaml`: commit targets and patch publication.

## Risks

- A consumer's `copier update` from an old pin conflicts in the files the deck extended. The consumers-copier change resolves those by hand.
- The frozen Vale rule snapshot lags the deck skill. The parity workflow reports it. The deck side grows `rules.json` first.
- The digests were computed from downloaded archives on 2026-09-10. A republished release would fail the install, which is the intended signal.
