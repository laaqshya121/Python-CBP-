"""Context-aware stadium AI — uses live engine data."""

import re
from typing import TYPE_CHECKING, Optional

from smartvenue_ai.database import log_chat

if TYPE_CHECKING:
    from smartvenue_ai.analytics import Analytics
    from smartvenue_ai.congestion_engine import CongestionEngine
    from smartvenue_ai.navigation_engine import NavigationEngine


class StadiumAI:
    """Knowledge engine with real-time stadium data integration."""

    def __init__(self) -> None:
        self._congestion: Optional["CongestionEngine"] = None
        self._nav: Optional["NavigationEngine"] = None
        self._analytics: Optional["Analytics"] = None
        self._user_location = "Playing Field"

    def bind(
        self,
        congestion: "CongestionEngine",
        nav: "NavigationEngine",
        analytics: "Analytics",
    ) -> None:
        self._congestion = congestion
        self._nav = nav
        self._analytics = analytics

    def set_location(self, location: str) -> None:
        self._user_location = location

    def respond(self, text: str) -> str:
        log_chat("user", text)
        lower = text.lower().strip()
        reply = self._resolve(lower)
        log_chat("assistant", reply)
        return reply

    def _resolve(self, lower: str) -> str:
        if not self._congestion:
            return "Systems initializing. Please try again in a moment."

        if re.search(r"(restroom|washroom|toilet|wc|bathroom)", lower):
            return self._nearest_washroom()
        if re.search(r"(exit|gate|leave|evacuate|fastest exit)", lower):
            return self._best_gate()
        if re.search(r"(food|eat|hungry|stall|snack|court)", lower):
            return self._best_food()
        if re.search(r"(route|navigate|path|shortest|direction|how do i get)", lower):
            return self._route_help(lower)
        if re.search(r"(crowd|busy|congest|packed|density|congestion)", lower):
            return self._crowd_analysis()
        if re.search(r"(queue|wait|prediction)", lower):
            return self._queue_prediction()
        if re.search(r"(hello|hi|help|hey)", lower):
            return (
                "SmartVenue AI online with live stadium data. "
                "Ask about restrooms, exits, food, routes, queues, or congestion."
            )
        return (
            "I have live access to crowd, queue, and navigation data. "
            "Try: 'nearest restroom', 'least crowded gate', 'shortest route to Gate B8', "
            "or 'congestion analysis'."
        )

    def _nearest_washroom(self) -> str:
        c = self._congestion
        assert c and self._nav
        targets = ["Washroom A", "Washroom B"]
        best = min(targets, key=lambda t: c.densities.get(t, 0.5))
        path = self._nav.dijkstra(self._user_location, best)
        mins = self._nav.estimate_minutes(path)
        wait = c.washroom_avg
        return (
            f"Nearest low-congestion restroom: {best} (~{mins} min walk from your area). "
            f"Current washroom avg wait: {wait} min. Path avoids high-density corridors."
        )

    def _best_gate(self) -> str:
        c = self._congestion
        assert c and self._nav
        gates = [g[0] for g in c.gate_feed]
        best_row = min(c.gate_feed, key=lambda x: x[1])
        path = self._nav.dijkstra(self._user_location, best_row[0])
        mins = self._nav.estimate_minutes(path)
        worst = max(c.gate_feed, key=lambda x: x[1])
        return (
            f"Least crowded gate: {best_row[0]} ({best_row[1]} min wait, {best_row[2]}). "
            f"Estimated walk: {mins} min. Avoid {worst[0]} ({worst[1]} min wait)."
        )

    def _best_food(self) -> str:
        c = self._congestion
        assert c
        courts = ["Food Court A", "Food Court B", "Food Court C"]
        best = min(courts, key=lambda z: c.densities.get(z, 0.5))
        dens = c.densities.get(best, 0) * 100
        return (
            f"Least crowded food area: {best} (~{dens:.0f}% density). "
            f"Food avg wait stadium-wide: {c.food_avg} min. "
            f"Food Court A is busiest — prefer {best}."
        )

    def _route_help(self, lower: str) -> str:
        assert self._nav and self._congestion
        dest = "Gate B8"
        for gate in [g[0] for g in self._congestion.gate_feed] + ["Gate East", "Gate North"]:
            if gate.lower() in lower:
                dest = gate
                break
        path = self._nav.dijkstra(self._user_location, dest)
        if not path:
            return f"No walkable path found to {dest}. Try another destination."
        mins = self._nav.estimate_minutes(path)
        instr = self._nav.instructions(path)
        hops = " → ".join(path[:5]) + ("…" if len(path) > 5 else "")
        return (
            f"Shortest congestion-aware route to {dest}: ~{mins} min.\n"
            f"{instr}\nVia: {hops}"
        )

    def _crowd_analysis(self) -> str:
        c = self._congestion
        assert c
        high = [z for z, d in c.densities.items() if d > 0.75 and "Gate" in z or "Stand" in z]
        low = [z for z, d in c.densities.items() if d < 0.35 and ("Stand" in z or "Gate" in z)]
        score = c.global_congestion_score()
        return (
            f"Stadium congestion index: {score:.0f}/100 ({c.congestion_level()}).\n"
            f"Hot zones: {', '.join(high[:4]) or 'none critical'}.\n"
            f"Clear zones: {', '.join(low[:4]) or 'monitoring'}.\n"
            f"Gate avg wait: {c.gate_avg} min."
        )

    def _queue_prediction(self) -> str:
        c = self._congestion
        a = self._analytics
        assert c and a
        pred_gate = int(a.predict_gate_wait())
        return (
            f"Queue intelligence: Gate avg {c.gate_avg} min (predicted next tick: ~{pred_gate} min). "
            f"Food {c.food_avg} min, Washroom {c.washroom_avg} min. "
            f"Trend: {'rising' if pred_gate > c.gate_avg else 'stable'}."
        )
