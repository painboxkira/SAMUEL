"""Textual TUI entrypoint for the code browser.

Run with:

    python tui.py [PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _directory_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.exists() or not path.is_dir():
        raise argparse.ArgumentTypeError(f"Not a directory: {value}")
    return path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the code browser TUI.")
    parser.add_argument(
        "path",
        nargs="?",
        type=_directory_path,
        default=Path.cwd(),
        help="Directory to open (defaults to the current working directory).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    from code_browser import CodeBrowser

    CodeBrowser(root_path=args.path).run()
