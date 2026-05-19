"""
SmartVenue AI — AI Chat Assistant
Simple keyword-intent NLP chatbot for venue queries.
"""

import re
import random
from typing import Tuple


# ── Intent patterns ────────────────────────────────────────────────────────────
INTENTS = [
    (r"(wait|queue|time|how long)", "queue"),
    (r"(food|eat|hungry|restaurant|stall|snack|drink)", "food"),
    (r"(washroom|toilet|bathroom|restroom|wc)", "washroom"),
    (r"(gate|entry|enter|exit|leave|out)", "gate"),
    (r"(medical|first.?aid|emergency|doctor|hurt|injur)", "medical"),
    (r"(park|parking|car)", "parking"),
    (r"(crowd|busy|congest|full|packed)", "crowd"),
    (r"(wifi|internet|signal|connect)", "wifi"),
    (r"(lost|find|where|location|navigate|direction)", "navigation"),
    (r"(vip|lounge|premium|suite)", "vip"),
    (r"(seat|section|row|block)", "seating"),
    (r"(help|hi|hello|hey|assist)", "greeting"),
    (r"(thanks|thank|great|awesome|cool)", "thanks"),
    (r"(evacuate|evacuation|danger|fire|alarm|emergency)", "emergency"),
]

RESPONSES = {
    "queue": [
        "🕐 Current wait times: Food Court A ~14 min, Gate South ~21 min, Washroom B-F ~15 min. I recommend Food Court B — only ~5 min wait right now.",
        "📊 Queue AI update: Gate East is moving fastest at 2 min wait. South Gate is backed up — use East or West instead.",
        "⚡ Live queue intel: Food Stall B2 has virtually no queue (1 min). Food Stall B1 is very busy (~34 min). Go B2!",
    ],
    "food": [
        "🍔 Food Court B is the least crowded right now (~40% capacity). Food Court A is at 81% — expect a 14-min wait. I'd suggest heading to Food Court B.",
        "🥤 Quick food options: Food Stall B2 (North-East corner) has the shortest queue — under 2 minutes. Food Court C is also relatively free.",
        "🌮 Stadium map shows Food Court A near Gate West and Food Court B near Gate East. Currently B is faster. Enjoy the game!",
    ],
    "washroom": [
        "🚻 Washroom B (East side) currently has an 8-person queue — just 1 min wait. Washroom A-Female is at ~45 people, expect 15 min. Recommend Washroom B.",
        "📍 Nearest washrooms: Level 1 by each gate, and inside each food court corridor. Washroom A-Male is currently free (3 min wait).",
        "ℹ️ Based on current data, washrooms near Gate East have the shortest queues.",
    ],
    "gate": [
        "🚪 Gate East is the least congested entry/exit right now — only ~30% capacity. Gate South is 90% — avoid if possible.",
        "🔑 All 4 gates are open. Gate West: 70% busy. Gate East: 30% (best choice). Gate North: 60%. Gate South: 90% (avoid).",
        "⚡ SmartRoute suggests using Gate East for fastest exit. Estimated clear time: 3 minutes from any stand.",
    ],
    "medical": [
        "🏥 Medical Bay is located in the South-West corner of the venue (near Gate West). Currently 8/50 capacity. 24/7 staffed. Call ext. 999 for emergencies.",
        "🩺 First Aid stations: main Medical Bay (SW corner) + smaller posts at each gate. All are lightly occupied. Stay safe!",
    ],
    "parking": [
        "🚗 Parking Lot A (North) is 65% full. Lot B (South) is 88% — nearly full. Lot C (East, 10-min walk) is only 40% full. Shuttle service available.",
        "🅿️ SmartParking tip: Use the East Lot — shortest wait for post-event exit based on current traffic flow predictions.",
    ],
    "crowd": [
        "📊 Crowd AI: South Stand is at 82% density — HIGH. North Stand at 64%, East Stand at 34% (LOW — plenty of space). West Stand at 80%.",
        "🌐 Real-time density: 3 zones currently flagged as HIGH (South Stand, Food Court A, Gate South). I recommend moving to East side for comfort.",
        "🔴 Current stadium fill: 68% total. Hotspots: South Stand, Gate South, Food Court A. Green zones: East Stand, Gate East, Medical Bay.",
    ],
    "wifi": [
        "📶 Free WiFi: Network 'SmartVenue_Guest' — no password needed. For faster speeds, use 'SmartVenue_5G' (password: VENUE2025). 50,000 concurrent users supported.",
        "🌐 WiFi coverage: 100% of seated areas covered. Speeds averaging 45 Mbps. If slow, try reconnecting — some sectors are load-balancing.",
    ],
    "navigation": [
        "🗺️ Use the Navigate tab (bottom bar) to find the optimal route between any two points. I can route you via fastest, least crowded, or safest path.",
        "📍 Tell me where you are and where you want to go! Use the Navigation panel on the right side of the Map view for turn-by-turn directions.",
        "🧭 Lost? Head to the nearest information pillar (marked with 'i' on the map) or I can calculate a route for you — just say 'take me to [destination]'.",
    ],
    "vip": [
        "⭐ VIP Lounge: Level 3, North Stand. Currently 210/300 capacity. Dedicated bar, private washrooms, 4K screens. Access with VIP wristband.",
        "🥂 VIP services: Private entry via Gate North VIP lane, dedicated food service (no queue), premium viewing deck open. Currently 70% occupied.",
    ],
    "seating": [
        "💺 Seating tip: East Stand (Blocks E1–E18) has the most space — only 34% occupied. Good sightlines from Block E9. North Stand upper tier also has availability.",
        "🎫 Check your ticket for block/row/seat. Staff at each gate can help with directions. The stadium map shows all sections in the Map tab.",
    ],
    "greeting": [
        "👋 Hello! I'm SmartVenue AI — your intelligent stadium assistant. I can help with queues, navigation, crowds, food, parking, medical, and more. What do you need?",
        "🤖 Hey there! SmartVenue AI online. Ask me about wait times, best routes, crowd levels, facilities, or anything venue-related. How can I help?",
        "🏟️ Welcome to SmartVenue Arena! I have real-time data on all zones. Ask me anything — queues, food, exits, crowd levels. Let's make your experience great!",
    ],
    "thanks": [
        "😊 Happy to help! Enjoy the event! Ask me anything else anytime.",
        "🎉 You're welcome! Have an amazing time at SmartVenue Arena!",
        "👍 Anytime! Stay safe and enjoy the game!",
    ],
    "emergency": [
        "🚨 EMERGENCY MODE: Nearest exits are Gate North (2 min) and Gate East (3 min). Follow green floor markings. DO NOT use elevators. Emergency services have been notified.",
        "🚨 If this is an emergency, call venue security: ext. 911. Evacuation routes are displayed on all screens. Move calmly to nearest exit — green overhead signs will guide you.",
    ],
    "default": [
        "🤔 I'm not sure about that specific query. I can help with: wait times, food, washrooms, gates, crowds, navigation, parking, WiFi, VIP, or emergencies. Try rephrasing?",
        "💡 I didn't quite catch that. Try asking about: 'queue times', 'food court', 'least crowded gate', 'directions to medical bay', or 'current crowd levels'.",
        "🔍 Hmm, let me think... I'm best at real-time venue data. Ask about queues, crowd density, navigation, or facilities!",
    ],
}


class ChatAssistant:
    """Keyword-intent NLP chatbot for venue queries."""

    def __init__(self):
        self._history = []

    def respond(self, user_message: str) -> str:
        """Return AI response for user message."""
        lower = user_message.lower().strip()
        intent = self._classify_intent(lower)
        replies = RESPONSES.get(intent, RESPONSES["default"])
        reply = random.choice(replies)
        self._history.append({"role": "user", "content": user_message})
        self._history.append({"role": "ai", "content": reply})
        return reply

    def _classify_intent(self, text: str) -> str:
        for pattern, intent in INTENTS:
            if re.search(pattern, text):
                return intent
        return "default"

    def get_history(self):
        return list(self._history)

    def clear_history(self):
        self._history.clear()
