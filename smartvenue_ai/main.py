"""SmartVenue AI — application entry point."""

import asyncio
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

from smartvenue_ai.config import APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from smartvenue_ai.dashboard import DashboardWindow
from smartvenue_ai.styles import app_stylesheet


class RoundedMainWindow(QMainWindow):
    """Main window with cyberpunk dark theme."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(1280, 720)
        self.setStyleSheet(app_stylesheet())
        self.setCentralWidget(DashboardWindow())


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    # Crisp icons and text on high-DPI / Windows
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    base = QFont("Segoe UI", 11)
    base.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    base.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(base)

    try:
        import qdarktheme
        qdarktheme.setup_theme("dark")
    except ImportError:
        pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    win = RoundedMainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
