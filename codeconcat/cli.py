# -*- coding: utf-8 -*-
# codeconcat/cli.py
import argparse
from typing import List, Optional

# Define parser at module level
parser = argparse.ArgumentParser(
    description=(
        "Concatenate text files from a source directory into a single output, "
        "respecting .gitignore, exclusion, and inclusion patterns."
    ),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "source_path",
    type=str,
    help="Path to the source directory to process.",
)
parser.add_argument(
    "output_path",
    type=str,
    nargs="?",
    default=None,
    help="Path to the output file. If omitted, output goes to standard output.",
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
        "Glob pattern to *only* include matching files/directories "
        "(e.g., '*.py', 'src/*'). If provided, only matching files are considered "
        "(after excludes). Overrides config file whitelist. Can be used multiple times."
    ),
)
parser.add_argument(
    "--no-gitignore",
    action="store_true",
    default=False,
    help="Disable processing of .gitignore files.",
)
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level).")


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses command-line arguments using the pre-defined parser.

    Args:
        args: Optional list of strings to parse. Defaults to sys.argv[1:].
    """
    return parser.parse_args(args)
