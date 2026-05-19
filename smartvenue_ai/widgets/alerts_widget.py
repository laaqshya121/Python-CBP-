"""Animated alerts feed — fade in, pulse by severity."""

from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from smartvenue_ai.config import COLORS
from smartvenue_ai.styles import title_qss


class AlertCard(QFrame):
    def __init__(self, zone: str, msg: str, sev: str, ts: str) -> None:
        super().__init__()
        colors = {
            "low": COLORS["green"], "medium": COLORS["yellow"],
            "high": COLORS["red"], "critical": COLORS["red"],
        }
        self._accent = colors.get(sev, COLORS["cyan"])
        self._apply_style(1.0)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        t = QLabel(f"<b>[{zone}]</b> {msg}")
        t.setWordWrap(True)
        t.setStyleSheet("background: transparent; font-size: 13px;")
        tm = QLabel(ts)
        tm.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10px; background: transparent;")
        lay.addWidget(t)
        lay.addWidget(tm)

        self._opacity = 0.0
        self._fade = QPropertyAnimation(self, b"cardOpacity")
        self._fade.setDuration(450)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        if sev in ("high", "critical"):
            self._pulse = QPropertyAnimation(self, b"cardOpacity")
            self._pulse.setDuration(700)
            self._pulse.setStartValue(0.85)
            self._pulse.setEndValue(1.0)
            self._pulse.setLoopCount(-1)

    def _apply_style(self, op: float) -> None:
        self.setStyleSheet(
            f"AlertCard {{ background: {COLORS['panel']}; border: 1px solid {COLORS['border']};"
            f"border-left: 3px solid {self._accent}; border-radius: 10px; opacity: {op}; }}"
        )

    def get_card_opacity(self) -> float:
        return self._opacity

    def set_card_opacity(self, v: float) -> None:
        self._opacity = v
        self._apply_style(v)

    cardOpacity = Property(float, get_card_opacity, set_card_opacity)

    def animate_in(self) -> None:
        self._fade.start()
        if hasattr(self, "_pulse"):
            self._pulse.start()


class AlertsWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        title = QLabel("Live Alerts")
        title.setStyleSheet(title_qss(16))
        lay.addWidget(title)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._inner = QWidget()
        self._inner_lay = QVBoxLayout(self._inner)
        self._inner_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._inner)
        lay.addWidget(self._scroll, 1)
        self._seen_ids: set = set()

    def set_alerts(self, alerts: list) -> None:
        for i, (zone, msg, sev, ts) in enumerate(alerts[:30]):
            key = (zone, msg, ts)
            if key in self._seen_ids:
                continue
            self._seen_ids.add(key)
            card = AlertCard(zone, msg, sev, ts)
            self._inner_lay.insertWidget(0, card)
            card.animate_in()
        while self._inner_lay.count() > 35:
            w = self._inner_lay.takeAt(self._inner_lay.count() - 1).widget()
            if w:
                w.deleteLater()
