"""
SmartVenue AI — Queue Simulation
Generates live queue updates for food stalls, washrooms, and gates.
"""

import numpy as np
import pandas as pd
import random
from typing import Dict


class QueueSimulator:
    """Simulates real-time queue wait times across venue locations."""

    def __init__(self, queues_csv: str = "data/queues.csv"):
        self.base_df = pd.read_csv(queues_csv)
        self._state: Dict[str, dict] = {}
        self._init_state()
        self._tick = 0

    def _init_state(self):
        for _, row in self.base_df.iterrows():
            self._state[row["location_id"]] = {
                "name": row["location_name"],
                "category": row["category"],
                "queue_length": int(row["queue_length"]),
                "service_rate": int(row["service_rate"]),
                "wait_min": int(row["estimated_wait_min"]),
            }

    def tick(self) -> pd.DataFrame:
        """Advance queue simulation one step."""
        self._tick += 1
        rows = []

        for loc_id, info in self._state.items():
            q = info["queue_length"]
            sr = info["service_rate"]

            # Random arrivals
            arrivals = np.random.poisson(sr * 0.8)
            departures = min(q, np.random.poisson(sr))
            new_q = max(0, q + arrivals - departures + random.randint(-2, 3))

            # Halftime surge
            if self._tick % 60 in range(5, 20) and info["category"] in ("food", "washroom"):
                new_q += random.randint(3, 12)

            new_q = min(new_q, 150)
            wait = max(0, int(new_q / max(sr, 1)))
            self._state[loc_id]["queue_length"] = new_q
            self._state[loc_id]["wait_min"] = wait

            rows.append({
                "location_id": loc_id,
                "location_name": info["name"],
                "category": info["category"],
                "queue_length": new_q,
                "service_rate": sr,
                "wait_min": wait,
                "status": self._classify_wait(wait),
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _classify_wait(wait: int) -> str:
        if wait >= 15:  return "high"
        if wait >= 7:   return "medium"
        return "low"
