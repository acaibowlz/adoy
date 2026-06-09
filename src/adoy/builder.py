import shutil
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, tostring

import frontmatter as fm_lib

from adoy.cache import BuildPlan, CacheStore, checksum, diff, load_cache, save_cache, update_cache
from adoy.models import Config, ContentCacheEntry, FrontMatter, Page
from adoy.renderer import Renderer


def _compute_output_path(fm: FrontMatter, section: str, permalink: str, output_dir: Path) -> Path:
    """Resolve a permalink pattern to an output file path.

    Supported variables:
      :slug    — front matter slug
      :section — content section (top-level directory under content/)
      :year    — four-digit year from date
      :month   — zero-padded month from date
      :day     — zero-padded day from date
      :title   — front matter title, lowercased and space-replaced with hyphens
    """
    path = (
        permalink
        .replace(":slug", fm.slug)
        .replace(":section", section)
        .replace(":year", fm.date.strftime("%Y"))
        .replace(":month", fm.date.strftime("%m"))
        .replace(":day", fm.date.strftime("%d"))
        .replace(":title", fm.title.lower().replace(" ", "-"))
        .lstrip("/")
    )
    return output_dir / path / "index.html"


def _build_content_file(
    content_path: Path,
    config: Config,
    project_root: Path,
    renderer: Renderer,
    output_dir: Path,
) -> tuple[ContentCacheEntry, FrontMatter] | None:
    post = fm_lib.load(str(content_path))
    fm = FrontMatter.model_validate(post.metadata)

    if fm.status != "active":
        return None

    content_dir = project_root / config.paths.content
    section = content_path.relative_to(content_dir).parts[0]
    content_config = config.content.get(section)
    if content_config is None:
        return None

    page = Page(front_matter=fm, body=post.content, source_path=content_path)

    output_path = _compute_output_path(fm, section, content_config.permalink, output_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Extract taxonomy terms from raw front matter
    terms: dict[str, list[str]] = {}
    for tax_name, tax_config in config.taxonomy.items():
        if section in tax_config.applies_to:
            field_terms = post.metadata.get(tax_name, [])
            if field_terms:
                terms[tax_name] = list(field_terms)

    html = renderer.render(page, content_config.template)
    output_path.write_text(html, encoding="utf-8")

    entry = ContentCacheEntry(
        checksum=checksum(content_path),
        output_path=str(output_path.relative_to(project_root)),
        taxonomy_terms=terms,
    )
    return entry, fm


def _build_taxonomy_pages(
    config: Config,
    project_root: Path,
    cache: CacheStore,
    built: dict[Path, ContentCacheEntry],
    renderer: Renderer,
    output_dir: Path,
    taxonomy_names: set[str] | None = None,
) -> None:
    # Merge newly built entries into the cache view
    merged: dict[str, ContentCacheEntry] = dict(cache.content)
    for path, entry in built.items():
        merged[str(path.relative_to(project_root))] = entry

    for tax_name, tax_config in config.taxonomy.items():
        if taxonomy_names is not None and tax_name not in taxonomy_names:
            continue

        # Collect front matters grouped by term
        terms: dict[str, list[FrontMatter]] = {}
        for rel, entry in merged.items():
            term_list = entry.taxonomy_terms.get(tax_name, [])
            if not term_list:
                continue
            source = project_root / rel
            if not source.exists():
                continue
            post = fm_lib.load(str(source))
            fm = FrontMatter.model_validate(post.metadata)
            if fm.status != "active":
                continue
            for term in term_list:
                terms.setdefault(term, []).append(fm)

        for term in terms:
            terms[term].sort(key=lambda p: p.date, reverse=True)

        # Taxonomy overview page
        overview_path = output_dir / tax_config.path.lstrip("/") / "index.html"
        overview_path.parent.mkdir(parents=True, exist_ok=True)
        overview_path.write_text(
            renderer.render_taxonomy_overview(tax_name, terms, tax_config.template_taxonomy),
            encoding="utf-8",
        )

        # Individual term pages
        for term, pages in terms.items():
            term_path = output_dir / tax_config.path.lstrip("/") / term / "index.html"
            term_path.parent.mkdir(parents=True, exist_ok=True)
            term_path.write_text(
                renderer.render_taxonomy_term(tax_name, term, pages, tax_config.template_term),
                encoding="utf-8",
            )


def _build_standalone_pages(
    config: Config,
    project_root: Path,
    renderer: Renderer,
    output_dir: Path,
) -> None:
    content_dir = project_root / config.paths.content
    for page_name, page_config in config.pages.items():
        content_path = content_dir / f"{page_name}.md"
        if not content_path.exists():
            continue
        post = fm_lib.load(str(content_path))
        fm = FrontMatter.model_validate(post.metadata)
        page = Page(front_matter=fm, body=post.content, source_path=content_path)
        output_path = output_dir / page_config.permalink.lstrip("/") / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(renderer.render(page, page_config.template), encoding="utf-8")


def _output_path_to_url(output_path: Path, output_dir: Path, base_url: str) -> str:
    rel = output_path.relative_to(output_dir)
    # Strip index.html to produce a clean trailing-slash URL
    if rel.name == "index.html":
        rel = rel.parent
    return base_url.rstrip("/") + "/" + str(rel).replace("\\", "/")


def _build_sitemap(
    base_url: str,
    output_dir: Path,
    urls: list[tuple[str, datetime | None]],
) -> None:
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for loc, lastmod in urls:
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = loc
        if lastmod:
            SubElement(url_el, "lastmod").text = lastmod.strftime("%Y-%m-%d")
    indent(urlset, space="  ")
    sitemap = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(urlset, encoding="unicode").encode()
    (output_dir / "sitemap.xml").write_bytes(sitemap)


def _build_robots(base_url: str, output_dir: Path) -> None:
    (output_dir / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base_url.rstrip('/')}/sitemap.xml\n"
    )


def build(config: Config, project_root: Path) -> None:
    cache = load_cache(project_root)
    plan = diff(cache, config, project_root)
    renderer = Renderer(config, project_root)
    output_dir = project_root / config.paths.output
    output_dir.mkdir(exist_ok=True)

    built: dict[Path, ContentCacheEntry] = {}
    sitemap_urls: list[tuple[str, datetime | None]] = []
    base_url = config.site.url

    if plan.full_rebuild:
        to_build = list((project_root / config.paths.content).rglob("*.md"))
        to_delete: set[Path] = set()
    else:
        to_build = list(plan.content_to_build)
        to_delete = plan.content_to_delete

    # Build content pages
    for content_path in to_build:
        result = _build_content_file(content_path, config, project_root, renderer, output_dir)
        if result:
            entry, fm = result
            built[content_path] = entry
            sitemap_urls.append((_output_path_to_url(project_root / entry.output_path, output_dir, base_url), fm.date))

    # Remove deleted content
    for content_path in to_delete:
        rel = str(content_path.relative_to(project_root))
        cached = cache.content.get(rel)
        if cached:
            out = project_root / cached.output_path
            if out.exists():
                out.unlink()

    # Build taxonomy pages
    if plan.full_rebuild:
        _build_taxonomy_pages(config, project_root, cache, built, renderer, output_dir)
    elif plan.taxonomy_terms_to_rebuild:
        _build_taxonomy_pages(
            config,
            project_root,
            cache,
            built,
            renderer,
            output_dir,
            taxonomy_names=set(plan.taxonomy_terms_to_rebuild.keys()),
        )

    # Collect taxonomy URLs for sitemap
    for tax_config in config.taxonomy.values():
        tax_dir = output_dir / tax_config.path.lstrip("/")
        for index in tax_dir.rglob("index.html"):
            sitemap_urls.append((_output_path_to_url(index, output_dir, base_url), None))

    # Build standalone pages
    _build_standalone_pages(config, project_root, renderer, output_dir)

    # Collect standalone page URLs for sitemap
    for page_config in config.pages.values():
        out = output_dir / page_config.permalink.lstrip("/") / "index.html"
        if out.exists():
            sitemap_urls.append((_output_path_to_url(out, output_dir, base_url), None))

    # Copy static assets
    static_dir = project_root / config.paths.static
    if static_dir.is_dir():
        shutil.copytree(static_dir, output_dir / "static", dirs_exist_ok=True)

    # Build sitemap and robots.txt
    _build_sitemap(base_url, output_dir, sitemap_urls)
    _build_robots(base_url, output_dir)

    new_cache = update_cache(cache, config, project_root, built, to_delete)
    save_cache(new_cache, project_root)
