import argparse
import os
from dotenv import load_dotenv
import requests

import github
import shutil
import magic


def remove_hashed_directory(src_path):
    dirs = os.listdir(src_path)
    if len(dirs) == 1:
        hashed_dir = os.path.join(src_path, dirs[0])
        for item in os.listdir(hashed_dir):
            shutil.move(os.path.join(hashed_dir, item), src_path)
        os.rmdir(hashed_dir)


def download_and_unpack_archive(url, dest_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open("temp.zip", "wb") as temp_zip_file:
        for chunk in response.iter_content(chunk_size=8192):
            temp_zip_file.write(chunk)

    shutil.unpack_archive("temp.zip", dest_path)
    os.remove("temp.zip")


def fetch_repository(repo_url, branch=None):
    load_dotenv()
    access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if not access_token:
        raise ValueError(
            "Please set the GITHUB_ACCESS_TOKEN environment variable")

    github = github(access_token)
    repo = github.get_repo(repo_url)

    if branch:
        repo = repo.get_branch(branch)

    repo_zip_url = repo.get_archive_link("zipball")

    return repo_zip_url


def filter_files(root, files):
    excluded_mime_types = ("application", "image", "audio", "video")
    filtered_files = []

    for f in files:
        file_path = os.path.join(root, f)
        mime_type = magic.from_file(file_path, mime=True).split('/')[0]

        if mime_type not in excluded_mime_types:
            filtered_files.append(f)

    return filtered_files


def generate_directory_tree(src_path):
    tree = []

    for root, dirs, files in os.walk(src_path):
        rel_path = os.path.relpath(root, src_path)
        tree.append(rel_path)
        files = filter_files(root, files)

        for f in files:
            tree.append(os.path.join(rel_path, f))

    return tree


def create_output_file(prefix_path, suffix_path, output_path, src_path, tree):
    with open(prefix_path, "r") as prefix_file, open(suffix_path, "r") as suffix_file, open(output_path, "w") as output_file:
        prefix_content = prefix_file.read()
        output_file.write(prefix_content)
        output_file.write("\n")

        for path in tree:

            full_path = os.path.join(src_path, path)

            if os.path.isfile(full_path):
                output_file.write(f"\n{path}\n")

                with open(full_path, "r") as file:
                    content = file.read()
                    output_file.write(content)

                output_file.write("\nFILE END\n ")

        suffix_content = suffix_file.read()
        output_file.write(suffix_content)


def main(repo_url, branch, prefix_path, suffix_path, output_path):
    repo_zip_url = fetch_repository(repo_url, branch)
    src_path = "temp_repo"

    download_and_unpack_archive(repo_zip_url, src_path)
    remove_hashed_directory(src_path)
    tree = generate_directory_tree(src_path)
    create_output_file(prefix_path, suffix_path, output_path, src_path, tree)
    shutil.rmtree(src_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Repository Processor")
    parser.add_argument(
        "repo_url", help="GitHub repository URL in the format <github_username/repository?/optional_branch_or_default_main>"
    )
    parser.add_argument("branch", nargs="?", help="Optional branch name")
    parser.add_argument("prefix_path", help="Path to the prefix file")
    parser.add_argument("suffix_path", help="Path to the suffix file")
    parser.add_argument("output_path", help="Path to the output file")

    args = parser.parse_args()

    main(
        args.repo_url,
        args.branch,
        args.prefix_path,
        args.suffix_path,
        args.output_path
    )
