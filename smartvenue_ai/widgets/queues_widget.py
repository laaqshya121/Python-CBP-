"""Queues tab — animated PyQtGraph bar charts."""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
import pyqtgraph as pg

from smartvenue_ai.analytics import Analytics
from smartvenue_ai.config import COLORS
from smartvenue_ai.styles import title_qss


class QueuesWidget(QFrame):
    def __init__(self, analytics: Analytics) -> None:
        super().__init__()
        self._a = analytics
        lay = QVBoxLayout(self)
        lay.addWidget(self._t("Real-Time Queue Intelligence"))
        row = QHBoxLayout()
        self._gate = self._chart_panel("Entry Gates", COLORS["cyan"])
        self._food = self._chart_panel("Food Stalls", COLORS["green"])
        self._wash = self._chart_panel("Washrooms", COLORS["yellow"])
        row.addWidget(self._gate, 1)
        row.addWidget(self._food, 1)
        row.addWidget(self._wash, 1)
        lay.addLayout(row, 1)

    @staticmethod
    def _t(text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(title_qss(16))
        return lb

    def _chart_panel(self, title: str, color: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; border-radius: 14px;"
        )
        vl = QVBoxLayout(f)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px;")
        vl.addWidget(lbl)
        plot = pg.PlotWidget()
        plot.setBackground(COLORS["panel"])
        plot.showGrid(x=True, y=True, alpha=0.15)
        for axis in ("bottom", "left"):
            plot.getAxis(axis).setPen(COLORS["muted"])
        bar = pg.BarGraphItem(x=[], height=[], width=0.55, brush=color)
        plot.addItem(bar)
        f._plot = plot  # type: ignore
        f._bar = bar  # type: ignore
        vl.addWidget(plot, 1)
        return f

    def refresh(self) -> None:
        self._update(self._gate, self._a.gate_waits, self._a.labels_gate)
        self._update(self._food, self._a.food_waits, self._a.labels_food)
        self._update(self._wash, self._a.wash_waits, self._a.labels_wash)

    @staticmethod
    def _update(panel: QFrame, heights: list, labels: list) -> None:
        x = list(range(len(heights)))
        panel._bar.setOpts(x=x, height=heights)  # type: ignore
        ax = panel._plot.getAxis("bottom")  # type: ignore
        ax.setTicks([[(i, labels[i]) for i in range(len(labels))]])
