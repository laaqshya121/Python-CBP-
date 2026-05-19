"""SmartVenue AI — main dashboard layout and simulation loop."""

import asyncio

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from smartvenue_ai.alerts_engine import AlertsEngine
from smartvenue_ai.analytics import Analytics
from smartvenue_ai.async_bridge import AsyncBridge
from smartvenue_ai.config import (
    ALERT_INTERVAL_MS, COLORS, DEFAULT_DEST, DEFAULT_ORIGIN,
    NAV_NODES, SIMULATION_INTERVAL_MS,
)
from smartvenue_ai.congestion_engine import CongestionEngine
from smartvenue_ai.ai_chat import StadiumAI
from smartvenue_ai.database import log_congestion, log_queue_snapshot, log_route, save_metrics
from smartvenue_ai.heatmap_engine import HeatmapEngine
from smartvenue_ai.navigation_engine import NavigationEngine
from smartvenue_ai.styles import (
    body_text_qss, field_label_qss, glass_panel_qss, muted_qss, neon_button_qss, title_qss,
)
from smartvenue_ai.widgets.ai_chat_widget import AIChatWidget
from smartvenue_ai.widgets.alerts_widget import AlertsWidget
from smartvenue_ai.widgets.bottom_nav import BottomNav
from smartvenue_ai.widgets.congestion_panel import CongestionPanel
from smartvenue_ai.widgets.metric_cards import MetricCardsRow
from smartvenue_ai.widgets.navigate_dialog import NavigateDialog
from smartvenue_ai.widgets.queue_analytics import QueueAnalyticsWidget
from smartvenue_ai.widgets.stadium_map import StadiumMapWidget


class LivePulse(QWidget):
    """Animated green LIVE dot."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(12, 12)
        self._phase = 0
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(500)

    def _tick(self) -> None:
        self._phase = (self._phase + 1) % 20
        self.update()

    def paintEvent(self, event) -> None:
        from PySide6.QtGui import QPainter
        p = QPainter(self)
        a = 120 + int(80 * abs(10 - self._phase) / 10)
        c = QColor(COLORS["green"])
        c.setAlpha(a)
        p.setBrush(c)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 8, 8)


class RoutePlannerPanel(QFrame):
    """Header glassmorphism route planner."""

    def __init__(self, nav: NavigationEngine, on_route) -> None:
        super().__init__()
        self._nav = nav
        self._on_route = on_route
        self.setStyleSheet(glass_panel_qss("border: 1px solid rgba(0,207,255,0.35);"))
        self.setFixedWidth(330)
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(40)
        glow.setColor(QColor(COLORS["cyan"]))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        self._origin = QComboBox()
        self._dest = QComboBox()
        for cb in (self._origin, self._dest):
            cb.addItems(NAV_NODES)
        self._origin.setCurrentText(DEFAULT_ORIGIN)
        self._dest.setCurrentText(DEFAULT_DEST)

        loc_lbl = QLabel("Current location")
        loc_lbl.setStyleSheet(field_label_qss())
        dest_lbl = QLabel("Destination")
        dest_lbl.setStyleSheet(field_label_qss())
        lay.addWidget(loc_lbl)
        lay.addWidget(self._origin)
        lay.addWidget(dest_lbl)
        lay.addWidget(self._dest)

        btn = QPushButton("Find Best Route →")
        btn.setStyleSheet(neon_button_qss())
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._compute)
        lay.addWidget(btn)

        self._time = QLabel("-3 min walk")
        self._time.setStyleSheet(
            f"color: {COLORS['green']}; font-weight: 800; font-size: 15px; background: transparent;"
        )
        self._elev = QLabel("Elevator available")
        self._elev.setStyleSheet(f"color: #a8c4e8; font-size: 12px; font-weight: 600; background: transparent;")
        self._instr = QLabel("Head West → turn North toward Gate B8")
        self._instr.setWordWrap(True)
        self._instr.setStyleSheet(body_text_qss(13))
        lay.addWidget(self._time)
        lay.addWidget(self._elev)
        lay.addWidget(self._instr)

    def _compute(self) -> None:
        o, d = self._origin.currentText(), self._dest.currentText()
        path = self._nav.dijkstra(o, d)
        mins = self._nav.estimate_minutes(path)
        saved = max(0, mins - 3)
        self._time.setText(f"-{saved} min walk" if saved else f"{mins} min walk")
        self._instr.setText(self._nav.instructions(path))
        self._on_route(path, o, d, mins)


class DashboardWindow(QWidget):
    """Root dashboard widget."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")

        self._congestion = CongestionEngine()
        self._nav = NavigationEngine()
        self._heatmap = HeatmapEngine()
        self._alerts = AlertsEngine()
        self._analytics = Analytics()
        self._ai = StadiumAI()
        self._ai.bind(self._congestion, self._nav, self._analytics)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)
        root.addWidget(self._header())

        self._content_row = QHBoxLayout()
        self._content_row.setSpacing(14)

        left = QVBoxLayout()
        self._map_section = self._build_map_section()
        left.addWidget(self._map_section, 1)
        self._metrics = MetricCardsRow()
        left.addWidget(self._metrics)
        self._content_row.addLayout(left, 1)

        self._congestion_panel = CongestionPanel()
        self._content_row.addWidget(self._congestion_panel)
        root.addLayout(self._content_row, 1)

        self._stack = QStackedWidget()
        self._nav_page = self._build_nav_page()
        self._queues = QueueAnalyticsWidget(self._analytics)
        self._alerts_w = AlertsWidget()
        self._chat = AIChatWidget(self._ai)
        for w in (QWidget(), self._nav_page, self._queues, self._alerts_w, self._chat):
            self._stack.addWidget(w)
        self._stack.hide()
        root.addWidget(self._stack, 1)

        self._nav_bar = BottomNav()
        self._nav_bar.tab_changed.connect(self._on_tab)
        root.addWidget(self._nav_bar)

        self._sim_timer = QTimer(self)
        self._sim_timer.timeout.connect(self._tick_sync)
        self._sim_timer.start(SIMULATION_INTERVAL_MS)

        self._alert_timer = QTimer(self)
        self._alert_timer.timeout.connect(self._tick_alerts)
        self._alert_timer.start(ALERT_INTERVAL_MS)

        self._async = AsyncBridge(SIMULATION_INTERVAL_MS, self._tick_async)
        self._async.start()

        self._tick_sync()

    def _header(self) -> QFrame:
        bar = QFrame()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 0, 0, 0)

        logo = QHBoxLayout()
        icon = QLabel("◉")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"color: {COLORS['cyan']}; font-size: 20px; border: 2px solid {COLORS['cyan']};"
            "border-radius: 20px; background: rgba(0,207,255,0.08);"
        )
        title = QLabel("<span style='font-family: Orbitron, Segoe UI'>"
                       "<b style='font-size:22px'>SMARTVENUE</b> <span style='color:#00cfff'>AI</span></span>")
        logo.addWidget(icon)
        logo.addWidget(title)
        lay.addLayout(logo)
        lay.addStretch()

        live = QFrame()
        live.setStyleSheet(
            f"background: rgba(0,255,136,0.1); border: 1px solid {COLORS['green']}; border-radius: 18px;"
        )
        ll = QHBoxLayout(live)
        ll.setContentsMargins(10, 4, 14, 4)
        ll.addWidget(LivePulse())
        live_lbl = QLabel("LIVE")
        live_lbl.setStyleSheet(f"color: {COLORS['green']}; font-weight: 700; letter-spacing: 2px;")
        ll.addWidget(live_lbl)
        lay.addWidget(live)
        lay.addStretch()

        self._planner = RoutePlannerPanel(self._nav, self._apply_route)
        lay.addWidget(self._planner)
        return bar

    def _build_map_section(self) -> QFrame:
        wrap = QFrame()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        hdr = QHBoxLayout()
        hdr.addWidget(self._lbl("Stadium Overview", title_qss()))
        hdr.addStretch()
        for c, t in [(COLORS["green"], "Low"), (COLORS["yellow"], "Medium"), (COLORS["red"], "High")]:
            hdr.addWidget(self._lbl(
                f"● {t}",
                f"color:{c}; font-size:13px; font-weight:700; margin-right:16px; background:transparent;",
            ))
        lay.addLayout(hdr)
        self._map = StadiumMapWidget()
        lay.addWidget(self._map, 1)
        return wrap

    def _build_nav_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.addWidget(self._lbl("Smart Navigation", title_qss(16)))
        row = QHBoxLayout()
        self._nav_o = QComboBox()
        self._nav_d = QComboBox()
        self._nav_o.addItems(NAV_NODES)
        self._nav_d.addItems(NAV_NODES)
        self._nav_o.setCurrentText(DEFAULT_ORIGIN)
        self._nav_d.setCurrentText(DEFAULT_DEST)
        nav_btn = QPushButton("NAVIGATE")
        nav_btn.setStyleSheet(neon_button_qss())
        nav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_btn.clicked.connect(self._open_navigate_dialog)
        src_lbl = QLabel("Source:")
        src_lbl.setStyleSheet(field_label_qss())
        dst_lbl = QLabel("Destination:")
        dst_lbl.setStyleSheet(field_label_qss())
        row.addWidget(src_lbl)
        row.addWidget(self._nav_o, 1)
        row.addWidget(dst_lbl)
        row.addWidget(self._nav_d, 1)
        row.addWidget(nav_btn)
        lay.addLayout(row)
        self._nav_map = StadiumMapWidget()
        lay.addWidget(self._nav_map, 1)
        return page

    @staticmethod
    def _lbl(text: str, style: str = "") -> QLabel:
        lb = QLabel(text)
        if style:
            lb.setStyleSheet(style)
        return lb

    def _open_navigate_dialog(self) -> None:
        dlg = NavigateDialog(self)
        dlg._origin.setCurrentText(self._nav_o.currentText())
        dlg._dest.setCurrentText(self._nav_d.currentText())
        dlg.route_requested.connect(self._on_navigate_requested)
        dlg.exec()

    def _on_navigate_requested(self, origin: str, dest: str) -> None:
        self._nav_o.setCurrentText(origin)
        self._nav_d.setCurrentText(dest)
        path = self._nav.dijkstra(origin, dest)
        self._draw_route(path, origin, dest)

    def _apply_route(self, path: list, origin: str, dest: str, mins: int) -> None:
        self._draw_route(path, origin, dest)
        log_route(origin, dest, mins)
        self._ai.set_location(origin)

    def _draw_route(self, path: list, origin: str, dest: str) -> None:
        if not path:
            return
        self._nav.set_active_route(origin, dest, path)
        pts = self._nav.path_points(path)
        self._map.show_route(pts)
        self._nav_map.show_route(pts)

    def _on_tab(self, index: int) -> None:
        if index == 0:
            self._map_section.show()
            self._congestion_panel.show()
            self._metrics.show()
            self._stack.hide()
        elif index == 1:
            self._map_section.hide()
            self._congestion_panel.hide()
            self._metrics.hide()
            self._stack.show()
            self._stack.setCurrentIndex(1)
            self._on_navigate_requested(self._nav_o.currentText(), self._nav_d.currentText())
        else:
            self._map_section.hide()
            self._congestion_panel.hide()
            self._metrics.show()
            self._stack.show()
            self._stack.setCurrentIndex(index)
            if index == 2:
                self._queues.refresh(
                    self._congestion.gate_avg,
                    self._congestion.food_avg,
                    self._congestion.washroom_avg,
                )
            elif index == 3:
                self._alerts_w.set_alerts(self._alerts.alerts)

    async def _tick_async(self) -> None:
        await asyncio.sleep(0)
        self._congestion.tick()
        self._analytics.tick()
        self._heatmap.update(self._congestion.nodes, self._congestion.particles)

    def _tick_sync(self) -> None:
        self._nav.update_crowd(self._congestion.densities)
        for zone in self._congestion.hottest_zones(2):
            log_congestion(zone, self._congestion.densities[zone], self._congestion.congestion_score(zone))
        self._map.update_simulation(self._congestion)
        self._nav_map.update_simulation(self._congestion)
        self._congestion_panel.set_data(self._congestion.gate_feed)
        self._metrics.update(self._congestion.gate_avg, self._congestion.food_avg, self._congestion.washroom_avg)
        save_metrics(self._congestion.gate_avg, self._congestion.food_avg, self._congestion.washroom_avg)
        for i, w in enumerate(self._analytics.gate_waits):
            log_queue_snapshot("gate", self._analytics.labels_gate[i], w)
        self._check_reroute()
        if self._stack.currentIndex() == 2 and self._stack.isVisible():
            self._queues.refresh(
                self._congestion.gate_avg,
                self._congestion.food_avg,
                self._congestion.washroom_avg,
            )

    def _check_reroute(self) -> None:
        if not self._nav.needs_reroute():
            return
        hot = self._congestion.hottest_zones(1)
        if hot:
            self._alerts.route_warning(hot[0])
        new_path = self._nav.reroute()
        if new_path and self._nav.active_origin and self._nav.active_dest:
            pts = self._nav.path_points(new_path)
            self._map.show_route(pts)
            self._nav_map.show_route(pts)

    def _tick_alerts(self) -> None:
        self._alerts.tick(self._congestion.hottest_zones(4))
        self._nav_bar.set_alert_count(self._alerts.unread_count)
        if self._stack.currentIndex() == 3 and self._stack.isVisible():
            self._alerts_w.set_alerts(self._alerts.alerts)
