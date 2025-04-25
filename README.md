[![CI/CD](https://github.com/lguibr/codeconcat/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/lguibr/codeconcat/actions/workflows/ci_cd.yml)
[![PyPI](https://img.shields.io/pypi/v/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![Python Version](https://img.shields.io/pypi/pyversions/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![License](https://img.shields.io/pypi/l/codeconcat.svg)](https://github.com/lguibr/codeconcat/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**CodeConcat** is a command-line tool to concatenate files within a directory into a single text file. It intelligently filters files based on common ignore patterns (like `.git`, `node_modules`), file extensions, and optional user-defined rules, making it ideal for preparing codebases for analysis or large language model (LLM) context stuffing.

## Key Features

-   **Smart Filtering**: Automatically excludes common unnecessary files/directories (e.g., `.git`, `__pycache__`, `node_modules`, hidden files) and prioritizes known text/code file extensions.
-   **Flexible Control**: Use `--exclude` and `--whitelist` with simple glob patterns (like `*.py`, `docs/*`, not complex regex) to fine-tune included/excluded files.
-   **Configuration File**: Define project-specific defaults in a `.codeconcat_config.json` file in your project root.
-   **Clear Output**: Prepends each file's content with its relative path (`--- File: path/to/file.py ---`).
-   **Standard Output**: Easily pipe the output to other commands or redirect to a file (`codeconcat . > output.txt`).
-   **Modern Tooling**: Built with modern Python practices, using `pyproject.toml`, `ruff` for linting/formatting, and `mypy` for type checking.

## Installation

Ensure you have Python 3.8+ installed.

```bash
pip install codeconcat
```

**System Dependency:** `codeconcat` uses `python-magic` for advanced file type detection, which relies on the `libmagic` library. You might need to install it separately:

-   **Debian/Ubuntu:** `sudo apt-get update && sudo apt-get install -y libmagic1`
-   **macOS (Homebrew):** `brew install libmagic`
-   **Windows:** Installation can be more complex. Consider using WSL or consult `python-magic` documentation.

If `libmagic` is not found, `codeconcat` will still work but rely solely on file extensions for filtering, which is often sufficient.

## How to Use

### Basic Command Structure

```bash
codeconcat <source_path> [output_file] [-e PATTERN] [-w PATTERN] [-v]
```

### Parameters

-   `<source_path>`: (Required) Path to the directory to process.
-   `[output_file]`: (Optional) Path to save the concatenated output. If omitted, output is sent to standard output (stdout).
-   `-e PATTERN`, `--exclude PATTERN`: (Optional) Add a glob pattern to exclude files/directories. Can be used multiple times (e.g., `-e '*.log' -e 'temp/'`). CLI excludes are added to defaults and config file excludes.
-   `-w PATTERN`, `--whitelist PATTERN`: (Optional) Add a glob pattern to *only* include matching files/directories (after excludes are processed). If omitted, common text/code files are included by default. If used, *only* files matching these patterns (and not excluded) will be included. Can be used multiple times (e.g., `-w '*.py' -w 'src/*'`). CLI whitelists override config file whitelists.
-   `-v`, `--verbose`: (Optional) Enable detailed logging output.

### Examples

**Concatenate current directory to stdout:**

```bash
codeconcat .
```

**Concatenate a specific repo to a file:**

```bash
codeconcat ./my-cool-project concatenated_code.txt
```

**Concatenate to a file, excluding log files and the `dist` directory:**

```bash
codeconcat ./my-cool-project output.txt -e "*.log" -e "dist/*"
```

**Concatenate only Python and Markdown files:**

```bash
codeconcat ./my-cool-project output.txt -w "*.py" -w "*.md"
```

**Pipe output to `less`:**

```bash
codeconcat . | less
```

### Configuration File (`.codeconcat_config.json`)

You can place a `.codeconcat_config.json` file in the root of your `<source_path>` directory to define default patterns.

**Example `.codeconcat_config.json`:**

```json
{
  "exclude": [
    "*.tmp",
    "**/test_data/*",
    ".cache/"
  ],
  "whitelist": [
    "src/**/*.py",
    "config/*.yaml",
    "*.md"
  ]
}
```

**Precedence Rules:**

1.  **Default Excludes:** Applied first (e.g., `.git`, `node_modules`).
2.  **Config File Excludes:** Added to the default excludes.
3.  **CLI `--exclude`:** Added to the combined default and config excludes.
4.  **Config File Whitelist:** If present, files must match these patterns *after* passing exclude checks.
5.  **CLI `--whitelist`:** If present, *overrides* the config file whitelist. Files must match these patterns *after* passing exclude checks.
6.  **Default Whitelist (Extensions):** If no CLI or config whitelist is active, common text/code file extensions are used as an implicit whitelist.
7.  **MIME Type Check:** As a final check (if `libmagic` is available), files identified as likely binary are excluded.

## Contributing

Contributions are welcome!

1.  **Set up:**
    ```bash
    git clone https://github.com/lguibr/codeconcat.git
    cd codeconcat
    python -m venv .venv
    source .venv/bin/activate # or .venv\Scripts\activate on Windows
    pip install -r requirements-dev.txt # Installs codeconcat in editable mode + dev tools
    pre-commit install # Install pre-commit hooks
    ```
2.  Make your changes.
3.  Run checks: `pre-commit run --all-files` (includes `ruff` format/lint, `mypy`)
4.  (Optional but Recommended) Add tests using `pytest`.
5.  Submit a Pull Request.

## License

CodeConcat is distributed under the MIT license. See the [LICENSE](LICENSE) file for more details.
