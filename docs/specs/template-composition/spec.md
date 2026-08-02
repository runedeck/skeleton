# Template Composition Specification

## Purpose

A scaffolded repository is the union of composable templates from a flat directory: `base` always, named templates layered over it in order, discovered through a picker when none are named. Composition is predictable, open to new templates without structural change, and safe to re-run on an existing repository.

## Requirements

### Requirement: Flat Template Directory

Templates SHALL live as sibling directories under `templates/`, with no dimensional grouping, and adding a template SHALL require nothing beyond creating its directory.

#### Scenario: New template appears

- **WHEN** a new directory is added under `templates/`
- **THEN** it is composable by name and offered by the picker, with no other change

### Requirement: Ordered Composition

`rune init <name> --with <a>,<b>` SHALL apply `templates/base` first and then each named template in list order, later templates overriding earlier files, except `.gitignore` fragments, which SHALL concatenate.

#### Scenario: Later template wins

- **WHEN** two named templates carry the same file
- **THEN** the repository receives the file from the template named later

#### Scenario: Ignore fragments accumulate

- **WHEN** a named template carries a `.gitignore` fragment
- **THEN** its entries append to the composed `.gitignore` and earlier entries survive

#### Scenario: Unknown template

- **WHEN** `--with` names a template that does not exist
- **THEN** composition fails before writing anything, naming the missing template and the available ones

### Requirement: Interactive Picker

`rune init` without `--with` SHALL offer an interactive picker over the available templates, and the picked set SHALL compose exactly as if it had been named.

#### Scenario: Bare invocation

- **WHEN** `rune init <name>` runs with no template arguments in an interactive terminal
- **THEN** the picker lists the available templates and composes the selection

#### Scenario: Noninteractive invocation

- **WHEN** no templates are named and no interactive terminal is available
- **THEN** composition applies `base` alone rather than blocking on a prompt

### Requirement: Idempotent Retrofit

Composition SHALL never overwrite an existing file, so re-running the same command on an existing repository adds only what is missing. The one exception is `.gitignore`: fragment entries absent from the existing file are appended, and entries already present are not duplicated, so retrofit and concatenation compose.

#### Scenario: Retrofit an existing repository

- **WHEN** `rune init --with <template>` runs in a repository that already has some composed files
- **THEN** existing files are untouched and only absent files are written

#### Scenario: Retrofit adds a toolchain ignore fragment

- **WHEN** `rune init --with <template>` runs in a repository whose `.gitignore` already exists
- **THEN** the template's ignore entries missing from the file are appended and nothing else in it changes

#### Scenario: Retrofit repeats

- **WHEN** the same retrofit runs twice
- **THEN** the second run appends no duplicate ignore entries

### Requirement: Placeholder Resolution

Template file contents and file names SHALL resolve `${VARIABLE}` placeholders at scaffold time.

#### Scenario: Placeholder in a file name

- **WHEN** a template carries a file whose name contains `${NAME}`
- **THEN** the scaffolded repository receives the file under the resolved name

### Requirement: Portable Base

`copier.yaml` SHALL expose `templates/base` as a Copier template, and direct Copier generation SHALL produce the same base files as Rune composition.

#### Scenario: Direct Copier generation

- **WHEN** a repository is generated from a tagged skeleton release with Copier
- **THEN** it receives the base ceremony and `.copier-answers.yml` without requiring Rune

#### Scenario: Offline Rune generation

- **WHEN** Rune generates a repository without network access
- **THEN** it uses the embedded copy of the same tagged base and writes compatible Copier answers

### Requirement: Tagged Updates

Generated repositories SHALL record the skeleton source, release tag, and rendering answers in `.copier-answers.yml`.

#### Scenario: New template release

- **WHEN** Copier updates a consumer from its recorded tag to a newer release
- **THEN** downstream edits are reapplied and the result is reviewed as an ordinary pull request

#### Scenario: Copier is unavailable

- **WHEN** Copier cannot run
- **THEN** template installation and updates are unavailable while repository checks and review lanes continue

### Requirement: Verbatim Files

Only files carrying the `.jinja` suffix SHALL be rendered by Copier; unsuffixed files SHALL be copied byte-for-byte.

#### Scenario: GitHub expression

- **WHEN** an unsuffixed workflow contains a `${{ github.ref }}` expression
- **THEN** Copier preserves the expression without interpreting it as a template variable
