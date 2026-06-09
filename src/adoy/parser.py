from pathlib import Path
from typing import Any

try:
    import tomllib  # pyright: ignore [reportMissingImports]
except ModuleNotFoundError:
    import tomli as tomllib

from adoy.models import Config


def load_config(project_root: Path) -> Config:
    config_file = project_root / "adoy.toml"

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with config_file.open("rb") as f:
        raw: dict[str, Any] = tomllib.load(f)

    return Config.model_validate(raw)
