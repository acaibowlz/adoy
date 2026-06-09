import pytest
from pydantic import ValidationError

from adoy.models import Config
from adoy.parser import load_config


def test_load_config_valid(project_dir):
    config = load_config(project_dir)
    assert isinstance(config, Config)
    assert config.site.title == "Test Site"
    assert config.site.url == "https://example.com"
    assert "blog" in config.content
    assert config.content["blog"].permalink == "/blog/:slug"
    assert "tags" in config.taxonomy


def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path)


def test_load_config_missing_required_site_field(tmp_path):
    (tmp_path / "adoy.toml").write_text("""\
[site]
subtitle = "Sub"
description = "Desc"
url = "https://example.com"
base_path = "/"

[build]
paginate = 10
timezone = "UTC"

[template]
default = "post.html"
base = "base.html"
""")
    with pytest.raises(ValidationError):
        load_config(tmp_path)


def test_load_config_path_defaults(project_dir):
    config = load_config(project_dir)
    assert config.paths.content == "content/"
    assert config.paths.output == "public/"
