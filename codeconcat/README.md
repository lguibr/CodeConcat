# CodeConcat Package Documentation

This directory contains the source code for the `codeconcat` application.

## Module Architecture

The application is structured into the following independent modules, orchestrating a flow from Input -> Processing -> Output.

### Core Modules

*   **`main.py`**: The entry point. Handles logic branching between CLI and Wizard modes, loads configuration, and orchestrates the pipeline.
*   **`cli.py`**: Defines the Command Line Interface using `argparse`. Handles arguments like `--force-include`, `--exclude`, and smart output flags.
*   **`wizard.py`**: Provides the Interactive Mode using `questionary` and `rich`. Guides users through configuration step-by-step.
*   **`config.py`**: Manages configuration loading from JSON files (Home/Project) and defines the `DEFAULT_EXCLUDE_PATTERNS`.
*   **`file_utils.py`**: The "Engine" of the application. Handles directory traversal, `.gitignore` parsing (via `pathspec`), and the complex filtering logic (Exclusion vs. Whitelist vs. Force Include).
*   **`output.py`**: Handles generating the Markdown output. Includes the ASCII tree generator and the `get_safe_fence` logic for verifying markdown integrity.

## Key Logic Flows

### Filtering Logic (`file_utils.generate_directory_tree`)
Deciding whether a file is included follows this precedence:
1.  **Exclude**: Matches `--exclude`? -> **SKIP**.
2.  **Whitelist (Exclusive)**: Is a whitelist active? If yes, does it match? -> **KEEP**. If not -> **SKIP**.
3.  **Force Include (Additive)**: Matches `--force-include`? -> **KEEP** (Bypass gitignore).
4.  **Gitignore**: Matches `.gitignore`? -> **SKIP**.
5.  **Default**: Is it a text code file? -> **KEEP**.

### Smart Output (`main.determine_output_target`)
Deciding where to write the output:
1.  **Interactive Terminal**: If running `codeconcat .` (no output arg), it automatically writes to `{DirectoryName}.md` to preserve the user's terminal buffer.
2.  **Piping**: If running `codeconcat . | pbcopy`, it detects the pipe and writes to **STDOUT**.
