## ADDED Requirements

### Requirement: Pinned Controller

A consumer MUST call the review controller at a seer tag, never at a moving branch. The caller and the body MUST carry one protocol version. A mismatch MUST fail closed with a message that names both versions. A controller change reaches a consumer only with that consumer's template sync.

#### Scenario: Body ahead of the caller

- **WHEN** a consumer's caller passes protocol 2 and the tagged body speaks protocol 3
- **THEN** the run fails before triage and the message names both versions

### Requirement: Ceremony Contract

The cli MUST emit the ceremony contract as golden files: open-seal message, merge-seal message, `ledger` check-run line, receipt, and staleness input, each with a negative sibling. Skeleton and seer tests MUST read those files and MUST NOT hand-write the shapes. A change to a writer MUST regenerate the files in the same pull request.

#### Scenario: Writer changes a field name

- **WHEN** the cli renames a seal field and regenerates the contract
- **THEN** the skeleton verifier test fails on the new file until the verifier reads the new name

### Requirement: Owner-Facing Notices

A notice the controller posts to the owner MUST name lanes and rounds, never money. The coverage key `free lanes only` MAY stay as the machine-readable value.

#### Scenario: Stand-down notice

- **WHEN** the triage stands the lane down because a required check is not green
- **THEN** the notice says which check, names the lanes that ran, and offers `review:runeseer` as "force a runeseer round"

### Requirement: Open Seal Transport and Resume

`rune sign open` MUST write the pull request body before the key touch. Its push MUST authenticate through the credential the gh login already holds or a trusted system or user helper, and MUST NOT ask the owner to add a machine-wide helper. A resume after a failed push MUST verify that the remote head, the sealed tree, and the nonce are unchanged and unused before any push, and MUST refuse otherwise.

#### Scenario: Push fails after the touch

- **WHEN** the pinned push fails after the seal is signed
- **THEN** the seal stays local, the body is already on the pull request, and `rune sign open --resume` pushes and flips once the remote head still matches

#### Scenario: Tree changed before resume

- **WHEN** the branch head moved between the touch and the resume
- **THEN** the resume refuses and names the sealed tree and the current head
