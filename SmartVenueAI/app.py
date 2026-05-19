"""
SmartVenue AI — Main Dashboard
Run with: streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import time

# ── Page config (MUST be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SmartVenue AI",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Imports ────────────────────────────────────────────────────────────────────
from utils.theme import get_css
from utils.config import APP_CONFIG, NAV_NODES, COLORS
from simulation.crowd_sim import CrowdSimulator
from simulation.queue_sim import QueueSimulator
from ai_models.crowd_predictor import CrowdPredictor
from ai_models.route_optimizer import RouteOptimizer
from ai_models.chat_assistant import ChatAssistant
from ui.stadium_map import build_stadium_map
from ui.charts import build_flow_chart, build_heatmap, build_queue_chart, build_zone_donut

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown(get_css(), unsafe_allow_html=True)

# ── Session-state singletons ──────────────────────────────────────────────────
@st.cache_resource
def get_simulators():
    crowd = CrowdSimulator("data/zones.csv")
    queue = QueueSimulator("data/queues.csv")
    pred  = CrowdPredictor()
    nav   = RouteOptimizer()
    return crowd, queue, pred, nav

crowd_sim, queue_sim, predictor, navigator = get_simulators()

if "chat_assistant" not in st.session_state:
    st.session_state.chat_assistant = ChatAssistant()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "route_result" not in st.session_state:
    st.session_state.route_result = None
if "highlight_route" not in st.session_state:
    st.session_state.highlight_route = None

# ── Tick simulation ───────────────────────────────────────────────────────────
crowd_df  = crowd_sim.get_dataframe()
queue_df  = queue_sim.tick()
densities = {r["zone_name"]: r["density"] for _, r in crowd_df.iterrows()}
navigator.update_crowd_weights(densities)
flow_df   = predictor.generate_flow_prediction()
heatmap_grid = crowd_sim.get_heatmap_grid(60)
recommendations = navigator.get_recommendations(densities)

total_attendees  = crowd_sim.get_total_attendees()
congested_zones  = crowd_sim.get_congested_zones(0.70)
avg_density      = crowd_sim.get_average_density()
active_zones     = len([d for d in densities.values() if d > 0.2])
avg_wait         = int(queue_df["wait_min"].mean())

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sv-header">
  <div class="sv-logo">Smart<span>Venue</span> AI</div>
  <div class="sv-event-badge">◈ {APP_CONFIG['event_name']}</div>
  <div class="sv-live-dot">LIVE MONITORING</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Top KPI Row ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi(col, label, value, sub, icon):
    col.markdown(f"""
    <div class="sv-metric-card">
      <div class="sv-metric-label">{label}</div>
      <div class="sv-metric-value">{value}</div>
      <div class="sv-metric-sub">{sub}</div>
      <div class="sv-metric-icon">{icon}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Total Attendees", f"{total_attendees:,}", f"of {APP_CONFIG['total_capacity']:,} cap.", "🏟️")
kpi(k2, "Active Zones", str(active_zones), "of 15 monitored", "📡")
kpi(k3, "Congested Zones", str(len(congested_zones)), "above 70% density", "🔴")
kpi(k4, "Avg Density", f"{avg_density:.0%}", "across all zones", "📊")
kpi(k5, "Avg Queue Wait", f"{avg_wait} min", "all locations", "⏱️")
fill_pct = total_attendees / APP_CONFIG["total_capacity"] * 100
kpi(k6, "Venue Fill Rate", f"{fill_pct:.0f}%", "real-time estimate", "📈")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Main Tabs ──────────────────────────────────────────────────────────────────
tab_map, tab_nav, tab_queues, tab_alerts, tab_chat, tab_cctv = st.tabs([
    "🗺️  Map", "🧭  Navigate", "⏱️  Queues", "🚨  Alerts", "🤖  AI Chat", "📹  CCTV"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab_map:
    left_col, right_col = st.columns([3, 1])

    with left_col:
        st.markdown('<div class="sv-section-title">LIVE STADIUM OVERVIEW</div>',
                    unsafe_allow_html=True)

        show_heat = st.toggle("Overlay Heatmap", value=False)

        fig_map = build_stadium_map(
            zone_densities=densities,
            show_heatmap=show_heat,
            highlight_route=st.session_state.highlight_route,
        )
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

        if show_heat:
            st.markdown('<div class="sv-section-title">CROWD DENSITY HEATMAP</div>',
                        unsafe_allow_html=True)
            fig_heat = build_heatmap(heatmap_grid)
            st.plotly_chart(fig_heat, use_container_width=True,
                            config={"displayModeBar": False})

        # AI Flow Prediction
        st.markdown('<div class="sv-section-title">AI CROWD FLOW PREDICTION</div>',
                    unsafe_allow_html=True)
        fig_flow = build_flow_chart(flow_df)
        st.plotly_chart(fig_flow, use_container_width=True,
                        config={"displayModeBar": False})

    with right_col:
        # Zone density sidebar
        st.markdown('<div class="sv-section-title">ZONE STATUS</div>',
                    unsafe_allow_html=True)

        for _, row in crowd_df.sort_values("density", ascending=False).iterrows():
            pct = row["density"]
            if pct >= 0.75:
                bar_color = COLORS["neon_red"]
                badge = "🔴"
            elif pct >= 0.45:
                bar_color = COLORS["neon_yellow"]
                badge = "🟡"
            else:
                bar_color = COLORS["neon_green"]
                badge = "🟢"

            bar_w = int(pct * 100)
            st.markdown(f"""
            <div class="sv-queue-card">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-family:var(--font-body);font-size:0.78rem;
                             color:#e8f4ff;">{badge} {row['zone_name']}</span>
                <span style="font-family:var(--font-mono);font-size:0.7rem;
                             color:#7aa8d4;">{pct:.0%}</span>
              </div>
              <div class="sv-queue-bar"
                   style="width:{bar_w}%;background:{bar_color}"></div>
            </div>""", unsafe_allow_html=True)

        # Donut chart
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sv-section-title">OCCUPANCY MIX</div>',
                    unsafe_allow_html=True)
        fig_donut = build_zone_donut(crowd_df)
        st.plotly_chart(fig_donut, use_container_width=True,
                        config={"displayModeBar": False})

        # AI Recommendations
        st.markdown('<div class="sv-section-title">AI TIPS</div>',
                    unsafe_allow_html=True)
        for tip in recommendations:
            st.markdown(f"""
            <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
                        border-radius:8px;padding:0.5rem 0.75rem;margin-bottom:0.4rem;
                        font-family:Rajdhani,sans-serif;font-size:0.8rem;color:#00d4ff;">
              💡 {tip}
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NAVIGATE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_nav:
    nav_left, nav_right = st.columns([2, 1])

    with nav_left:
        st.markdown('<div class="sv-section-title">SMART NAVIGATION</div>',
                    unsafe_allow_html=True)

        origin_col, dest_col = st.columns(2)
        with origin_col:
            origin = st.selectbox("📍 CURRENT LOCATION", options=NAV_NODES, index=0)
        with dest_col:
            dest_options = [n for n in NAV_NODES if n != origin]
            destination = st.selectbox("🎯 DESTINATION", options=dest_options, index=2)

        if st.button("⚡  CALCULATE OPTIMAL ROUTES", use_container_width=True):
            routes = navigator.find_routes(origin, destination)
            st.session_state.route_result = routes
            if routes:
                # Highlight the fastest route on the map
                best_key = "fastest" if "fastest" in routes else list(routes.keys())[0]
                st.session_state.highlight_route = routes[best_key]["path"]

        if st.session_state.route_result:
            routes = st.session_state.route_result
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            r_cols = st.columns(len(routes))
            for col, (rtype, rinfo) in zip(r_cols, routes.items()):
                with col:
                    path_str = " → ".join(rinfo["path"])
                    steps_html = "".join(
                        f'<div class="sv-route-step">{step}</div>'
                        for step in rinfo["path"]
                    )
                    col.markdown(f"""
                    <div class="sv-route-box">
                      <div style="font-size:1rem;font-weight:700;
                                  color:{rinfo['color']};margin-bottom:0.5rem">
                        {rinfo['label']}
                      </div>
                      <div style="font-size:1.3rem;font-family:Orbitron,monospace;
                                  color:#e8f4ff;margin-bottom:0.5rem">
                        ⏱ {rinfo['time_min']} min
                      </div>
                      {steps_html}
                    </div>""", unsafe_allow_html=True)

        # Emergency evacuation section
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sv-section-title">EMERGENCY EVACUATION</div>',
                    unsafe_allow_html=True)

        evac_col1, evac_col2 = st.columns(2)
        with evac_col1:
            evac_zone = st.selectbox("⚠️ Incident Zone", options=NAV_NODES)
        with evac_col2:
            evac_count = st.number_input("Affected People", min_value=1, max_value=500, value=50)

        if st.button("🚨  SIMULATE EVACUATION ROUTES", use_container_width=True):
            evac_exits = ["Gate North", "Gate South", "Gate East", "Gate West"]
            evac_exits = [g for g in evac_exits if g != evac_zone]
            evac_routes = {}
            for gate in evac_exits:
                r = navigator.find_routes(evac_zone, gate)
                if r and "safest" in r:
                    evac_routes[gate] = r["safest"]
            if evac_routes:
                st.markdown("""<div class="sv-alert sv-alert-critical">
                  <span class="sv-alert-blink" style="background:#ff3366"></span>
                  🚨 EVACUATION SIMULATION ACTIVE — All exits calculated below
                </div>""", unsafe_allow_html=True)
                for gate, info in evac_routes.items():
                    path_steps = " → ".join(info["path"])
                    st.markdown(f"""
                    <div class="sv-route-box" style="margin-bottom:0.5rem">
                      <b style="color:#ff3366">Exit via {gate}</b> —
                      <span style="color:#ffcc00">~{info['time_min']} min</span><br>
                      <span style="font-size:0.7rem;color:#7aa8d4">{path_steps}</span>
                    </div>""", unsafe_allow_html=True)

    with nav_right:
        st.markdown('<div class="sv-section-title">LIVE ROUTE MAP</div>',
                    unsafe_allow_html=True)
        fig_nav_map = build_stadium_map(
            zone_densities=densities,
            highlight_route=st.session_state.highlight_route,
        )
        st.plotly_chart(fig_nav_map, use_container_width=True,
                        config={"displayModeBar": False})

        # Walking time legend
        st.markdown("""
        <div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;
                    color:#3a6080;border-top:1px solid #0e2444;padding-top:0.5rem">
          <div style="color:#7aa8d4;margin-bottom:4px">📏 DISTANCE LEGEND</div>
          ▸ Average walking speed: 1.4 m/s<br>
          ▸ Base edge weight = walking minutes<br>
          ▸ Crowd penalty applied dynamically
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — QUEUES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_queues:
    st.markdown('<div class="sv-section-title">REAL-TIME QUEUE INTELLIGENCE</div>',
                unsafe_allow_html=True)

    q_food, q_wash, q_gate = st.columns(3)

    def render_queue_section(col, category: str, title: str, icon: str):
        df_cat = queue_df[queue_df["category"] == category].sort_values("wait_min")
        with col:
            col.markdown(f'<div class="sv-section-title">{icon} {title}</div>',
                         unsafe_allow_html=True)
            for _, row in df_cat.iterrows():
                wait = row["wait_min"]
                q_len = row["queue_length"]
                status = row["status"]
                color = {"low": "#00ff88", "medium": "#ffcc00", "high": "#ff3366"}.get(status, "#0a84ff")
                bar_w = min(100, int(q_len / 1.5))
                col.markdown(f"""
                <div class="sv-queue-card">
                  <div style="display:flex;justify-content:space-between">
                    <span style="font-family:Rajdhani,sans-serif;font-size:0.82rem;
                                 color:#e8f4ff;font-weight:600">{row['location_name']}</span>
                    <span style="font-family:Orbitron,monospace;font-size:0.85rem;
                                 color:{color};font-weight:700">{wait} min</span>
                  </div>
                  <div style="font-family:Share Tech Mono,monospace;font-size:0.62rem;
                              color:#3a6080;margin-top:2px">{q_len} people in queue</div>
                  <div class="sv-queue-bar" style="width:{bar_w}%;background:{color}"></div>
                </div>""", unsafe_allow_html=True)

            fig_bar = build_queue_chart(queue_df, category)
            col.plotly_chart(fig_bar, use_container_width=True,
                             config={"displayModeBar": False})

    render_queue_section(q_food,  "food",        "FOOD STALLS",   "🍔")
    render_queue_section(q_wash,  "washroom",    "WASHROOMS",     "🚻")
    render_queue_section(q_gate,  "gate",        "ENTRY GATES",   "🚪")

    # ML Prediction hint
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(10,132,255,0.06);border:1px solid rgba(10,132,255,0.2);
                border-radius:10px;padding:0.75rem 1rem;
                font-family:Share Tech Mono,monospace;font-size:0.72rem;color:#3a6080">
      🤖 <span style="color:#0a84ff">ML ENGINE</span> — Queue times predicted using
      Gradient Boosting Regressor trained on 10,000+ historical data points.
      Halftime surge model active. Predictions update every 3 seconds.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ALERTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown('<div class="sv-section-title">AI ALERT SYSTEM</div>',
                unsafe_allow_html=True)

    alerts_df = pd.read_csv("data/alerts.csv")
    active_alerts = alerts_df[alerts_df["active"] == True].copy()

    al1, al2 = st.columns([2, 1])

    with al1:
        for _, alert in active_alerts.sort_values("severity",
            key=lambda x: x.map({"critical":0,"high":1,"medium":2,"low":3})).iterrows():

            sev = alert["severity"]
            cls = f"sv-alert-{sev}"
            dot_color = {
                "critical": "#ff0044", "high": "#ff8800",
                "medium": "#ffcc00", "low": "#00ff88"
            }.get(sev, "#0a84ff")
            icon = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}.get(sev)

            st.markdown(f"""
            <div class="sv-alert {cls}">
              <span class="sv-alert-blink" style="background:{dot_color}"></span>
              {icon} <b>[{alert['zone']}]</b> {alert['message']}
              <span style="float:right;font-size:0.7rem;opacity:0.6">
                {alert['timestamp'].split(' ')[1]}
              </span>
            </div>""", unsafe_allow_html=True)

        # Generate live alert
        if st.button("⚡  GENERATE SIMULATED ALERT"):
            import random
            zone = random.choice(["North Stand", "Gate East", "Food Court A", "West Stand"])
            msgs = [
                f"Crowd density spike detected at {zone}",
                f"Queue backing up at {zone} — action recommended",
                f"Staff requested at {zone}",
                f"Movement anomaly detected near {zone}",
            ]
            sevs = ["medium", "high", "critical"]
            sev = random.choice(sevs)
            dot = {"critical":"#ff0044","high":"#ff8800","medium":"#ffcc00"}.get(sev)
            icon = {"critical":"🚨","high":"⚠️","medium":"⚡"}.get(sev)
            st.markdown(f"""
            <div class="sv-alert sv-alert-{sev}" style="margin-top:0.5rem">
              <span class="sv-alert-blink" style="background:{dot}"></span>
              {icon} <b>[LIVE — {zone}]</b> {random.choice(msgs)}
              <span style="float:right;font-size:0.7rem;opacity:0.6">NOW</span>
            </div>""", unsafe_allow_html=True)

    with al2:
        # Alert summary stats
        sev_counts = active_alerts["severity"].value_counts()
        st.markdown('<div class="sv-section-title">ALERT SUMMARY</div>',
                    unsafe_allow_html=True)

        for sev, label, color in [
            ("critical", "CRITICAL", "#ff0044"),
            ("high",     "HIGH",     "#ff8800"),
            ("medium",   "MEDIUM",   "#ffcc00"),
            ("low",      "LOW",      "#00ff88"),
        ]:
            count = int(sev_counts.get(sev, 0))
            st.markdown(f"""
            <div class="sv-metric-card" style="margin-bottom:0.4rem">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-family:Share Tech Mono,monospace;font-size:0.7rem;
                             color:{color};letter-spacing:1px">{label}</span>
                <span style="font-family:Orbitron,monospace;font-size:1.4rem;
                             font-weight:700;color:{color}">{count}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # Smart recommendations
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sv-section-title">SMART ACTIONS</div>',
                    unsafe_allow_html=True)
        actions = [
            ("Open Gate C overflow lane", "high"),
            ("Deploy staff to Gate South", "high"),
            ("Announce Food Court B availability", "medium"),
            ("Alert medical team on standby", "medium"),
        ]
        for action, priority in actions:
            p_color = "#ff8800" if priority == "high" else "#ffcc00"
            st.markdown(f"""
            <div style="background:rgba(8,15,30,0.8);border:1px solid {p_color}22;
                        border-left:3px solid {p_color};border-radius:6px;
                        padding:0.5rem 0.75rem;margin-bottom:0.3rem;
                        font-family:Rajdhani,sans-serif;font-size:0.78rem;
                        color:#e8f4ff">
              → {action}
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — AI CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    chat_col, _ = st.columns([2, 1])
    with chat_col:
        st.markdown('<div class="sv-section-title">AI VENUE ASSISTANT</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
                    border-radius:10px;padding:0.75rem;margin-bottom:1rem;
                    font-family:Rajdhani,sans-serif;font-size:0.82rem;color:#00d4ff">
          🤖 SmartVenue AI Assistant — I can answer questions about queues, navigation,
          crowd levels, facilities, food, parking, and emergencies.
        </div>""", unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="sv-chat-msg-user">{msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="sv-chat-msg-ai">{msg["content"]}</div>',
                            unsafe_allow_html=True)

        # Input
        user_input = st.text_input("Type your question...",
                                   key="chat_input",
                                   placeholder="e.g. Which food court has the shortest queue?")

        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            if st.button("📨  SEND", use_container_width=True):
                if user_input and user_input.strip():
                    assistant = st.session_state.chat_assistant
                    reply = assistant.respond(user_input)
                    st.session_state.chat_history.append(
                        {"role": "user", "content": user_input})
                    st.session_state.chat_history.append(
                        {"role": "ai", "content": reply})
                    st.rerun()
        with btn_col2:
            if st.button("🗑️ Clear"):
                st.session_state.chat_history = []
                st.session_state.chat_assistant.clear_history()
                st.rerun()

        # Quick prompts
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sv-section-title">QUICK QUESTIONS</div>',
                    unsafe_allow_html=True)
        quick = [
            "Which gate has the shortest queue?",
            "Where's the nearest food court?",
            "What's the current crowd level?",
            "How do I get to the medical bay?",
        ]
        qc = st.columns(2)
        for i, q in enumerate(quick):
            with qc[i % 2]:
                if st.button(q, use_container_width=True, key=f"quick_{i}"):
                    assistant = st.session_state.chat_assistant
                    reply = assistant.respond(q)
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    st.session_state.chat_history.append({"role": "ai", "content": reply})
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CCTV
# ═══════════════════════════════════════════════════════════════════════════════
with tab_cctv:
    st.markdown('<div class="sv-section-title">SIMULATED CCTV ANALYTICS</div>',
                unsafe_allow_html=True)

    cctv_feeds = [
        ("CAM-01", "Gate North",    0.60),
        ("CAM-02", "Gate South",    0.90),
        ("CAM-03", "North Stand",   0.64),
        ("CAM-04", "South Stand",   0.82),
        ("CAM-05", "Food Court A",  0.81),
        ("CAM-06", "Food Court B",  0.40),
        ("CAM-07", "East Stand",    0.34),
        ("CAM-08", "Medical Bay",   0.16),
    ]

    cols = st.columns(4)
    for i, (cam_id, zone, density) in enumerate(cctv_feeds):
        col = cols[i % 4]
        pct = int(density * 100)
        bar_color = "#ff3366" if density > 0.75 else "#ffcc00" if density > 0.45 else "#00ff88"

        # Simulated camera grid using ASCII art / colored blocks
        import random as _rand
        _rand.seed(i * 17 + int(time.time() / 5))
        crowd_chars = "".join(
            _rand.choice(["█","▓","░"," "]) for _ in range(int(density * 30))
        ) + " " * (30 - int(density * 30))

        col.markdown(f"""
        <div class="sv-cctv-feed">
          <div style="font-family:Share Tech Mono,monospace;font-size:0.58rem;
                      color:#3a6080;margin-top:14px;background:#020508;
                      padding:6px;border-radius:4px;text-align:left;
                      line-height:1.4;letter-spacing:0px;">
            <span style="color:#0a84ff">{cam_id}</span> | {zone}<br>
            <span style="color:{bar_color}">{crowd_chars[:15]}</span>
            <span style="color:{bar_color}66">{crowd_chars[15:]}</span><br>
            <span style="color:{bar_color}">■</span>
            DENSITY: <span style="color:{bar_color}">{pct}%</span><br>
            MOTION: {'HIGH' if density>0.7 else 'MED' if density>0.4 else 'LOW'} |
            PERSONS: ~{int(density*200)}
          </div>
          <div style="font-family:Share Tech Mono,monospace;font-size:0.55rem;
                      color:#3a6080;margin-top:4px;">{cam_id} ◈ LIVE</div>
        </div>""", unsafe_allow_html=True)

    # Analytics row
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sv-section-title">CCTV AI ANALYTICS</div>',
                unsafe_allow_html=True)

    an1, an2, an3 = st.columns(3)
    with an1:
        st.markdown("""
        <div class="sv-metric-card">
          <div class="sv-metric-label">Active Cameras</div>
          <div class="sv-metric-value">8 / 8</div>
          <div class="sv-metric-sub">All feeds online</div>
          <div class="sv-metric-icon">📹</div>
        </div>""", unsafe_allow_html=True)
    with an2:
        st.markdown("""
        <div class="sv-metric-card">
          <div class="sv-metric-label">Motion Alerts</div>
          <div class="sv-metric-value" style="color:#ff8800">3</div>
          <div class="sv-metric-sub">High motion zones</div>
          <div class="sv-metric-icon">🎯</div>
        </div>""", unsafe_allow_html=True)
    with an3:
        st.markdown("""
        <div class="sv-metric-card">
          <div class="sv-metric-label">AI Object Detection</div>
          <div class="sv-metric-value" style="color:#00ff88">Active</div>
          <div class="sv-metric-sub">YOLOv8 simulation mode</div>
          <div class="sv-metric-icon">🤖</div>
        </div>""", unsafe_allow_html=True)

# ── Auto-refresh footer ────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1rem;
            font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#1a3050;
            border-top:1px solid #0e2444;margin-top:1rem">
  SmartVenue AI ◈ v2.5.0 ◈ All data is simulated for demonstration purposes ◈
  Powered by Streamlit · Plotly · scikit-learn · NetworkX
</div>""", unsafe_allow_html=True)

# Auto-refresh every 5s via meta tag
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="autorefresh")
except ImportError:
    pass
