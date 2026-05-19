"""AI Chat tab — typing animation + live engine integration."""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from smartvenue_ai.ai_chat import StadiumAI
from smartvenue_ai.config import COLORS
from smartvenue_ai.styles import neon_button_qss, title_qss


class AIChatWidget(QFrame):
    def __init__(self, ai: StadiumAI) -> None:
        super().__init__()
        self._ai = ai
        self._typing_timer: QTimer | None = None
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.addWidget(self._mk_label("Stadium AI Assistant", title_qss(16)))

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._msgs = QWidget()
        self._msg_lay = QVBoxLayout(self._msgs)
        self._msg_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._msgs)
        root.addWidget(self._scroll, 1)

        self._msg_lay.addWidget(self._bubble(
            "SmartVenue AI connected to live congestion, navigation, and queue engines.",
            ai=True,
        ))

        row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask about restrooms, exits, routes, queues…")
        send = QPushButton("Send →")
        send.setStyleSheet(neon_button_qss())
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.clicked.connect(self._on_send)
        self._input.returnPressed.connect(self._on_send)
        row.addWidget(self._input, 1)
        row.addWidget(send)
        root.addLayout(row)

    @staticmethod
    def _mk_label(text: str, style: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(style)
        return lb

    def _bubble(self, text: str, ai: bool = False) -> QLabel:
        lb = QLabel(text)
        lb.setWordWrap(True)
        lb.setMaximumWidth(580)
        if ai:
            lb.setStyleSheet(
                f"background: rgba(0,207,255,0.12); color: {COLORS['text']};"
                f"border: 1px solid {COLORS['cyan']}; border-radius: 12px; padding: 10px 14px;"
            )
        else:
            lb.setStyleSheet(
                f"background: {COLORS['panel_light']}; color: {COLORS['text']};"
                f"border-radius: 12px; padding: 10px 14px;"
            )
        return lb

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._msg_lay.addWidget(self._bubble(text, ai=False))
        reply = self._ai.respond(text)
        self._type_reply(reply)

    def _type_reply(self, full: str) -> None:
        container = QLabel("")
        container.setWordWrap(True)
        container.setMaximumWidth(580)
        container.setStyleSheet(
            f"background: rgba(0,207,255,0.12); color: {COLORS['text']};"
            f"border: 1px solid {COLORS['cyan']}; border-radius: 12px; padding: 10px 14px;"
        )
        self._msg_lay.addWidget(container)
        idx = [0]

        def tick() -> None:
            idx[0] += 2
            container.setText(full[: idx[0]])
            if idx[0] >= len(full) and self._typing_timer:
                self._typing_timer.stop()
            self._scroll.verticalScrollBar().setValue(self._scroll.verticalScrollBar().maximum())

        if self._typing_timer:
            self._typing_timer.stop()
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(tick)
        self._typing_timer.start(16)
