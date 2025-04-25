# -*- coding: utf-8 -*-
# codeconcat/main.py
import argparse
import logging
import re
import sys
from pathlib import Path  # <<< Added missing import

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
        default=[],  # Default handled by config merge later
        help="Regex pattern to exclude files/directories. Can be used multiple times.",
    )
    parser.add_argument(
        "--whitelist",
        action="append",  # Allow multiple --whitelist flags
        default=[],  # Default handled by config merge later
        help=(
            "Regex pattern to *only* include files/directories. "
            "Overrides default MIME/extension checks. Can be used multiple times."
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
    config = get_config()

    # Determine final settings, command-line args override config file
    use_gitignore = (
        not args.no_gitignore
        if args.no_gitignore
        else config.get("use_gitignore", DEFAULT_CONFIG["use_gitignore"])
    )
    # Combine patterns from config and args, ensuring args take precedence if provided
    config_exclude = config.get("exclude_patterns", DEFAULT_CONFIG["exclude_patterns"])
    config_whitelist = config.get("whitelist_patterns", DEFAULT_CONFIG["whitelist_patterns"])

    final_exclude_patterns = args.exclude if args.exclude else config_exclude
    final_whitelist_patterns = args.whitelist if args.whitelist else config_whitelist

    # Ensure output target is valid
    if not args.destination_file and not args.stdout:
        # Shortened line below
        logger.error("Error: Either destination_file or --stdout must be specified.")
        sys.exit(1)
    if args.destination_file and args.stdout:
        logger.error("Error: Cannot specify both destination_file and --stdout.")
        sys.exit(1)

    # Add destination file to exclude patterns if it's specified
    if args.destination_file:
        # Resolve paths to handle relative/absolute cases better
        try:
            src_path_abs = Path(args.source_path).resolve()
            dest_path_abs = Path(args.destination_file).resolve()
            # Check if destination is within source directory
            if dest_path_abs.is_relative_to(src_path_abs):
                # Create pattern matching the absolute path, escaped
                exclude_pattern = f"^{re.escape(str(dest_path_abs))}$"
                if exclude_pattern not in final_exclude_patterns:
                    final_exclude_patterns.append(exclude_pattern)
                    logger.debug(f"Auto-excluding destination file pattern: {exclude_pattern}")
        except Exception as e:  # Catch potential path errors
            # Shortened line below
            logger.warning(
                "Could not reliably check if destination is within source. "
                f"Manual exclusion might be needed. Error: {e}"
            )

    logger.info(f"Source Path: {args.source_path}")
    logger.info(f"Output Target: {'stdout' if args.stdout else args.destination_file}")
    logger.info(f"Using .gitignore: {use_gitignore}")
    logger.info(f"Exclude Patterns: {final_exclude_patterns}")
    logger.info(f"Whitelist Patterns: {final_whitelist_patterns}")

    # --- Generate File List ---
    try:
        tree = generate_directory_tree(
            args.source_path,
            final_exclude_patterns,
            final_whitelist_patterns,
            use_gitignore,
        )
    except Exception as e:
        logger.error(f"An error occurred during file collection: {e}", exc_info=args.verbose)
        sys.exit(1)

    # --- Create Output ---
    if tree:
        try:
            create_output(args.destination_file, args.source_path, tree, args.stdout)
        except Exception as e:
            logger.error(f"An error occurred during output creation: {e}", exc_info=args.verbose)
            sys.exit(1)


if __name__ == "__main__":
    main()
