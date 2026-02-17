"""Reusable widgets for the code browser (tabs, modals)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Tab


def path_to_tab_id(path: str) -> str:
    """Convert a file path into a valid CSS widget ID."""
    return "ftab-" + hashlib.md5(path.encode()).hexdigest()[:12]


class ConfirmSaveScreen(ModalScreen[str]):
    """Modal dialog asking the user to save, discard, or cancel."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ConfirmSaveScreen {
        align: center middle;
    }
    #confirm-dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        background: #1b0a11;
        border: round #ff2a5a;
    }
    #confirm-message {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
        color: #ffd9e2;
    }
    #confirm-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    #confirm-buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str = "You have unsaved changes."):
        super().__init__()
        self._message = message

    def compose(self):
        with Vertical(id="confirm-dialog"):
            yield Label(self._message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Discard", variant="warning", id="btn-discard")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id.replace("btn-", ""))

    def action_cancel(self):
        self.dismiss("cancel")


class FileTab(Tab):
    """A Tab subclass that remembers the file path it represents."""

    def __init__(self, file_path: str, dirty: bool = False):
        name = Path(file_path).name
        prefix = "● " if dirty else ""
        super().__init__(f"{prefix}{name}", id=path_to_tab_id(file_path))
        self.file_path = file_path
