# CodeConcat

[![CI](https://github.com/lguibr/codeconcat/workflows/CI/badge.svg)](https://github.com/lguibr/codeconcat/actions)
[![PyPI](https://img.shields.io/pypi/v/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![Python Version](https://img.shields.io/pypi/pyversions/codeconcat.svg)](https://pypi.org/project/codeconcat/)
[![License](https://img.shields.io/pypi/l/codeconcat.svg)](https://github.com/lguibr/codeconcat/blob/main/LICENSE)

CodeConcat is a command-line interface (CLI) tool that enables developers to quickly and easily concatenate an entire local code repository into a single text file. This bundled file includes a directory tree, file paths, and file content, making it an excellent resource for code review, documentation, or sharing with others.

## Features

- Process code from any local repository
- Generate a directory tree for the entire codebase
- Include file paths and file content in the output
- Produce a human-readable text file
- Customize the output file path and name
- Exclude specific files or directories using patterns
- Include only specific files or directories using whitelist patterns

## Installation

To install CodeConcat, you can use pip:

```bash

pip install codeconcat
```

## Usage

To use CodeConcat, run the following command with the required arguments:

```bash

codeconcat <repo_path> <output_path> [--exclude <pattern>] [--whitelist <pattern>]
```

## Arguments

<repo_path>: The path to the local repository you want to process.
<output_path>: The path to the output file where the concatenated codebase will be saved.
--exclude <pattern> (optional): Exclude files or directories matching the given pattern.
--whitelist <pattern> (optional): Include only files or directories matching the given pattern.

## Example

Suppose you want to concatenate the codebase from the ~/projects/my-repo directory and save it in a file called output.txt in the current directory. The command would look like this:

```bash
codeconcat ~/projects/my-repo output.txt

```

If you want to exclude certain files or directories, you can use the --exclude option:

```bash
codeconcat ~/projects/my-repo output.txt --exclude "tests/\*"

```

To include only specific files or directories, you can use the --whitelist option:

```bash

codeconcat ~/projects/my-repo output.txt --whitelist "src/\*"
```
