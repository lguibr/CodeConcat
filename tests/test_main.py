# -*- coding: utf-8 -*-
# tests/test_main.py
import logging
import sys
from pathlib import Path
from unittest.mock import patch  # Added MagicMock

# Import config constants and functions for patching/checking
from codeconcat.config import HOME_CONFIG_PATH, PROJECT_CONFIG_PATH

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
    """Test basic file concatenation without special flags."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "file1.py": "print('hello')",
            "subdir/file2.txt": "world",
            ".hidden": "ignore me",  # Should be included by default (text file)
            "file3.log": "a log file",  # Should be included by default (in LANGUAGE_EXTENSIONS)
        },
    )

    # Simulate command line: codeconcat ./src output.txt
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    print(
        f"\n--- Output for test_basic_concatenation ---\n{content}\n--------------------------------------"
    )  # Debug print
    # Assertions updated to reflect that .hidden and .log ARE included by default rules
    assert "File: file1.py" in content
    assert '""""""\nprint(\'hello\')\n""""""' in content
    assert "File: subdir/file2.txt" in content
    assert '""""""\nworld\n""""""' in content
    assert "File: .hidden" in content  # <<< CHANGED ASSERTION
    assert '""""""\nignore me\n""""""' in content
    assert "File: file3.log" in content  # <<< CHANGED ASSERTION
    assert '""""""\na log file\n""""""' in content


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
    """Test the --exclude command-line flag."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "include.py": "include",
            "exclude.log": "exclude",
            "also_include.txt": "include 2",
        },
    )

    # Simulate command line: codeconcat ./src output.txt --exclude ".*\\.log$"
    test_args = [
        "codeconcat",
        str(source_dir),
        str(output_file),
        "--exclude",
        r".*\.log$",
    ]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "include.py" in content
    assert "also_include.txt" in content
    assert "exclude.log" not in content


def test_whitelist_flag(tmp_path: Path):
    """Test the --whitelist command-line flag."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "include.py": "include",
            "exclude.txt": "exclude",
            "also_include.py": "include 2",
        },
    )

    # Simulate command line: codeconcat ./src output.txt --whitelist "\.py$"
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


def test_no_gitignore_flag(tmp_path: Path):
    """Test that --no-gitignore includes files normally ignored by .gitignore."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"file.py": "py", "ignored_by_git.tmp": "tmp"})
    # Create a .gitignore file that ignores *.tmp
    (source_dir / ".gitignore").write_text("*.tmp\n")

    # Simulate command line: codeconcat ./src output.txt --no-gitignore
    test_args = ["codeconcat", str(source_dir), str(output_file), "--no-gitignore"]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "file.py" in content
    assert "ignored_by_git.tmp" in content  # Should be included now


def test_gitignore_default(tmp_path: Path):
    """Test that .gitignore is used by default."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"file.py": "py", "ignored_by_git.tmp": "tmp"})
    # Create a .gitignore file that ignores *.tmp
    (source_dir / ".gitignore").write_text("*.tmp\n")

    # Simulate command line: codeconcat ./src output.txt (no --no-gitignore)
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    assert "file.py" in content
    assert "ignored_by_git.tmp" not in content  # Should be excluded by default


@patch("codeconcat.config.create_default_config_if_needed")  # Patch the creation function
@patch("codeconcat.config.load_config_file")  # Still need to mock loading
def test_config_file_creation(mock_load_config, mock_create_default, tmp_path: Path):
    """Test that the default config creation function is called when no config exists."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(source_dir, {"file1.txt": "hello"})

    # Simulate that load_config_file finds nothing
    mock_load_config.return_value = None

    test_args = ["codeconcat", str(source_dir), str(output_file)]

    # Patch sys.argv and run main
    # We don't need to patch HOME/PROJECT_CONFIG_PATH here because we mock load_config_file
    with patch.object(sys, "argv", test_args):
        main()

    # Assert that our specific creation function was called exactly once
    # It should be called with the *real* HOME_CONFIG_PATH constant
    mock_create_default.assert_called_once_with(HOME_CONFIG_PATH)

    # Check that the main operation still worked (output file created on disk)
    assert output_file.exists()
    assert "file1.txt" in output_file.read_text()


# Patch load_config_file directly instead of builtins.open
@patch("codeconcat.config.load_config_file")
def test_config_file_loading_home_only(mock_load_config, tmp_path: Path):
    """Test loading config solely from the home directory config file."""
    source_dir = tmp_path / "src"
    output_file = tmp_path / "output.txt"
    create_test_files(
        source_dir,
        {
            "file.py": "py",
            "file.log": "log",  # This should be excluded by the config
        },
    )

    # Define what load_config_file should return for home and project paths
    home_config_content = {
        "use_gitignore": False,
        "exclude_patterns": [r"\.log$"],
        "whitelist_patterns": [],
    }

    def load_side_effect(path):
        if path == HOME_CONFIG_PATH:
            return home_config_content
        elif path == PROJECT_CONFIG_PATH:
            return None  # Simulate project config not found
        return None  # Default case

    mock_load_config.side_effect = load_side_effect

    test_args = ["codeconcat", str(source_dir), str(output_file)]

    with patch.object(sys, "argv", test_args):
        main()

    # Check output reflects config (gitignore off, logs excluded)
    assert output_file.exists()  # <<< This should now pass
    content = output_file.read_text()
    assert "file.py" in content
    assert "file.log" not in content


# Patch load_config_file directly instead of builtins.open
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

    # Define side effect for load_config_file
    home_config_content = {"exclude_patterns": [r"\.log$"]}
    project_config_content = {"exclude_patterns": [r"\.py$"]}

    def load_side_effect(path):
        if path == HOME_CONFIG_PATH:
            return home_config_content
        elif path == PROJECT_CONFIG_PATH:
            return project_config_content
        return None

    mock_load_config.side_effect = load_side_effect

    test_args = [
        "codeconcat",
        str(source_dir),
        str(output_file),
        "--no-gitignore",  # Turn off gitignore to isolate config effect
    ]

    with patch.object(sys, "argv", test_args):
        main()

    # Check output reflects project config (py excluded, txt included)
    assert output_file.exists()  # <<< This should now pass
    content = output_file.read_text()
    assert "file.py" not in content
    assert "file.txt" in content


def test_no_files_found(tmp_path: Path, caplog):
    """Test the warning when no files match criteria."""
    source_dir = tmp_path / "src"
    source_dir.mkdir()  # Empty directory
    output_file = tmp_path / "output.txt"

    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with (
        patch.object(sys, "argv", test_args),
        caplog.at_level(logging.WARNING),
    ):  # Capture warnings
        main()

    assert not output_file.exists()  # Should not create empty file
    assert "No files found matching the criteria" in caplog.text


def test_exclude_output_file_implicitly(tmp_path: Path):
    """Test that the output file is excluded automatically if inside source."""
    source_dir = tmp_path / "src"
    output_file = source_dir / "output.txt"  # Output *inside* source
    create_test_files(
        source_dir,
        {
            "file1.py": "print('hello')",
        },
    )
    # Pre-create the output file to see if it gets included
    output_file.write_text("PRE_EXISTING_OUTPUT_CONTENT")

    # Simulate command line: codeconcat ./src ./src/output.txt
    test_args = ["codeconcat", str(source_dir), str(output_file)]
    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()
    content = output_file.read_text()
    # Check that the original file is there
    assert "File: file1.py" in content
    assert "print('hello')" in content
    # Check that the output file itself wasn't read and included
    assert "PRE_EXISTING_OUTPUT_CONTENT" not in content
    assert f"File: {output_file.name}" not in content  # Check header wasn't added


# Add more tests for edge cases:
# - Empty files
# - Files with encoding issues (though errors='replace' handles some)
# - Complex directory structures
# - Interactions between exclude, whitelist, gitignore, and config files
# - Symlinks (current os.walk might follow them depending on python version/OS)
