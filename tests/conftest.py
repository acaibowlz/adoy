from datetime import datetime
from pathlib import Path

import pytest

from adoy.models import (
    BuildConfig,
    Config,
    ContentConfig,
    FrontMatter,
    PathConfig,
    SiteConfig,
    TaxonomyConfig,
    TemplateConfig,
)

SAMPLE_TOML = """\
[site]
title = "Test Site"
subtitle = "A subtitle"
description = "A description"
url = "https://example.com"
base_path = "/"

[build]
paginate = 10
timezone = "UTC"

[template]
default = "post.html"
base = "base.html"

[content.blog]
section = "blog"
template = "post.html"
permalink = "/blog/:slug"

[taxonomy.tags]
name = "tags"
path = "/tags"
applies_to = ["blog"]
sort_by = "date"
template_taxonomy = "tags.html"
template_term = "tag.html"
"""

SAMPLE_POST = """\
---
title: Hello World
description: A test post
summary: Summary
date: 2026-03-28
content_type: blog
slug: hello-world
status: active
tags:
  - python
  - adoy
---

# Hello World

This is a test post.
"""


@pytest.fixture
def sample_fm() -> FrontMatter:
    return FrontMatter(
        title="Hello World",
        description="A test post",
        summary="Summary",
        date=datetime(2026, 3, 28),
        content_type="blog",
        slug="hello-world",
        status="active",
    )


@pytest.fixture
def sample_config() -> Config:
    return Config(
        site=SiteConfig(
            title="Test Site",
            subtitle="A subtitle",
            description="A description",
            url="https://example.com",
            base_path="/",
        ),
        paths=PathConfig(),
        build=BuildConfig(paginate=10, timezone="UTC"),
        template=TemplateConfig(default="post.html", base="base.html"),
        content={
            "blog": ContentConfig(section="blog", template="post.html", permalink="/blog/:slug"),
        },
        taxonomy={
            "tags": TaxonomyConfig(
                name="tags",
                path="/tags",
                applies_to=["blog"],
                sort_by="date",
                template_taxonomy="tags.html",
                template_term="tag.html",
            ),
        },
    )


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    (tmp_path / "content" / "blog").mkdir(parents=True)
    (tmp_path / "templates").mkdir()
    (tmp_path / "static").mkdir()

    (tmp_path / "adoy.toml").write_text(SAMPLE_TOML)

    (tmp_path / "templates" / "base.html").write_text(
        "<!DOCTYPE html><html><head><title>{% block title %}{% endblock %}</title></head>"
        "<body>{% block content %}{% endblock %}</body></html>"
    )
    (tmp_path / "templates" / "post.html").write_text(
        "{% extends 'base.html' %}"
        "{% block title %}{{ page.title }}{% endblock %}"
        "{% block content %}<h1>{{ page.title }}</h1>{{ content }}{% endblock %}"
    )
    (tmp_path / "templates" / "tags.html").write_text(
        "{% extends 'base.html' %}"
        "{% block title %}Tags{% endblock %}"
        "{% block content %}{% for term in terms %}<a href='/tags/{{ term }}'>{{ term }}</a>{% endfor %}{% endblock %}"
    )
    (tmp_path / "templates" / "tag.html").write_text(
        "{% extends 'base.html' %}"
        "{% block title %}{{ term }}{% endblock %}"
        "{% block content %}{% for page in pages %}<a href='/blog/{{ page.slug }}'>{{ page.title }}</a>{% endfor %}{% endblock %}"
    )
    (tmp_path / "content" / "blog" / "hello-world.md").write_text(SAMPLE_POST)

    return tmp_path
