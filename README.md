# CodeConcat

[![CI](https://github.com/lguibr/codeconcat/workflows/CI/badge.svg)](https://github.com/lguibr/codeconcat/actions)
[![PyPI](https://img.shields.io/pypi/v/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![Python Version](https://img.shields.io/pypi/pyversions/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![License](https://img.shields.io/pypi/l/codeconcat.svg)](https://github.com/lguibr/codeconcat/blob/main/LICENSE)

**CodeConcat** is a powerful command-line tool designed to simplify the process of concatenating the entire contents of local directories or code repositories into a single text file. This tool is particularly useful for developers who need to prepare large datasets for analysis or training in machine learning models, especially those that benefit from understanding the broader context provided by having complete codebases in a single file.

## Key Features

- **Efficiency**: Quickly concatenate entire directories or repositories.
- **Flexibility**: Use include and exclude patterns to control exactly what gets included in the output.
- **Clarity**: Each file's path is included in the output, maintaining the context necessary for large language models.
- **Simplicity**: A straightforward command-line interface that integrates easily into any developer's workflow.

## Installation

You can install CodeConcat directly from PyPI:

```bash
pip install codeconcat
```

## How to Use

### Basic Command Structure

```bash
codeconcat <source_path> [destination_file] [--stdout] [--exclude <pattern>] [--whitelist <pattern>]
```

### Parameters

- `<source_path>`: Path to the directory or repository to process.
- `[destination_file]`: (Optional) Path where the concatenated output will be saved. Required if `--stdout` is not used.
- `--stdout`: (Optional) If specified, output the concatenated content directly to standard output instead of writing to a file. Cannot be used with `destination_file`.
- `--exclude <pattern>`: (Optional) Exclude files matching this pattern.
- `--whitelist <pattern>`: (Optional) Only include files matching this pattern.

### Examples

**Basic Concatenation:**

```bash
codeconcat ./my-repo output.txt
```

**Output to Standard Output:**
```bash
codeconcat ./my-repo --stdout > output.txt
```

**Using Exclude Patterns:**

```bash
codeconcat ./my-repo output.txt --exclude "*.log"
```

**Using Whitelist Patterns:**

```bash
codeconcat ./my-repo output.txt --whitelist "*.py"
```

## Contributing

Contributions to CodeConcat are welcome! Please check out the [issues on GitHub](https://github.com/lguibr/codeconcat/issues) or submit a pull request if you have an improvement or bug fix.

## License

CodeConcat is distributed under the MIT license. See the [LICENSE](LICENSE) file for more details.
