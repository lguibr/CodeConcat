# -*- coding: utf-8 -*-
# codeconcat/main.py
"""
Main Execution Module.

This module acts as the entry point for the CodeConcat application. It is responsible for:
1.  **Orchestration**: Coordinating the CLI parsing, configuration loading, and execution flow.
2.  **Smart Defaults**: intelligently determining whether to run the interactive wizard
    or execute in "Headless" CLI mode.
3.  **Context-Aware Output**: automatically deciding whether to write to a file (named after
    the repository) or stream to standard output (for piping), based on the TTY state.
4.  **Logging**: Setting up rich-text logging for better developer experience.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .cli import parse_arguments

# Import from local modules
from .config import get_config
from .file_utils import generate_directory_tree
from .output import create_output
from .wizard import run_wizard

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
logger = logging.getLogger("codeconcat")
console = Console()


def determine_output_target(
    source_path_str: str, explicit_output: Optional[str], force_stdout: bool = False
) -> tuple[Optional[str], bool]:
    """
    Intelligently determines the output destination (File vs Stdout).

    Logic:
    1. If `explicit_output` is provided -> Use it (File).
    2. If `force_stdout` flag is set -> Use Stdout.
    3. If running in a TTY (interactive terminal):
       - Defaults to creating a file named `{DirectoryName}.md` in the current working dir.
       - This prevents flooding the terminal with markdown and enables single-command usage
         like `codeconcat .`.
    4. If output is piped (not a TTY) -> Use Stdout (preserves `codeconcat . | pbcopy`).

    Args:
        source_path_str (str): Path to the source directory.
        explicit_output (str | None): Output path provided by user.
        force_stdout (bool): Whether stdout was explicitly requested.

    Returns:
        tuple[str | None, bool]: (Output File Path, Write to Stdout Boolean)
    """
    # 1. Explicit file requested
    if explicit_output:
        return explicit_output, False

    # 2. Forced Stdout
    if force_stdout:
        return None, True

    # 3. Smart TTY Check
    # If stdout is a TTY (user running in terminal), default to file.
    # If stdout is NOT a TTY (piped), default to stdout.
    if sys.stdout.isatty():
        source_path = Path(source_path_str).resolve()
        # Fallback for root dir or weird paths
        name = source_path.name or "codebase"
        auto_filename = f"{name}.md"
        logger.info(f"Terminal detected: Auto-targeting output to '{auto_filename}'")
        return auto_filename, False
    else:
        # Piped usage
        return None, True


def main() -> None:
    """
    Main execution entry point.

    Flow:
    - Parse CLI arguments.
    - If interactive mode requested or source missing -> Run Wizard.
    - Load and merge configurations (Base Defaults < Home Config < Project Config < CLI Args).
    - Resolve exclusions/whitelists/force patterns.
    - Generate File Tree (Traverse & Filter).
    - Generate Output (Assemble Markdown).
    """
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    # --- Determine Mode (CLI vs Wizard) ---
    # Trigger wizard if:
    # 1. --interactive flag is used
    # 2. No source_path is provided
    use_wizard = args.interactive or not args.source_path

    if use_wizard:
        try:
            config_overrides = run_wizard()
            # Wizard returns fully qualified paths strings
        except ImportError:
            # Fallback if dependencies missing (unlikely if installed correctly)
            logger.error("Wizard dependencies missing. Please install 'rich' and 'questionary'.")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[bold red]Cancelled.[/bold red]")
            sys.exit(0)
    else:
        # CLI Mode - Map args to config structure
        config_overrides = {
            "source_path": args.source_path,
            "destination_file": args.output_path,
            "use_gitignore": not args.no_gitignore,
            "exclude": args.exclude,
            "whitelist": args.whitelist,
            "force_patterns": args.force_include,
            "stdout_flag": args.stdout,  # Renamed to avoid key collision with logic
        }

    # --- Configuration Loading and Merging ---
    base_config = get_config()  # Default + File Config

    # Merge overrides (CLI or Wizard) into base config
    source_path_str = config_overrides.get("source_path")
    if not source_path_str:
        logger.error("No source path provided.")
        sys.exit(1)

    use_gitignore = config_overrides.get("use_gitignore")
    if use_gitignore is None:
        use_gitignore = base_config.get("use_gitignore", True)

    # Merge lists unique
    base_excludes = base_config.get("exclude_patterns", [])
    override_excludes = config_overrides.get("exclude", []) or []
    files_excludes = list(set(base_excludes + override_excludes))  # Unique

    base_whitelist = base_config.get("whitelist_patterns", [])
    override_whitelist = config_overrides.get("whitelist", []) or []
    files_whitelist = list(set(base_whitelist + override_whitelist))  # Unique

    # Force patterns (Additive) - No config base yet, just overrides
    files_force = config_overrides.get("force_patterns", []) or []

    # --- Output Target Resolution ---
    # Apply Smart TTY Logic if not in Wizard mode (Wizard sets destination_file explicitly)
    if use_wizard:
        # Wizard handles its own output logic (always file or stdout based on question)
        output_target = config_overrides.get("destination_file")
        to_stdout = config_overrides.get("stdout", False)
    else:
        raw_output = config_overrides.get("destination_file")
        force_stdout = config_overrides.get("stdout_flag", False)
        output_target, to_stdout = determine_output_target(source_path_str, raw_output, force_stdout)

    # --- Auto-Exclude Output File ---
    # Prevent the tool from reading its own output file if it's currently being written to source dir
    if output_target and source_path_str:
        try:
            src = Path(source_path_str).resolve()
            dest = Path(output_target).resolve()
            if dest.is_relative_to(src):
                rel_dest = dest.relative_to(src).as_posix()
                # Exclude exact match regex
                import re

                patt = f"^{re.escape(rel_dest)}$"
                if patt not in files_excludes:
                    files_excludes.append(patt)
                    logger.debug(f"Auto-excluding output file: {rel_dest}")
        except Exception:
            pass

    # --- Execution ---
    with console.status("[bold green]Scanning files...[/bold green]"):
        try:
            tree = generate_directory_tree(
                source_path_str, files_excludes, files_whitelist, files_force, use_gitignore
            )
        except Exception as e:
            logger.error(f"Error collecting files: {e}")
            sys.exit(1)

    if not tree:
        logger.warning("No files found matching criteria.")
        sys.exit(0)

    logger.info(f"Found {len(tree)} files.")

    with console.status("[bold green]Generating output...[/bold green]"):
        try:
            create_output(output_target, source_path_str, tree, to_stdout)
            if not to_stdout and output_target:
                console.print(
                    f"[bold green]Success![/bold green] Output written to: "
                    f"[underline]{output_target}[/underline]"
                )
        except Exception as e:
            logger.error(f"Error creating output: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
