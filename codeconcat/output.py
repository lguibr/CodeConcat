# -*- coding: utf-8 -*-
# codeconcat/output.py
import logging
import sys
from pathlib import Path
from typing import List, Optional, TextIO, Tuple, Union

logger = logging.getLogger(__name__)


def _open_output_stream(output_path: Optional[Path]) -> Union[TextIO, None]:
    """Opens the appropriate output stream (file or stdout)."""
    if output_path:
        try:
            return open(output_path, "w", encoding="utf-8", errors="replace")
        except OSError as e:
            logger.error(f"Failed to open output file {output_path}: {e}")
            return None
    else:
        # Ensure stdout uses replace for errors if possible
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(errors="replace")
            except Exception:  # pragma: no cover
                logger.debug("Could not reconfigure stdout error handling.")
        return sys.stdout


def _write_file_content(output_stream: TextIO, file_path: Path, src_path: Path) -> bool:
    """
    Reads a single file and writes its content to the stream.
    Returns True on success.
    """
    try:
        if not file_path.is_file():
            logger.warning(f"File disappeared before reading: {file_path}")
            return False

        with file_path.open("r", encoding="utf-8", errors="replace") as infile:
            content = infile.read()

        relative_path = file_path.relative_to(src_path)
        header_path = str(relative_path.as_posix())
        output_stream.write(f"--- File: {header_path} ---\n")
        output_stream.write(content)
        if not content.endswith("\n"):
            output_stream.write("\n")
        output_stream.write("\n\n")
        return True
    except OSError as e:
        logger.warning(
            f"Skipping file due to OS error: {file_path.relative_to(src_path)} ({e})"
        )
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error processing file {file_path.relative_to(src_path)}: {e}"
        )
        return False


def create_output(
    files: List[Path], src_path: Path, output_path: Optional[Path]
) -> Tuple[int, int]:
    """
    Writes the content of the collected files to the output destination.
    """
    output_stream = _open_output_stream(output_path)
    if output_stream is None:  # Handle case where file couldn't be opened
        return 0, len(files)

    written_files = 0
    skipped_files = 0

    try:
        for file_path in files:
            if _write_file_content(output_stream, file_path, src_path):
                written_files += 1
            else:
                skipped_files += 1
    finally:
        # Close the file stream only if it's not stdout
        if output_path and output_stream is not sys.stdout:
            if not output_stream.closed:
                output_stream.close()
            logger.info(f"Concatenated {written_files} files into {output_path}.")
        elif output_path is None:  # Log counts to stderr when using stdout
            logger.info(f"Concatenated {written_files} files to stdout.")

        if skipped_files > 0:
            logger.warning(f"Skipped {skipped_files} files due to errors.")

    return written_files, skipped_files
