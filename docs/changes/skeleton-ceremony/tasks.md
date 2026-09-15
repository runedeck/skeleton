## 1. Implementation

- [x] 1.1 Canary: `RUFF_NO_CACHE=true`, failed-step names, red run, Copier probe in Quality
- [x] 1.2 Remove `opened` from both cascade callers
- [x] 1.3 Re-id DECK-0001 to SKEL-0001 and adopt CORE-0010, CORE-0011, CORE-0012 as SKEL-0004 to SKEL-0006
- [x] 1.4 Divergence register at root and in the template
- [x] 1.5 Pin the six linters with four digests each, install them, and add guarded hooks to both prek configs
- [x] 1.6 Generate the Vale STE style from the frozen rule snapshot with a staleness check
- [x] 1.7 Upstream the jj push check, its tests, and the Quality steps
- [x] 1.8 Consumer-parity script and weekly workflow
- [x] 1.9 Template-update accepts commit targets and publishes a patch
- [x] 1.10 Spec reconciliation for skeleton#22 and the modified Tagged Updates requirement
- [x] 1.11 Root `Makefile` and `.githooks/` as copies of the template payload, with a parity test
- [x] 1.12 Opposition fixes: shellcheck selects shell files, rune hook skips without a pin, protected paths cover lint config, parity audits labels-only consumers, baseline removals, modes, extensions, fetch errors, and STE source freshness, front matter is not prose

## 2. Verification

- [x] 2.1 `python3 -m unittest discover -s tests` passes
- [x] 2.2 `actionlint`, `shellcheck`, `ruff`, and `rune spec validate skeleton-ceremony` pass
- [ ] 2.3 First nightly canary and first weekly parity run complete on main

## 3. Delivery

- [ ] 3.1 Owner pushes the commit to skeleton main
- [ ] 3.2 Owner posts the #22 mapping comment and the #10 and #18 closure comments
- [ ] 3.3 consumers-copier propagates to deck, cli, and seer
