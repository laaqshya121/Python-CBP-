# 🏟️ SmartVenue AI — Futuristic Stadium Intelligence Dashboard

> A production-grade AI-powered stadium management system built entirely in Python.
> Dark cyberpunk UI · Real-time simulation · ML crowd prediction · Smart navigation

---

## ✨ Features

| Module | Tech |
|---|---|
| Live Stadium Map | Plotly interactive top-view |
| Crowd Density AI | Gradient Boosting (scikit-learn) |
| Smart Navigation | NetworkX shortest-path (3 modes) |
| Queue Prediction | ML + Poisson arrival simulation |
| AI Alert System | Rule-based + anomaly detection |
| AI Chat Assistant | Keyword-intent NLP |
| CCTV Analytics | Simulated computer vision |
| Emergency Evacuation | Multi-exit route optimizer |

---

## 🚀 Quick Start

### 1. Clone / unzip the project

```bash
cd SmartVenueAI
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501** automatically.

---

## 📁 Project Structure

```
SmartVenueAI/
├── app.py                    # Main Streamlit dashboard
├── requirements.txt
├── README.md
│
├── ui/                       # Visualization modules
│   ├── stadium_map.py        # Plotly stadium top-view
│   └── charts.py             # Flow, heatmap, queue charts
│
├── ai_models/                # AI & ML modules
│   ├── crowd_predictor.py    # GBR crowd density prediction
│   ├── route_optimizer.py    # NetworkX route engine
│   └── chat_assistant.py     # NLP chatbot
│
├── simulation/               # Real-time simulation engines
│   ├── crowd_sim.py          # Zone crowd dynamics
│   └── queue_sim.py          # Queue wait time simulator
│
├── utils/                    # Utilities
│   ├── config.py             # Colors, zones, nav graph
│   └── theme.py              # CSS dark theme injector
│
└── data/                     # Sample datasets
    ├── zones.csv             # Stadium zone capacities
    ├── queues.csv            # Queue baseline data
    └── alerts.csv            # Alert definitions
```

---

## 🎮 Dashboard Tabs

| Tab | Description |
|---|---|
| 🗺️ Map | Live top-down stadium view with density overlays |
| 🧭 Navigate | Find fastest / safest / least-crowded routes |
| ⏱️ Queues | Real-time wait times for food, washrooms, gates |
| 🚨 Alerts | AI-generated alerts with severity levels |
| 🤖 AI Chat | Natural language venue assistant |
| 📹 CCTV | Simulated camera analytics grid |

---

## 🔧 Requirements

- Python 3.9+
- All dependencies in `requirements.txt`

---

## 🖥️ VS Code Tips

1. Install the **Python** extension
2. Set your interpreter to the venv: `Ctrl+Shift+P → Python: Select Interpreter`
3. Open integrated terminal: `` Ctrl+` ``
4. Run: `streamlit run app.py`

---

## 📊 Technology Stack

- **UI**: Streamlit + custom CSS (glassmorphism, neon theme)
- **Charts**: Plotly (interactive maps, heatmaps, flow charts)
- **ML**: scikit-learn (Gradient Boosting Regressor)
- **Navigation**: NetworkX (Dijkstra's algorithm, 3 route modes)
- **Simulation**: NumPy + Pandas + SciPy
- **Fonts**: Orbitron, Rajdhani, Share Tech Mono (Google Fonts)

---

*SmartVenue AI — All simulation data is synthetic and for demonstration purposes only.*
