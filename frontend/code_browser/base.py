from __future__ import annotations

import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive, var
from textual.widgets import DirectoryTree, Footer, Header, Input, Static, TextArea


class CodeBrowserBase(App):
    """Textual code browser app."""

    CSS_PATH = "code_browser.tcss"
    BINDINGS = [
        Binding("f", "toggle_files", "Toggle Files"),
        Binding("c", "toggle_request", "Code Request", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("i", "toggle_insert", "Toggle Insert Mode"),
        Binding("v", "toggle_selection", "Toggle Selection"),
        Binding("y", "yank_selection", "Yank Selection"),
        Binding("p", "paste_yank", "Paste Yank"),
        Binding("d", "delete_selection", "Delete Selection"),
        Binding("s", "save_all", "Save All"),
        Binding("escape", "exit_insert", "Exit Insert Mode", priority=True),
    ]

    show_tree = var(True)
    insert_mode = var(False)
    request_mode = var(False)
    selection_mode = var(False)
    path: reactive[str | None] = reactive(None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.buffers: dict[str, str] = {}
        self.saved_buffers: dict[str, str] = {}
        self.dirty_buffers: set[str] = set()
        self._loading_buffer = False
        self._request_insert_location: tuple[int, int] | None = None
        self._gaggle = None
        self._selection_anchor: tuple[int, int] | None = None
        self._yank_buffer = ""
        self._syncing_selection = False

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header()
        with Container():
            yield DirectoryTree(path, id="tree-view")
            yield Static(id="code-static", expand=True)
            yield TextArea.code_editor(id="code-editor", read_only=True)
        with Container(id="request-panel"):
            yield Static("Describe the code to generate:", id="request-label")
            yield Input(placeholder="Ask for code...", id="request-input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

        def theme_change(_signal) -> None:
            """Force the syntax to use a different theme."""
            self.watch_path(self.path)

        self.theme_changed_signal.subscribe(self, theme_change)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Enable/disable actions based on current mode and state."""
        if action == "quit":
            return not self.insert_mode
        if action == "exit_insert":
            return self.insert_mode
        if action == "save_all":
            return not self.insert_mode
        if action == "toggle_insert":
            return self.path is not None or self.insert_mode
        if action in {
            "toggle_selection",
            "yank_selection",
            "paste_yank",
            "delete_selection",
        }:
            return self.path is not None and not self.insert_mode and not self.request_mode
        return None
