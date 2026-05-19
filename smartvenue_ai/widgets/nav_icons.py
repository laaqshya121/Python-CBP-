"""Crisp vector-style tab icons drawn with QPainter (no blurry emoji)."""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QBrush


def _pix(size: int, draw_fn) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    draw_fn(p, size)
    p.end()
    return pix


def _icon(size: int, draw_fn) -> QIcon:
    return QIcon(_pix(size, draw_fn))


def _pen(color: str, w: float = 2.0) -> QPen:
    pen = QPen(QColor(color))
    pen.setWidthF(w)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def icon_map(color: str, size: int = 32) -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(_pen(color, 2.2))
        p.drawRect(6, 6, s - 12, s - 12)
        p.drawLine(s // 2, 8, s // 2, s - 8)
        p.drawLine(8, s // 2, s - 8, s // 2)
    return _icon(size, draw)


def icon_navigate(color: str, size: int = 32) -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(_pen(color, 2.4))
        p.setBrush(Qt.BrushStyle.NoBrush)
        # compass / arrow
        cx, cy = s // 2, s // 2
        p.drawEllipse(cx - 10, cy - 10, 20, 20)
        p.drawLine(cx, cy - 8, cx, cy + 2)
        p.drawLine(cx, cy - 8, cx - 4, cy - 2)
        p.drawLine(cx, cy - 8, cx + 4, cy - 2)
    return _icon(size, draw)


def icon_queues(color: str, size: int = 32) -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(color)))
        for i, h in enumerate((10, 16, 22)):
            x = 8 + i * 7
            p.drawRoundedRect(x, s - 6 - h, 5, h, 2, 2)
    return _icon(size, draw)


def icon_alerts(color: str, size: int = 32) -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(_pen(color, 2.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        # bell
        p.drawEllipse(10, 8, 12, 10)
        p.drawLine(16, 18, 16, 22)
        p.drawLine(12, 22, 20, 22)
        p.drawLine(16, 6, 16, 8)
    return _icon(size, draw)


def icon_chat(color: str, size: int = 32) -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(_pen(color, 2.2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(6, 8, 20, 14, 4, 4)
        p.drawLine(10, 22, 14, 26)
        p.drawLine(14, 26, 14, 22)
    return _icon(size, draw)


ICON_BUILDERS = {
    "map": icon_map,
    "navigate": icon_navigate,
    "queues": icon_queues,
    "alerts": icon_alerts,
    "chat": icon_chat,
}


def tab_icon(key: str, color: str, size: int = 32) -> QIcon:
    builder = ICON_BUILDERS.get(key, icon_map)
    return builder(color, size)
