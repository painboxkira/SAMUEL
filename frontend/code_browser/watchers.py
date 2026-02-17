from __future__ import annotations

from pathlib import Path

from rich.traceback import Traceback
from textual.highlight import highlight
from textual.widgets import Input, Static, Tabs, TextArea
from textual.widgets.text_area import Selection

from .widgets import path_to_tab_id


class WatchersMixin:
    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def watch_insert_mode(self, insert_mode: bool) -> None:
        """Called when insert_mode is modified."""
        self.set_class(insert_mode, "-insert-mode")
        code_view = self.query_one("#code-editor", TextArea)
        code_view.read_only = not insert_mode
        if insert_mode:
            code_view.focus()
        else:
            if self.path is not None:
                current_text = code_view.text
                self.buffers[self.path] = current_text
                self.query_one("#code-static", Static).update(
                    highlight(current_text, path=self.path)
                )
            code_view.focus()

    def watch_request_mode(self, request_mode: bool) -> None:
        """Called when request_mode is modified."""
        self.set_class(request_mode, "-request-mode")
        request_input = self.query_one("#request-input", Input)
        if request_mode:
            request_input.focus()
        else:
            request_input.value = ""
            self.query_one("#code-editor", TextArea).focus()

    def watch_selection_mode(self, selection_mode: bool) -> None:
        """Called when selection mode is modified."""
        self.set_class(selection_mode, "-selection-mode")
        code_view = self.query_one("#code-editor", TextArea)
        if selection_mode:
            anchor = self._selection_anchor or code_view.cursor_location
            code_view.selection = Selection(anchor, code_view.cursor_location)
        else:
            code_view.selection = Selection.cursor(code_view.cursor_location)
            self._selection_anchor = None

    def watch_path(self, path: str | None) -> None:
        """Called when path changes."""
        self.selection_mode = False
        code_view = self.query_one("#code-editor", TextArea)
        static_view = self.query_one("#code-static", Static)
        if path is None:
            self._loading_buffer = True
            code_view.text = ""
            self._loading_buffer = False
            static_view.update("")
            return

        if path in self.buffers:
            code = self.buffers[path]
        else:
            try:
                code = Path(path).read_text(encoding="utf-8")
            except Exception:
                self._loading_buffer = True
                code_view.text = "Unable to read file"
                self._loading_buffer = False
                static_view.update(Traceback(theme="github-dark", width=None))
                self.sub_title = "ERROR"
                return
            self.buffers[path] = code
            self.saved_buffers[path] = code

        self._loading_buffer = True
        code_view.text = code
        self._loading_buffer = False
        static_view.update(highlight(code, path=path))
        self._apply_editor_language(path, code)
        saved_cursor = self.cursor_positions.get(path, (0, 0))
        code_view.cursor_location = saved_cursor
        if path not in self.cursor_positions:
            code_view.scroll_home(animate=False)
        code_view.focus()
        self.sub_title = path

        # Activate the corresponding tab
        tab_id = path_to_tab_id(path)
        try:
            tabs = self.query_one("#file-tabs", Tabs)
            if tabs.active != tab_id:
                self._switching_tab = True
                try:
                    tabs.active = tab_id
                finally:
                    self._switching_tab = False
        except Exception:
            pass
