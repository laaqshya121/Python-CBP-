"""
SmartVenue AI — Crowd Simulation Engine
Simulates real-time crowd movement across stadium zones.
"""

import numpy as np
import pandas as pd
import time
import random
from typing import Dict, List, Tuple


class CrowdSimulator:
    """Simulates crowd density and movement across stadium zones."""

    def __init__(self, zones_csv: str = "data/zones.csv"):
        self.zones_df = pd.read_csv(zones_csv)
        self._state: Dict[str, float] = {}
        self._init_state()
        self._tick = 0

    # ── Internal ──────────────────────────────────────────────────────────────

    def _init_state(self):
        """Seed each zone with its initial occupancy ratio."""
        for _, row in self.zones_df.iterrows():
            ratio = row["current_occupancy"] / max(row["capacity"], 1)
            self._state[row["zone_name"]] = min(ratio, 1.0)

    # ── Public API ────────────────────────────────────────────────────────────

    def tick(self) -> Dict[str, float]:
        """Advance simulation by one step. Returns zone → density (0‒1) dict."""
        self._tick += 1
        noise_scale = 0.04

        # Event-driven spikes every ~30 ticks
        spike_zone = None
        if self._tick % 30 == 0:
            spike_zone = random.choice(list(self._state.keys()))

        for zone in list(self._state.keys()):
            base = self._state[zone]
            drift = np.random.normal(0, noise_scale)

            # Halftime effect — fills up the concourse
            if self._tick % 60 in range(5, 15):
                if "Food" in zone or "Washroom" in zone:
                    drift += 0.06

            # Spike simulation
            if zone == spike_zone:
                drift += random.uniform(0.08, 0.15)

            # Mean-reversion pull toward zone's "natural" level
            natural = self._get_natural_density(zone)
            reversion = (natural - base) * 0.05
            new_val = base + drift + reversion
            self._state[zone] = float(np.clip(new_val, 0.0, 1.0))

        return dict(self._state)

    def get_dataframe(self) -> pd.DataFrame:
        """Return current state as a tidy DataFrame."""
        state = self.tick()
        rows = []
        for _, zrow in self.zones_df.iterrows():
            name = zrow["zone_name"]
            density = state.get(name, 0.0)
            occupancy = int(density * zrow["capacity"])
            rows.append({
                "zone_name": name,
                "density": density,
                "occupancy": occupancy,
                "capacity": zrow["capacity"],
                "alert_level": self._density_to_level(density),
                "zone_id": zrow["zone_id"],
            })
        return pd.DataFrame(rows)

    def get_heatmap_grid(self, size: int = 60) -> np.ndarray:
        """
        Render a 2D NumPy grid (0‒1) suitable for a heatmap overlay
        based on current crowd densities.
        """
        from utils.config import STADIUM_ZONES
        grid = np.zeros((size, size))
        state = self._state

        for zone_name, bounds in STADIUM_ZONES.items():
            if zone_name == "Playing Field":
                continue
            density = state.get(zone_name, 0.0)
            x0 = int(bounds["x"][0] * size)
            x1 = int(bounds["x"][1] * size)
            y0 = int(bounds["y"][0] * size)
            y1 = int(bounds["y"][1] * size)
            grid[y0:y1, x0:x1] = density

        # Smooth with a simple blur
        from scipy.ndimage import gaussian_filter
        grid = gaussian_filter(grid, sigma=1.5)
        return grid

    def get_total_attendees(self) -> int:
        """Sum of all zone occupancies."""
        df = self.get_dataframe()
        return int(df["occupancy"].sum())

    def get_congested_zones(self, threshold: float = 0.7) -> List[str]:
        """Return list of zone names above density threshold."""
        return [z for z, d in self._state.items() if d >= threshold]

    def get_average_density(self) -> float:
        vals = list(self._state.values())
        return float(np.mean(vals)) if vals else 0.0

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _get_natural_density(zone: str) -> float:
        """Natural 'resting' density per zone type."""
        if "Stand" in zone:     return 0.65
        if "Food Court" in zone: return 0.55
        if "Gate" in zone:       return 0.45
        if "Washroom" in zone:   return 0.35
        if "Medical" in zone:    return 0.10
        if "VIP" in zone:        return 0.50
        return 0.40

    @staticmethod
    def _density_to_level(d: float) -> str:
        if d >= 0.75: return "high"
        if d >= 0.45: return "medium"
        return "low"
