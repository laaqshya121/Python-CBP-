"""Bottom navigation — crisp icons + sharp text (no nested QLabel blur)."""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QToolButton

from smartvenue_ai.config import COLORS
from smartvenue_ai.widgets.nav_icons import tab_icon


class BottomNav(QFrame):
    tab_changed = Signal(int)

    TABS = [
        ("map", "MAP", "Stadium map overview"),
        ("navigate", "NAVIGATE", "Route planner & navigation"),
        ("queues", "QUEUES", "Live queue analytics"),
        ("alerts", "ALERTS", "Live stadium alerts"),
        ("chat", "AI CHAT", "Stadium AI assistant"),
    ]

    ICON_SIZE = 30
    FONT_FAMILY = "Segoe UI"

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("bottomNav")
        self.setFixedHeight(96)
        self.setStyleSheet(
            f"#bottomNav {{ background-color: {COLORS['panel']};"
            f"border: 1px solid {COLORS['border']}; border-radius: 14px; }}"
        )
        self._idx = 0
        self._buttons: list[QToolButton] = []
        self._keys: list[str] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        nav_font = QFont(self.FONT_FAMILY)
        nav_font.setPixelSize(13)
        nav_font.setWeight(QFont.Weight.Bold)
        nav_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)

        for i, (key, name, tip) in enumerate(self.TABS):
            btn = QToolButton()
            btn.setText(name)
            btn.setFont(nav_font)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tip)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
            btn.setMinimumHeight(74)
            btn.setMinimumWidth(112)
            btn.setProperty("navKey", key)
            btn.clicked.connect(lambda checked=False, ix=i: self.select(ix))
            self._buttons.append(btn)
            self._keys.append(key)
            lay.addWidget(btn, 1)

        self.select(0)

    def set_alert_count(self, count: int) -> None:
        """Append badge to Alerts button text."""
        for btn, key in zip(self._buttons, self._keys):
            if key == "alerts":
                badge = "99+" if count > 99 else str(max(1, count))
                btn.setText(f"ALERTS  [{badge}]")
                break

    def _style_tab(self, index: int, active: bool) -> None:
        btn = self._buttons[index]
        key = self._keys[index]
        color = COLORS["cyan"] if active else "#b8d4f0"
        icon_color = COLORS["cyan"] if active else "#8eb8e8"

        btn.setIcon(tab_icon(key, icon_color, self.ICON_SIZE))

        if active:
            btn.setStyleSheet(
                f"QToolButton {{"
                f"  background-color: rgba(0, 207, 255, 0.20);"
                f"  border: 2px solid {COLORS['cyan']};"
                f"  border-radius: 12px;"
                f"  color: #ffffff;"
                f"  font-weight: 800;"
                f"  padding: 6px 8px;"
                f"}}"
            )
        else:
            btn.setStyleSheet(
                f"QToolButton {{"
                f"  background-color: rgba(17, 34, 64, 0.85);"
                f"  border: 1px solid {COLORS['border']};"
                f"  border-radius: 12px;"
                f"  color: #e8f4ff;"
                f"  font-weight: 700;"
                f"  padding: 6px 8px;"
                f"}}"
                f"QToolButton:hover {{"
                f"  background-color: rgba(0, 207, 255, 0.12);"
                f"  border-color: {COLORS['cyan']};"
                f"  color: #ffffff;"
                f"}}"
            )

    def select(self, index: int) -> None:
        self._idx = index
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            self._style_tab(i, i == index)
        self.tab_changed.emit(index)
