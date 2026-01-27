[![CI/CD](https://github.com/lguibr/codeconcat/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/lguibr/codeconcat/actions/workflows/ci_cd.yml)
[![PyPI](https://img.shields.io/pypi/v/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![Python Version](https://img.shields.io/pypi/pyversions/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![License](https://img.shields.io/pypi/l/codeconcat.svg)](https://github.com/lguibr/codeconcat/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# CodeConcat v3.0

<p align="center">
  <img src="bitmap.png" alt="Logo" width="300"/>
</p>

**The State-of-the-Art tool for preparing codebases for LLM usage.**

CodeConcat turns your messy project folders into a **single, clean, markdown-formatted file** optimized for Large Language Models (LLMs) like Claude, GPT-4, and Gemini. It handles parsing, ignoring, and formatting so you don't have to.

## 🚀 Key Features

-   **🧙‍♂️ Interactive Wizard**: New in v3.0! Just run `codeconcat` and let the step-by-step wizard guide you.
-   **🌲 ASCII File Tree**: Every output starts with a beautiful ASCII representation of your directory structure to give the LLM context.
-   **🧠 Smart Context**: Automatically respects `.gitignore`, skipping `node_modules`, `.git`, and binary files.
-   **💎 Granular Control**:
    -   **Force Include**: Bypass `.gitignore` for specific files (like `.env` or specific build artifacts) using the new "Force Include" logic.
    -   **Whitelist/Exclude**: Powerful glob patterns for fine-tuning.
-   **🛡️ Safe Fencing**: Intelligent code block detection prevents nested backticks from breaking your markdown structure.
-   **✨ Beautiful UI**: Powered by `rich` and `questionary` for a modern, clean terminal experience.

## 📦 Installation

Ensure you have Python 3.8+ installed.

```bash
pip install codeconcat
```

## 🛠️ Usage

### 1. Interactive Wizard (Recommended)

Simply run the command without arguments to start the configuration wizard.

```bash
codeconcat
```

You will be asked:
1.  Source directory?
2.  Output filename?
3.  Respect `.gitignore`?
4.  **Force include** specific files? (Grab those `.env` files or `dist/` builds easily!)
5.  Verification & Summary.

### 2. Command Line Interface (CLI)

For power users or scripts, use the widely compatible CLI.

**Concatenate current directory:**
```bash
codeconcat .
```

**Force Include specific ignored files (New in v3.0):**
Grab your `.env.local` even though it's gitignored:
```bash
codeconcat --force-include ".env.local"
```

**Exclude logs and include only Python files:**
```bash
codeconcat . codebase.md -e "*.log" -w "*.py"
```

### Options

| Flag | Description |
|------|-------------|
| `-i`, `--interactive` | Force the interactive wizard mode. |
| `--force-include` | **Additive**: Include these files even if they are in `.gitignore`. |
| `-e`, `--exclude` | **subtractive**: Exclude files matching this glob pattern. |
| `-w`, `--whitelist` | **Exclusive**: ONLY include files matching this glob pattern. |
| `--no-gitignore` | Disable `.gitignore` processing entirely. |
| `--stdout` | Output to console instead of a file. |

## 📄 Output Format

The output is a single Markdown file structured for maximum LLM comprehension:

1.  **Header**: Project Name.
2.  **File Tree**:
    ```text
    src/
    ├── main.py
    ├── utils.py
    └── config.py
    ```
3.  **Content**:
    ```markdown
    ### File: `src/main.py`

    ```python
    print("Hello World")
    ```
    ```

## 🤝 Contributing

Contributions are welcome!

1.  Clone repo: `git clone https://github.com/lguibr/codeconcat.git`
2.  Install dev setup: `pip install -e .`
3.  Run tests: `pytest`

## License

MIT License.
