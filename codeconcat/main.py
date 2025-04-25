# -*- coding: utf-8 -*-
# File: codeconcat/main.py
import argparse
import logging
import re
import sys
from pathlib import Path

# Import from local modules
from .config import DEFAULT_CONFIG, get_config
from .file_utils import generate_directory_tree
from .output import create_output

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Concatenate files from a directory into a single output, respecting .gitignore and config files."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # Show defaults
    )
    parser.add_argument("source_path", help="Path to the source directory to process.")
    parser.add_argument(
        "destination_file",
        nargs="?",  # Optional if --stdout is used
        default=None,
        help="Path to the output file. Required if --stdout is not used.",
    )
    parser.add_argument(
        "--exclude",
        action="append",  # Allow multiple --exclude flags
        default=None,  # Use None to differentiate from empty list explicitly passed
        help="Regex pattern to exclude files/directories. Overrides config excludes.",
    )
    parser.add_argument(
        "--whitelist",
        action="append",  # Allow multiple --whitelist flags
        default=None,  # Use None to differentiate from empty list explicitly passed
        help=(
            "Regex pattern to *only* include files/directories. "
            "Overrides default MIME/extension checks and config whitelists. Can be used multiple times."
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output the concatenated content to stdout instead of a file.",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not use .gitignore files for exclusion patterns.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging.")

    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    # --- Configuration Loading and Merging ---
    config = get_config()  # Loads default, home, project configs

    # Determine final settings, command-line args override config file AND defaults
    # Handle boolean flags directly
    use_gitignore = (
        not args.no_gitignore
        if args.no_gitignore is True
        else config.get("use_gitignore", DEFAULT_CONFIG["use_gitignore"])
    )

    # Handle pattern lists: CLI args override config, which overrides defaults
    # If args.exclude/whitelist is not None (meaning the flag was used, even if empty like --exclude '')
    # then use args. Otherwise, use config, falling back to default.
    final_exclude_patterns = (
        args.exclude
        if args.exclude is not None
        else config.get("exclude_patterns", DEFAULT_CONFIG["exclude_patterns"])
    )
    final_whitelist_patterns = (
        args.whitelist
        if args.whitelist is not None
        else config.get("whitelist_patterns", DEFAULT_CONFIG["whitelist_patterns"])
    )

    # Ensure output target is valid
    if not args.destination_file and not args.stdout:
        logger.error("Error: Either destination_file or --stdout must be specified.")
        sys.exit(1)
    if args.destination_file and args.stdout:
        logger.error("Error: Cannot specify both destination_file and --stdout.")
        sys.exit(1)

    # Add destination file to exclude patterns if it's specified AND inside source_path
    if args.destination_file:
        try:
            src_path_abs = Path(args.source_path).resolve()
            dest_path_abs = Path(args.destination_file).resolve()

            # Check if destination is within source directory using is_relative_to
            if dest_path_abs.is_relative_to(src_path_abs):
                # Calculate relative path from source dir
                dest_path_rel = dest_path_abs.relative_to(src_path_abs)
                # Create pattern matching the RELATIVE path, anchored and escaped
                # Use forward slashes for cross-platform regex compatibility
                exclude_pattern = f"^{re.escape(dest_path_rel.as_posix())}$"
                if exclude_pattern not in final_exclude_patterns:
                    # Make sure final_exclude_patterns is a list before appending
                    if not isinstance(final_exclude_patterns, list):
                        final_exclude_patterns = list(
                            final_exclude_patterns
                        )  # Convert if needed (e.g., from tuple)
                    final_exclude_patterns.append(exclude_pattern)
                    logger.debug(f"Auto-excluding destination file pattern (relative): {exclude_pattern}")
            else:
                logger.debug(
                    "Destination file is outside the source directory, no implicit exclusion needed."
                )

        except ValueError:
            logger.debug("Destination file is not within the source directory, no implicit exclusion needed.")
        except OSError as e:  # Catch potential path resolution errors
            logger.warning(
                f"Could not reliably check if destination '{args.destination_file}'",
                f"is within source '{args.source_path}'. "
                f"Manual exclusion might be needed if it is. Error: {e}",
            )
        except Exception as e:  # Catch unexpected errors
            logger.warning(f"Unexpected error while checking destination path relation: {e}")

    # Ensure patterns are lists for generate_directory_tree
    if not isinstance(final_exclude_patterns, list):
        final_exclude_patterns = []
    if not isinstance(final_whitelist_patterns, list):
        final_whitelist_patterns = []

    logger.info(f"Source Path: {Path(args.source_path).resolve()}")  # Log resolved path
    output_target = (
        "stdout" if args.stdout else Path(args.destination_file).resolve() if args.destination_file else "N/A"
    )
    logger.info(f"Output Target: {output_target}")  # Log resolved path
    logger.info(f"Using .gitignore: {use_gitignore}")
    # Use pprint or similar if lists get too long? For now, just log.
    logger.info(f"Final Exclude Patterns: {final_exclude_patterns}")
    logger.info(f"Final Whitelist Patterns: {final_whitelist_patterns}")

    # --- Generate File List ---
    try:
        # Pass resolved source path string
        tree = generate_directory_tree(
            str(Path(args.source_path).resolve()),
            final_exclude_patterns,
            final_whitelist_patterns,
            use_gitignore,
        )
    except Exception as e:
        logger.error(f"An error occurred during file collection: {e}", exc_info=args.verbose)
        sys.exit(1)

    # --- Create Output ---
    if tree:  # Only proceed if files were found
        try:
            # Pass resolved source path string for relative path calculation in output
            create_output(
                args.destination_file,
                str(Path(args.source_path).resolve()),
                tree,
                args.stdout,
            )
        except Exception as e:
            logger.error(f"An error occurred during output creation: {e}", exc_info=args.verbose)
            sys.exit(1)
    # If no tree, generate_directory_tree already logged a warning


if __name__ == "__main__":
    main()
