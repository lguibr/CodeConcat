# -*- coding: utf-8 -*-
# codeconcat/cli.py
"""
Command-Line Interface Module.

This module defines the argument parser for CodeConcat. It handles:
- Positional arguments (Source Path, Output Path)
- Optional flags (Verbose, Interactive)
- Pattern lists (Exclude, Whitelist, Force Include)

It is designed to be easily extensible and provides clear help messages.
"""

import argparse
from typing import List, Optional

# Define parser at module level so it can be picked up by documentation tools
parser = argparse.ArgumentParser(
    description=(
        "Concatenate text files from a source directory into a single output, "
        "respecting .gitignore, exclusion, and inclusion patterns."
    ),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    epilog="For more help, see the README or visit the GitHub repository.",
)

parser.add_argument(
    "source_path",
    type=str,
    nargs="?",  # Make optional to trigger wizard if missing
    help="Path to the source directory to process. If omitted, interactive wizard starts.",
)

parser.add_argument(
    "output_path",
    type=str,
    nargs="?",
    default=None,
    help=(
        "Path to the output file. If omitted:"
        "\n  1. If running interactively (TTY), defaults to '{DirectoryName}.md'."
        "\n  2. If piped, defaults to stdout."
    ),
)

parser.add_argument(
    "-e",
    "--exclude",
    action="append",
    default=[],
    metavar="PATTERN",
    help=(
        "Glob pattern for files/directories to exclude (e.g., '*.log', 'dist/'). "
        "Applied after .gitignore. Can be used multiple times. "
        "Overrides config file excludes."
    ),
)

parser.add_argument(
    "-w",
    "--whitelist",
    action="append",
    default=[],
    metavar="PATTERN",
    help=(
        "EXCLUSIVE: Glob pattern to *only* include matching files. "
        "If provided, standard file detection is disabled and ONLY matching files "
        "(that are not excluded) are processed. "
        "Example: -w '*.py' -w 'src/*'"
    ),
)

parser.add_argument(
    "--force-include",
    action="append",
    default=[],
    metavar="PATTERN",
    help=(
        "ADDITIVE: Glob pattern to force include files even if they are in .gitignore. "
        "Includes these files ON TOP of standard files. "
        "Example: --force-include '.env' to grab environment files."
    ),
)

parser.add_argument(
    "--no-gitignore",
    action="store_true",
    default=False,
    help="Disable processing of .gitignore files (treat all files as visible).",
)

parser.add_argument(
    "-i",
    "--interactive",
    action="store_true",
    help="Force launch of the interactive configuration wizard.",
)

parser.add_argument(
    "--stdout",
    action="store_true",
    help="Force output to standard output (stdout), even if running in a terminal.",
)

parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level) for troubleshooting."
)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses command-line arguments using the pre-defined parser.

    Args:
        args (Optional[List[str]]): List of arguments to parse.
                                    Defaults to sys.argv[1:] if None.

    Returns:
        argparse.Namespace: Namespace object containing parsed arguments.
    """
    return parser.parse_args(args)
