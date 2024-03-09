import argparse
import logging
import os
from typing import List
import shutil
import magic
import re

EXCLUDED_MIME_TYPES = ("application", "image", "audio", "video")

logger = logging.getLogger(__name__)

def remove_hashed_directory(src_path: str) -> None:
    dirs = os.listdir(src_path)
    if len(dirs) == 1:
        hashed_dir = os.path.join(src_path, dirs[0])
        for item in os.listdir(hashed_dir):
            shutil.move(os.path.join(hashed_dir, item), src_path)
        os.rmdir(hashed_dir)

def generate_directory_tree(src_path: str, exclude_pattern: str, whitelist_pattern: str) -> List[str]:
    tree = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            file_path = os.path.join(root, file)
            if whitelist_pattern and not re.search(whitelist_pattern, file_path):
                continue
            if exclude_pattern and re.search(exclude_pattern, file_path):
                continue
            mime_type = magic.from_file(file_path, mime=True)
            if not any(excluded in mime_type for excluded in EXCLUDED_MIME_TYPES):
                tree.append(file_path)
    return tree

def create_output_file(output_path: str, src_path: str, tree: List[str]) -> None:
    with open(output_path, "w", encoding="utf-8") as output_file:
        for file_path in tree:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
            except UnicodeDecodeError:
                logger.warning(f"Skipping file {file_path} due to encoding issues.")
                continue

            relative_path = os.path.relpath(file_path, src_path)
            output_file.write(f"File: {relative_path}\n")
            output_file.write(content)
            output_file.write("\n\n")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Repository Processor")
    parser.add_argument("repo_path", help="Path to the local repository")
    parser.add_argument("output_path", help="Path to the output file")
    parser.add_argument("--exclude", default="", help="Exclude files or directories matching the given pattern")
    parser.add_argument("--whitelist", default="", help="Include only files or directories matching the given pattern")

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    repo_path = args.repo_path
    output_path = args.output_path
    exclude_pattern = args.exclude
    whitelist_pattern = args.whitelist

    remove_hashed_directory(repo_path)
    tree = generate_directory_tree(repo_path, exclude_pattern, whitelist_pattern)
    create_output_file(output_path, repo_path, tree)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

