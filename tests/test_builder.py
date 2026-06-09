from datetime import datetime
from pathlib import Path

import pytest

from adoy.builder import _compute_output_path, build
from adoy.models import FrontMatter
from adoy.parser import load_config


@pytest.fixture
def fm():
    return FrontMatter(
        title="My Post",
        description="Desc",
        summary="Sum",
        date=datetime(2026, 3, 28),
        content_type="blog",
        slug="my-post",
        status="active",
    )


def test_compute_output_path_slug(fm, tmp_path):
    out = _compute_output_path(fm, "blog", "/blog/:slug", tmp_path)
    assert out == tmp_path / "blog" / "my-post" / "index.html"


def test_compute_output_path_date_vars(fm, tmp_path):
    out = _compute_output_path(fm, "blog", "/:year/:month/:day/:slug", tmp_path)
    assert out == tmp_path / "2026" / "03" / "28" / "my-post" / "index.html"


def test_compute_output_path_section(fm, tmp_path):
    out = _compute_output_path(fm, "blog", "/:section/:slug", tmp_path)
    assert out == tmp_path / "blog" / "my-post" / "index.html"


def test_compute_output_path_title(fm, tmp_path):
    out = _compute_output_path(fm, "blog", "/posts/:title", tmp_path)
    assert out == tmp_path / "posts" / "my-post" / "index.html"


def test_build_creates_content_page(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)
    assert (project_dir / "public" / "blog" / "hello-world" / "index.html").exists()


def test_build_creates_taxonomy_pages(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)
    assert (project_dir / "public" / "tags" / "index.html").exists()
    assert (project_dir / "public" / "tags" / "python" / "index.html").exists()
    assert (project_dir / "public" / "tags" / "adoy" / "index.html").exists()


def test_build_creates_sitemap(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)
    sitemap = project_dir / "public" / "sitemap.xml"
    assert sitemap.exists()
    content = sitemap.read_text()
    assert "https://example.com/blog/hello-world" in content
    assert "2026-03-28" in content


def test_build_creates_robots_txt(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)
    robots = project_dir / "public" / "robots.txt"
    assert robots.exists()
    assert "Sitemap: https://example.com/sitemap.xml" in robots.read_text()


def test_build_skips_draft(project_dir):
    post = project_dir / "content" / "blog" / "draft-post.md"
    post.write_text("""\
---
title: Draft Post
description: Draft
summary: Sum
date: 2026-03-28
content_type: blog
slug: draft-post
status: draft
---
Draft content.
""")
    config = load_config(project_dir)
    build(config, project_dir)
    assert not (project_dir / "public" / "blog" / "draft-post" / "index.html").exists()


def test_build_removes_deleted_content(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)

    output = project_dir / "public" / "blog" / "hello-world" / "index.html"
    assert output.exists()

    (project_dir / "content" / "blog" / "hello-world.md").unlink()
    build(config, project_dir)

    assert not output.exists()


def test_incremental_build_only_rebuilds_changed(project_dir):
    config = load_config(project_dir)
    build(config, project_dir)

    # Add a second post
    (project_dir / "content" / "blog" / "second-post.md").write_text("""\
---
title: Second Post
description: Second
summary: Sum
date: 2026-03-29
content_type: blog
slug: second-post
status: active
tags:
  - python
---
Second post.
""")
    build(config, project_dir)
    assert (project_dir / "public" / "blog" / "second-post" / "index.html").exists()
    # Original post should still exist
    assert (project_dir / "public" / "blog" / "hello-world" / "index.html").exists()
