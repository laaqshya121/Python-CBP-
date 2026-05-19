"""Bridge asyncio coroutines to Qt event loop."""

import asyncio
from typing import Awaitable, Callable, Optional

from PySide6.QtCore import QObject, QTimer


class AsyncBridge(QObject):
    """Runs async simulation tasks without blocking the UI."""

    def __init__(self, interval_ms: int, coro_factory: Callable[[], Awaitable[None]], parent=None) -> None:
        super().__init__(parent)
        self._coro_factory = coro_factory
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._dispatch)
        self._running = False

    def start(self) -> None:
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._running = True
        self._timer.start()

    def stop(self) -> None:
        self._running = False
        self._timer.stop()

    def _dispatch(self) -> None:
        if not self._running or self._loop is None:
            return
        task = self._coro_factory()
        if asyncio.iscoroutine(task):
            asyncio.ensure_future(task, loop=self._loop)
