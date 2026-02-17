from __future__ import annotations

from pathlib import Path

from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
from textual.widgets import TextArea
from textual.widgets.text_area import LanguageDoesNotExist

from bot.gaggle import Gaggle


class LanguageMixin:
    def _register_optional_languages(self) -> None:
        code_view = self.query_one("#code-editor", TextArea)
        if "c" in code_view.available_languages:
            return

        try:
            from tree_sitter import Language
            import tree_sitter_c

            code_view.register_language(
                "c",
                Language(tree_sitter_c.language()),
                tree_sitter_c.HIGHLIGHTS_QUERY,
            )
        except Exception:
            return

    @staticmethod
    def _language_from_path(path: str) -> str | None:
        suffix = Path(path).suffix.lower()
        return {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".jsx": "jsx",
            ".json": "json",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".tcss": "css",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".toml": "toml",
            ".sh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".sql": "sql",
            ".xml": "xml",
        }.get(suffix)

    @staticmethod
    def _textual_language_from_pygments_alias(alias: str) -> str | None:
        return {
            "py": "python",
            "python": "python",
            "js": "javascript",
            "javascript": "javascript",
            "ts": "typescript",
            "typescript": "typescript",
            "tsx": "tsx",
            "jsx": "jsx",
            "json": "json",
            "md": "markdown",
            "markdown": "markdown",
            "html": "html",
            "css": "css",
            "yaml": "yaml",
            "yml": "yaml",
            "toml": "toml",
            "bash": "bash",
            "sh": "bash",
            "zsh": "bash",
            "rust": "rust",
            "go": "go",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "c++": "cpp",
            "csharp": "csharp",
            "cs": "csharp",
            "php": "php",
            "ruby": "ruby",
            "rb": "ruby",
            "sql": "sql",
            "xml": "xml",
        }.get(alias)

    def _language_from_content(self, code: str) -> str | None:
        if not code.strip():
            return None
        try:
            lexer = guess_lexer(code)
        except ClassNotFound:
            return None
        aliases = getattr(lexer, "aliases", [])
        for alias in aliases:
            mapped = self._textual_language_from_pygments_alias(alias)
            if mapped is not None:
                return mapped
        return None

    def _language_for_code(self, path: str, code: str) -> str | None:
        by_path = self._language_from_path(path)
        if by_path is not None:
            return by_path
        return self._language_from_content(code)

    def _apply_editor_language(self, path: str | None, code: str) -> None:
        if path is None:
            return
        language = self._language_for_code(path, code)
        code_view = self.query_one("#code-editor", TextArea)
        if hasattr(code_view, "language"):
            if code_view.language == language:
                return
            try:
                code_view.language = language
            except LanguageDoesNotExist:
                code_view.language = None

    def _build_code_prompt(self, request_text: str) -> str:
        language = self._resolved_language_for_path(self.path)
        return (
            f"Generate only {language} code. "
            "Return plain code text only. "
            f"Request: {request_text}"
        )

    def _resolved_language_for_path(self, path: str | None) -> str:
        if not path:
            return "text"
        mapped_language = self._language_from_path(path)
        if mapped_language is not None:
            return mapped_language
        suffix = Path(path).suffix.lower().lstrip(".")
        return suffix or "text"

    def _get_gaggle(self) -> Gaggle | None:
        if self._gaggle is not None:
            return self._gaggle
        try:
            self._gaggle = Gaggle()
        except ValueError:
            self.sub_title = "MISSING GEMINI_API_KEY"
            return None
        return self._gaggle
