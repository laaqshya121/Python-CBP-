"""Dijkstra congestion-aware pathfinding on stadium graph."""

import heapq
from typing import Dict, List, Optional, Tuple

from smartvenue_ai.config import NAV_EDGES, NAV_NODES, NODE_POSITIONS


class NavigationEngine:
    """Weighted graph router with crowd penalties."""

    def __init__(self) -> None:
        self._adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in NAV_NODES}
        for u, v, w in NAV_EDGES:
            if u in self._adj and v in self._adj:
                self._adj[u].append((v, float(w)))
                self._adj[v].append((u, float(w)))
        self._crowd: Dict[str, float] = {n: 0.35 for n in NAV_NODES}
        self.active_origin: Optional[str] = None
        self.active_dest: Optional[str] = None
        self.active_path: List[str] = []

    def update_crowd(self, densities: Dict[str, float]) -> None:
        self._crowd.update(densities)

    def set_active_route(self, origin: str, dest: str, path: List[str]) -> None:
        self.active_origin = origin
        self.active_dest = dest
        self.active_path = list(path)

    def clear_active_route(self) -> None:
        self.active_origin = None
        self.active_dest = None
        self.active_path = []

    def needs_reroute(self, threshold: float = 0.82) -> bool:
        if not self.active_path or len(self.active_path) < 2:
            return False
        for node in self.active_path[1:-1]:
            if self._crowd.get(node, 0) >= threshold:
                return True
        return False

    def reroute(self) -> List[str]:
        if not self.active_origin or not self.active_dest:
            return []
        new_path = self.dijkstra(self.active_origin, self.active_dest)
        if new_path:
            self.active_path = new_path
        return new_path

    def _weight(self, u: str, v: str, base: float) -> float:
        cu = self._crowd.get(u, 0.3)
        cv = self._crowd.get(v, 0.3)
        return base * (1.0 + (cu + cv) * 1.8)

    def dijkstra(self, origin: str, destination: str) -> List[str]:
        if origin == destination:
            return [origin]
        if origin not in self._adj or destination not in self._adj:
            return []

        dist = {n: float("inf") for n in self._adj}
        prev: Dict[str, Optional[str]] = {n: None for n in self._adj}
        dist[origin] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, origin)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == destination:
                break
            for v, bw in self._adj[u]:
                nd = d + self._weight(u, v, bw)
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dist[destination] == float("inf"):
            return []

        path: List[str] = []
        cur: Optional[str] = destination
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def path_points(self, path: List[str]) -> List[Tuple[float, float]]:
        return [NODE_POSITIONS[n] for n in path if n in NODE_POSITIONS]

    def estimate_minutes(self, path: List[str]) -> int:
        if len(path) < 2:
            return 0
        total = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            for nbr, bw in self._adj.get(u, []):
                if nbr == v:
                    total += self._weight(u, v, bw)
                    break
        return max(1, int(total * 1.15))

    def instructions(self, path: List[str]) -> str:
        if len(path) < 2:
            return "Select source and destination"
        segments: List[str] = []
        for i in range(len(path) - 1):
            a = NODE_POSITIONS.get(path[i], (400, 300))
            b = NODE_POSITIONS.get(path[i + 1], (400, 300))
            dx, dy = b[0] - a[0], b[1] - a[1]
            if abs(dx) >= abs(dy):
                segments.append("West" if dx < 0 else "East")
            else:
                segments.append("North" if dy < 0 else "South")
        primary = max(set(segments), key=segments.count)
        return f"Head {primary} → turn toward {path[-1]}"
