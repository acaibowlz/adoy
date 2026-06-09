from datetime import datetime

import pytest
from pydantic import ValidationError

from adoy.models import (
    CacheStore,
    Config,
    ContentCacheEntry,
    ContentConfig,
    FrontMatter,
    Page,
    PathConfig,
    TaxonomyConfig,
)


def test_front_matter_valid(sample_fm):
    assert sample_fm.title == "Hello World"
    assert sample_fm.slug == "hello-world"
    assert sample_fm.status == "active"
    assert isinstance(sample_fm.date, datetime)


def test_front_matter_date_parsed_from_string():
    fm = FrontMatter(
        title="Post",
        description="Desc",
        summary="Sum",
        date="2026-03-28",
        content_type="blog",
        slug="post",
        status="active",
    )
    assert fm.date == datetime(2026, 3, 28)


def test_front_matter_missing_required_field():
    with pytest.raises(ValidationError):
        FrontMatter(
            title="Post",
            description="Desc",
            summary="Sum",
            # date missing
            content_type="blog",
            slug="post",
            status="active",
        )


def test_path_config_defaults():
    paths = PathConfig()
    assert paths.content == "content/"
    assert paths.templates == "templates/"
    assert paths.static == "static/"
    assert paths.output == "public/"


def test_config_content_and_taxonomy_are_dicts(sample_config):
    assert "blog" in sample_config.content
    assert isinstance(sample_config.content["blog"], ContentConfig)
    assert "tags" in sample_config.taxonomy
    assert isinstance(sample_config.taxonomy["tags"], TaxonomyConfig)


def test_config_empty_dicts_by_default():
    from adoy.models import BuildConfig, SiteConfig, TemplateConfig
    config = Config(
        site=SiteConfig(title="T", subtitle="S", description="D", url="https://x.com", base_path="/"),
        build=BuildConfig(paginate=10, timezone="UTC"),
        template=TemplateConfig(default="post.html", base="base.html"),
    )
    assert config.content == {}
    assert config.pages == {}
    assert config.taxonomy == {}


def test_content_cache_entry():
    entry = ContentCacheEntry(
        checksum="abc123",
        output_path="public/blog/hello-world/index.html",
        taxonomy_terms={"tags": ["python", "adoy"]},
    )
    assert entry.taxonomy_terms["tags"] == ["python", "adoy"]


def test_cache_store_roundtrip():
    entry = ContentCacheEntry(
        checksum="abc123",
        output_path="public/blog/hello-world/index.html",
        taxonomy_terms={"tags": ["python"]},
    )
    store = CacheStore(
        config_checksum="cfg123",
        template_checksums={"post.html": "tpl123"},
        content={"content/blog/hello-world.md": entry},
    )
    dumped = store.model_dump()
    restored = CacheStore.model_validate(dumped)
    assert restored.config_checksum == "cfg123"
    assert restored.content["content/blog/hello-world.md"].checksum == "abc123"
