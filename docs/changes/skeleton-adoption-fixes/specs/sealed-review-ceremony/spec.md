## MODIFIED Requirements

### Requirement: Finding Resolution

Only the reviewer identity MUST resolve review threads, acting on the verdict's disposition list inside the correctness round. Threads listed `fixed` are resolved. Threads listed `rejected` or `owner` stay open. The owner MAY resolve by hand. An agent MUST NOT resolve a thread or comment on a pull request. A fix commit MAY name the thread it answers with a `Resolves-Thread:` trailer. The trailer MUST be bookkeeping for the verdict and MUST NOT narrow the range a review judges. The template MUST NOT carry a separate resolver workflow, which raced the controller on the next push.

#### Scenario: Verdict lists fixed

- **WHEN** the verdict lists a thread as `fixed`
- **THEN** the correctness round that recorded the verdict resolves that thread, and the resolution traces to the verdict

#### Scenario: Trailer names a thread

- **WHEN** a pushed commit carries `Resolves-Thread:` naming a thread on its pull request
- **THEN** the verdict may cite the commit as the fix, and the review still judges the full range since the last verdict

#### Scenario: No standalone resolver

- **WHEN** a consumer adopts the template
- **THEN** it receives no `thread-resolver` workflow, and a consumer that still carries one may drop it at any time
