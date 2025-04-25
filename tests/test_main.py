# -*- coding: utf-8 -*-
# tests/test_main.py
import json
import logging
import sys
import types  # Import types for ModuleType
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Make the module importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from specific modules now
from codeconcat import cli as codeconcat_cli
from codeconcat import config as codeconcat_config
from codeconcat import main as codeconcat_main

# Mock magic if it's not installed or for consistent testing
magic: Optional[types.ModuleType]  # Add type hint here
try:
    from codeconcat.file_utils import magic as file_utils_magic  # Import with alias

    magic = file_utils_magic  # Assign if successful
except ImportError:
    magic = None  # Assign None if import fails


# --- Helper Functions ---
def create_structure(base_path: Path, structure: Dict[str, Any]):
    """Recursively creates a directory structure with files and content."""
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, str):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        elif isinstance(content, bytes):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        elif content is None:
            path.mkdir(parents=True, exist_ok=True)


def run_test_flow(args_list: List[str], monkeypatch=None) -> str:
    """
    Parses arguments, runs the core concatenation logic, and captures stdout.
    Handles SystemExit gracefully for testing purposes.
    """
    captured_output = StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output  # Always patch stdout for tests

    try:
        # Parse arguments using the cli module's function
        args = codeconcat_cli.parse_arguments(args_list)
        # Run the main orchestration logic from the main module
        codeconcat_main.run_concatenation(args)
    except SystemExit as e:
        # Log SystemExit for debugging tests, but don't stop test execution
        print(f"SystemExit caught during test run with code: {e.code}")
    finally:
        # Ensure stdout is restored even if errors occur
        sys.stdout = original_stdout

    return captured_output.getvalue()


# --- Fixtures (Defined at top level of the file) ---


@pytest.fixture
def test_dir(tmp_path: Path) -> Path:
    """Creates a common temporary test directory structure."""
    structure = {
        "file1.py": "print('hello')",
        "file2.txt": "simple text",
        "subdir": {
            "file3.js": "console.log('world');",
            "file4.log": "some log data",  # Included by default now
            "nested": {"file5.py": "# python nested"},
        },
        "other_dir": {
            "file6.css": "body { color: blue; }",
        },
        ".hiddenfile": "secret",
        "binary.bin": b"\x00\x01\x02\x03",  # Use bytes for binary content
        ".git": None,  # Represents an empty .git directory
        ".venv": {"pyvenv.cfg": "config"},  # Represents a virtual env dir
    }
    # Create structure in a subdirectory of tmp_path for clarity
    base_dir = tmp_path / "test_src"
    base_dir.mkdir()
    create_structure(base_dir, structure)
    return base_dir


@pytest.fixture(autouse=True)  # Applied automatically to all tests in this module
def mock_magic(monkeypatch):
    """Mocks the python-magic library functions for consistent testing."""
    target_module = "codeconcat.file_utils"
    # Use the 'magic' variable defined at the module level of this test file
    global magic

    if magic is None:
        # If magic couldn't be imported originally, ensure it's None in file_utils
        monkeypatch.setattr(f"{target_module}.magic", None, raising=False)
    else:
        # Define the mock function behavior
        def mock_from_file(filepath, mime=False):
            p = Path(filepath)
            if p.suffix == ".bin":
                return "application/octet-stream" if mime else "data"
            if p.suffix == ".py":
                return (
                    "text/x-python" if mime else "Python script, ASCII text executable"
                )
            if p.suffix == ".js":
                return (
                    "application/javascript"
                    if mime
                    else "JavaScript source, ASCII text"
                )
            if p.suffix == ".css":
                return "text/css" if mime else "CSS source, ASCII text"
            if p.suffix == ".log":
                return "text/plain" if mime else "ASCII text"
            # Default fallback for other text files
            return "text/plain" if mime else "ASCII text"

        # Patch the 'from_file' function within the mocked magic object
        try:
            # Check if the magic object *actually* exists in file_utils before patching
            if getattr(sys.modules.get(target_module), "magic", None):
                monkeypatch.setattr(f"{target_module}.magic.from_file", mock_from_file)
        except AttributeError:
            pass  # Should not happen if magic is not None, but safe to have


# --- Test Cases ---
# (No changes needed in the test case functions themselves)


def test_basic_concatenation(test_dir: Path, monkeypatch):
    """Test concatenating default text files to stdout."""
    output = run_test_flow([str(test_dir)], monkeypatch)
    print("\n--- Captured Output (Basic) ---")
    print(output)
    print("--- End Captured Output ---")
    assert "--- File: file1.py ---" in output
    assert "--- File: file2.txt ---" in output
    assert "--- File: subdir/file3.js ---" in output
    assert "--- File: subdir/file4.log ---" in output
    assert "--- File: subdir/nested/file5.py ---" in output
    assert "--- File: other_dir/file6.css ---" in output
    assert "--- File: .hiddenfile ---" not in output
    assert "--- File: binary.bin ---" not in output
    assert ".git" not in output
    assert ".venv" not in output


def test_output_to_file(test_dir: Path, tmp_path: Path):
    """Test writing output to a specified file instead of stdout."""
    output_file = tmp_path / "output.txt"
    args = codeconcat_cli.parse_arguments([str(test_dir), str(output_file)])
    try:
        codeconcat_main.run_concatenation(args)
    except SystemExit as e:
        pytest.fail(f"run_concatenation exited unexpectedly with code: {e.code}")
    assert output_file.is_file()
    content = output_file.read_text()
    assert "--- File: file1.py ---" in content
    assert "--- File: subdir/file4.log ---" in content
    assert "console.log('world');" in content


def test_exclude_cli(test_dir: Path, monkeypatch):
    """Test excluding specific file types using CLI --exclude."""
    output = run_test_flow([str(test_dir), "-e", "*.py"], monkeypatch)
    assert "--- File: file1.py ---" not in output
    assert "--- File: subdir/nested/file5.py ---" not in output
    assert "--- File: file2.txt ---" in output
    assert "--- File: subdir/file4.log ---" in output


def test_exclude_directory_cli(test_dir: Path, monkeypatch):
    """Test excluding an entire directory using CLI --exclude."""
    output = run_test_flow([str(test_dir), "-e", "subdir"], monkeypatch)
    assert "--- File: subdir/file3.js ---" not in output
    assert "--- File: subdir/file4.log ---" not in output
    assert "--- File: subdir/nested/file5.py ---" not in output
    assert "--- File: file1.py ---" in output


def test_whitelist_cli(test_dir: Path, monkeypatch):
    """Test including only specific file types using CLI --whitelist."""
    output = run_test_flow([str(test_dir), "-w", "*.js"], monkeypatch)
    assert "--- File: subdir/file3.js ---" in output
    assert "--- File: file1.py ---" not in output
    assert "--- File: file2.txt ---" not in output
    assert "--- File: subdir/file4.log ---" not in output
    assert "--- File: other_dir/file6.css ---" not in output


def test_whitelist_includes_log_files(test_dir: Path, monkeypatch):
    """Test that an explicit whitelist correctly includes files like logs."""
    output = run_test_flow([str(test_dir), "-w", "*.log"], monkeypatch)
    assert "--- File: subdir/file4.log ---" in output
    assert "some log data" in output
    assert "--- File: file1.py ---" not in output
    assert "--- File: file2.txt ---" not in output


def test_config_file_exclude(test_dir: Path, monkeypatch):
    """Test loading and applying exclude patterns from a config file."""
    config_data = {"exclude": ["*.txt", "other_dir"]}
    config_path = test_dir / codeconcat_config.CONFIG_FILE_NAME
    config_path.write_text(json.dumps(config_data))
    output = run_test_flow([str(test_dir)], monkeypatch)
    assert "--- File: file2.txt ---" not in output
    assert "--- File: other_dir/file6.css ---" not in output
    assert "--- File: file1.py ---" in output


def test_config_file_whitelist(test_dir: Path, monkeypatch):
    """Test loading and applying whitelist patterns from a config file."""
    config_data = {"whitelist": ["*.py"]}
    config_path = test_dir / codeconcat_config.CONFIG_FILE_NAME
    config_path.write_text(json.dumps(config_data))
    output = run_test_flow([str(test_dir)], monkeypatch)
    assert "--- File: file1.py ---" in output
    assert "--- File: subdir/nested/file5.py ---" in output
    assert "--- File: file2.txt ---" not in output
    assert "--- File: subdir/file3.js ---" not in output
    assert "--- File: subdir/file4.log ---" not in output


def test_cli_overrides_config(test_dir: Path, monkeypatch):
    """Test that CLI whitelist/exclude args override config file settings."""
    config_data = {"exclude": ["*.txt"], "whitelist": ["*.js"]}
    config_path = test_dir / codeconcat_config.CONFIG_FILE_NAME
    config_path.write_text(json.dumps(config_data))
    output = run_test_flow([str(test_dir), "-e", "*.py", "-w", "*.css"], monkeypatch)
    assert "--- File: file1.py ---" not in output
    assert "--- File: other_dir/file6.css ---" in output
    assert "--- File: file2.txt ---" not in output
    assert "--- File: subdir/file3.js ---" not in output
    assert "--- File: subdir/file4.log ---" not in output


def test_gitignore_basic(test_dir: Path, monkeypatch):
    """Test excluding files based on patterns in a root .gitignore file."""
    gitignore_content = "*.txt\nsubdir/file3.js\n*.log\n"
    (test_dir / ".gitignore").write_text(gitignore_content)
    output = run_test_flow([str(test_dir)], monkeypatch)
    assert "--- File: file2.txt ---" not in output
    assert "--- File: subdir/file3.js ---" not in output
    assert "--- File: subdir/file4.log ---" not in output
    assert "--- File: file1.py ---" in output


def test_gitignore_in_subdir(test_dir: Path, monkeypatch):
    """Test behavior with .gitignore in a subdirectory (simple model)."""
    gitignore_content_subdir = "nested/file5.py\n"
    (test_dir / "subdir" / ".gitignore").write_text(gitignore_content_subdir)
    output_subdir = run_test_flow([str(test_dir)], monkeypatch)
    assert (
        "--- File: subdir/nested/file5.py ---" in output_subdir
    )  # Simple model includes

    gitignore_content_root = "subdir/nested/file5.py\n"
    (test_dir / ".gitignore").write_text(gitignore_content_root)
    (test_dir / "subdir" / ".gitignore").unlink(missing_ok=True)
    output_root = run_test_flow([str(test_dir)], monkeypatch)
    assert "--- File: subdir/nested/file5.py ---" not in output_root  # Root excludes


def test_no_gitignore_option(test_dir: Path, monkeypatch):
    """Test that --no-gitignore flag disables .gitignore processing."""
    gitignore_content = "*.txt\n*.py"
    (test_dir / ".gitignore").write_text(gitignore_content)
    output = run_test_flow([str(test_dir), "--no-gitignore"], monkeypatch)
    assert "--- File: file1.py ---" in output
    assert "--- File: file2.txt ---" in output
    assert "--- File: subdir/nested/file5.py ---" in output
    assert "--- File: subdir/file4.log ---" in output


def test_empty_directory(tmp_path: Path, monkeypatch):
    """Test behavior when the source directory is empty."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    output = run_test_flow([str(empty_dir)], monkeypatch)
    assert output == ""


def test_no_matching_files(test_dir: Path, monkeypatch):
    """Test behavior when whitelist patterns match no files."""
    output = run_test_flow([str(test_dir), "-w", "*.nonexistent"], monkeypatch)
    assert output == ""


def test_verbose_logging(test_dir: Path, caplog):
    """Test that the -v/--verbose flag enables DEBUG level logging."""
    caplog.set_level(logging.DEBUG)
    run_test_flow([str(test_dir), "-v"])
    debug_logs_found = any(record.levelno == logging.DEBUG for record in caplog.records)
    assert debug_logs_found, "No DEBUG messages found in logs when -v was used."
    assert "Verbose logging enabled." in caplog.text
    assert "Final combined exclude patterns:" in caplog.text


def test_nonexistent_source(tmp_path: Path):
    """Test that the program exits cleanly when the source path doesn't exist."""
    non_existent_path = tmp_path / "does_not_exist"
    args_list = [str(non_existent_path)]
    args = codeconcat_cli.parse_arguments(args_list)
    with pytest.raises(SystemExit) as excinfo:
        codeconcat_main.run_concatenation(args)
    assert excinfo.value.code != 0


def test_output_is_directory(test_dir: Path, tmp_path: Path):
    """Test that the program exits cleanly if the output path is a directory."""
    output_dir = tmp_path / "output_dir_exists"
    output_dir.mkdir()
    args_list = [str(test_dir), str(output_dir)]
    args = codeconcat_cli.parse_arguments(args_list)
    with pytest.raises(SystemExit) as excinfo:
        codeconcat_main.run_concatenation(args)
    assert excinfo.value.code != 0
