# -*- coding: utf-8 -*-
import argparse
import logging
import os
import re
import shutil
from typing import List

import magic

EXCLUDED_MIME_TYPES = ("application", "image", "audio", "video")
LANGUAGE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".go",
    ".rs",
    ".kt",
    ".scala",
    ".pl",
    ".pm",
    ".sh",
    ".bat",
    ".cmd",
    ".ps1",
    ".vim",
    ".el",
    ".lisp",
    ".clj",
    ".hs",
    ".ml",
    ".fs",
    ".fsx",
    ".lua",
    ".r",
    ".m",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".log",
    ".csv",
    ".tsv",
    ".rst",
    ".tex",
    ".bib",
    ".org",
    ".nfo",
    ".asc",
    ".asciidoc",
    ".adoc",
    ".ahk",
    ".applescript",
    ".as",
    ".au3",
    ".bas",
    ".bat",
    ".btm",
    ".cmd",
    ".coffee",
    ".d",
    ".dart",
    ".dpr",
    ".feature",
    ".groovy",
    ".haml",
    ".hs",
    ".ino",
    ".ipp",
    ".jsx",
    ".lhs",
    ".lua",
    ".m4",
    ".mak",
    ".matlab",
    ".ml",
    ".mm",
    ".nc",
    ".p",
    ".pas",
    ".php",
    ".pl",
    ".pm",
    ".pp",
    ".pro",
    ".ps1",
    ".psd1",
    ".psm1",
    ".py",
    ".pyc",
    ".pyd",
    ".pyi",
    ".pyw",
    ".pyx",
    ".pxd",
    ".pxi",
    ".r",
    ".rb",
    ".rkt",
    ".rpy",
    ".rs",
    ".s",
    ".scm",
    ".sh",
    ".sql",
    ".swift",
    ".tcl",
    ".tj",
    ".ts",
    ".tsx",
    ".v",
    ".vb",
    ".vbs",
    ".vcxproj",
    ".vhd",
    ".vhdl",
    ".xaml",
    ".xsl",
    ".zsh",
)

logger = logging.getLogger(__name__)


def remove_hashed_directory(src_path: str) -> None:
    dirs = os.listdir(src_path)
    if len(dirs) == 1:
        hashed_dir = os.path.join(src_path, dirs[0])
        for item in os.listdir(hashed_dir):
            shutil.move(os.path.join(hashed_dir, item), src_path)
        os.rmdir(hashed_dir)


def generate_directory_tree(
    src_path: str, exclude_pattern: str, whitelist_pattern: str
) -> List[str]:
    tree = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            file_path = os.path.join(root, file)
            if whitelist_pattern and not re.search(
                whitelist_pattern, file_path, re.IGNORECASE
            ):
                continue
            if exclude_pattern and re.search(exclude_pattern, file_path):
                continue
            mime_type = magic.from_file(file_path, mime=True)
            is_valid_mime_type = not any(
                excluded in mime_type for excluded in EXCLUDED_MIME_TYPES
            )
            is_language_file = file.lower().endswith(LANGUAGE_EXTENSIONS)
            if is_valid_mime_type or is_language_file:
                tree.append(file_path)
    return tree


def create_output_file(
    output_path: str,
    src_path: str,
    tree: List[str],
) -> None:
    with open(output_path, "w", encoding="utf-8") as output_file:
        for file_path in tree:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except UnicodeDecodeError:
                logger.warning(f"Skipping file {file_path} - encoding issue")
                continue

            relative_path = os.path.relpath(file_path, src_path)
            output_file.write(f"File: {relative_path}\n")
            output_file.write(content)
            output_file.write("\n\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Repository Processor")
    parser.add_argument("repo_path", help="Path to the local repository")
    parser.add_argument("output_path", help="Path to the output file")
    parser.add_argument(
        "--exclude",
        default="",
        help="Exclude files or directories matching the given pattern",
    )
    parser.add_argument(
        "--whitelist",
        default="",
        help="Include only files or directories matching the given pattern",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    repo_path = args.repo_path
    output_path = args.output_path
    exclude_pattern = args.exclude
    whitelist_pattern = args.whitelist

    remove_hashed_directory(repo_path)
    tree = generate_directory_tree(
        repo_path,
        exclude_pattern,
        whitelist_pattern,
    )
    create_output_file(output_path, repo_path, tree)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
