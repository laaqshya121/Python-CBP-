"""Full queue analytics — bar, line, radial PyQtGraph charts."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout
import pyqtgraph as pg

from smartvenue_ai.analytics import Analytics
from smartvenue_ai.config import COLORS
from smartvenue_ai.styles import title_qss


class QueueAnalyticsWidget(QFrame):
    """Production queue intelligence dashboard."""

    def __init__(self, analytics: Analytics) -> None:
        super().__init__()
        self._a = analytics
        self.setStyleSheet("background: transparent; border: none;")
        root = QVBoxLayout(self)
        root.addWidget(self._title("Real-Time Queue Intelligence"))

        grid = QGridLayout()
        grid.setSpacing(12)
        self._gate_bars = self._panel("Gate Wait Times", COLORS["cyan"])
        self._food_bars = self._panel("Food Stall Queues", COLORS["green"])
        self._wash_bars = self._panel("Washroom Waits", COLORS["yellow"])
        self._gate_line = self._line_panel("Gate Avg Trend", COLORS["cyan"])
        self._food_line = self._line_panel("Food Avg Trend", COLORS["green"])
        self._radial = self._radial_panel("Occupancy Mix")

        grid.addWidget(self._gate_bars, 0, 0)
        grid.addWidget(self._food_bars, 0, 1)
        grid.addWidget(self._wash_bars, 0, 2)
        grid.addWidget(self._gate_line, 1, 0)
        grid.addWidget(self._food_line, 1, 1)
        grid.addWidget(self._radial, 1, 2)
        root.addLayout(grid, 1)

        pred = QLabel()
        pred.setObjectName("prediction")
        pred.setStyleSheet(
            f"color: {COLORS['muted']}; font-size: 12px; padding: 8px;"
            f"background: {COLORS['panel']}; border-radius: 10px; border: 1px solid {COLORS['border']};"
        )
        root.addWidget(pred)
        self._pred_lbl = pred

    @staticmethod
    def _title(text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet(title_qss(16))
        return lb

    def _panel(self, title: str, color: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; border-radius: 14px;"
        )
        vl = QVBoxLayout(f)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")
        vl.addWidget(lbl)
        plot = pg.PlotWidget()
        plot.setBackground(COLORS["panel"])
        plot.showGrid(x=True, y=True, alpha=0.12)
        for ax in ("bottom", "left"):
            plot.getAxis(ax).setPen(COLORS["muted"])
        bar = pg.BarGraphItem(x=[], height=[], width=0.55, brush=color)
        plot.addItem(bar)
        f._plot = plot  # type: ignore
        f._bar = bar  # type: ignore
        vl.addWidget(plot, 1)
        return f

    def _line_panel(self, title: str, color: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; border-radius: 14px;"
        )
        vl = QVBoxLayout(f)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")
        vl.addWidget(lbl)
        plot = pg.PlotWidget()
        plot.setBackground(COLORS["panel"])
        plot.showGrid(x=True, y=True, alpha=0.12)
        f._curve = plot.plot(pen=pg.mkPen(color, width=2))  # type: ignore
        f._plot = plot  # type: ignore
        vl.addWidget(plot, 1)
        return f

    def _radial_panel(self, title: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; border-radius: 14px;"
        )
        vl = QVBoxLayout(f)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")
        vl.addWidget(lbl)
        plot = pg.PlotWidget()
        plot.setBackground(COLORS["panel"])
        plot.hideAxis("bottom")
        plot.hideAxis("left")
        f._plot = plot  # type: ignore
        f._bars = []  # type: ignore
        vl.addWidget(plot, 1)
        return f

    def refresh(self, gate_avg: int, food_avg: int, wash_avg: int) -> None:
        self._update_bars(self._gate_bars, self._a.gate_waits, self._a.labels_gate)
        self._update_bars(self._food_bars, self._a.food_waits, self._a.labels_food)
        self._update_bars(self._wash_bars, self._a.wash_waits, self._a.labels_wash)

        x = list(range(len(self._a.gate_history)))
        self._gate_line._curve.setData(x, list(self._a.gate_history))  # type: ignore
        self._food_line._curve.setData(x, list(self._a.food_history))  # type: ignore

        self._update_radial(gate_avg, food_avg, wash_avg)
        pred = self._a.predict_gate_wait()
        self._pred_lbl.setText(
            f"ML prediction — Next gate avg: ~{pred} min | "
            f"Current: Gate {gate_avg} min · Food {food_avg} min · Washroom {wash_avg} min"
        )

    @staticmethod
    def _update_bars(panel: QFrame, heights: list, labels: list) -> None:
        x = list(range(len(heights)))
        panel._bar.setOpts(x=x, height=heights)  # type: ignore
        panel._plot.getAxis("bottom").setTicks([[(i, labels[i]) for i in range(len(labels))]])  # type: ignore

    def _update_radial(self, gate: int, food: int, wash: int) -> None:
        plot = self._radial._plot  # type: ignore
        for item in self._radial._bars:  # type: ignore
            plot.removeItem(item)
        self._radial._bars.clear()  # type: ignore
        vals = [gate, food, wash]
        colors = [COLORS["cyan"], COLORS["green"], COLORS["yellow"]]
        labels = ["Gate", "Food", "Wash"]
        total = max(sum(vals), 1)
        for i, (v, c, lb) in enumerate(zip(vals, colors, labels)):
            angle = i * 120
            bar = pg.BarGraphItem(
                x=[angle], height=[v / total * 50], width=40,
                brush=c,
            )
            plot.addItem(bar)
            self._radial._bars.append(bar)  # type: ignore
