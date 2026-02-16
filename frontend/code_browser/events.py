from __future__ import annotations

from textual import events
from textual.widgets import DirectoryTree, Input, TextArea
from textual.widgets.text_area import Selection


class EventsMixin:
    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        if self.path is not None:
            self.buffers[self.path] = self.query_one("#code-editor", TextArea).text
        self.path = str(event.path)

    def on_text_area_selection_changed(self, event: TextArea.SelectionChanged) -> None:
        """Keep TextArea native selection in sync while visual mode is enabled."""
        if event.text_area.id != "code-editor":
            return
        if self._syncing_selection:
            return
        if not self.selection_mode or self._selection_anchor is None:
            return

        desired = Selection(self._selection_anchor, event.selection.end)
        if event.selection == desired:
            return

        self._syncing_selection = True
        event.text_area.selection = desired
        self._syncing_selection = False

    def on_key(self, event: events.Key) -> None:
        """Fallback for Escape when focused widgets consume key bindings."""
        if event.key == "c" and not self.request_mode:
            event.stop()
            self.action_toggle_request()
            return
        if event.key == "escape" and self.request_mode:
            event.stop()
            self.request_mode = False
            return
        if event.key == "escape" and self.insert_mode:
            event.stop()
            self.action_exit_insert()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Generate code from Gemini and insert it at cursor location."""
        if event.input.id != "request-input":
            return
        request_text = event.value.strip()
        if not request_text:
            self.sub_title = "EMPTY REQUEST"
            return
        if self.path is None:
            self.sub_title = "NO FILE OPEN"
            self.request_mode = False
            return

        gaggle = self._get_gaggle()
        if gaggle is None:
            self.request_mode = False
            return

        self.sub_title = "GENERATING..."
        language = self._resolved_language_for_path(self.path)
        prompt = self._build_code_prompt(request_text)
        try:
            generated = gaggle.generate_response(prompt, language=language)
        except Exception as error:
            message = str(error).strip() or type(error).__name__
            self.sub_title = f"GEN FAIL: {message[:60]}"
            self.request_mode = False
            return
        if not generated:
            self.sub_title = "EMPTY RESPONSE"
            self.request_mode = False
            return

        code_view = self.query_one("#code-editor", TextArea)
        if self._request_insert_location is not None:
            code_view.cursor_location = self._request_insert_location
        was_insert_mode = self.insert_mode
        if not was_insert_mode:
            code_view.read_only = False
        code_view.insert(generated)
        if not was_insert_mode:
            code_view.read_only = True
        if self.path is not None:
            current_text = code_view.text
            self.buffers[self.path] = current_text
            self._apply_editor_language(self.path, current_text)
            if current_text == self.saved_buffers.get(self.path, ""):
                self.dirty_buffers.discard(self.path)
            else:
                self.dirty_buffers.add(self.path)
        self.request_mode = False
        self.sub_title = "CODE INSERTED"

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Track unsaved changes for the active file while in insert mode."""
        if event.text_area.id != "code-editor":
            return
        if self._loading_buffer:
            return
        if not self.insert_mode or self.path is None:
            return
        new_text = event.text_area.text
        self.buffers[self.path] = new_text
        self._apply_editor_language(self.path, new_text)
        if new_text == self.saved_buffers.get(self.path, ""):
            self.dirty_buffers.discard(self.path)
        else:
            self.dirty_buffers.add(self.path)
