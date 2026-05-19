"""OpenCV-smoothed density heatmap grid."""

import cv2
import numpy as np


class HeatmapEngine:
    def __init__(self, rows: int = 48, cols: int = 72) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=np.float32)

    def update(self, nodes: list, particles: list) -> np.ndarray:
        self.grid *= 0.82
        for src in nodes + [{"x": p.x, "y": p.y, "level": p.level} for p in particles]:
            cx = int(src["x"] / 800 * self.cols)
            cy = int(src["y"] / 600 * self.rows)
            cx = int(np.clip(cx, 0, self.cols - 1))
            cy = int(np.clip(cy, 0, self.rows - 1))
            intensity = {"low": 0.25, "medium": 0.55, "high": 0.92}.get(src.get("level", "medium"), 0.5)
            self.grid[cy, cx] = min(1.0, self.grid[cy, cx] + intensity * 0.35)
        self.grid = cv2.GaussianBlur(self.grid, (7, 7), 1.4)
        return self.grid
