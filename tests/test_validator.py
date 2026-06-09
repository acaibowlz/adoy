import pytest

from adoy.parser import load_config
from adoy.validator import ConfigValidationError, validate_config


def test_validate_valid_config(project_dir):
    config = load_config(project_dir)
    validate_config(config, project_dir)  # should not raise


def test_validate_missing_content_dir(project_dir):
    (project_dir / "content").rename(project_dir / "content_bak")
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert any("paths.content" in e for e in exc_info.value.errors)


def test_validate_missing_templates_dir(project_dir):
    (project_dir / "templates").rename(project_dir / "templates_bak")
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert any("paths.templates" in e for e in exc_info.value.errors)


def test_validate_missing_content_template(project_dir):
    (project_dir / "templates" / "post.html").unlink()
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert any("content.blog" in e for e in exc_info.value.errors)


def test_validate_missing_taxonomy_template(project_dir):
    (project_dir / "templates" / "tags.html").unlink()
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert any("taxonomy.tags" in e for e in exc_info.value.errors)


def test_validate_applies_to_unknown_section(project_dir):
    toml = (project_dir / "adoy.toml").read_text()
    toml = toml.replace('applies_to = ["blog"]', 'applies_to = ["nonexistent"]')
    (project_dir / "adoy.toml").write_text(toml)
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert any("nonexistent" in e for e in exc_info.value.errors)


def test_validate_collects_multiple_errors(project_dir):
    (project_dir / "templates" / "post.html").unlink()
    (project_dir / "templates" / "tags.html").unlink()
    config = load_config(project_dir)
    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config, project_dir)
    assert len(exc_info.value.errors) >= 2
