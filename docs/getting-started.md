# Getting Started

## Installation

adoy requires Python 3.10 or later. Install it with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install adoy
```

Or add it to a project:

```bash
uv add adoy
```

## Creating a project

```bash
adoy init my-site
cd my-site
```

This creates the following structure:

```
my-site/
├── adoy.toml          # site configuration
├── CLAUDE.md          # agent instructions for this project
├── content/
│   └── blog/
│       └── hello-world.md
├── templates/
│   ├── base.html
│   ├── post.html
│   ├── tags.html
│   └── tag.html
├── static/            # assets copied as-is to public/static/
└── .gitignore
```

## Building the site

```bash
adoy build
```

Output is written to `public/`. The first build is always a full build. Subsequent builds are incremental — only changed files are rebuilt.

```bash
adoy build --clean-build   # force a full rebuild
```

## Local development

```bash
adoy serve
```

Starts a local server at `http://localhost:8000` and watches for changes. Any edit to `content/`, `templates/`, or `adoy.toml` triggers a rebuild automatically.

```bash
adoy serve --port 3000     # use a different port
```

## Next steps

- [Configuration](./configuration.md) — site metadata, paths, content sections, taxonomies
- [Content](./content.md) — writing posts, managing sections and front matter
- [Theming](./theming.md) — templates, Tailwind CSS, customising the design
