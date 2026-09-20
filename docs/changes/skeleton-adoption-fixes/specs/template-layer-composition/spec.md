## MODIFIED Requirements

### Requirement: Placeholder Resolution

Template file contents and file names MUST resolve `${VARIABLE}` placeholders at scaffold time.
A placeholder inside a TOML string MUST sit in a basic string, because the scaffolder escapes the value for one, and a literal string cannot hold an apostrophe.

#### Scenario: Placeholder in a file name

- **WHEN** a template carries a file whose name contains `${NAME}`
- **THEN** the scaffolded repository receives the file under the resolved name

#### Scenario: Brief with a quote in a manifest

- **WHEN** the brief contains an apostrophe or a double quote and a layer manifest names it in `description`
- **THEN** the scaffolded manifest parses as TOML and carries the brief unchanged
