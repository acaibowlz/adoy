# adoy

A static site generator designed for large sites with fast incremental builds and first-class support for multiple content types.

## Features

- **Incremental builds** — only changed content, templates, or config triggers a rebuild. Large sites stay fast.
- **Multiple content types** — define sections with independent templates and permalink patterns.
- **Taxonomies** — aggregate content across sections with tags, categories, series, or any custom grouping.
- **Agent-first** — every project includes a `CLAUDE.md` so an AI agent can manage content and templates from natural language instructions.

## Quick start

```bash
uv tool install adoy
adoy init my-site
cd my-site
adoy serve
```

→ [Getting Started](./getting-started.md)
