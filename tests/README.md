# Testing Strategy

This directory contains the test suite for `codeconcat`. We follow a multi-layer verification strategy.

## Test Files

*   **`test_full_surface.py`**: The primary integration test suite.
    *   Creates a real temporary filesystem structure (files, directories, .gitignore).
    *   Verifies `generate_directory_tree` logic against real files.
    *   Tests the **Additive** nature of "Force Include" (ensuring `.env` files are captured when requested).
    *   Tests the ASCII tree generation.
    *   Mocks the `wizard` to ensure it passes correct configuration dictionaries.

*   **`test_main.py`**: Unit tests for argument parsing and main execution flow.
*   **`verify_fence.py`**: A specialized verification script for the "Safe Fencing" logic, ensuring markdown code blocks are properly escaped.

## Running Tests

We use `pytest` for all testing.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_full_surface.py
```
