"""
SmartVenue AI — Route Optimization Engine
Uses NetworkX to compute fastest, safest, and least-crowded routes.
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional
from utils.config import NAV_NODES, NAV_EDGES


class RouteOptimizer:
    """
    Builds a weighted graph of the venue and finds optimal routes
    between any two points using different criteria.
    """

    def __init__(self):
        self.G_base = nx.Graph()
        self.G_base.add_nodes_from(NAV_NODES)
        for src, dst, weight in NAV_EDGES:
            self.G_base.add_edge(src, dst, weight=weight, base_weight=weight)
        self._crowd_weights: Dict[str, float] = {}

    # ── Update ────────────────────────────────────────────────────────────────

    def update_crowd_weights(self, zone_densities: Dict[str, float]):
        """Re-weight edges based on current crowd density."""
        self._crowd_weights = zone_densities

        for src, dst, data in self.G_base.edges(data=True):
            base = data["base_weight"]
            # Average density of the two endpoints
            d1 = zone_densities.get(src, 0.0)
            d2 = zone_densities.get(dst, 0.0)
            avg = (d1 + d2) / 2
            # Crowd penalty: up to 3× the base weight
            crowd_factor = 1 + avg * 2
            self.G_base[src][dst]["weight"] = base * crowd_factor

    # ── Routing ───────────────────────────────────────────────────────────────

    def find_routes(
        self,
        origin: str,
        destination: str,
    ) -> Dict[str, dict]:
        """
        Return three route options: fastest, safest, least_crowded.
        Each value is a dict with keys: path (list), time_min (int), score (str).
        """
        if origin == destination:
            return {}
        if origin not in self.G_base.nodes or destination not in self.G_base.nodes:
            return {}

        results = {}

        # 1. Fastest — base walking time only
        try:
            G_fast = nx.Graph()
            G_fast.add_nodes_from(self.G_base.nodes)
            for u, v, d in self.G_base.edges(data=True):
                G_fast.add_edge(u, v, weight=d["base_weight"])
            path = nx.shortest_path(G_fast, origin, destination, weight="weight")
            length = nx.shortest_path_length(G_fast, origin, destination, weight="weight")
            results["fastest"] = {
                "path": path,
                "time_min": max(1, int(length * 1.2)),
                "label": "⚡ Fastest",
                "color": "#0a84ff",
            }
        except nx.NetworkXNoPath:
            pass

        # 2. Least crowded — crowd-weighted
        try:
            path = nx.shortest_path(self.G_base, origin, destination, weight="weight")
            length = nx.shortest_path_length(self.G_base, origin, destination, weight="weight")
            results["least_crowded"] = {
                "path": path,
                "time_min": max(1, int(length * 1.2)),
                "label": "🌿 Least Crowded",
                "color": "#00ff88",
            }
        except nx.NetworkXNoPath:
            pass

        # 3. Safest — avoids high-density zones by penalising them heavily
        try:
            G_safe = nx.Graph()
            G_safe.add_nodes_from(self.G_base.nodes)
            for u, v, d in self.G_base.edges(data=True):
                base = d["base_weight"]
                d1 = self._crowd_weights.get(u, 0)
                d2 = self._crowd_weights.get(v, 0)
                # Exponential penalty for high-density corridors
                safety_factor = 1 + max(d1, d2) ** 3 * 5
                G_safe.add_edge(u, v, weight=base * safety_factor)
            path = nx.shortest_path(G_safe, origin, destination, weight="weight")
            length = nx.shortest_path_length(G_safe, origin, destination, weight="weight")
            results["safest"] = {
                "path": path,
                "time_min": max(1, int(length * 1.4)),
                "label": "🛡️ Safest",
                "color": "#ffcc00",
            }
        except nx.NetworkXNoPath:
            pass

        return results

    def get_recommendations(
        self,
        zone_densities: Dict[str, float],
    ) -> List[str]:
        """Generate smart venue recommendations based on current density."""
        tips = []

        # Find least crowded gate
        gate_densities = {
            k: v for k, v in zone_densities.items() if "Gate" in k
        }
        if gate_densities:
            best_gate = min(gate_densities, key=gate_densities.get)
            worst_gate = max(gate_densities, key=gate_densities.get)
            if gate_densities.get(worst_gate, 0) > 0.6:
                tips.append(f"Use {best_gate} — {worst_gate} is congested")

        # Food courts
        food_densities = {
            k: v for k, v in zone_densities.items() if "Food Court" in k
        }
        if food_densities:
            best_food = min(food_densities, key=food_densities.get)
            worst_food = max(food_densities, key=food_densities.get)
            if food_densities.get(worst_food, 0) > 0.65:
                tips.append(f"{best_food} is less crowded right now")

        # Stand tips
        stand_densities = {
            k: v for k, v in zone_densities.items() if "Stand" in k
        }
        if stand_densities:
            congested = [k for k, v in stand_densities.items() if v > 0.8]
            if congested:
                tips.append(f"Avoid {congested[0]} — standing room only")

        if not tips:
            tips.append("All areas operating normally")

        return tips[:3]
