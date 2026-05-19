"""
SmartVenue AI — CSS Injector
Injects the cyberpunk dark theme into Streamlit.
"""

def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

/* ── Root Variables ─────────────────────────── */
:root {
  --bg0: #050a14;
  --bg1: #080f1e;
  --bg2: #0a1628;
  --bg3: #0d1e38;
  --border: #0e2444;
  --neon: #0a84ff;
  --cyan: #00d4ff;
  --green: #00ff88;
  --yellow: #ffcc00;
  --orange: #ff8800;
  --red: #ff3366;
  --purple: #9b59ff;
  --txt1: #e8f4ff;
  --txt2: #7aa8d4;
  --txt3: #3a6080;
  --font-display: 'Orbitron', monospace;
  --font-body: 'Rajdhani', sans-serif;
  --font-mono: 'Share Tech Mono', monospace;
}

/* ── Global Reset ───────────────────────────── */
* { box-sizing: border-box; }

.stApp {
  background: var(--bg0) !important;
  font-family: var(--font-body) !important;
  color: var(--txt1) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--neon); border-radius: 2px; }

/* ── Hide Streamlit chrome ──────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container { padding: 0.5rem 1rem 1rem !important; max-width: 100% !important; }

/* ── Top Header Bar ─────────────────────────── */
.sv-header {
  background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 0 30px rgba(10,132,255,0.15);
}
.sv-logo {
  font-family: var(--font-display);
  font-size: 1.3rem; font-weight: 900;
  color: var(--neon);
  text-shadow: 0 0 20px rgba(10,132,255,0.8);
  letter-spacing: 2px;
}
.sv-logo span { color: var(--cyan); }
.sv-event-badge {
  font-family: var(--font-mono);
  font-size: 0.65rem; color: var(--cyan);
  border: 1px solid var(--cyan);
  padding: 3px 10px; border-radius: 2px;
  letter-spacing: 1px;
  animation: borderPulse 3s ease-in-out infinite;
}
@keyframes borderPulse {
  0%,100% { box-shadow: 0 0 4px var(--cyan); }
  50%      { box-shadow: 0 0 12px var(--cyan), inset 0 0 8px rgba(0,212,255,0.1); }
}
.sv-live-dot {
  display: flex; align-items: center; gap: 6px;
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--green);
}
.sv-live-dot::before {
  content: '';
  width: 8px; height: 8px; background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--green);
  animation: livePulse 1.2s ease-in-out infinite;
  display: inline-block;
}
@keyframes livePulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.4; transform: scale(0.7); }
}

/* ── Metric Cards ───────────────────────────── */
.sv-metric-card {
  background: linear-gradient(135deg, var(--bg2), var(--bg3));
  border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.2rem;
  position: relative; overflow: hidden;
  transition: border-color 0.3s, transform 0.2s;
}
.sv-metric-card:hover {
  border-color: var(--neon);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(10,132,255,0.2);
}
.sv-metric-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon), transparent);
  animation: scanline 4s ease-in-out infinite;
}
@keyframes scanline {
  0%,100% { opacity: 0.3; }
  50%      { opacity: 1; box-shadow: 0 0 10px var(--neon); }
}
.sv-metric-label {
  font-family: var(--font-mono); font-size: 0.6rem;
  color: var(--txt3); letter-spacing: 2px; text-transform: uppercase;
  margin-bottom: 0.3rem;
}
.sv-metric-value {
  font-family: var(--font-display); font-size: 1.6rem; font-weight: 700;
  color: var(--txt1); line-height: 1;
}
.sv-metric-sub {
  font-family: var(--font-body); font-size: 0.75rem;
  color: var(--txt2); margin-top: 0.2rem;
}
.sv-metric-icon {
  position: absolute; top: 0.8rem; right: 0.8rem;
  font-size: 1.4rem; opacity: 0.3;
}

/* ── Section Title ──────────────────────────── */
.sv-section-title {
  font-family: var(--font-display); font-size: 0.75rem; font-weight: 700;
  color: var(--neon); letter-spacing: 3px; text-transform: uppercase;
  margin-bottom: 0.75rem;
  display: flex; align-items: center; gap: 8px;
}
.sv-section-title::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--neon), transparent);
}

/* ── Glass Card ─────────────────────────────── */
.sv-glass {
  background: rgba(10,22,40,0.7);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: 14px; padding: 1rem;
}

/* ── Queue Cards ────────────────────────────── */
.sv-queue-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 10px; padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
  position: relative; overflow: hidden;
}
.sv-queue-card:hover { border-color: var(--cyan); }
.sv-queue-bar {
  height: 4px; border-radius: 2px;
  margin-top: 0.5rem;
  transition: width 1s ease-in-out;
  position: relative; overflow: hidden;
}
.sv-queue-bar::after {
  content: '';
  position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 2s infinite;
}
@keyframes shimmer {
  0%  { left: -100%; }
  100%{ left: 200%; }
}

/* ── Alert Badges ───────────────────────────── */
.sv-alert {
  border-radius: 8px; padding: 0.7rem 0.9rem;
  margin-bottom: 0.4rem; font-size: 0.82rem;
  font-family: var(--font-body);
  border-left: 3px solid;
  position: relative;
}
.sv-alert-critical {
  background: rgba(255,0,68,0.08);
  border-color: var(--red);
  color: #ffaabb;
}
.sv-alert-high {
  background: rgba(255,136,0,0.08);
  border-color: var(--orange);
  color: #ffcc99;
}
.sv-alert-medium {
  background: rgba(255,204,0,0.08);
  border-color: var(--yellow);
  color: #ffe066;
}
.sv-alert-low {
  background: rgba(0,255,136,0.06);
  border-color: var(--green);
  color: #99ffcc;
}
.sv-alert-blink {
  display: inline-block; width: 7px; height: 7px;
  border-radius: 50%; margin-right: 7px; vertical-align: middle;
  animation: alertBlink 0.8s ease-in-out infinite;
}
@keyframes alertBlink {
  0%,100% { opacity: 1; }
  50%      { opacity: 0.1; }
}

/* ── Navigation Panel ───────────────────────── */
.sv-nav-option {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.3rem;
  cursor: pointer; font-family: var(--font-body); font-size: 0.85rem;
  color: var(--txt2); transition: all 0.2s;
}
.sv-nav-option:hover { border-color: var(--neon); color: var(--neon); }
.sv-nav-option.selected { border-color: var(--cyan); color: var(--cyan);
  background: rgba(0,212,255,0.08); }

/* ── Route Result ───────────────────────────── */
.sv-route-box {
  background: linear-gradient(135deg, rgba(10,132,255,0.1), rgba(0,212,255,0.05));
  border: 1px solid var(--neon);
  border-radius: 10px; padding: 1rem;
  font-family: var(--font-mono); font-size: 0.78rem;
  color: var(--txt1);
}
.sv-route-step {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; color: var(--txt2);
}
.sv-route-step::before {
  content: '▸'; color: var(--neon);
}

/* ── Chat Box ───────────────────────────────── */
.sv-chat-msg-user {
  background: rgba(10,132,255,0.15);
  border: 1px solid rgba(10,132,255,0.3);
  border-radius: 10px 10px 2px 10px;
  padding: 0.6rem 0.9rem; margin: 0.3rem 0;
  margin-left: 20%; font-family: var(--font-body);
  font-size: 0.85rem; color: var(--txt1);
}
.sv-chat-msg-ai {
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 10px 10px 10px 2px;
  padding: 0.6rem 0.9rem; margin: 0.3rem 0;
  margin-right: 20%; font-family: var(--font-body);
  font-size: 0.85rem; color: var(--cyan);
}

/* ── CCTV Grid ──────────────────────────────── */
.sv-cctv-feed {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px; padding: 0.5rem;
  text-align: center; position: relative;
  font-family: var(--font-mono); font-size: 0.6rem; color: var(--txt3);
  overflow: hidden;
}
.sv-cctv-feed::before {
  content: '● REC';
  position: absolute; top: 6px; left: 8px;
  color: var(--red); font-size: 0.55rem;
  animation: recBlink 1.5s ease-in-out infinite;
}
@keyframes recBlink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }

/* ── Streamlit Widget Overrides ─────────────── */
div[data-testid="stSelectbox"] > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--txt1) !important;
}
div[data-testid="stSelectbox"] label {
  color: var(--txt2) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
}
.stButton > button {
  background: linear-gradient(135deg, var(--neon), var(--cyan)) !important;
  border: none !important; border-radius: 8px !important;
  color: var(--bg0) !important; font-family: var(--font-display) !important;
  font-weight: 700 !important; letter-spacing: 2px !important;
  text-transform: uppercase !important; font-size: 0.75rem !important;
  padding: 0.5rem 1.5rem !important;
  box-shadow: 0 4px 15px rgba(10,132,255,0.4) !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 25px rgba(10,132,255,0.6) !important;
}
div[data-testid="stTextInput"] input {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--txt1) !important;
  font-family: var(--font-mono) !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg1) !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 6px 6px 0 0 !important;
  color: var(--txt3) !important;
  font-family: var(--font-display) !important;
  font-size: 0.7rem !important; letter-spacing: 1px !important;
  text-transform: uppercase !important; padding: 0.5rem 1rem !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(10,132,255,0.1) !important;
  border-color: var(--neon) !important;
  color: var(--neon) !important;
}
[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important; padding: 0.8rem !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  color: var(--txt1) !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--font-mono) !important;
  font-size: 0.65rem !important; color: var(--txt2) !important;
  letter-spacing: 1px !important;
}
div[data-testid="column"] { padding: 0 4px !important; }
.stMarkdown p { color: var(--txt2); font-family: var(--font-body); }
</style>
"""
