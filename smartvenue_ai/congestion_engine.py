"""Live crowd simulation with Gaussian particle movement."""

import random
from typing import Dict, List

import numpy as np
import pandas as pd

from smartvenue_ai.config import COLORS, GATE_FEED, NAV_NODES


class CrowdParticle:
    __slots__ = ("x", "y", "vx", "vy", "level", "phase")

    def __init__(self, x: float, y: float, level: str) -> None:
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-1.2, 1.2)
        self.level = level
        self.phase = random.uniform(0, 6.28)


class CongestionEngine:
    LEVELS = ("low", "medium", "high")

    def __init__(self) -> None:
        self.densities: Dict[str, float] = {n: random.uniform(0.15, 0.75) for n in NAV_NODES}
        self.particles: List[CrowdParticle] = [
            CrowdParticle(random.uniform(100, 700), random.uniform(90, 510), random.choice(self.LEVELS))
            for _ in range(28)
        ]
        self.nodes: List[Dict] = [
            {"x": random.uniform(120, 680), "y": random.uniform(100, 500),
             "level": random.choice(self.LEVELS), "r": random.uniform(8, 16), "phase": random.random() * 6.28}
            for _ in range(14)
        ]
        self.gate_feed: List[list] = [list(row) for row in GATE_FEED]
        self.gate_avg = 17
        self.food_avg = 9
        self.washroom_avg = 5

    def tick(self) -> None:
        for n in NAV_NODES:
            self.densities[n] = float(np.clip(self.densities[n] + random.gauss(0, 0.055), 0.08, 0.98))

        for p in self.particles:
            p.x = float(np.clip(p.x + p.vx + random.gauss(0, 2.2), 70, 730))
            p.y = float(np.clip(p.y + p.vy + random.gauss(0, 2.2), 70, 530))
            p.vx = float(np.clip(p.vx + random.gauss(0, 0.15), -2.5, 2.5))
            p.vy = float(np.clip(p.vy + random.gauss(0, 0.15), -2.5, 2.5))
            p.phase += 0.12
            if random.random() < 0.08:
                p.level = random.choice(self.LEVELS)

        for node in self.nodes:
            node["x"] = float(np.clip(node["x"] + random.gauss(0, 6), 80, 720))
            node["y"] = float(np.clip(node["y"] + random.gauss(0, 6), 80, 520))
            node["phase"] = node.get("phase", 0) + 0.1
            if random.random() < 0.12:
                node["level"] = random.choice(self.LEVELS)

        for card in self.gate_feed:
            card[1] = int(np.clip(card[1] + random.gauss(0, 1.8), 3, 35))
            card[3] = "low" if card[1] < 10 else "medium" if card[1] < 18 else "high"

        self.gate_avg = int(np.mean([c[1] for c in self.gate_feed]))
        self.food_avg = int(np.clip(self.food_avg + random.gauss(0, 1), 4, 22))
        self.washroom_avg = int(np.clip(self.washroom_avg + random.gauss(0, 0.7), 2, 14))

    def level_color(self, level: str) -> str:
        return {"low": COLORS["green"], "medium": COLORS["yellow"], "high": COLORS["red"]}.get(
            level, COLORS["cyan"]
        )

    def congestion_score(self, zone: str) -> float:
        d = self.densities.get(zone, 0.3)
        return float(np.clip(d * 100, 0, 100))

    def global_congestion_score(self) -> float:
        vals = list(self.densities.values())
        return float(np.mean(vals) * 100) if vals else 0.0

    def congestion_level(self) -> str:
        s = self.global_congestion_score()
        if s < 40:
            return "LOW"
        if s < 70:
            return "MODERATE"
        return "HIGH"

    def hottest_zones(self, n: int = 3) -> List[str]:
        ranked = sorted(self.densities.items(), key=lambda x: x[1], reverse=True)
        return [z for z, _ in ranked[:n]]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.gate_feed, columns=["gate", "wait_min", "entrance", "level"])
