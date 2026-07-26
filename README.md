# Skeleton

> Empty-repo archetypes composed by `rune init`. Nothing here runs on its own.

## Templates

A new repo is the union of templates, applied in order: `base` always, then every template named with `--with`, later templates overriding earlier files. One exception: `.gitignore` fragments concatenate across templates, so a toolchain template adds its entries without losing the base set.

| Template | Contents |
|----------|----------|
| `templates/base/` | hooks, CI stub, Makefile, license, KEYS, editor and git config, agent briefs, schemas |
| `templates/rust/`, `python/`, `shell/`, `node/` | toolchain files and the toolchain's `.gitignore` fragment |
| `templates/tool/`, `module/`, `spine/` | README shape and role-specific files |

The directory is flat and open: a new template is a new directory, with no fixed dimensions to fit. Composition is idempotent, since existing files are never overwritten, so the same command retrofits an old repo; `.gitignore` is the one exception, accumulating missing fragment entries without duplicating existing ones.

The toolchain `.gitignore` fragments come from [github/gitignore](https://github.com/github/gitignore). For toolchains without a curated template, composition falls back to the matching file from a local clone of that repository.

## Usage

```sh
rune init weather-stats --with rust,tool
rune init --with python              # retrofit the current directory
rune init weather-stats              # interactive template picker
```

Without `--with`, `rune init` opens a picker over the available templates.

## Placeholders

Template files carry `${VARIABLE}` placeholders resolved at scaffold time:

| Variable | Content |
|----------|---------|
| `${NAME}` | repo slug, kebab-case (`weather-stats`) |
| `${TITLE}` | human title (`Weather Stats`) |
| `${BRIEF}` | one-sentence description |
| `${OWNER}` | GitHub owner |

File and directory names carry placeholders too (`templates/shell/bin/${NAME}`); they are renamed during composition.

## License

Everything scaffolded defaults to EUPL-1.2; the license file ships in `templates/base/`.
