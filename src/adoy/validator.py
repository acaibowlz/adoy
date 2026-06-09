from pathlib import Path

from adoy.models import Config


class ConfigValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(f"- {e}" for e in errors))


def validate_config(config: Config, project_root: Path) -> None:
    """Validate a loaded Config against the filesystem. Raises ConfigValidationError if any issues are found."""
    errors: list[str] = []

    templates_dir = project_root / config.paths.templates

    # Validate required directories exist
    for label, rel_path in [
        ("content", config.paths.content),
        ("templates", config.paths.templates),
        ("static", config.paths.static),
    ]:
        if not (project_root / rel_path).is_dir():
            errors.append(f"[paths.{label}] directory not found: {rel_path}")

    # Validate base templates exist
    for label, template in [
        ("template.default", config.template.default),
        ("template.base", config.template.base),
    ]:
        if not (templates_dir / template).is_file():
            errors.append(f"[{label}] template not found: {template}")

    # Validate content section templates
    for section, content_config in config.content.items():
        if not (templates_dir / content_config.template).is_file():
            errors.append(f"[content.{section}] template not found: {content_config.template}")

    # Validate page templates
    for name, page_config in config.pages.items():
        if not (templates_dir / page_config.template).is_file():
            errors.append(f"[pages.{name}] template not found: {page_config.template}")

    # Validate taxonomy templates and applies_to references
    for name, taxonomy in config.taxonomy.items():
        if not (templates_dir / taxonomy.template_taxonomy).is_file():
            errors.append(f"[taxonomy.{name}] template_taxonomy not found: {taxonomy.template_taxonomy}")
        if not (templates_dir / taxonomy.template_term).is_file():
            errors.append(f"[taxonomy.{name}] template_term not found: {taxonomy.template_term}")
        for section in taxonomy.applies_to:
            if section not in config.content:
                errors.append(f"[taxonomy.{name}] applies_to references unknown section: {section}")

    if errors:
        raise ConfigValidationError(errors)
