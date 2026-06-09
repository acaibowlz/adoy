# {name}

Built with [adoy](https://github.com/acaibowlz/adoy) — a static site generator with incremental builds.

## Build commands

```bash
adoy build                # incremental build
adoy build --clean-build  # force full rebuild (clears cache)
adoy serve                # build + live-reload server at localhost:8000
```

---

## Working with content

### Creating a post

Create a `.md` file under `content/<section>/`. All front matter fields are required:

```yaml
---
title: My Post
description: One sentence about this post.
summary: Even shorter — used in listing pages.
date: 2026-06-09
content_type: blog
slug: my-post
status: active
tags:
  - example
---

Body text in Markdown goes here.
```

| Field | Type | Notes |
|---|---|---|
| `title` | string | |
| `description` | string | |
| `summary` | string | |
| `date` | `YYYY-MM-DD` | |
| `content_type` | string | must match the section name in `adoy.toml` |
| `slug` | string | used in the URL permalink |
| `status` | `active` / `draft` / `archive` | only `active` files are built |

Taxonomy fields (e.g. `tags`) are optional lists appended below the required fields.

### Publishing, drafting, archiving

Change the `status` field in the front matter:

- `active` — built and included in the site
- `draft` — silently skipped (no output file, no error)
- `archive` — silently skipped

### Adding a new content section

1. Create the directory: `content/<section>/`
2. Add to `adoy.toml`:

```toml
[content.<section>]
section = "<section>"
template = "<section>.html"
permalink = "/<section>/:slug"
```

3. Create `templates/<section>.html` (extend `base.html`).

Supported permalink variables: `:slug`, `:section`, `:year`, `:month`, `:day`, `:title`.

---

## Working with taxonomies

A taxonomy aggregates content across sections (e.g. tags, categories, series).

### Adding a taxonomy

1. Add to `adoy.toml`:

```toml
[taxonomy.<name>]
name = "<name>"
path = "/<name>"
applies_to = ["blog"]
sort_by = "date"
template_taxonomy = "<name>s.html"
template_term = "<name>.html"
```

2. Create `templates/<name>s.html` — the overview page listing all terms.
3. Create `templates/<name>.html` — the per-term page listing pages with that term.
4. Add the taxonomy field to front matter of content files (as a YAML list).

### Template context for taxonomy templates

**Overview template** (`<name>s.html`):

| Variable | Type | Description |
|---|---|---|
| `taxonomy` | `str` | taxonomy name |
| `terms` | `dict[str, list[FrontMatter]]` | term → pages |

**Term template** (`<name>.html`):

| Variable | Type | Description |
|---|---|---|
| `taxonomy` | `str` | taxonomy name |
| `term` | `str` | this term |
| `pages` | `list[FrontMatter]` | pages carrying this term, newest first |

---

## Working with standalone pages

Standalone pages have no section, no taxonomy, and are not indexed.

### Adding a standalone page

1. Create `content/<name>.md` with front matter.
2. Add to `adoy.toml`:

```toml
[pages.<name>]
template = "<name>.html"
permalink = "/<name>"
```

3. Create `templates/<name>.html`.

---

## Working with templates

All templates use [Jinja2](https://jinja.palletsprojects.com/). Every page template must extend `base.html`:

```html
{% extends "base.html" %}
{% block title %}{{ page.title }}{% endblock %}
{% block content %}
  ...
{% endblock %}
```

### Context for content and standalone page templates

| Variable | Type | Description |
|---|---|---|
| `page` | FrontMatter | parsed front matter |
| `content` | `str` | body rendered to HTML |
| `site` | SiteConfig | global — available in every template |

`page` attributes: `page.title`, `page.description`, `page.summary`, `page.date` (datetime), `page.content_type`, `page.slug`, `page.status`.

`site` attributes: `site.title`, `site.subtitle`, `site.description`, `site.url`, `site.base_path`. Available in all template types including taxonomy and standalone page templates.

---

## Theming

The theme lives entirely in `templates/base.html` and `static/`. Changes to `base.html` propagate to every page because all templates extend it.

```
templates/base.html    ← single theming entry point
static/                ← CSS, fonts, images — copied as-is to public/static/
```

### Tailwind CSS (recommended)

Tailwind keeps all visual decisions in the templates as utility classes, which makes it straightforward to adjust by describing the design in natural language.

**Quick start — CDN (no build step):**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900 antialiased">
  <div class="max-w-2xl mx-auto px-4 py-12">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

Use `<div class="prose prose-gray max-w-none">{{ content }}</div>` to style Markdown-rendered HTML. The typography plugin is bundled in the CDN build.

### Design intent → Tailwind classes

When the user describes a design in natural language, apply the corresponding changes to `base.html` (layout, colours, fonts) and to the individual templates (spacing, typography on specific elements).

| Intent | Where | What to change |
|---|---|---|
| Narrow / wide layout | `base.html` `<div>` | `max-w-2xl` → `max-w-4xl` (wide) or `max-w-prose` (narrow) |
| Dark background | `base.html` `<body>` | `bg-white text-gray-900` → `bg-gray-950 text-gray-100` |
| Dark mode (auto) | `<html>` + `<body>` | add `dark` class to `<html>`; use `dark:bg-gray-950 dark:text-gray-100` on `<body>` |
| Serif body font | `base.html` `<body>` | add `font-serif` |
| Monospace / code aesthetic | `base.html` `<body>` | add `font-mono` |
| Larger body text | `base.html` `<body>` | add `text-lg` |
| Minimal, no decoration | `base.html` | remove all colour classes, keep only `max-w-* mx-auto px-* py-*` |
| Coloured accent | links in templates | `text-blue-600 hover:underline` (swap colour as needed) |

**Adding a navigation bar** — insert above `{% block content %}` in `base.html`:

```html
<nav class="flex gap-6 mb-10 text-sm font-medium">
  <a href="/" class="hover:underline">Home</a>
  <a href="/blog" class="hover:underline">Blog</a>
  <a href="/about" class="hover:underline">About</a>
</nav>
```

**Production build** — use the standalone Tailwind CLI to generate a purged `static/style.css`, then replace the CDN `<script>` with `<link rel="stylesheet" href="/static/style.css">`.

---

## Debugging build errors

### Common errors

| Symptom | Cause | Fix |
|---|---|---|
| `ValidationError` on build | Front matter missing a required field or wrong type | Check all required fields are present and `date` is `YYYY-MM-DD` |
| `TemplateNotFound` | Template name in `adoy.toml` does not match a file in `templates/` | Verify the filename exactly (case-sensitive) |
| Content file produces no output, no error | `status` is `draft` or `archive` | Set `status: active` |
| Section files not built | `[content.<section>]` missing from `adoy.toml` | Add the section config block |
| Taxonomy pages not generated | `applies_to` does not include the section, or no content has that taxonomy field | Check both `adoy.toml` and front matter |
| Stale output after rename/delete | Incremental cache out of sync | Run `adoy build --clean-build` |
| `FileNotFoundError: adoy.toml` | Running `adoy build` from wrong directory | `cd` into the project root first |

### Diagnosing silently skipped files

adoy never errors on a content file with `status: draft` or `archive` — it simply produces no output. If a page is missing from the build output:

1. Open the source `.md` file and check `status:`.
2. Confirm the file is under a directory that matches a section in `adoy.toml`.
3. Confirm the section's `template` value matches an actual file in `templates/`.

### When to use `--clean-build`

Use it when the incremental cache is suspected to be stale: after manually deleting files from `public/`, after renaming templates, or when output looks wrong despite source files being correct.
