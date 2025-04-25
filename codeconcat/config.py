# -*- coding: utf-8 -*-
# codeconcat/config.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

HOME_CONFIG_PATH = Path.home() / ".codeconcat_config.json"
PROJECT_CONFIG_PATH = Path(".") / ".codeconcat_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "use_gitignore": True,
    "exclude_patterns": [],
    "whitelist_patterns": [],
    # Add other future config options here with defaults
}

# Flag to ensure default config creation happens only once per run if needed
_default_config_created = False


def load_config_file(path: Path) -> Optional[Dict[str, Any]]:
    """Loads configuration from a JSON file."""
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from config file: {path}")
        except OSError as e:
            logger.warning(f"Could not read config file: {path}. Error: {e}")
    return None


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merges two config dictionaries. Override takes precedence."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            # Combine lists for patterns? Or override? Let's override for simplicity.
            # Ensure uniqueness if combining later.
            merged[key] = value
        else:
            merged[key] = value
    return merged


def get_config() -> Dict[str, Any]:
    """Loads configuration from home and project files, merging them."""
    config = DEFAULT_CONFIG.copy()

    home_config = load_config_file(HOME_CONFIG_PATH)
    if home_config:
        config = merge_configs(config, home_config)
        logger.info(f"Loaded configuration from {HOME_CONFIG_PATH}")

    project_config = load_config_file(PROJECT_CONFIG_PATH)
    if project_config:
        config = merge_configs(config, project_config)
        logger.info(f"Loaded configuration from {PROJECT_CONFIG_PATH} (overrides home config)")

    # Create default home config only if neither home nor project config existed
    if not home_config and not project_config:
        create_default_config_if_needed(HOME_CONFIG_PATH)

    return config


def create_default_config_if_needed(path: Path) -> None:
    """Creates a default config file at the specified path if it doesn't exist."""
    global _default_config_created
    if not path.exists() and not _default_config_created:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info(f"Created default configuration file at: {path}")
            _default_config_created = True  # Mark as created for this run
        except OSError as e:
            logger.warning(f"Could not create default config file at {path}. Error: {e}")
