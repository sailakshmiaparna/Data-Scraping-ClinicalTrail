from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    """Load and minimally validate application configuration."""
    with Path(path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}
    for key in ("topic", "source", "search", "output"):
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    return config
