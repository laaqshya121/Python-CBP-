"""Queue analytics with history buffers for live charts."""

import random
from collections import deque
from typing import Deque, List

import numpy as np
import pandas as pd


class Analytics:
    HISTORY = 24

    def __init__(self) -> None:
        self.gate_waits = [12, 19, 8, 14, 22, 6, 11]
        self.food_waits = [9, 14, 7, 11, 5, 8]
        self.wash_waits = [5, 8, 3, 6, 4]
        self.labels_gate = ["B8", "A4", "C2", "N", "S", "E", "W"]
        self.labels_food = ["FC-A", "FC-B", "FC-C", "St1", "St2", "St3"]
        self.labels_wash = ["W-A", "W-B", "W-C", "W-D", "W-E"]
        self.gate_history: Deque[float] = deque([17.0] * self.HISTORY, maxlen=self.HISTORY)
        self.food_history: Deque[float] = deque([9.0] * self.HISTORY, maxlen=self.HISTORY)
        self.wash_history: Deque[float] = deque([5.0] * self.HISTORY, maxlen=self.HISTORY)

    def tick(self) -> None:
        self.gate_waits = [int(np.clip(x + random.gauss(0, 1.5), 2, 32)) for x in self.gate_waits]
        self.food_waits = [int(np.clip(x + random.gauss(0, 1.2), 2, 24)) for x in self.food_waits]
        self.wash_waits = [int(np.clip(x + random.gauss(0, 0.8), 1, 16)) for x in self.wash_waits]
        self.gate_history.append(float(np.mean(self.gate_waits)))
        self.food_history.append(float(np.mean(self.food_waits)))
        self.wash_history.append(float(np.mean(self.wash_waits)))

    def predict_gate_wait(self) -> int:
        arr = np.array(self.gate_history)
        if len(arr) < 3:
            return int(np.mean(self.gate_waits))
        trend = arr[-1] - arr[-3]
        return int(np.clip(arr[-1] + trend * 0.5 + random.gauss(0, 0.5), 3, 35))

    def gate_df(self) -> pd.DataFrame:
        return pd.DataFrame({"gate": self.labels_gate, "wait_min": self.gate_waits})

    def summary(self) -> dict:
        return {
            "gate": float(np.mean(self.gate_waits)),
            "food": float(np.mean(self.food_waits)),
            "washroom": float(np.mean(self.wash_waits)),
        }
