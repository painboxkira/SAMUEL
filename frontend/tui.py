"""Textual TUI entrypoint for the code browser.

Run with:

    python tui.py PATH
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_browser import CodeBrowser


if __name__ == "__main__":
    CodeBrowser().run()
