"""Scrollable right-side congestion feed."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from smartvenue_ai.config import COLORS
from smartvenue_ai.styles import title_qss


class CongestionCard(QFrame):
    def __init__(self, gate: str, wait: int, entrance: str, level: str) -> None:
        super().__init__()
        self._gate = gate
        colors = {"low": COLORS["green"], "medium": COLORS["yellow"], "high": COLORS["red"]}
        self._badge_color = colors.get(level, COLORS["cyan"])
        self._set_border(False)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(COLORS["border"]))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        top = QLabel(f"<span style='font-size:14px'><b>{gate}</b></span>"
                     f" <span style='color:{self._badge_color};font-weight:700'>{wait} min</span>")
        top.setStyleSheet("background: transparent;")
        sub = QLabel(entrance)
        sub.setStyleSheet(f"color: #b8cfe8; font-size: 12px; font-weight: 500; background: transparent;")
        badge = QLabel(level.upper())
        badge.setStyleSheet(
            f"color: {self._badge_color}; font-size: 11px; font-weight: 800; background: transparent;"
        )
        lay.addWidget(top)
        lay.addWidget(sub)
        lay.addWidget(badge)

    def _set_border(self, selected: bool) -> None:
        border = COLORS["cyan"] if selected else COLORS["border"]
        w = 2 if selected else 1
        self.setStyleSheet(
            f"CongestionCard {{ background: {COLORS['panel']}; border: {w}px solid {border}; border-radius: 12px; }}"
        )

    def set_selected(self, on: bool) -> None:
        self._set_border(on)
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setColor(QColor(COLORS["cyan"] if on else COLORS["border"]))


class CongestionPanel(QFrame):
    card_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(290)
        self.setStyleSheet("background: transparent; border: none;")
        root = QVBoxLayout(self)
        title = QLabel("Congestion Feed")
        title.setStyleSheet(title_qss(16) + " padding-bottom: 4px;")
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._lay = QVBoxLayout(self._inner)
        self._lay.setSpacing(10)
        self._lay.setContentsMargins(2, 4, 6, 4)
        scroll.setWidget(self._inner)
        root.addWidget(scroll, 1)
        self._cards: list[CongestionCard] = []

    def set_data(self, rows: list) -> None:
        while self._lay.count():
            w = self._lay.takeAt(0).widget()
            if w:
                w.deleteLater()
        self._cards.clear()
        for i, row in enumerate(rows):
            card = CongestionCard(row[0], row[1], row[2], row[3])
            gate = row[0]
            card.mousePressEvent = lambda e, g=gate, ix=i: self._pick(g, ix)
            self._lay.addWidget(card)
            self._cards.append(card)
        self._lay.addStretch()

    def _pick(self, gate: str, idx: int) -> None:
        for i, c in enumerate(self._cards):
            c.set_selected(i == idx)
        self.card_selected.emit(gate)
