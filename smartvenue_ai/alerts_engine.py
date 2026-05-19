"""Live alert engine — congestion, routes, exits, food."""

import random
from datetime import datetime
from typing import List, Optional, Tuple

from smartvenue_ai.database import log_alert

ZONES = [
    "Gate B8", "North Stand", "South Stand", "East Stand",
    "Exit corridor", "Food Court A", "Food Court B", "West Stand",
]

TEMPLATES = [
    ("{zone} congestion increased", "high"),
    ("{zone} traffic easing", "low"),
    ("Exit corridor overloaded near {zone}", "critical"),
    ("Food Court wait time rising at {zone}", "medium"),
    ("Queue spike detected at {zone}", "high"),
    ("Route congestion warning — avoid {zone}", "medium"),
    ("Staff deployed to {zone}", "low"),
]


class AlertsEngine:
    def __init__(self) -> None:
        now = self._ts()
        self.alerts: List[Tuple[str, str, str, str]] = [
            ("Gate B8", "Gate B8 congestion increased", "high", now),
            ("North Stand", "North Stand traffic easing", "medium", now),
            ("Exit corridor", "Exit corridor overloaded", "critical", now),
            ("Food Court A", "Food Court wait time rising", "medium", now),
        ]

    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%H:%M:%S")

    @property
    def unread_count(self) -> int:
        return min(99, len([a for a in self.alerts if a[2] in ("high", "critical")]))

    def tick(self, hot_zones: Optional[List[str]] = None) -> None:
        if random.random() < 0.5:
            zone = random.choice(hot_zones or ZONES)
            tpl, default_sev = random.choice(TEMPLATES)
            msg = tpl.format(zone=zone)
            sev = default_sev if hot_zones and zone in hot_zones else random.choice(
                ("low", "medium", "high", "critical")
            )
            self.push(zone, msg, sev)

    def push(self, zone: str, message: str, severity: str) -> None:
        self.alerts.insert(0, (zone, message, severity, self._ts()))
        log_alert(zone, message, severity)
        if len(self.alerts) > 80:
            self.alerts.pop()

    def route_warning(self, zone: str) -> None:
        self.push(zone, f"Route rerouted — {zone} congestion spike detected", "high")
