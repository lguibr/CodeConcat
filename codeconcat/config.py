# -*- coding: utf-8 -*-
# codeconcat/config.py
"""
Configuration Management Module for CodeConcat.

This module handles the loading, merging, and creation of configuration
files for CodeConcat. It supports a hierarchy of configuration sources:
1. Default Configuration (Built-in)
2. Home Directory Configuration (`~/.codeconcat_config.json`)
3. Project Directory Configuration (`./.codeconcat_config.json`)
4. CLI Arguments (Overrides everything)

The module also defines the extensive default exclusion patterns used
to filter out non-essential files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

HOME_CONFIG_PATH = Path.home() / ".codeconcat_config.json"
PROJECT_CONFIG_PATH = Path(".") / ".codeconcat_config.json"

# --- Comprehensive Default Exclusions ---
# List of regex patterns to exclude common non-source files/directories
DEFAULT_EXCLUDE_PATTERNS = [
    # Version Control Systems
    r"(?:^|/)\.git/",
    r"(?:^|/)\.svn/",
    r"(?:^|/)\.hg/",
    r"(?:^|/)\.bzr/",
    # OS Generated Files
    r"\.DS_Store$",
    r"Thumbs\.db$",
    # Python Specific
    r"(?:^|/)__pycache__/",
    r".*\.py[co]$",  # .pyc, .pyo
    r"(?:^|/)\.venv/",
    r"(?:^|/)venv/",
    r"(?:^|/)env/",
    r"(?:^|/)\.env",
    r"(?:^|/)\.pytest_cache/",
    r"(?:^|/)\.mypy_cache/",
    r"(?:^|/)build/",
    r"(?:^|/)dist/",
    r".*\.egg-info/",
    r"(?:^|/)htmlcov/",  # Coverage reports
    # Node.js / Javascript / Typescript Specific
    r"(?:^|/)node_modules/",
    r"\.npm/",
    r".*\.log$",  # General logs, often from node
    r"npm-debug\.log.*",
    r"yarn-debug\.log.*",
    r"yarn-error\.log.*",
    # Maybe keep lock files? Let's exclude build outputs for now.
    # r"package-lock\.json$",
    # r"yarn\.lock$",
    r"(?:^|/)dist/",  # Common JS build output dir
    r"(?:^|/)build/",  # Common JS build output dir
    r"(?:^|/)coverage/",  # JS Coverage reports
    # Java Specific
    r".*\.class$",
    r".*\.jar$",
    r".*\.war$",
    r".*\.ear$",
    r"(?:^|/)target/",
    r"(?:^|/)\.settings/",
    r"\.classpath$",
    r"\.project$",
    # C / C++ Specific
    r".*\.o$",  # Object files
    r".*\.a$",  # Static libraries
    r".*\.so$",  # Shared libraries (Linux)
    r".*\.dylib$",  # Shared libraries (macOS)
    r".*\.dll$",  # Shared libraries (Windows)
    r".*\.exe$",  # Executables (Windows)
    r".*\.out$",  # Common executable name (Unix)
    r"(?:^|/)bin/",  # Common output dir
    r"(?:^|/)build/",  # Common build dir
    r"(?:^|/)Debug/",  # Common build config dir
    r"(?:^|/)Release/",  # Common build config dir
    # IDE / Editor Specific
    r"(?:^|/)\.vscode/",
    r"(?:^|/)\.idea/",
    r".*\.swp$",  # Vim swap files
    r".*~$",  # Backup files
    r".*\.sublime-.*",  # Sublime Text files
    # General Cache / Temp / Logs
    r".*[cC]ache.*",  # General cache directories/files
    r"(?:^|/)logs/",
    r"(?:^|/)[Tt]emp/",
    r"(?:^|/)[Tt]mp/",
    # Tool Specific (Add more as needed)
    r"(?:^|/)\.terraform/",
    # Common Output Files (add more if needed)
    # Note: The actual output file is handled dynamically in main.py
    # But we can exclude common names users might choose.
    r"output\.txt$",
    r"resumed\.txt$",
    r"concatenated_code\.txt$",
]

# --- Default Configuration Dictionary ---
DEFAULT_CONFIG: Dict[str, Any] = {
    "use_gitignore": True,  # Still respect .gitignore by default
    "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
    "whitelist_patterns": [],  # No default whitelist
    # Add other future config options here with defaults
}

# Flag to ensure default config creation happens only once per run if needed
_default_config_created = False


def load_config_file(path: Path) -> Optional[Dict[str, Any]]:
    """
    Loads configuration from a JSON file.

    Args:
        path (Path): Aboslute path to the configuration file.

    Returns:
        Optional[Dict[str, Any]]: Configuration dictionary if successful, None otherwise.
        Returns None if file does not exist or JSON is invalid.
    """
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
    """
    Merges two config dictionaries. Override takes precedence.

    List values (like patterns) in the override dictionary will *replace*
    the lists in the base dictionary, rather than appending to them.

    Args:
        base (Dict[str, Any]): The base configuration dictionary.
        override (Dict[str, Any]): The configuration dictionary to merge on top.

    Returns:
        Dict[str, Any]: A new merged configuration dictionary.
    """
    merged = base.copy()
    for key, value in override.items():
        # If key exists and types are compatible for merging (e.g., both dicts)
        # you could implement deeper merging. For now, override replaces.
        merged[key] = value
    return merged


def get_config() -> Dict[str, Any]:
    """
    Loads configuration from default, home, and project files, merging them.

    Hierarchy (Highest precedence last):
    1. Default Config (Memory)
    2. Home Config (~/.codeconcat_config.json)
    3. Project Config (./.codeconcat_config.json)

    Returns:
        Dict[str, Any]: The final consolidated configuration dictionary.
    """
    config = DEFAULT_CONFIG.copy()
    home_loaded = False
    project_loaded = False

    home_config = load_config_file(HOME_CONFIG_PATH)
    if home_config:
        config = merge_configs(config, home_config)
        logger.info(f"Loaded configuration from {HOME_CONFIG_PATH}")
        home_loaded = True

    project_config = load_config_file(PROJECT_CONFIG_PATH)
    if project_config:
        config = merge_configs(config, project_config)
        logger.info(f"Loaded configuration from {PROJECT_CONFIG_PATH} (overrides home config)")
        project_loaded = True

    # Create default home config only if neither home nor project config existed
    if not home_loaded and not project_loaded:
        create_default_config_if_needed(HOME_CONFIG_PATH)

    return config


def create_default_config_if_needed(path: Path) -> None:
    """
    Creates a default config file at the specified path if it doesn't exist.

    This ensures the user has a starting point for customization.

    Args:
        path (Path): Path where the default config should be created.
    """
    global _default_config_created
    # Check existence again, as another process might have created it
    if not path.exists() and not _default_config_created:
        try:
            # Ensure parent directory exists (for home dir, usually does)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info(f"Created default configuration file with extensive excludes at: {path}")
            _default_config_created = True  # Mark as created for this run
        except OSError as e:
            logger.warning(f"Could not create default config file at {path}. Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating default config at {path}: {e}")
