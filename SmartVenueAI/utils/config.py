"""
SmartVenue AI — Theme & Configuration
Central design tokens and color palette for the dashboard.
"""

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":      "#050a14",
    "bg_secondary":    "#080f1e",
    "bg_card":         "#0a1628",
    "bg_card_hover":   "#0d1e38",
    "border":          "#0e2444",
    "border_glow":     "#0a84ff",

    "neon_blue":       "#0a84ff",
    "neon_cyan":       "#00d4ff",
    "neon_green":      "#00ff88",
    "neon_yellow":     "#ffcc00",
    "neon_orange":     "#ff8800",
    "neon_red":        "#ff3366",
    "neon_purple":     "#9b59ff",

    "text_primary":    "#e8f4ff",
    "text_secondary":  "#7aa8d4",
    "text_muted":      "#3a6080",

    "low":             "#00ff88",
    "medium":          "#ffcc00",
    "high":            "#ff3366",
    "critical":        "#ff0044",
}

# ─── Chart / Plotly Theme ─────────────────────────────────────────────────────
PLOTLY_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font_color":    COLORS["text_primary"],
    "font_family":   "Rajdhani, monospace",
    "gridcolor":     "#0e2444",
    "zerolinecolor": "#0e2444",
}

# ─── Stadium Layout ───────────────────────────────────────────────────────────
STADIUM_ZONES = {
    "North Stand":     {"x": (0.25, 0.75), "y": (0.80, 0.95), "capacity": 5000},
    "South Stand":     {"x": (0.25, 0.75), "y": (0.05, 0.20), "capacity": 5000},
    "East Stand":      {"x": (0.80, 0.95), "y": (0.25, 0.75), "capacity": 3500},
    "West Stand":      {"x": (0.05, 0.20), "y": (0.25, 0.75), "capacity": 3500},
    "Playing Field":   {"x": (0.25, 0.75), "y": (0.25, 0.75), "capacity": 0},
    "Food Court A":    {"x": (0.07, 0.22), "y": (0.07, 0.22), "capacity": 800},
    "Food Court B":    {"x": (0.78, 0.93), "y": (0.07, 0.22), "capacity": 800},
    "Food Court C":    {"x": (0.78, 0.93), "y": (0.78, 0.93), "capacity": 600},
    "Gate North":      {"x": (0.45, 0.55), "y": (0.92, 1.00), "capacity": 200},
    "Gate South":      {"x": (0.45, 0.55), "y": (0.00, 0.08), "capacity": 200},
    "Gate East":       {"x": (0.92, 1.00), "y": (0.45, 0.55), "capacity": 200},
    "Gate West":       {"x": (0.00, 0.08), "y": (0.45, 0.55), "capacity": 200},
    "Medical Bay":     {"x": (0.07, 0.22), "y": (0.78, 0.93), "capacity": 50},
    "VIP Lounge":      {"x": (0.38, 0.62), "y": (0.88, 0.97), "capacity": 300},
}

# ─── Navigation Graph Nodes ───────────────────────────────────────────────────
NAV_NODES = [
    "Gate North", "Gate South", "Gate East", "Gate West",
    "North Stand", "South Stand", "East Stand", "West Stand",
    "Food Court A", "Food Court B", "Food Court C",
    "Medical Bay", "VIP Lounge", "Playing Field",
    "Washroom A", "Washroom B",
]

NAV_EDGES = [
    ("Gate North", "North Stand", 2),
    ("Gate North", "VIP Lounge", 3),
    ("Gate South", "South Stand", 2),
    ("Gate East", "East Stand", 2),
    ("Gate East", "Food Court B", 4),
    ("Gate West", "West Stand", 2),
    ("Gate West", "Food Court A", 4),
    ("North Stand", "East Stand", 5),
    ("North Stand", "West Stand", 5),
    ("North Stand", "VIP Lounge", 3),
    ("South Stand", "East Stand", 5),
    ("South Stand", "West Stand", 5),
    ("South Stand", "Food Court A", 6),
    ("South Stand", "Food Court B", 6),
    ("East Stand", "Food Court B", 3),
    ("East Stand", "Food Court C", 4),
    ("West Stand", "Food Court A", 3),
    ("West Stand", "Medical Bay", 4),
    ("Food Court A", "Washroom A", 2),
    ("Food Court B", "Washroom B", 2),
    ("Food Court C", "Medical Bay", 5),
    ("VIP Lounge", "Playing Field", 4),
    ("North Stand", "Playing Field", 6),
    ("South Stand", "Playing Field", 6),
    ("Washroom A", "Medical Bay", 3),
    ("Washroom B", "Food Court C", 3),
]

# ─── App Settings ─────────────────────────────────────────────────────────────
APP_CONFIG = {
    "refresh_interval": 3000,   # ms
    "total_capacity":   22000,
    "venue_name":       "SmartVenue Arena",
    "event_name":       "Championship Finals 2025",
}
