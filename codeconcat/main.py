# -*- coding: utf-8 -*-
# codeconcat/main.py
import logging
import sys
from pathlib import Path
from typing import Tuple

# Imports moved to top
from .cli import parse_arguments
from .config import CONFIG_FILE_NAME, load_config
from .file_utils import collect_all_gitignore_patterns, collect_files
from .output import create_output

# No need to import magic here, file_utils handles it

# Configure logging first
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_concatenation(args) -> Tuple[int, int]:
    """Runs the core concatenation logic, separated for testability."""
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    src_path = Path(args.source_path).resolve()
    output_path = Path(args.output_path).resolve() if args.output_path else None

    if not src_path.is_dir():
        logger.error(f"Source path is not a valid directory: {src_path}")
        raise SystemExit(1)

    if output_path and output_path.is_dir():
        logger.error(f"Output path cannot be a directory: {output_path}")
        raise SystemExit(1)

    config_path = src_path / CONFIG_FILE_NAME
    config = load_config(config_path)

    gitignore_patterns = []
    if not args.no_gitignore:
        gitignore_patterns = collect_all_gitignore_patterns(src_path)
    else:
        logger.info("Processing of .gitignore files is disabled.")

    files_to_process = collect_files(
        src_path,
        args.exclude,
        args.whitelist,
        config.get("exclude", []),
        config.get("whitelist", []),
        gitignore_patterns,
    )

    if not files_to_process:
        logger.warning("No files found matching the criteria. No output generated.")
        return 0, 0

    written, skipped = create_output(files_to_process, src_path, output_path)
    return written, skipped


def main() -> None:
    """Main execution entry point."""
    args = parse_arguments()
    try:
        run_concatenation(args)
    except SystemExit as e:
        # Propagate the exit code from SystemExit if available
        sys.exit(e.code if isinstance(e.code, int) else 1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
