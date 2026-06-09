# Content

## File layout

Content files are Markdown (`.md`) with a YAML front matter block. They live under `content/`:

```
content/
├── blog/
│   ├── hello-world.md
│   └── second-post.md
├── projects/
│   └── my-project.md
└── about.md              # standalone page
```

Files directly under a section directory (e.g. `content/blog/`) are built as section content. Files at the top level of `content/` are built as standalone pages if they are declared in `[pages.*]` in `adoy.toml`.

## Front matter

Every content file requires a YAML front matter block:

```yaml
---
title: Hello World
description: A brief introduction to adoy.
summary: Getting started with adoy.
date: 2026-06-10
content_type: blog
slug: hello-world
status: active
tags:
  - adoy
  - tutorial
---

Body text in Markdown goes here.
```

### Required fields

| Field | Type | Description |
|---|---|---|
| `title` | string | Page title |
| `description` | string | Short description, used in meta tags |
| `summary` | string | One-line summary for listing pages |
| `date` | `YYYY-MM-DD` | Publication date |
| `content_type` | string | Must match the section name in `adoy.toml` |
| `slug` | string | URL identifier used in the permalink |
| `status` | string | `active`, `draft`, or `archive` |

### Status

| Value | Behaviour |
|---|---|
| `active` | Built and included in the site |
| `draft` | Skipped — no output file, no error |
| `archive` | Skipped — no output file, no error |

### Custom fields

Any additional front matter field is preserved and available in templates as an attribute on the `page` object:

```yaml
cover_image: /static/images/hero.jpg
author: Jane
```

```html
<img src="{{ page.cover_image }}" alt="">
<span>{{ page.author }}</span>
```

### Taxonomy fields

Taxonomy terms are declared as YAML lists using the taxonomy name as the key:

```yaml
tags:
  - python
  - tutorial
series:
  - building-adoy
```

The taxonomy must be defined in `adoy.toml` under `[taxonomy.*]` and must list the content's section in `applies_to`.

## Adding a new content section

1. Create the section directory:

   ```bash
   mkdir content/notes
   ```

2. Add the section to `adoy.toml`:

   ```toml
   [content.notes]
   section = "notes"
   template = "note.html"
   permalink = "/notes/:slug"
   ```

3. Create the template at `templates/note.html`.

4. Create content files under `content/notes/`.

## Standalone pages

Standalone pages sit outside the section system — they have no taxonomy and are not listed in any index.

1. Create `content/about.md` with front matter.
2. Declare the page in `adoy.toml`:

   ```toml
   [pages.about]
   template = "about.html"
   permalink = "/about"
   ```

3. Create `templates/about.html`.

## Markdown

The body is rendered to HTML using [mistune](https://mistune.lepture.com/). Standard CommonMark syntax is supported: headings, bold, italic, links, images, lists, blockquotes, and fenced code blocks.
