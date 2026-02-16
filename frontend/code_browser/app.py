from __future__ import annotations

from .actions import ActionsMixin
from .base import CodeBrowserBase
from .events import EventsMixin
from .language import LanguageMixin
from .watchers import WatchersMixin


class CodeBrowser(
    EventsMixin,
    ActionsMixin,
    WatchersMixin,
    LanguageMixin,
    CodeBrowserBase,
):
    pass
