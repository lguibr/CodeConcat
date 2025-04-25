# -*- coding: utf-8 -*-
# codeconcat/file_utils.py
import logging
import os
import re
from pathlib import Path
from typing import List, Optional

import magic
import pathspec  # For .gitignore parsing

logger = logging.getLogger(__name__)

# Keep these constants or move them to config if they should be configurable
EXCLUDED_MIME_TYPES = ("application", "image", "audio", "video")
# This list becomes less important if whitelist is used effectively, but good fallback
LANGUAGE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".go",
    ".rs",
    ".kt",
    ".scala",
    ".pl",
    ".pm",
    ".sh",
    ".bat",
    ".cmd",
    ".ps1",
    ".vim",
    ".el",
    ".lisp",
    ".clj",
    ".hs",
    ".ml",
    ".fs",
    ".fsx",
    ".lua",
    ".r",
    ".m",
    ".sql",
    ".html",
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
    ".md",
    ".txt",
    ".log",
    ".csv",
    ".tsv",
    ".rst",
    ".tex",
    ".bib",
    ".org",
    ".nfo",
    ".asc",
    ".asciidoc",
    ".adoc",
    ".feature",
    ".gitignore",
    "LICENSE",
    # Add other common text/code file extensions
)


def load_gitignore_patterns(start_path: Path) -> Optional[pathspec.PathSpec]:
    """Loads .gitignore patterns starting from a path and walking upwards."""
    patterns = []
    current_path = start_path.resolve()

    while True:
        gitignore_file = current_path / ".gitignore"
        if gitignore_file.is_file():
            try:
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    # We need patterns relative to the root where os.walk starts.
                    # pathspec works best with paths relative to .gitignore location.
                    # This requires careful handling during the walk.
                    # For simplicity here, let's collect raw lines first.
                    f.seek(0)  # Reset file pointer
                    patterns.extend(f.read().splitlines())
                logger.info(f"Loaded patterns from {gitignore_file}")
            except OSError as e:
                logger.warning(f"Could not read {gitignore_file}. Error: {e}")

        parent = current_path.parent
        if parent == current_path:  # Reached root
            break
        current_path = parent

    if patterns:
        # Create a single PathSpec from all collected patterns
        # Note: This simple combination might not perfectly replicate
        # git's precedence rules, but it's a good approximation.
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)
    return None


def generate_directory_tree(
    src_path_str: str,
    exclude_patterns: List[str],
    whitelist_patterns: List[str],
    use_gitignore: bool,
) -> List[str]:
    """
    Generates a list of file paths to include, applying filters.
    Order of operations:
    1. Check explicit exclude patterns.
    2. Check .gitignore patterns (if enabled).
    3. Check whitelist patterns (if provided).
    4. Check default MIME type / extension (if no whitelist).
    """
    tree: List[str] = []
    src_path = Path(src_path_str).resolve()
    gitignore_spec = load_gitignore_patterns(src_path) if use_gitignore else None

    # Compile regex patterns once
    compiled_exclude = [re.compile(p) for p in exclude_patterns]
    compiled_whitelist = [re.compile(p) for p in whitelist_patterns]

    for root, dirs, files in os.walk(src_path_str, topdown=True):
        current_path = Path(root).resolve()

        # --- Filter Directories ---
        original_dirs = list(dirs)
        dirs[:] = []
        for d in original_dirs:
            dir_path_obj = current_path / d
            dir_path_rel = dir_path_obj.relative_to(src_path)
            dir_path_str = str(dir_path_obj)

            if any(p.search(dir_path_str) for p in compiled_exclude):
                # logger.debug(f"Excluding dir by exclude: {dir_path_rel}")
                continue

            # Add trailing slash for dirs when checking gitignore
            if use_gitignore and gitignore_spec and gitignore_spec.match_file(str(dir_path_rel) + "/"):
                # logger.debug(f"Excluding dir by gitignore: {dir_path_rel}")
                continue

            dirs.append(d)

        # --- Filter Files ---
        for file in files:
            file_path_obj = current_path / file
            file_path_str = str(file_path_obj)
            relative_file_path = file_path_obj.relative_to(src_path)

            # 1. Check explicit exclude patterns
            if any(p.search(file_path_str) for p in compiled_exclude):
                # logger.debug(f"Excluding file by exclude: {relative_file_path}")
                continue

            # 2. Check .gitignore patterns (if enabled)
            if use_gitignore and gitignore_spec and gitignore_spec.match_file(str(relative_file_path)):
                # logger.debug(f"Excluding file by gitignore: {relative_file_path}")
                continue

            # 3. Check whitelist patterns (if provided)
            is_whitelisted = False
            if compiled_whitelist:
                if any(p.search(file_path_str) for p in compiled_whitelist):
                    is_whitelisted = True
                else:
                    # logger.debug(f"Skipping file not in whitelist: {relative_file_path}") # Shortened
                    continue
            if is_whitelisted:
                tree.append(file_path_str)
                # logger.debug(f"Including whitelisted file: {relative_file_path}")
                continue

            # 4. Default Inclusion (No whitelist provided, rely on MIME/Extension)
            if not compiled_whitelist:
                try:
                    mime_type = magic.from_file(file_path_str, mime=True)
                    is_excluded_mime = any(excluded in mime_type for excluded in EXCLUDED_MIME_TYPES)
                    is_language_file = file.lower().endswith(LANGUAGE_EXTENSIONS) or file == "LICENSE"

                    if not is_excluded_mime or is_language_file:
                        tree.append(file_path_str)
                        # logger.debug(f"Including file by default: {relative_file_path}") # Shortened
                    # else:
                    # logger.debug(f"Skipping file by default (MIME): {relative_file_path}") # Shortened

                except magic.MagicException as e:
                    logger.warning(f"Skipping file {file_path_str} - magic error: {e}")
                except FileNotFoundError:
                    logger.warning(f"Skipping file {file_path_str} - Not found during processing.")
                except Exception as e:
                    logger.warning(f"Skipping file {file_path_str} - Unexpected error: {e}")

    logger.info(f"Found {len(tree)} files matching criteria.")
    if not tree:
        logger.warning("No files found matching the criteria. No output generated.")

    return tree
