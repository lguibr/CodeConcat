# -*- coding: utf-8 -*-
# File: codeconcat/file_utils.py
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
# (Keep your existing LANGUAGE_EXTENSIONS list here)
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


# Need to re-add the load_gitignore_patterns function definition
def load_gitignore_patterns(start_path: Path) -> Optional[pathspec.PathSpec]:
    """Loads .gitignore patterns starting from a path and walking upwards."""
    patterns = []
    current_path = start_path.resolve()

    while True:
        gitignore_file = current_path / ".gitignore"
        if gitignore_file.is_file():
            try:
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
                    # Filter out empty lines and comments
                    valid_patterns = [
                        line for line in lines if line.strip() and not line.strip().startswith("#")
                    ]
                    if valid_patterns:
                        patterns.extend(valid_patterns)
                        logger.debug(
                            f"Loaded {len(valid_patterns)} patterns from {gitignore_file}"
                        )  # Use debug
            except OSError as e:
                logger.warning(f"Could not read {gitignore_file}. Error: {e}")

        parent = current_path.parent
        if parent == current_path:  # Reached root
            break
        current_path = parent

    if patterns:
        try:
            # Create a single PathSpec from all collected patterns
            spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)
            logger.debug(f"Compiled PathSpec from {len(patterns)} total gitignore patterns.")
            return spec
        except Exception as e:
            logger.error(f"Failed to compile gitignore patterns: {e}")
            return None
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
    1. Check explicit exclude patterns (using relative paths).
    2. Check .gitignore patterns (if enabled, using relative paths).
    3. Check whitelist patterns (if provided, using relative paths).
    4. Check default MIME type / extension (if no whitelist).
    """
    tree: List[str] = []
    src_path = Path(src_path_str).resolve()
    gitignore_spec = load_gitignore_patterns(src_path) if use_gitignore else None

    # Compile regex patterns, skip empty strings
    compiled_exclude = [re.compile(p) for p in exclude_patterns if p]
    compiled_whitelist = [re.compile(p) for p in whitelist_patterns if p]

    logger.debug(f"Source Path Resolved: {src_path}")
    logger.debug(f"Compiled Excludes: {[p.pattern for p in compiled_exclude]}")
    logger.debug(f"Compiled Whitelists: {[p.pattern for p in compiled_whitelist]}")
    logger.debug(f"Gitignore Spec Loaded: {gitignore_spec is not None}")

    for root, dirs, files in os.walk(str(src_path), topdown=True):  # Ensure os.walk gets a string
        current_path = Path(root).resolve()

        # --- Filter Directories ---
        original_dirs = list(dirs)
        dirs[:] = []  # Modify dirs in place
        for d in original_dirs:
            dir_path_obj = current_path / d
            try:
                # Use relative path for pattern matching and gitignore
                dir_path_rel = dir_path_obj.relative_to(src_path)
                dir_path_rel_str = str(dir_path_rel)
            except ValueError:
                logger.warning(f"Could not get relative path for dir {dir_path_obj}, skipping checks.")
                dirs.append(d)  # Keep dir if relative path fails? Or skip? Skipping is safer.
                continue

            # Check compiled exclude patterns against RELATIVE path string
            if compiled_exclude and any(p.search(dir_path_rel_str) for p in compiled_exclude):
                logger.debug(f"Excluding dir by exclude pattern: {dir_path_rel_str}")
                continue

            # Check gitignore patterns (needs trailing slash for directories)
            if (
                use_gitignore
                and gitignore_spec
                and gitignore_spec.match_file(dir_path_rel_str + "/")  # Add trailing slash for dir match
            ):
                logger.debug(f"Excluding dir by gitignore: {dir_path_rel_str}")
                continue

            dirs.append(d)  # Keep the directory if not excluded

        # --- Filter Files ---
        for file in files:
            file_path_obj = current_path / file
            try:
                # Use relative path for pattern matching and gitignore
                relative_file_path = file_path_obj.relative_to(src_path)
                relative_file_path_str = str(relative_file_path)
                # Keep absolute path only needed for magic
                file_path_abs_str = str(file_path_obj.resolve())
            except ValueError:
                logger.warning(f"Could not get relative path for file {file_path_obj}, skipping checks.")
                continue

            # 1. Check explicit exclude patterns against RELATIVE path string
            if compiled_exclude and any(p.search(relative_file_path_str) for p in compiled_exclude):
                logger.debug(f"Excluding file by exclude pattern: {relative_file_path_str}")
                continue

            # 2. Check .gitignore patterns
            if use_gitignore and gitignore_spec and gitignore_spec.match_file(relative_file_path_str):
                logger.debug(f"Excluding file by gitignore: {relative_file_path_str}")
                continue

            # 3. Check whitelist patterns against RELATIVE path string
            is_whitelisted = False
            if compiled_whitelist:
                if any(p.search(relative_file_path_str) for p in compiled_whitelist):
                    is_whitelisted = True
                else:
                    logger.debug(f"Skipping file not in whitelist: {relative_file_path_str}")
                    continue

            # If whitelisted, add and continue (don't check default rules)
            if is_whitelisted:
                tree.append(file_path_abs_str)  # Store absolute path for reading later
                logger.debug(f"Including whitelisted file: {relative_file_path_str}")
                continue

            # 4. Default Inclusion (Only if NO whitelist was provided)
            if not compiled_whitelist:
                try:
                    # Magic needs the absolute path
                    mime_type = magic.from_file(file_path_abs_str, mime=True)
                    is_excluded_mime = any(excluded in mime_type for excluded in EXCLUDED_MIME_TYPES)
                    # Check extension on the filename itself
                    file_name = file_path_obj.name
                    is_language_file = (
                        file_name.lower().endswith(LANGUAGE_EXTENSIONS) or file_name == "LICENSE"
                    )

                    if not is_excluded_mime or is_language_file:
                        tree.append(file_path_abs_str)  # Store absolute path for reading later
                        logger.debug(f"Including file by default rules: {relative_file_path_str}")

                except magic.MagicException as e:
                    # Check if libmagic is missing
                    if "failed to find magic" in str(e).lower():
                        logger.warning(f"libmagic not found. Relying on file extensions only. Error: {e}")
                        # Fallback to extension check if magic fails critically
                        file_name = file_path_obj.name
                        is_language_file = (
                            file_name.lower().endswith(LANGUAGE_EXTENSIONS) or file_name == "LICENSE"
                        )
                        if is_language_file:
                            tree.append(file_path_abs_str)
                            logger.debug(f"Including file by extension fallback: {relative_file_path_str}")
                        else:
                            logger.debug(f"Skipping file by extension fallback: {relative_file_path_str}")

                    else:
                        logger.warning(f"Skipping file {relative_file_path_str} - magic error: {e}")
                except FileNotFoundError:
                    # This might happen in race conditions, log and continue
                    logger.warning(f"Skipping file {relative_file_path_str} - Not found during processing.")
                except Exception as e:
                    # Catch other potential errors during file processing
                    logger.warning(f"Skipping file {relative_file_path_str} - Unexpected error: {e}")

    logger.info(f"Found {len(tree)} files matching criteria.")
    if not tree:
        logger.warning("No files found matching the criteria. No output generated.")

    # Sort the tree for consistent output order (optional, but nice)
    tree.sort()
    return tree
