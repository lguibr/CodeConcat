# -*- coding: utf-8 -*-
# codeconcat/wizard.py
"""
Interactive Wizard Module.

This module provides a user-friendly, interactive command-line interface (CLI)
for configuring CodeConcat. It uses `questionary` for prompts and `rich` for
visual feedback.

It guides the user through:
1.  Selecting the source directory.
2.  Choosing an output file path.
3.  Configuring .gitignore behavior.
4.  Adding custom file exclusions.
5.  Selecting "Force Include" patterns (Granularity).
"""

import os
import sys
from typing import Any, Dict

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_wizard() -> Dict[str, Any]:
    """
    Runs the interactive configuration wizard.

    Prompts the user for all necessary configuration options and returns
    a dictionary compatible with the application's config structure.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - source_path (str)
            - destination_file (str)
            - use_gitignore (bool)
            - exclude (List[str])
            - whitelist (List[str]) - Used for Force Includes here
            - stdout (bool) - Always False for wizard
    """
    console.print(
        Panel.fit(
            "[bold cyan]CodeConcat Interactive Configuration[/bold cyan]",
            subtitle="Configure your file concatenation",
        )
    )

    # 1. Source Path
    source_path = questionary.path(
        "Where is the source directory?",
        default=os.getcwd(),
        only_directories=True,
    ).ask()
    if not source_path:
        sys.exit(0)  # User cancelled

    # 2. Output File
    default_output = "codebase.md"
    output_path = questionary.text(
        "Where should the output file be saved?",
        default=default_output,
    ).ask()
    if not output_path:
        sys.exit(0)

    # 3. Gitignore
    use_gitignore = questionary.confirm(
        "Do you want to respect .gitignore rules?",
        default=True,
    ).ask()

    # 4. Additional Excludes (optional)
    exclude_patterns = []
    while True:
        add_exclude = questionary.confirm(
            "Do you want to exclude any additional files/folders?",
            default=False,
        ).ask()
        if not add_exclude:
            break

        pattern = questionary.text("Enter glob pattern (e.g. *.log, node_modules/):").ask()
        if pattern:
            exclude_patterns.append(pattern)

    # 5. Granularity / Force Includes
    # Allow user to pick specific extensions to include even if ignored
    force_extensions = []
    want_granularity = questionary.confirm(
        "Do you want to force include specific files/types even if ignored (e.g. .env, specific js files)?",
        default=False,
    ).ask()

    if want_granularity:
        # Common extensions to offer
        common_exts = [".js", ".ts", ".jsx", ".tsx", ".json", ".py", ".md", ".css", ".html"]
        selected_exts = questionary.checkbox(
            "Select extensions to force include:",
            choices=[questionary.Choice(ext, checked=False) for ext in common_exts],
        ).ask()
        if selected_exts:
            # Convert to glob patterns for whitelist
            # If user selected .js, we want **/*.js
            force_extensions = [f"**/*{ext}" for ext in selected_exts]

        # Custom patterns
        custom_force = questionary.text("Enter any custom whitelist patterns (comma separated):").ask()
        if custom_force:
            force_extensions.extend([p.strip() for p in custom_force.split(",") if p.strip()])

    # Confirm settings
    table = Table(title="Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Source Path", source_path)
    table.add_row("Output File", output_path)
    table.add_row("Respect .gitignore", str(use_gitignore))
    table.add_row("Additional Excludes", ", ".join(exclude_patterns) if exclude_patterns else "None")
    table.add_row("Force Includes", ", ".join(force_extensions) if force_extensions else "None")

    console.print(table)

    confirm = questionary.confirm("Start processing?", default=True).ask()
    if not confirm:
        sys.exit(0)

    return {
        "source_path": source_path,
        "destination_file": output_path,
        "use_gitignore": use_gitignore,
        "exclude": exclude_patterns,
        # In Wizard, "Force Includes" means "Add to the list even if ignored", so it maps to force_patterns
        "whitelist": [],  # Wizard doesn't currently support Exclusive whitelist (subtractive), only Additive
        "force_patterns": force_extensions,
        "stdout": False,  # Wizard always saves to file by default, unless we add an option
    }


if __name__ == "__main__":
    run_wizard()
