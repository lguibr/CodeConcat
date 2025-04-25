# -*- coding: utf-8 -*-
# codeconcat/config.py
import json
import logging
from pathlib import Path

# Use typing.Tuple for broader compatibility if MyPy struggles with tuple[]
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

# --- Constants ---

CONFIG_FILE_NAME = ".codeconcat_config.json"
GITIGNORE_FILE_NAME = ".gitignore"

# Heuristic: MIME types that are likely binary or not useful text content
# Use typing.Tuple explicitly
EXCLUDED_MIME_PREFIXES: Tuple[str, ...] = ("application/", "image/", "audio/", "video/")

# Common text/code file extensions (Set for faster lookups)
DEFAULT_WHITELIST_EXTENSIONS: Set[str] = {
    # Code
    ".py",
    ".pyw",
    ".pyi",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".go",
    ".rs",
    ".kt",
    ".kts",
    ".scala",
    ".pl",
    ".pm",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".lua",
    ".sql",
    ".r",
    ".dart",
    ".groovy",
    ".hs",
    ".lhs",
    ".ml",
    ".mli",
    ".fs",
    ".fsx",
    ".fsi",
    ".elm",
    ".clj",
    ".cljs",
    ".edn",
    ".ex",
    ".exs",
    ".erl",
    ".hrl",
    ".vim",
    ".el",
    # Markup & Config
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".properties",
    ".md",
    ".markdown",
    ".rst",
    ".adoc",
    ".asciidoc",
    ".tex",
    ".bib",
    ".csv",
    ".tsv",
    ".log",
    ".txt",
    ".env",
    ".dockerfile",
    "dockerfile",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    # Other potentially useful text
    ".nfo",
    ".readme",
    ".inf",
    ".url",
}

# Default patterns to exclude (common build artifacts, caches, envs, etc.)
DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    ".*",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.o",
    "*.a",
    "*.dll",
    "*.exe",
    "node_modules",
    "vendor",
    "build",
    "dist",
    "target",
    "*.egg-info",
    ".venv",
    "venv",
    "env",
    ".env",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "*.swp",
    "*.swo",
]

# --- Functions ---


def load_config(config_path: Path) -> Dict[str, List[str]]:
    """Loads configuration from a JSON file."""
    config: Dict[str, List[str]] = {"exclude": [], "whitelist": []}
    if config_path.is_file():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                loaded_exclude = data.get("exclude")
                loaded_whitelist = data.get("whitelist")
                if isinstance(loaded_exclude, list):
                    config["exclude"] = [
                        str(p) for p in loaded_exclude if isinstance(p, str)
                    ]
                if isinstance(loaded_whitelist, list):
                    config["whitelist"] = [
                        str(p) for p in loaded_whitelist if isinstance(p, str)
                    ]
                logger.info(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError:
            logger.warning(
                f"Could not decode JSON from {config_path}. Using defaults/CLI args."
            )
        except Exception as e:
            logger.warning(
                f"Error reading config file {config_path}: {e}. "
                "Using defaults/CLI args."
            )
    else:
        logger.debug(f"No config file found at {config_path}.")
    return config
