# -*- coding: utf-8 -*-
# codeconcat/file_utils.py
import fnmatch
import logging
from pathlib import Path
from typing import List, Set

# Import constants from config module
from .config import (
    DEFAULT_EXCLUDE_PATTERNS,
    DEFAULT_WHITELIST_EXTENSIONS,
    EXCLUDED_MIME_PREFIXES,
    GITIGNORE_FILE_NAME,
)

# Try importing magic, handle potential ImportError
try:
    import magic
except ImportError:
    magic = None  # type: ignore[assignment]
    # Note: The warning message is printed in main.py upon import attempt there

logger = logging.getLogger(__name__)


def read_gitignore_patterns(gitignore_path: Path) -> List[str]:
    """Reads patterns from a single .gitignore file."""
    patterns = []
    if gitignore_path.is_file():
        try:
            with gitignore_path.open("r", encoding="utf-8") as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith("#"):
                        patterns.append(stripped_line.rstrip("/"))
        except Exception as e:
            logger.warning(f"Could not read {gitignore_path}: {e}")
    return patterns


def collect_all_gitignore_patterns(src_path: Path) -> List[str]:
    """Finds all .gitignore files and collects their patterns."""
    all_patterns: Set[str] = set()
    root_gitignore = src_path / GITIGNORE_FILE_NAME
    if root_gitignore.is_file():
        logger.debug(f"Reading patterns from {root_gitignore}")
        all_patterns.update(read_gitignore_patterns(root_gitignore))

    for gitignore_file in src_path.rglob(f"**/{GITIGNORE_FILE_NAME}"):
        if gitignore_file != root_gitignore:
            logger.debug(f"Reading patterns from {gitignore_file}")
            all_patterns.update(read_gitignore_patterns(gitignore_file))

    all_patterns.add(".git")
    logger.info(f"Collected {len(all_patterns)} unique patterns from .gitignore files.")
    return list(all_patterns)


def is_match(relative_path: Path, patterns: List[str]) -> bool:
    """
    Checks if the relative path object matches any of the fnmatch patterns.
    """
    path_str = relative_path.as_posix()

    for pattern in patterns:
        if fnmatch.fnmatch(path_str, pattern):
            return True
        if fnmatch.fnmatch(relative_path.name, pattern):
            return True
        pattern_for_dir = pattern.strip("/")
        if pattern_for_dir in relative_path.parts:
            try:
                match_index = relative_path.parts.index(pattern_for_dir)
                if match_index < len(relative_path.parts) - 1:
                    return True
            except ValueError:
                pass
        if "*" in pattern and fnmatch.fnmatch(path_str, pattern):
            return True
    return False


def is_likely_text_file(file_path: Path) -> bool:
    """
    Determines if a file is likely text-based using extensions and MIME types.
    """
    if file_path.suffix.lower() in DEFAULT_WHITELIST_EXTENSIONS:
        return True

    if magic:  # Check if magic object is available (import succeeded)
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type:
                if mime_type.startswith("text/") or mime_type in (
                    "application/json",
                    "application/xml",
                    "application/yaml",
                    "application/javascript",
                ):
                    return True
                if any(
                    mime_type.startswith(prefix) for prefix in EXCLUDED_MIME_PREFIXES
                ):
                    logger.debug(
                        f"Excluding {file_path} based on MIME type: {mime_type}"
                    )
                    return False
        except magic.MagicException as e:
            logger.warning(f"MIME check failed for {file_path}: {e}")
        except FileNotFoundError:
            logger.warning(f"File not found during MIME check: {file_path}")
            return False

    logger.debug(
        f"Excluding {file_path} (unknown extension and inconclusive/no MIME type)."
    )
    return False


def collect_files(
    src_path: Path,
    cli_exclude: List[str],
    cli_whitelist: List[str],
    config_exclude: List[str],
    config_whitelist: List[str],
    gitignore_patterns: List[str],
) -> List[Path]:
    """
    Walks the directory and collects files based on combined filter rules.
    """
    collected: List[Path] = []

    exclude_patterns = set(DEFAULT_EXCLUDE_PATTERNS)
    exclude_patterns.update(config_exclude)
    exclude_patterns.update(cli_exclude)
    exclude_patterns.update(gitignore_patterns)
    final_exclude_list = list(exclude_patterns)
    logger.debug(f"Final combined exclude patterns: {final_exclude_list}")

    active_whitelist = cli_whitelist if cli_whitelist else config_whitelist
    has_active_whitelist = bool(active_whitelist)
    logger.debug(f"Active whitelist patterns: {active_whitelist}")
    logger.debug(f"Has active whitelist: {has_active_whitelist}")

    for item in src_path.rglob("*"):
        try:
            if not item.exists():
                continue

            relative_path = item.relative_to(src_path)

            # 1. Check combined excludes FIRST
            if is_match(relative_path, final_exclude_list):
                logger.debug(
                    f"Excluding '{relative_path.as_posix()}' due to "
                    f"combined exclude pattern."
                )
                continue

            # Only consider files past this point
            if not item.is_file():
                continue

            # 2. Check active whitelist (if one exists)
            passes_whitelist = True
            if has_active_whitelist:
                passes_whitelist = is_match(relative_path, active_whitelist)
                if not passes_whitelist:
                    logger.debug(
                        f"Skipping '{relative_path.as_posix()}' (not in active "
                        f"whitelist)."
                    )
                    continue

            # 3. Check if likely text file (only if passes other checks)
            if not is_likely_text_file(item):
                continue

            # --- If all checks passed, collect the file ---
            logger.debug(f"Including '{relative_path.as_posix()}'")
            collected.append(item)

        except Exception as e:
            logger.warning(f"Error processing path {item}: {e}")

    collected.sort()
    return collected
