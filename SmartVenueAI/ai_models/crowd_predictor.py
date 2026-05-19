"""
SmartVenue AI — AI Prediction Module
ML-based crowd and queue prediction using scikit-learn.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")


class CrowdPredictor:
    """
    Predicts next-5-minute crowd density for each zone
    using a gradient-boosting regressor trained on synthetic history.
    """

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=80, max_depth=4, learning_rate=0.1,
            subsample=0.8, random_state=42
        )
        self.scaler = StandardScaler()
        self._trained = False
        self._train_on_synthetic_data()

    # ── Training ──────────────────────────────────────────────────────────────

    def _train_on_synthetic_data(self):
        """Generate synthetic historical crowd data and train model."""
        np.random.seed(42)
        n = 2000
        hour = np.random.uniform(8, 23, n)
        match_progress = np.random.uniform(0, 90, n)       # minutes into match
        is_halftime = ((match_progress >= 43) & (match_progress <= 50)).astype(float)
        is_goal_event = np.random.binomial(1, 0.05, n).astype(float)
        day_of_week = np.random.randint(0, 7, n)
        base_density = np.random.uniform(0.2, 0.9, n)

        # Feature matrix
        X = np.column_stack([
            hour, match_progress, is_halftime, is_goal_event,
            day_of_week, base_density, base_density ** 2
        ])

        # Target: next density
        noise = np.random.normal(0, 0.05, n)
        y = np.clip(
            base_density * 0.85
            + is_halftime * 0.12
            + is_goal_event * 0.05
            + np.sin(match_progress / 15) * 0.04
            + noise,
            0, 1
        )

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self._trained = True

    # ── Prediction ────────────────────────────────────────────────────────────

    def predict_density(
        self,
        current_density: float,
        match_minute: int = 45,
        hour: int = 20,
    ) -> float:
        """Predict density for a single zone over the next 5 minutes."""
        if not self._trained:
            return current_density

        is_halftime = float(43 <= match_minute <= 50)
        is_goal = float(np.random.random() < 0.04)
        X = np.array([[hour, match_minute, is_halftime, is_goal, 5,
                        current_density, current_density ** 2]])
        X_scaled = self.scaler.transform(X)
        pred = float(self.model.predict(X_scaled)[0])
        return float(np.clip(pred, 0, 1))

    def predict_all_zones(
        self,
        zone_densities: dict,
        match_minute: int = 45,
        hour: int = 20,
    ) -> dict:
        """Predict future density for every zone."""
        return {
            zone: self.predict_density(density, match_minute, hour)
            for zone, density in zone_densities.items()
        }

    def generate_flow_prediction(self, n_steps: int = 20) -> pd.DataFrame:
        """
        Generate a time-series crowd-flow prediction for charting.
        Returns DataFrame with columns: minute, zone, predicted_density.
        """
        np.random.seed(int(np.random.random() * 100))
        zones = ["North Stand", "South Stand", "Food Court A", "Gate South", "Washroom A-F"]
        rows = []
        for z in zones:
            density = np.random.uniform(0.3, 0.8)
            for step in range(n_steps):
                minute = 40 + step * 2
                density = float(np.clip(
                    density + np.random.normal(0, 0.03)
                    + (0.06 if 43 <= minute <= 50 else -0.01),
                    0, 1
                ))
                rows.append({"minute": minute, "zone": z, "density": density})
        return pd.DataFrame(rows)
