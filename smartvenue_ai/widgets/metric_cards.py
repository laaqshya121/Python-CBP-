"""Glossy bottom metric KPI cards."""

from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout

from smartvenue_ai.config import COLORS


class MetricCard(QFrame):
    def __init__(self, value: str, label: str, icon: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        self._lift = 0.0
        self._accent = accent
        self.setMinimumHeight(90)
        self._apply_style(0)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(accent))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        col = QVBoxLayout()
        self._val = QLabel(value)
        self._val.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {COLORS['text']};")
        sub = QLabel(label)
        sub.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: #d0e4ff; background: transparent;"
        )
        col.addWidget(self._val)
        col.addWidget(sub)
        lay.addLayout(col)
        lay.addStretch()
        ic = QLabel(icon)
        ic.setStyleSheet("font-size: 28px;")
        lay.addWidget(ic)

        self._anim = QPropertyAnimation(self, b"lift")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _apply_style(self, lift: int) -> None:
        self.setStyleSheet(
            f"QFrame#metricCard {{ background: {COLORS['panel']}; border: 1px solid {COLORS['border']};"
            f"border-radius: 14px; border-left: 3px solid {self._accent}; margin-top: {-lift}px; }}"
            f"QFrame#metricCard:hover {{ border-color: {COLORS['cyan']}; }}"
        )

    def get_lift(self) -> float:
        return self._lift

    def set_lift(self, v: float) -> None:
        self._lift = v
        self._apply_style(int(v))

    lift = Property(float, get_lift, set_lift)

    def enterEvent(self, event) -> None:
        self._anim.stop()
        self._anim.setEndValue(4.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._anim.stop()
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)

    def set_value(self, text: str) -> None:
        self._val.setText(text)


class MetricCardsRow(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(self)
        lay.setSpacing(16)
        self.gate = MetricCard("17 min", "Gate Avg Wait", "🚪", COLORS["cyan"])
        self.food = MetricCard("9 min", "Food Avg Wait", "🍔", COLORS["green"])
        self.wash = MetricCard("5 min", "Washroom Wait", "🚻", COLORS["yellow"])
        lay.addWidget(self.gate, 1)
        lay.addWidget(self.food, 1)
        lay.addWidget(self.wash, 1)

    def update(self, gate: int, food: int, wash: int) -> None:
        self.gate.set_value(f"{gate} min")
        self.food.set_value(f"{food} min")
        self.wash.set_value(f"{wash} min")
