## ADDED Requirements

### Requirement: Status Comment Upsert

A workflow-authored status comment MUST carry a header marker.
Later rounds MUST update the comment with that marker.
A lane MUST NOT post another status comment with the same marker on the pull request.

#### Scenario: Owner reminder repeats

- **WHEN** the dashboard sweep finds a pull request still waiting on the owner
- **THEN** the existing reminder updates its age instead of a second reminder appearing

#### Scenario: Autofix patch changes

- **WHEN** a later suggest run produces a different patch
- **THEN** the suggestion comment updates to the new patch
