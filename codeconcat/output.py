# -*- coding: utf-8 -*-
# codeconcat/output.py
"""
Output Generation Module.

This module is responsible for formatting and writing the final concatenated output.
It includes features for:
1.  **ASCII File Tree**: Generating a visual directory structure at the top of the file.
2.  **Safe Markdown Fencing**: Wrapping code blocks in enough backticks to prevent breakage
    when the code itself contains backticks (e.g., Markdown files, SQL with templates).
3.  **Language Detection**: Mapping file extensions to Markdown language tags.
4.  **Stream Handling**: Writing to either a file or stdout seamlessly.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

logger = logging.getLogger(__name__)


def generate_ascii_tree(file_list: List[str], root_path: Path) -> str:
    """
    Generates a hierarchical ASCII tree representation of the provided file list.

    This visual aid helps LLMs (and humans) understand the project structure immediately.

    Args:
        file_list (List[str]): List of absolute file paths included in the output.
        root_path (Path): The root directory against which relative paths are calculated.

    Returns:
        str: A multi-line string containing the ASCII tree.
    """
    # Build a nested dictionary structure
    tree_structure: Dict[str, Any] = {}
    for file_path_str in file_list:
        path = Path(file_path_str)
        try:
            rel_path = path.relative_to(root_path)
            parts = rel_path.parts
            current_level = tree_structure
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        except ValueError:
            continue  # Should not happen if paths are correct

    lines = []

    def _recurse(structure, prefix=""):
        # Sort items: directories first? or just alphabetical
        # Alphabetical is standard and predictable
        items = sorted(structure.keys())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{item}")

            # Prepare prefix for children
            extension = "    " if is_last else "│   "
            _recurse(structure[item], prefix + extension)

    lines.append(root_path.name + "/")
    _recurse(tree_structure)
    return "\n".join(lines)


def get_safe_fence(content: str) -> str:
    """
    Determines the safe code block fence to use.

    It scans the content for the longest sequence of backticks and returns a fence
    that is one backtick longer. This ensures that a file containing "```" is wrapped
    in "````", preventing the Markdown parser from closing the block prematurely.

    Args:
        content (str): The code content to be wrapped.

    Returns:
        str: A string of backticks (e.g. "```", "````") suitable for fencing.
    """
    import re

    # Find all sequences of backticks
    matches = re.findall(r"`+", content)
    if not matches:
        return "```"

    max_ticks = max(len(m) for m in matches)
    return "`" * (max_ticks + 1)


def create_output(
    output_path_str: Optional[str],
    src_path_str: str,
    tree: List[str],
    to_stdout: bool = False,
) -> None:
    """
    Orchestrates the creation of the final output.

    It writes the header, the ASCII tree, and then iterates through all files,
    reading their content and writing them with safe fencing and relative path headers.

    Args:
        output_path_str (Optional[str]): Path to the output file.
        src_path_str (str): Path to the source directory.
        tree (List[str]): List of files to process.
        to_stdout (bool): If True, writes to sys.stdout instead of a file.
    """
    output_stream: Optional[TextIO] = None
    src_path = Path(src_path_str).resolve()

    try:
        if to_stdout:
            output_stream = sys.stdout
        elif output_path_str:
            output_path = Path(output_path_str)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_stream = open(output_path, "w", encoding="utf-8")
        else:
            logger.error("Output target not specified (file path or --stdout).")
            return

        if not tree:
            return

        # --- Write Header and Tree ---
        output_stream.write(f"# Project Codebase: {src_path.name}\n\n")

        output_stream.write("## File Tree\n\n")
        output_stream.write("```text\n")
        output_stream.write(generate_ascii_tree(tree, src_path))
        output_stream.write("\n```\n\n")

        output_stream.write("## File Contents\n\n")

        for file_path_str in tree:
            file_path = Path(file_path_str)
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    content = file.read()
            except UnicodeDecodeError:
                logger.warning(f"Skipping file {file_path_str} due to unhandled encoding issue.")
                continue
            except OSError as e:
                logger.warning(f"Skipping file {file_path_str} due to read error: {e}")
                continue
            except Exception as e:
                logger.warning(f"Skipping file {file_path_str} due to unexpected error: {e}")
                continue

            try:
                relative_path = file_path.relative_to(src_path)
            except ValueError:
                relative_path = file_path

            # Determine language for highlighting
            ext = relative_path.suffix.lstrip(".").lower()
            if not ext:
                ext = "text"  # Default

            # Specific mappings if needed
            if ext in ["js", "jsx"]:
                ext = "javascript"
            if ext in ["ts", "tsx"]:
                ext = "typescript"

            fence = get_safe_fence(content)

            output_stream.write(f"### File: `{relative_path.as_posix()}`\n\n")
            output_stream.write(f"{fence}{ext}\n")
            output_stream.write(content)
            # Ensure newline before closing fence
            if not content.endswith("\n"):
                output_stream.write("\n")
            output_stream.write(f"{fence}\n\n")

        # Only log success message if NOT writing to stdout (to avoid polluting pipe)
        if not to_stdout and output_stream != sys.stdout:
            # Just defensive check
            logger.info(f"Successfully wrote {len(tree)} files to {output_path_str}")

    except OSError as e:
        target = "stdout" if to_stdout else output_path_str
        logger.error(f"Error writing to output {target}. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during output generation: {e}")
    finally:
        # Close file stream, but NEVER close stdout
        if not to_stdout and output_stream and output_stream != sys.stdout and not output_stream.closed:
            output_stream.close()
