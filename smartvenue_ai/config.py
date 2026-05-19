"""SmartVenue AI — global configuration and design tokens."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"
FONTS = ASSETS / "fonts"

APP_NAME = "SmartVenue AI"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
SIMULATION_INTERVAL_MS = 2000
ALERT_INTERVAL_MS = 4500

COLORS = {
    "bg": "#07111f",
    "panel": "#0d1b2d",
    "panel_light": "#112240",
    "border": "#14345c",
    "cyan": "#00cfff",
    "green": "#00ff88",
    "red": "#ff355e",
    "yellow": "#ffd600",
    "text": "#ffffff",
    "muted": "#8ca6c9",
}

FONT_DISPLAY = '"Orbitron", "Segoe UI", sans-serif'
FONT_BODY = '"Inter", "Segoe UI", sans-serif'

NAV_NODES = [
    "Gate North", "Gate South", "Gate East", "Gate West",
    "Gate B8", "Gate A4", "Gate C2",
    "North Stand", "South Stand", "East Stand", "West Stand",
    "Food Court A", "Food Court B", "Food Court C",
    "Medical Bay", "VIP Lounge", "Playing Field",
    "Washroom A", "Washroom B", "Exit West", "Exit East",
]

NAV_EDGES = [
    ("Gate North", "North Stand", 2), ("Gate North", "VIP Lounge", 3),
    ("Gate South", "South Stand", 2), ("Gate East", "East Stand", 2),
    ("Gate East", "Food Court B", 4), ("Gate West", "West Stand", 2),
    ("Gate West", "Food Court A", 4), ("Gate B8", "South Stand", 3),
    ("Gate B8", "West Stand", 4), ("Gate A4", "North Stand", 3),
    ("Gate C2", "East Stand", 2), ("North Stand", "East Stand", 5),
    ("North Stand", "West Stand", 5), ("South Stand", "East Stand", 5),
    ("South Stand", "West Stand", 5), ("East Stand", "Food Court B", 3),
    ("West Stand", "Food Court A", 3), ("Food Court A", "Washroom A", 2),
    ("Food Court B", "Washroom B", 2), ("VIP Lounge", "Playing Field", 4),
    ("North Stand", "Playing Field", 6), ("South Stand", "Playing Field", 6),
    ("Exit West", "Gate West", 2), ("Exit East", "Gate East", 2),
    ("Medical Bay", "West Stand", 4), ("Food Court C", "East Stand", 4),
]

NODE_POSITIONS = {
    "Gate North": (400, 48), "Gate South": (400, 552),
    "Gate East": (752, 300), "Gate West": (48, 300),
    "Gate B8": (165, 485), "Gate A4": (635, 75), "Gate C2": (710, 415),
    "North Stand": (400, 125), "South Stand": (400, 475),
    "East Stand": (670, 300), "West Stand": (130, 300),
    "Food Court A": (115, 415), "Food Court B": (685, 415),
    "Food Court C": (685, 175), "Medical Bay": (115, 185),
    "VIP Lounge": (400, 195), "Playing Field": (400, 300),
    "Washroom A": (195, 395), "Washroom B": (605, 395),
    "Exit West": (90, 250), "Exit East": (710, 250),
}

GATE_FEED = [
    ("Gate B8", 19, "South-West Entrance", "high"),
    ("Gate A4", 8, "North Entrance", "low"),
    ("Gate C2", 14, "East Corridor", "medium"),
    ("Gate North", 11, "North Stand", "medium"),
    ("Gate South", 22, "South Stand", "high"),
    ("Gate East", 6, "East Stand", "low"),
    ("Gate West", 12, "West Corridor", "medium"),
]

DEFAULT_ORIGIN = "Playing Field"
DEFAULT_DEST = "Gate B8"

FACILITY_MARKERS = [
    ("gate", "Gate N", 400, 35), ("gate", "B8", 155, 470),
    ("food", "🍔", 110, 405), ("food", "🍔", 690, 405),
    ("wc", "🚻", 185, 385), ("wc", "🚻", 615, 385),
    ("exit", "EXIT", 85, 240), ("exit", "EXIT", 715, 240),
]
