"""Global Qt stylesheets and glass panel helpers."""

from smartvenue_ai.config import COLORS, FONT_BODY, FONT_DISPLAY


def app_stylesheet() -> str:
    c = COLORS
    return f"""
    QMainWindow, QWidget#root {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: {FONT_BODY};
    }}
    QLabel {{ background: transparent; color: {c['text']}; }}
    QComboBox {{
        background: rgba(7, 17, 31, 0.95);
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 12px;
        color: #ffffff;
        font-size: 13px;
        font-weight: 600;
        min-height: 34px;
    }}
    QComboBox:hover, QComboBox:focus {{
        border-color: {c['cyan']};
    }}
    QComboBox QAbstractItemView {{
        background: {c['panel']};
        border: 1px solid {c['border']};
        selection-background-color: rgba(0, 207, 255, 0.35);
        color: {c['text']};
    }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{
        background: {c['bg']};
        width: 7px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 4px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['cyan']}; }}
    QLineEdit {{
        background: rgba(13, 27, 45, 0.95);
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 10px 14px;
        color: {c['text']};
    }}
    QLineEdit:focus {{ border-color: {c['cyan']}; }}
    """


def glass_panel_qss(extra: str = "") -> str:
    c = COLORS
    return (
        f"background-color: rgba(13, 27, 45, 0.88);"
        f"border: 1px solid {c['border']};"
        f"border-radius: 14px;"
        f"{extra}"
    )


def neon_button_qss() -> str:
    c = COLORS
    return (
        f"QPushButton {{ background: {c['cyan']}; color: #07111f;"
        f"font-weight: 700; font-size: 13px; border: none; border-radius: 10px;"
        f"padding: 12px 18px; }}"
        f"QPushButton:hover {{ background: #33d9ff; }}"
        f"QPushButton:pressed {{ background: #00a8cc; }}"
    )


def title_qss(size: int = 17) -> str:
    return (
        f"font-family: {FONT_DISPLAY}; font-size: {size}px;"
        f"font-weight: 700; color: {COLORS['text']}; letter-spacing: 1px;"
    )


def muted_qss(size: int = 11) -> str:
    return f"color: {COLORS['muted']}; font-size: {size}px;"


def field_label_qss() -> str:
    """Clear labels for form fields (route planner, etc.)."""
    return (
        f"color: #d0e4ff; font-size: 13px; font-weight: 600;"
        f"background: transparent; padding-bottom: 2px;"
    )


def body_text_qss(size: int = 13) -> str:
    return f"color: {COLORS['text']}; font-size: {size}px; font-weight: 500; background: transparent;"
