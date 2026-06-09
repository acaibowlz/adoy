from pathlib import Path

import pytest

from adoy.models import Page
from adoy.parser import load_config
from adoy.renderer import Renderer


@pytest.fixture
def renderer(project_dir):
    config = load_config(project_dir)
    return Renderer(config, project_dir)


def test_render_page(renderer, sample_fm):
    page = Page(front_matter=sample_fm, body="**bold**", source_path=Path("content/blog/hello-world.md"))
    html = renderer.render(page, "post.html")
    assert "<h1>Hello World</h1>" in html
    assert "<strong>bold</strong>" in html


def test_render_page_extra_context(renderer, sample_fm):
    page = Page(front_matter=sample_fm, body="", source_path=Path("content/blog/hello-world.md"))
    html = renderer.render(page, "post.html", extra={"custom": "value"})
    assert "<title>Hello World</title>" in html


def test_render_taxonomy_overview(renderer, sample_fm):
    terms = {"python": [sample_fm], "adoy": [sample_fm]}
    html = renderer.render_taxonomy_overview("tags", terms, "tags.html")
    assert "python" in html
    assert "adoy" in html


def test_render_taxonomy_term(renderer, sample_fm):
    html = renderer.render_taxonomy_term("tags", "python", [sample_fm], "tag.html")
    assert "python" in html
    assert "Hello World" in html


def test_render_markdown_to_html(renderer, sample_fm):
    page = Page(front_matter=sample_fm, body="# Heading\n\nA paragraph.", source_path=Path("content/blog/hello-world.md"))
    html = renderer.render(page, "post.html")
    assert "<h1>Heading</h1>" in html
    assert "<p>A paragraph.</p>" in html
