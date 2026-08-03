# Skeleton

> Portable repository archetypes installed by Copier or composed offline by `rune init`.

## Portable base

Copier installs `templates/base` directly and records the template release in `answers.yaml`:

```sh
copier copy https://github.com/runedeck/skeleton.git weather-stats
```

Later releases arrive through `copier update`. The generated repository keeps operating when Copier is absent; only template installation and updates require it.

## Composable templates

A repository created by Rune is the union of templates applied in order: `base` always, then every template named with `--with`. Later templates override earlier files. One exception is `.gitignore`, whose fragments concatenate across templates.

| Template | Contents |
|----------|----------|
| `templates/base/` | hooks, CI, Makefile, license, KEYS, editor and git config, agent briefs, schemas |
| `templates/rust/`, `python/`, `shell/`, `node/` | toolchain files and the toolchain's `.gitignore` fragment |
| `templates/tool/`, `module/`, `spine/` | README shape and role-specific files |

The directory is flat and open: a new template is a new directory. Composition is idempotent because existing files are never overwritten. `.gitignore` accumulates missing fragment entries without duplicating existing ones.

The toolchain `.gitignore` fragments come from [github/gitignore](https://github.com/github/gitignore). For toolchains without a curated template, composition uses the matching file from a local clone of that repository.

## Rune usage

```sh
rune init weather-stats --with rust,tool
rune init --with python
rune init weather-stats
```

Without `--with`, `rune init` opens a picker over the available templates. Rune embeds the same portable base for offline scaffolding and writes Copier-compatible answers metadata.

## Placeholders

Template files carry `${VARIABLE}` placeholders resolved at scaffold time:

| Variable | Content |
|----------|---------|
| `${NAME}` | repo slug, kebab-case (`weather-stats`) |
| `${TITLE}` | human title (`Weather Stats`) |
| `${BRIEF}` | one-sentence description |
| `${OWNER}` | GitHub owner |

Copier-rendered files use the `.jinja` suffix, which is removed in generated repositories. Files without the suffix are copied verbatim, including GitHub Actions expressions such as `${{ github.ref }}`.

## License

Everything scaffolded defaults to EUPL-1.2; the license file ships in `templates/base/`.
