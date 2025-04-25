# -*- coding: utf-8 -*-
# codeconcat/output.py
import logging
import sys
from pathlib import Path
from typing import List, Optional, TextIO

logger = logging.getLogger(__name__)


def create_output(
    output_path_str: Optional[str],
    src_path_str: str,
    tree: List[str],
    to_stdout: bool = False,
) -> None:
    """Writes the content of the files in the tree to the output, wrapping content."""
    output_stream: Optional[TextIO] = None
    src_path = Path(src_path_str).resolve()

    try:
        if to_stdout:
            output_stream = sys.stdout
        elif output_path_str:
            output_path = Path(output_path_str)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_stream = open(output_path, "w", encoding="utf-8")
        else:
            logger.error("Output target not specified (file path or --stdout).")
            return

        if not tree:
            return

        for file_path_str in tree:
            file_path = Path(file_path_str)
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    content = file.read()
            except UnicodeDecodeError:
                logger.warning(f"Skipping file {file_path_str} due to unhandled encoding issue.")
                continue
            except OSError as e:
                logger.warning(f"Skipping file {file_path_str} due to read error: {e}")
                continue
            except Exception as e:
                logger.warning(f"Skipping file {file_path_str} due to unexpected error: {e}")
                continue

            try:
                relative_path = file_path.relative_to(src_path)
            except ValueError:
                relative_path = file_path

            # --- Write Output with New Formatting ---
            output_stream.write(f"File: {relative_path.as_posix()}\n")
            output_stream.write('""""""\n')
            output_stream.write(content)
            # Ensure newline before closing marker
            if not content.endswith("\n"):
                output_stream.write("\n")
            output_stream.write('""""""\n')
            output_stream.write("\n\n")
            # --- End of Formatting Change ---

        logger.info(f"Successfully wrote {len(tree)} files to {'stdout' if to_stdout else output_path_str}")

    except OSError as e:
        logger.error(f"Error writing to output {'stdout' if to_stdout else output_path_str}. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during output generation: {e}")
    finally:
        if not to_stdout and output_stream and not output_stream.closed:
            output_stream.close()
