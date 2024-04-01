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
    ".py", ".js", ".ts", ".tsx", ".java", ".c", ".cpp", ".cs", ".rb", ".php", ".swift",
    ".go", ".rs", ".kt", ".scala", ".pl", ".pm", ".sh", ".bat", ".cmd", ".ps1", ".vim",
    ".el", ".lisp", ".clj", ".hs", ".ml", ".fs", ".fsx", ".lua", ".r", ".m", ".sql",
    ".html", ".css", ".scss", ".sass", ".less", ".xml", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".md", ".txt", ".log", ".csv", ".tsv", ".rst", ".tex", ".bib",
    ".org", ".nfo", ".asc", ".asciidoc", ".adoc", ".ahk", ".applescript", ".as", ".au3",
    ".bas", ".bat", ".btm", ".cmd", ".coffee", ".d", ".dart", ".dpr", ".feature", ".groovy",
    ".haml", ".hs", ".ino", ".ipp", ".jsx", ".lhs", ".lua", ".m4", ".mak", ".matlab", ".ml",
    ".mm", ".nc", ".p", ".pas", ".php", ".pl", ".pm", ".pp", ".pro", ".ps1", ".psd1", ".psm1",
    ".py", ".pyc", ".pyd", ".pyi", ".pyw", ".pyx", ".pxd", ".pxi", ".r", ".rb", ".rkt", ".rpy",
    ".rs", ".s", ".scm", ".sh", ".sql", ".swift", ".tcl", ".tj", ".ts", ".tsx", ".v", ".vb",
    ".vbs", ".vcxproj", ".vhd", ".vhdl", ".xaml", ".xsl", ".zsh"
)

logger = logging.getLogger(__name__)

def remove_hashed_directory(src_path: str) -> None:
    # ... (rest of the code remains the same)

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
            if is_valid_mime_type or file.lower().endswith(LANGUAGE_EXTENSIONS):
                tree.append(file_path)
    return tree

def create_output_file(
    output_path: str, src_path: str, tree: List[str],
) -> None:
    # ... (rest of the code remains the same)

def parse_arguments() -> argparse.Namespace:
    # ... (rest of the code remains the same)

def main() -> None:
    # ... (rest of the code remains the same)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()