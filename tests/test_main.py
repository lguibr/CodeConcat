# -*- coding: utf-8 -*-
# tests/test_main.py
import logging
import sys
from pathlib import Path
from unittest.mock import patch

# Import config constants and functions for patching/checking
from codeconcat.config import (
    HOME_CONFIG_PATH,
    PROJECT_CONFIG_PATH,
)

# Assuming your main function is in codeconcat.main
from codeconcat.main import main


# Helper function to create test files
def create_test_files(base_path: Path, files_dict: dict):
    """Creates files with content in a base path."""
    for name, content in files_dict.items():
        path = base_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# --- Test Cases ---


def test_basic_concatenation(tmp_path: Path):
    """Test basic file concatenation without special flags (uses default excludes)."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "file1.py": "print('hello')",
            "subdir/file2.txt": "world",
            ".hidden": "ignore me",  # Should be included by default (text file)
            "file3.log": "a log file",  # Should be included by default (in LANGUAGE_EXTENSIONS)
            "node_modules/some_dep.js": "excluded",  # Should be excluded by default config
            "build/output.o": "excluded",  # Should be excluded by default config
        },
    )

    # Simulate command line: codeconcat ./src output.txt
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    print(f"\n--- Output for test_basic_concatenation ---\n{content}\n--------------------------------------")
    assert "File: file1.py" in content
    assert '""""""\nprint(\'hello\')\n""""""' in content
    assert "File: subdir/file2.txt" in content
    assert '""""""\nworld\n""""""' in content
    assert "File: .hidden" in content
    assert '""""""\nignore me\n""""""' in content
    assert "File: file3.log" in content
    assert '""""""\na log file\n""""""' in content
    # Check that default excludes worked


def test_stdout_output(tmp_path: Path, capsys):
    """Test outputting to stdout."""
    source_dir = tmp_path / "src"
    create_test_files(source_dir, {"file1.py": "data"})

    # Simulate command line: codeconcat ./src --stdout
    test_args = ["codeconcat", str(source_dir), "--stdout"]
    with patch.object(sys, "argv", test_args):
        main()

    captured = capsys.readouterr()
    stdout_content = captured.out
    assert "File: file1.py" in stdout_content
    assert '""""""\ndata\n""""""' in stdout_content


def test_exclude_flag(tmp_path: Path):
    """Test the --exclude command-line flag (overrides default excludes)."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "include.py": "include",
            "exclude.log": "exclude",  # This specific log should be excluded by flag
            "other.log": "include",  # This log should be included as default excludes are overridden
            "node_modules/stuff.js": "include",  # This should be included as default excludes are overridden
        },
    )

    # Simulate command line: codeconcat ./src output.txt --exclude "exclude\\.log$"
    # Providing --exclude overrides the default list entirely
    test_args = [
        "codeconcat",
        str(source_dir),
        str(output_file),
        "--exclude",
        r"exclude\.log$",
    ]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "include.py" in content
    assert "other.log" in content
    assert "node_modules/stuff.js" in content
    assert "exclude.log" not in content  # Only this specific log is excluded


def test_whitelist_flag(tmp_path: Path):
    """Test the --whitelist command-line flag (ignores default excludes)."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "include.py": "include",
            "exclude.txt": "exclude",
            "also_include.py": "include 2",
            "node_modules/stuff.js": "exclude",  # Normally excluded, but whitelist overrides
        },
    )

    # Simulate command line: codeconcat ./src output.txt --whitelist "\.py$"
    # Whitelist means ONLY python files are included, regardless of defaults
    test_args = [
        "codeconcat",
        str(source_dir),
        str(output_file),
        "--whitelist",
        r"\.py$",
    ]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "include.py" in content
    assert "also_include.py" in content
    assert "exclude.txt" not in content
    assert "node_modules" not in content


# --- Tests focusing on .gitignore interaction ---


def test_no_gitignore_flag(tmp_path: Path):
    """Test --no-gitignore includes files normally ignored by .gitignore."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"my_code.py": "py", "ignored_by_git.dat": "dat"})
    (source_dir / ".gitignore").write_text("*.dat\n")

    # Simulate command line: codeconcat ./src output.txt --no-gitignore --exclude ''
    # ADDED --exclude '' to disable default config excludes for this test
    test_args = [
        "codeconcat",
        str(source_dir),
        str(output_file),
        "--no-gitignore",
        "--exclude",
        "",
    ]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists(), "Output file should be created when files are found"
    content = output_file.read_text()
    assert "my_code.py" in content
    assert "ignored_by_git.dat" in content, "--no-gitignore should include .dat file"


def test_gitignore_default(tmp_path: Path):
    """Test that .gitignore is used by default."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"my_code.py": "py", "ignored_by_git.dat": "dat"})
    (source_dir / ".gitignore").write_text("*.dat\n")

    # Simulate command line: codeconcat ./src output.txt --exclude ''
    # ADDED --exclude '' to disable default config excludes for this test
    # This isolates the effect of ONLY the .gitignore file
    test_args = ["codeconcat", str(source_dir), str(output_file), "--exclude", ""]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists(), "Output file should be created when files are found"
    content = output_file.read_text()
    assert "my_code.py" in content
    assert "ignored_by_git.dat" not in content, ".gitignore should exclude .dat file"


# --- Tests focusing on Config file interaction ---


@patch("codeconcat.config.create_default_config_if_needed")
@patch("codeconcat.config.load_config_file")
def test_config_file_creation(mock_load_config, mock_create_default, tmp_path: Path):
    """Test that the default config creation function is called when no config exists."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"file1.txt": "hello"})
    mock_load_config.return_value = None
    test_args = ["codeconcat", str(source_dir), str(output_file)]

    with patch.object(sys, "argv", test_args):
        main()

    mock_create_default.assert_called_once_with(HOME_CONFIG_PATH)
    assert output_file.exists()
    assert "file1.txt" in output_file.read_text()


@patch("codeconcat.config.load_config_file")
def test_config_file_loading_home_only(mock_load_config, tmp_path: Path):
    """Test loading config solely from the home directory config file."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "file.py": "py",
            "file.log": "log",  # This should be excluded by the loaded config
        },
    )
    home_config_content = {
        "use_gitignore": False,
        "exclude_patterns": [r"\.log$"],  # Only exclude .log
        "whitelist_patterns": [],
    }

    def load_side_effect(path):
        return home_config_content if path == HOME_CONFIG_PATH else None

    mock_load_config.side_effect = load_side_effect
    test_args = ["codeconcat", str(source_dir), str(output_file)]

    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "file.py" in content  # Should be included (use_gitignore=False, not excluded)
    assert "file.log" not in content  # Excluded by loaded config


@patch("codeconcat.config.load_config_file")
def test_config_file_loading_project_overrides(mock_load_config, tmp_path: Path):
    """Test that project config overrides home config."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "file.py": "py",  # Should be excluded by project config
            "file.txt": "txt",  # Should be included
        },
    )
    home_config_content = {"exclude_patterns": [r"\.log$"]}
    project_config_content = {"exclude_patterns": [r"\.py$"]}  # Override excludes

    def load_side_effect(path):
        if path == HOME_CONFIG_PATH:
            return home_config_content
        if path == PROJECT_CONFIG_PATH:
            return project_config_content
        return None

    mock_load_config.side_effect = load_side_effect
    test_args = ["codeconcat", str(source_dir), str(output_file), "--no-gitignore"]

    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "file.py" not in content  # Excluded by project config
    assert "file.txt" in content


def test_no_files_found(tmp_path: Path, caplog):
    """Test the warning when no files match criteria."""
    source_dir = tmp_path / "src"
    source_dir.mkdir()  # Empty directory
    output_file = tmp_path / "output.txt"
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args), caplog.at_level(logging.WARNING):
        main()

    assert not output_file.exists()
    assert "No files found matching the criteria" in caplog.text


def test_exclude_output_file_implicitly(tmp_path: Path):
    """Test that the output file is excluded automatically if inside source."""
    source_dir = tmp_path / "src"
    output_file = source_dir / "output.txt"  # Output *inside* source
    create_test_files(source_dir, {"file1.py": "print('hello')"})
    output_file.write_text("PRE_EXISTING_OUTPUT_CONTENT")
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "File: file1.py" in content
    assert "print('hello')" in content
    assert "PRE_EXISTING_OUTPUT_CONTENT" not in content
    assert f"File: {output_file.name}" not in content
