"""Navigate dialog — source and destination gate selection."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
)

from smartvenue_ai.config import COLORS, DEFAULT_DEST, DEFAULT_ORIGIN, NAV_NODES
from smartvenue_ai.styles import neon_button_qss


class NavigateDialog(QDialog):
    route_requested = Signal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SmartVenue Navigation")
        self.setMinimumWidth(420)
        self.setStyleSheet(
            f"QDialog {{ background: {COLORS['panel']}; color: {COLORS['text']}; }}"
        )
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("<b>Select route</b>"))
        lay.addWidget(QLabel("Source gate / location"))
        self._origin = QComboBox()
        self._origin.addItems(NAV_NODES)
        self._origin.setCurrentText(DEFAULT_ORIGIN)
        lay.addWidget(self._origin)
        lay.addWidget(QLabel("Destination gate"))
        self._dest = QComboBox()
        self._dest.addItems(NAV_NODES)
        self._dest.setCurrentText(DEFAULT_DEST)
        lay.addWidget(self._dest)
        row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        go = QPushButton("NAVIGATE →")
        go.setStyleSheet(neon_button_qss())
        go.clicked.connect(self._go)
        row.addWidget(cancel)
        row.addWidget(go)
        lay.addLayout(row)

    def _go(self) -> None:
        self.route_requested.emit(self._origin.currentText(), self._dest.currentText())
        self.accept()
