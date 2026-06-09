from pathlib import Path

import pytest

from adoy.cache import checksum, diff, load_cache, save_cache
from adoy.models import CacheStore, ContentCacheEntry


def test_checksum_is_deterministic(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    assert checksum(f) == checksum(f)


def test_checksum_differs_for_different_content(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("world")
    assert checksum(a) != checksum(b)


def test_load_cache_missing_file_returns_empty(tmp_path):
    store = load_cache(tmp_path)
    assert store.config_checksum == ""
    assert store.content == {}
    assert store.template_checksums == {}


def test_save_and_load_cache_roundtrip(tmp_path):
    entry = ContentCacheEntry(
        checksum="abc",
        output_path="public/blog/post/index.html",
        taxonomy_terms={"tags": ["python"]},
    )
    store = CacheStore(
        config_checksum="cfg",
        template_checksums={"post.html": "tpl"},
        content={"content/blog/post.md": entry},
    )
    save_cache(store, tmp_path)
    loaded = load_cache(tmp_path)
    assert loaded.config_checksum == "cfg"
    assert loaded.template_checksums == {"post.html": "tpl"}
    assert loaded.content["content/blog/post.md"].checksum == "abc"
    assert loaded.content["content/blog/post.md"].taxonomy_terms == {"tags": ["python"]}


def test_diff_fresh_cache_triggers_full_rebuild(project_dir, sample_config):
    plan = diff(load_cache(project_dir), sample_config, project_dir)
    assert plan.full_rebuild is True


def test_diff_unchanged_after_build(project_dir):
    from adoy.builder import build
    from adoy.parser import load_config
    config = load_config(project_dir)
    build(config, project_dir)
    plan = diff(load_cache(project_dir), config, project_dir)
    assert plan.full_rebuild is False
    assert len(plan.content_to_build) == 0
    assert len(plan.content_to_delete) == 0


def test_diff_detects_modified_content(project_dir):
    from adoy.builder import build
    from adoy.parser import load_config
    config = load_config(project_dir)
    build(config, project_dir)

    post = project_dir / "content" / "blog" / "hello-world.md"
    post.write_text(post.read_text() + "\nMore content.\n")

    plan = diff(load_cache(project_dir), config, project_dir)
    assert post in plan.content_to_build


def test_diff_detects_deleted_content(project_dir):
    from adoy.builder import build
    from adoy.parser import load_config
    config = load_config(project_dir)
    build(config, project_dir)

    post = project_dir / "content" / "blog" / "hello-world.md"
    post.unlink()

    plan = diff(load_cache(project_dir), config, project_dir)
    assert post in plan.content_to_delete


def test_diff_full_rebuild_on_config_change(project_dir):
    from adoy.builder import build
    from adoy.parser import load_config
    config = load_config(project_dir)
    build(config, project_dir)

    toml = (project_dir / "adoy.toml").read_text()
    (project_dir / "adoy.toml").write_text(toml.replace("Test Site", "Updated Site"))

    config = load_config(project_dir)
    plan = diff(load_cache(project_dir), config, project_dir)
    assert plan.full_rebuild is True
