# Glossary

A specification marks a term it defines in *italics* the first time it uses it. Every marked term has an entry here. The rune CLI's house lint (CLI-0040) reports a marked term with no entry, through the `rune-spec-doctor` hook once a pinned rune release joins the tool versions.

- **agentic review lanes**: the automated reviewers that examine a pull request. Each lane is a distinct harness and model, reports one check run, and MUST be summoned by a review label. The default lanes are Macroscope and Runeseer. Cursor and CodeRabbit are optional standalone lanes.
- **review funnel**: the ordered run of agentic review lanes on one pull request. Later lanes start only after earlier lanes settle clean, so paid stages run only on work every cheaper stage has passed. Runeseer adjudicates last, and the human enters after the funnel reports the change ready.
- **trailer**: a `Key: value` line in the last paragraph of a commit message, as `git interpret-trailers` reads it. `Co-Authored-By` trailers name model contributors. `Resolves-Thread` trailers name review threads a fix answers.
- **merge base**: the most recent commit that a pull request head and its base branch both descend from, as `git merge-base` reports it. The commits a pull request introduces are the range from that commit to the head.
