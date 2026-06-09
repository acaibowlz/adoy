# Configuration

adoy is configured through `adoy.toml` in the project root.

## Site

```toml
[site]
title = "My Site"
subtitle = "A site built with adoy"
description = "My personal site"
url = "https://example.com"
base_path = "/"
```

| Field | Description |
|---|---|
| `title` | Site name — available in templates as `{{ site.title }}` |
| `subtitle` | Short tagline |
| `description` | Used in meta tags |
| `url` | Canonical base URL, used in `sitemap.xml` |
| `base_path` | URL prefix for subdirectory deployments (e.g. `"/my-repo/"` for GitHub Pages) |

All `[site]` fields are available in every template via the `site` global.

## Build

```toml
[build]
paginate = 10
timezone = "UTC"
```

| Field | Description |
|---|---|
| `paginate` | Number of items per page on listing pages |
| `timezone` | Timezone used when parsing dates without an explicit offset |

## Template

```toml
[template]
default = "post.html"
base = "base.html"
```

| Field | Description |
|---|---|
| `default` | Fallback template when no section-specific template is configured |
| `base` | The base layout template that all other templates extend |

## Paths

```toml
[paths]
content = "content/"
templates = "templates/"
static = "static/"
output = "public/"
```

All paths are relative to the project root. The defaults shown above apply if `[paths]` is omitted.

## Content sections

Each section groups content files that share a template and permalink pattern.

```toml
[content.blog]
section = "blog"
template = "post.html"
permalink = "/blog/:slug"

[content.projects]
section = "projects"
template = "project.html"
permalink = "/projects/:slug"
```

Files under `content/<section>/` are built using that section's template and permalink.

### Permalink variables

| Variable | Resolves to |
|---|---|
| `:slug` | `slug` field from front matter |
| `:section` | Section directory name |
| `:year` | Four-digit year from `date` |
| `:month` | Zero-padded month from `date` |
| `:day` | Zero-padded day from `date` |
| `:title` | `title` lowercased, spaces replaced with `-` |

## Taxonomies

Taxonomies aggregate content across one or more sections.

```toml
[taxonomy.tags]
name = "tags"
path = "/tags"
applies_to = ["blog", "projects"]
sort_by = "date"
template_taxonomy = "tags.html"
template_term = "tag.html"
```

| Field | Description |
|---|---|
| `name` | Taxonomy identifier — must match the front matter field name |
| `path` | URL path for the taxonomy overview page |
| `applies_to` | Sections this taxonomy indexes |
| `sort_by` | How to sort pages within a term (`"date"` is the only supported value) |
| `template_taxonomy` | Template for the overview page listing all terms |
| `template_term` | Template for individual term pages |

## Standalone pages

One-off pages with no section and no taxonomy indexing.

```toml
[pages.about]
template = "about.html"
permalink = "/about"

[pages.contact]
template = "contact.html"
permalink = "/contact"
```

The content file for a standalone page must be placed at `content/<name>.md`.
