"""Futuristic interactive stadium map — QGraphicsScene / QGraphicsView."""

from PySide6.QtCore import Property, QPropertyAnimation, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QGraphicsObject, QGraphicsScene, QGraphicsTextItem,
    QGraphicsView, QPushButton, QVBoxLayout, QWidget,
)

from smartvenue_ai.config import COLORS, FACILITY_MARKERS
from smartvenue_ai.widgets.route_animator import RouteAnimator


class PulseRing(QGraphicsObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__()
        self.setPos(x, y)
        self.setZValue(80)
        self._scale = 1.0
        self._anim = QPropertyAnimation(self, b"ringScale")
        self._anim.setDuration(1600)
        self._anim.setStartValue(0.75)
        self._anim.setEndValue(1.4)
        self._anim.setLoopCount(-1)

    def boundingRect(self) -> QRectF:
        return QRectF(-28, -28, 56, 56)

    def paint(self, painter, option, widget=None) -> None:
        pen = QPen(QColor(COLORS["cyan"]))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(-20, -20, 40, 40)

    def get_ring_scale(self) -> float:
        return self._scale

    def set_ring_scale(self, s: float) -> None:
        self._scale = s
        self.setScale(s)
        self.setOpacity(max(0.15, 1.3 - s * 0.45))

    ringScale = Property(float, get_ring_scale, set_ring_scale)

    def start(self) -> None:
        self._anim.start()


class ParticleItem(QGraphicsObject):
    def __init__(self, x: float, y: float, color: QColor) -> None:
        super().__init__()
        self.setPos(x, y)
        self._color = color
        self._r = 3.0
        self.setZValue(25)

    def boundingRect(self) -> QRectF:
        return QRectF(-4, -4, 8, 8)

    def paint(self, painter, option, widget=None) -> None:
        c = QColor(self._color)
        c.setAlpha(200)
        painter.setBrush(c)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-self._r, -self._r, self._r * 2, self._r * 2))

    def move_to(self, x: float, y: float) -> None:
        self.setPos(x, y)


class StadiumMapWidget(QFrame):
    SCENE_W, SCENE_H = 800, 600

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            f"StadiumMapWidget {{ background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; border-radius: 16px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._scene = QGraphicsScene(0, 0, self.SCENE_W, self.SCENE_H)
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self._view.setFrameShape(QFrame.Shape.NoFrame)
        self._view.setStyleSheet("background: #0a1528; border: none; border-radius: 16px;")
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lay.addWidget(self._view)

        self._route: RouteAnimator | None = None
        self._heat_items: list = []
        self._particle_items: list[ParticleItem] = []
        self._pulse: PulseRing | None = None

        self._build_scene()
        self._build_zoom_controls()

    def _build_scene(self) -> None:
        s = self._scene
        s.setBackgroundBrush(QBrush(QColor("#0a1528")))

        grid_pen = QPen(QColor("#14345c"))
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        for x in range(0, self.SCENE_W + 1, 40):
            s.addLine(x, 0, x, self.SCENE_H, grid_pen)
        for y in range(0, self.SCENE_H + 1, 40):
            s.addLine(0, y, self.SCENE_W, y, grid_pen)

        ring = QPen(QColor(COLORS["border"]))
        ring.setWidth(3)
        s.addEllipse(55, 38, 690, 524, ring)
        glow = QPen(QColor(COLORS["cyan"]))
        glow.setWidth(1)
        glow.setStyle(Qt.PenStyle.DashLine)
        s.addEllipse(68, 50, 664, 500, glow)

        field_pen = QPen(QColor("#1a5c38"))
        field_pen.setWidth(2)
        field_brush = QBrush(QColor("#0d2818"))
        s.addRect(215, 175, 370, 250, field_pen, field_brush)
        s.addLine(400, 175, 400, 425, field_pen)
        s.addEllipse(365, 268, 70, 70, field_pen)

        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        for text, x, y in [
            ("NORTH STAND", 340, 88), ("SOUTH STAND", 330, 518),
            ("EAST STAND", 700, 288), ("WEST STAND", 45, 288),
        ]:
            t = s.addText(text, font)
            t.setDefaultTextColor(QColor(COLORS["muted"]))
            t.setPos(x, y)

        for kind, label, x, y in FACILITY_MARKERS:
            t = s.addText(label if kind != "food" else label)
            t.setPos(x, y)
            t.setDefaultTextColor(QColor(COLORS["cyan"] if kind == "gate" else COLORS["muted"]))

        self._pulse = PulseRing(400, 300)
        s.addItem(self._pulse)
        self._pulse.start()
        core = s.addEllipse(393, 293, 14, 14, QPen(Qt.PenStyle.NoPen), QBrush(QColor(COLORS["cyan"])))
        core.setZValue(81)
        you = s.addText("YOU")
        you.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        you.setDefaultTextColor(QColor(COLORS["cyan"]))
        you.setPos(382, 312)
        you.setZValue(82)

    def _build_zoom_controls(self) -> None:
        self._ctrl = QWidget(self)
        self._ctrl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        btn_qss = (
            f"QPushButton {{ background: rgba(13,27,45,0.92); color: {COLORS['cyan']};"
            f"border: 1px solid {COLORS['border']}; border-radius: 10px; font-size: 15px; min-width: 38px; min-height: 38px; }}"
            f"QPushButton:hover {{ border-color: {COLORS['cyan']}; background: rgba(0,207,255,0.15); }}"
        )
        self._zi = QPushButton("+", self._ctrl)
        self._zo = QPushButton("−", self._ctrl)
        self._rc = QPushButton("⌖", self._ctrl)
        for b in (self._zi, self._zo, self._rc):
            b.setStyleSheet(btn_qss)
            b.setFixedSize(38, 38)
        self._zi.clicked.connect(lambda: self._view.scale(1.12, 1.12))
        self._zo.clicked.connect(lambda: self._view.scale(0.89, 0.89))
        self._rc.clicked.connect(self.reset_view)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        self._ctrl.setGeometry(w - 56, 72, 48, 130)
        self._zi.move(5, 0)
        self._zo.move(5, 44)
        self._rc.move(5, 88)

    def reset_view(self) -> None:
        self._view.resetTransform()
        self._view.fitInView(QRectF(0, 0, self.SCENE_W, self.SCENE_H), Qt.AspectRatioMode.KeepAspectRatio)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(80, self.reset_view)

    def update_simulation(self, engine) -> None:
        for item in self._heat_items:
            self._scene.removeItem(item)
        self._heat_items.clear()

        colors = {"low": COLORS["green"], "medium": COLORS["yellow"], "high": COLORS["red"]}
        import math
        for node in engine.nodes:
            c = QColor(colors.get(node["level"], COLORS["cyan"]))
            pulse = 0.85 + 0.15 * math.sin(node.get("phase", 0))
            r = node.get("r", 10) * pulse
            c.setAlpha(170)
            ell = self._scene.addEllipse(node["x"] - r, node["y"] - r, r * 2, r * 2, QPen(Qt.PenStyle.NoPen), QBrush(c))
            ell.setZValue(22)
            self._heat_items.append(ell)

        while len(self._particle_items) < len(engine.particles):
            p = ParticleItem(0, 0, QColor(COLORS["cyan"]))
            self._scene.addItem(p)
            self._particle_items.append(p)
        for i, part in enumerate(engine.particles):
            col = QColor(engine.level_color(part.level))
            self._particle_items[i]._color = col
            self._particle_items[i].move_to(part.x, part.y)

    def show_route(self, points: list) -> None:
        if self._route:
            self._scene.removeItem(self._route)
        if len(points) < 2:
            return
        self._route = RouteAnimator(points)
        self._scene.addItem(self._route)
        self._route.start()

    def clear_route(self) -> None:
        if self._route:
            self._scene.removeItem(self._route)
            self._route = None
