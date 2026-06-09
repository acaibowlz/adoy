# adoy

A static site generator designed for large sites with fast incremental builds and first-class support for multiple content types.

## Tech stack

- **Python >=3.10**
- **uv** — package manager

### Dependencies

| Package | Role |
|---|---|
| `typer` | CLI framework — powers `init`, `build`, `serve` commands |
| `pydantic` | Data validation and typed models for config and front matter |
| `tomli` / `tomllib` | TOML parsing — `tomllib` is used on 3.11+, `tomli` backfills 3.10 |
| `python-frontmatter` | Parses Markdown files with YAML front matter |
| `mistune` | Markdown → HTML rendering |
| `watchdog` | File system watching for the `serve` live-reload loop |

## Project structure

```
src/adoy/
├── cli.py          # Entry point — init, build, serve commands (typer)
├── parser.py       # Loads adoy.toml into config models
├── validator.py    # Validates config — fields, path existence, etc.
├── models.py       # Pydantic data models (config, front matter, taxonomies)
├── builder.py      # Orchestrates the build — file discovery, front matter + MD parsing, taxonomy extraction
├── cache.py        # Loads/writes .adoy-cache.json, computes checksums, diffs against source files
└── renderer.py     # Jinja2 environment, renders Markdown content into HTML via templates
```

### Module responsibilities

- **`cli.py`** orchestrates commands but contains no business logic.
- **`parser.py`** is only for config — it reads `adoy.toml` and returns typed models. It does not touch content files.
- **`validator.py`** validates the loaded config — required fields, path existence, and any cross-field constraints.
- **`builder.py`** owns content processing: file discovery, front matter + Markdown parsing (`python-frontmatter`), taxonomy extraction, and handing off to the renderer.
- **`cache.py`** owns all incremental build state — loading/writing `.adoy-cache.json`, computing checksums, and diffing to determine what needs rebuilding.
- **`renderer.py`** owns the Jinja2 environment and template rendering. It takes structured content and produces HTML.
- **`serve`** watches the source tree with `watchdog`, triggers a rebuild on change, and serves the output directory over HTTP.

### Conventions

- Use `pathlib.Path` for all file and directory paths — never raw strings.
- Use Pydantic models for all structured data (config, front matter, etc.).

## Build pipeline

### Incremental builds

The build state is stored in `.adoy-cache.json` at the project root. It tracks checksums for config, content files, and templates, and maps each content file to its output path and taxonomy terms.

The cache must stay consistent with source files — deleted content files have their HTML removed from `public/` and their entry removed from the cache.

### Pipeline stages

```
1. Load + validate config
   ├── Parse adoy.toml (syntax → fields → path existence)
   └── If invalid: abort
       If config checksum changed: mark full rebuild

2. Load .adoy-cache.json (or start fresh)

3. Diff source files against cache
   ├── Config changed       → full rebuild
   ├── Template changed     → rebuild all pages using that template
   ├── Content added/modified → rebuild that page + affected taxonomy index pages
   └── Content deleted      → delete output HTML, remove from cache

4. Render rebuild set
   └── Parse front matter + Markdown → render via Jinja2 → write HTML

5. Generate sitemap.xml and robots.txt

6. Write updated .adoy-cache.json
```

### Cache structure

The cache stores per content file:
- Source checksum
- Output path (for deletion)
- Taxonomy terms (to identify affected index pages on change)

Also stores checksums for `adoy.toml` and each template file.

## Content model

### Content types

Content is organised into sections (e.g. `blog`, `projects`). Each section is defined in `adoy.toml` under `[content.<section>]` and specifies a template and permalink pattern. All files under `content/<section>/` share that section's config.

```toml
[content.blog]
template = "post.html"
permalink = "/blog/:slug"          # or /:year/:month/:day/:slug, etc.

[content.projects]
template = "project.html"
permalink = "/projects/:slug"
```

### Taxonomies

Taxonomies aggregate content across one or more sections. A taxonomy is defined under `[taxonomy.<name>]` and lists which sections it applies to via `applies_to`.

```toml
[taxonomy.tags]
path = "/tags"
applies_to = ["blog", "projects"]
sort_by = "date"
template_taxonomy = "tags.html"
template_term = "tag.html"
```

Supported permalink variables: `:slug`, `:section`, `:year`, `:month`, `:day`, `:title`.

### Standalone pages

One-off pages (e.g. `about`, `contact`) are defined under `[pages.<name>]`. They have no section, no taxonomy, and are not indexed.

```toml
[pages.about]
template = "about.html"
permalink = "/about"
```

## Site structure (on disk)

Configured via `adoy.toml`. Defaults:

```
content/      # Markdown source files
templates/    # Jinja2 templates
static/       # Static assets copied as-is
public/       # Build output (generated)
```
