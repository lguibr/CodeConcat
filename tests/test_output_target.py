# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from unittest.mock import patch
from codeconcat.main import determine_output_target

def test_determine_output_target_explicit():
    """Test when explicit output is provided."""
    # We mock logging to avoid errors during tests if logging is not fully initialized
    with patch("codeconcat.main.logger"):
        output, to_stdout = determine_output_target("source", "explicit.md", False)
        assert output == "explicit.md"
        assert to_stdout is False

def test_determine_output_target_force_stdout():
    """Test when force_stdout flag is set."""
    with patch("codeconcat.main.logger"):
        output, to_stdout = determine_output_target("source", None, True)
        assert output is None
        assert to_stdout is True

def test_determine_output_target_tty_fallback():
    """Test fallback to file when in a TTY."""
    with patch("sys.stdout.isatty", return_value=True), \
         patch("codeconcat.main.logger"):
        output, to_stdout = determine_output_target("my_project", None, False)
        # my_project is relative, so it should be resolved
        expected_name = f"{Path('my_project').resolve().name}.md"
        assert output == expected_name
        assert to_stdout is False

def test_determine_output_target_non_tty_fallback():
    """Test fallback to stdout when not in a TTY (piped)."""
    with patch("sys.stdout.isatty", return_value=False), \
         patch("codeconcat.main.logger"):
        output, to_stdout = determine_output_target("source", None, False)
        assert output is None
        assert to_stdout is True

def test_determine_output_target_root_fallback():
    """Test fallback when source path name is empty (e.g. root)."""
    with patch("sys.stdout.isatty", return_value=True), \
         patch("codeconcat.main.logger"):
        # On Linux/macOS, Path("/").name is ""
        output, to_stdout = determine_output_target("/", None, False)
        assert output == "codebase.md"
        assert to_stdout is False
