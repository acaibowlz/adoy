# Theming

adoy has no built-in theme system. A theme is CSS (and optional JS) loaded by `templates/base.html`, with assets stored in `static/`. Because every page template extends `base.html`, changes there propagate everywhere.

```
templates/base.html    ← single theming entry point
static/                ← CSS, fonts, images — copied to public/static/ on build
```

## Template structure

All templates use [Jinja2](https://jinja.palletsprojects.com/). Page templates must extend `base.html` and fill in its blocks:

```html
{% extends "base.html" %}
{% block title %}{{ page.title }}{% endblock %}
{% block content %}
  <h1>{{ page.title }}</h1>
  {{ content }}
{% endblock %}
```

`base.html` defines two blocks:

| Block | Purpose |
|---|---|
| `title` | Content of the `<title>` tag (the base appends ` — {{ site.title }}`) |
| `title_suffix` | Override to suppress or change the site name suffix |
| `content` | Main page body |

## Template context

### All templates

| Variable | Type | Description |
|---|---|---|
| `site` | SiteConfig | Site-wide config from `adoy.toml` — `site.title`, `site.url`, `site.base_path`, etc. |

### Content and standalone page templates

| Variable | Type | Description |
|---|---|---|
| `page` | FrontMatter | Parsed front matter. Core fields plus any custom fields. |
| `content` | `str` | Body rendered to HTML |

### Taxonomy overview templates

| Variable | Type | Description |
|---|---|---|
| `taxonomy` | `str` | Taxonomy name (e.g. `"tags"`) |
| `terms` | `dict[str, list[FrontMatter]]` | Term name → pages carrying that term |

### Taxonomy term templates

| Variable | Type | Description |
|---|---|---|
| `taxonomy` | `str` | Taxonomy name |
| `term` | `str` | This term (e.g. `"python"`) |
| `pages` | `list[FrontMatter]` | Pages carrying this term, sorted newest first |

## Tailwind CSS

Tailwind is the recommended approach. All visual decisions live as utility classes directly in the templates, which makes the design easy to read and adjust without a separate stylesheet.

### Quick start — CDN

No build step required. Add one script tag to `base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{% endblock %}{% block title_suffix %} — {{ site.title }}{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900 antialiased">
  <div class="max-w-2xl mx-auto px-4 py-12">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

Use the `prose` class from the bundled Typography plugin to style Markdown-rendered HTML:

```html
<div class="prose prose-gray max-w-none">{{ content }}</div>
```

### Production — Tailwind CLI

The CDN Play build is not suitable for production (large bundle, no purging). Use the standalone Tailwind CLI — no Node.js required:

```bash
# Download (Linux x64)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64 && mv tailwindcss-linux-x64 tailwindcss

# Generate a purged CSS file
./tailwindcss -i /dev/null -o static/style.css --content "templates/**/*.html" --minify
```

Replace the CDN `<script>` tag with:

```html
<link rel="stylesheet" href="{{ site.base_path }}static/style.css">
```

### Common design adjustments

| Intent | Element | Change |
|---|---|---|
| Wider layout | `<div>` in `<body>` | `max-w-2xl` → `max-w-4xl` |
| Narrower, book-like | `<div>` in `<body>` | `max-w-2xl` → `max-w-prose` |
| Dark background | `<body>` | `bg-white text-gray-900` → `bg-gray-950 text-gray-100` |
| Auto dark mode | `<html>` + `<body>` | Add `dark` class to `<html>`; use `dark:` variants on `<body>` |
| Serif body font | `<body>` | Add `font-serif` |
| Monospace aesthetic | `<body>` | Add `font-mono` |
| Larger text | `<body>` | Add `text-lg` |

### Adding a navigation bar

Insert above `{% block content %}` in `base.html`:

```html
<nav class="flex gap-6 mb-10 text-sm font-medium">
  <a href="{{ site.base_path }}" class="hover:underline">Home</a>
  <a href="{{ site.base_path }}blog" class="hover:underline">Blog</a>
  <a href="{{ site.base_path }}about" class="hover:underline">About</a>
</nav>
```

## Static assets

Files in `static/` are copied to `public/static/` on every build. Reference them in templates using `site.base_path` as a prefix so subdirectory deployments work correctly:

```html
<link rel="stylesheet" href="{{ site.base_path }}static/style.css">
<img src="{{ site.base_path }}static/images/logo.png" alt="Logo">
```
