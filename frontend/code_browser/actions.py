from __future__ import annotations

from pathlib import Path

from textual.highlight import highlight
from textual.widgets import Static, TextArea
from textual.widgets.text_area import Selection


class ActionsMixin:
    @staticmethod
    def _cursor_to_index(text: str, cursor: tuple[int, int]) -> int:
        lines = text.split("\n")
        if not lines:
            return 0
        row, col = cursor
        row = max(0, min(row, len(lines) - 1))
        col = max(0, min(col, len(lines[row])))
        return sum(len(lines[line_index]) + 1 for line_index in range(row)) + col

    @staticmethod
    def _index_to_cursor(text: str, index: int) -> tuple[int, int]:
        index = max(0, min(index, len(text)))
        prefix = text[:index]
        row = prefix.count("\n")
        last_newline = prefix.rfind("\n")
        if last_newline == -1:
            col = len(prefix)
        else:
            col = len(prefix) - last_newline - 1
        return row, col

    def _selection_span(self) -> tuple[int, int] | None:
        if not self.selection_mode or self._selection_anchor is None or self.path is None:
            return None
        code_view = self.query_one("#code-editor", TextArea)
        text = code_view.text
        start = self._cursor_to_index(text, code_view.selection.start)
        end = self._cursor_to_index(text, code_view.selection.end)
        if start == end:
            return None
        if start > end:
            start, end = end, start
        return start, end

    def _sync_active_buffer_from_editor(self) -> None:
        if self.path is None:
            return
        code_view = self.query_one("#code-editor", TextArea)
        current_text = code_view.text
        self.buffers[self.path] = current_text
        self._apply_editor_language(self.path, current_text)
        if current_text == self.saved_buffers.get(self.path, ""):
            self.dirty_buffers.discard(self.path)
        else:
            self.dirty_buffers.add(self.path)
        self.query_one("#code-static", Static).update(highlight(current_text, path=self.path))

    def _replace_editor_text(self, text: str, cursor: tuple[int, int]) -> None:
        code_view = self.query_one("#code-editor", TextArea)
        was_read_only = code_view.read_only
        if was_read_only:
            code_view.read_only = False
        self._loading_buffer = True
        code_view.text = text
        self._loading_buffer = False
        code_view.cursor_location = cursor
        if was_read_only:
            code_view.read_only = True
        self._sync_active_buffer_from_editor()

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    def action_toggle_insert(self) -> None:
        """Called in response to key binding."""
        if self.request_mode:
            return
        if not self.insert_mode and self.path is None:
            self.sub_title = "NO FILE OPEN"
            return
        self.insert_mode = not self.insert_mode

    def action_toggle_request(self) -> None:
        """Show/hide request input for Gemini code generation."""
        if self.request_mode:
            self.request_mode = False
            return
        if self.path is None:
            self.sub_title = "OPEN A FILE FIRST"
            return
        code_view = self.query_one("#code-editor", TextArea)
        self._request_insert_location = code_view.cursor_location
        self.request_mode = True

    def action_toggle_selection(self) -> None:
        """Toggle visual selection anchored at current cursor location."""
        if self.path is None or self.request_mode or self.insert_mode:
            return
        if self.selection_mode:
            self.selection_mode = False
            self.sub_title = "SELECTION CLEARED"
            return
        code_view = self.query_one("#code-editor", TextArea)
        self._selection_anchor = code_view.cursor_location
        code_view.selection = Selection.cursor(code_view.cursor_location)
        self.selection_mode = True
        self.sub_title = "SELECTION ON"

    def action_yank_selection(self) -> None:
        """Copy selected text into yank buffer."""
        if self.path is None or self.request_mode or self.insert_mode:
            return
        span = self._selection_span()
        if span is None:
            self.sub_title = "NO SELECTION"
            return
        code_view = self.query_one("#code-editor", TextArea)
        self._yank_buffer = code_view.selected_text
        self.selection_mode = False
        self.sub_title = "YANKED"

    def action_paste_yank(self) -> None:
        """Paste yanked text at the current cursor location."""
        if self.path is None or self.request_mode or self.insert_mode:
            return
        if not self._yank_buffer:
            self.sub_title = "YANK BUFFER EMPTY"
            return
        code_view = self.query_one("#code-editor", TextArea)
        current_text = code_view.text
        cursor_index = self._cursor_to_index(current_text, code_view.cursor_location)
        new_text = (
            current_text[:cursor_index] + self._yank_buffer + current_text[cursor_index:]
        )
        new_cursor = self._index_to_cursor(new_text, cursor_index + len(self._yank_buffer))
        self._replace_editor_text(new_text, new_cursor)
        self.selection_mode = False
        self.sub_title = "PASTED"

    def action_delete_selection(self) -> None:
        """Delete current selected text."""
        if self.path is None or self.request_mode or self.insert_mode:
            return
        span = self._selection_span()
        if span is None:
            self.sub_title = "NO SELECTION"
            return
        code_view = self.query_one("#code-editor", TextArea)
        code_view.replace("", code_view.selection.start, code_view.selection.end)
        self._sync_active_buffer_from_editor()
        self.selection_mode = False
        self.sub_title = "DELETED"

    def action_exit_insert(self) -> None:
        """Exit insert mode with Escape."""
        if self.request_mode:
            self.request_mode = False
            return
        if self.insert_mode:
            self.action_toggle_insert()

    def action_save_all(self) -> None:
        """Save all dirty file buffers to disk when not in insert mode."""
        if self.insert_mode:
            return
        if not self.dirty_buffers:
            self.sub_title = "NO CHANGES"
            return

        failed: list[str] = []
        for file_path in list(self.dirty_buffers):
            buffer_text = self.buffers.get(file_path)
            if buffer_text is None:
                continue
            try:
                Path(file_path).write_text(buffer_text, encoding="utf-8")
            except Exception:
                failed.append(file_path)
            else:
                self.saved_buffers[file_path] = buffer_text
                self.dirty_buffers.discard(file_path)

        if self.path is not None and self.path in self.buffers:
            self.query_one("#code-static", Static).update(
                highlight(self.buffers[self.path], path=self.path)
            )

        if failed:
            self.sub_title = f"FAILED TO SAVE: {len(failed)}"
        else:
            self.sub_title = "SAVED ALL"
