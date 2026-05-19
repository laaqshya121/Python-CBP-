"""Animated neon route path with particles — QPainterPath + QPropertyAnimation."""

from PySide6.QtCore import Property, QPropertyAnimation, QPointF, QRectF, Qt, QEasingCurve
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsObject

from smartvenue_ai.config import COLORS


class RouteAnimator(QGraphicsObject):
    """Progressive cyan route with glow and moving particles."""

    def __init__(self, points: list, parent=None) -> None:
        super().__init__(parent)
        self._points = [QPointF(x, y) for x, y in points]
        self._progress = 0.0
        self._particle = 0.0
        self._pulse = 0.0
        self.setZValue(200)

        self._draw_anim = QPropertyAnimation(self, b"progress")
        self._draw_anim.setDuration(2400)
        self._draw_anim.setStartValue(0.0)
        self._draw_anim.setEndValue(1.0)
        self._draw_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._particle_anim = QPropertyAnimation(self, b"particle")
        self._particle_anim.setDuration(1400)
        self._particle_anim.setStartValue(0.0)
        self._particle_anim.setEndValue(1.0)
        self._particle_anim.setLoopCount(-1)

        self._pulse_anim = QPropertyAnimation(self, b"pulse")
        self._pulse_anim.setDuration(900)
        self._pulse_anim.setStartValue(0.4)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setLoopCount(-1)

    def boundingRect(self) -> QRectF:
        if not self._points:
            return QRectF()
        xs = [p.x() for p in self._points]
        ys = [p.y() for p in self._points]
        pad = 36
        return QRectF(min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad)

    def _curved_path(self) -> QPainterPath:
        path = QPainterPath()
        if not self._points:
            return path
        path.moveTo(self._points[0])
        for i in range(1, len(self._points)):
            a, b = self._points[i - 1], self._points[i]
            cx = (a.x() + b.x()) / 2 + (b.y() - a.y()) * 0.08
            cy = (a.y() + b.y()) / 2 + (a.x() - b.x()) * 0.08
            path.quadTo(QPointF(cx, cy), b)
        return path

    def _subpath(self, path: QPainterPath, end_frac: float) -> QPainterPath:
        sub = QPainterPath()
        steps = 100
        for i in range(steps + 1):
            t = end_frac * (i / steps)
            t = min(max(t, 0), 1)
            pt = path.pointAtPercent(t)
            if i == 0:
                sub.moveTo(pt)
            else:
                sub.lineTo(pt)
        return sub

    def paint(self, painter, option, widget=None) -> None:
        full = self._curved_path()
        if full.isEmpty():
            return
        end = self._progress
        visible = self._subpath(full, end)

        glow = QPen(QColor(COLORS["cyan"]))
        glow.setWidth(int(8 + 4 * self._pulse))
        glow.setCapStyle(Qt.PenCapStyle.RoundCap)
        glow.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setOpacity(0.25 + 0.15 * self._pulse)
        painter.setPen(glow)
        painter.drawPath(visible)

        core = QPen(QColor(COLORS["cyan"]))
        core.setWidth(3)
        core.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setOpacity(1.0)
        painter.setPen(core)
        painter.drawPath(visible)

        if end > 0.05:
            t = (self._particle % 1.0) * end
            pt = full.pointAtPercent(min(t, 0.995))
            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pt, 4 + self._pulse * 2, 4 + self._pulse * 2)
            painter.setBrush(QColor(COLORS["cyan"]))
            painter.drawEllipse(pt, 2.5, 2.5)

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, v: float) -> None:
        self._progress = v
        self.update()

    progress = Property(float, get_progress, set_progress)

    def get_particle(self) -> float:
        return self._particle

    def set_particle(self, v: float) -> None:
        self._particle = v
        self.update()

    particle = Property(float, get_particle, set_particle)

    def get_pulse(self) -> float:
        return self._pulse

    def set_pulse(self, v: float) -> None:
        self._pulse = v
        self.update()

    pulse = Property(float, get_pulse, set_pulse)

    def set_points(self, points: list) -> None:
        self._points = [QPointF(x, y) for x, y in points]
        self.prepareGeometryChange()

    def start(self) -> None:
        self._progress = 0.0
        self._draw_anim.stop()
        self._particle_anim.stop()
        self._pulse_anim.stop()
        self._draw_anim.start()
        self._particle_anim.start()
        self._pulse_anim.start()
