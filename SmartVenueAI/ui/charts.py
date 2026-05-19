"""
SmartVenue AI — Charts & Analytics Module
Plotly-based charts for crowd flow, heatmap, and queue analytics.
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from utils.config import COLORS


# ── Crowd Flow Prediction Chart ───────────────────────────────────────────────

def build_flow_chart(flow_df: pd.DataFrame) -> go.Figure:
    """Line chart of predicted crowd density over time."""
    zone_colors = {
        "North Stand":   "#0a84ff",
        "South Stand":   "#ff3366",
        "Food Court A":  "#ffcc00",
        "Gate South":    "#ff8800",
        "Washroom A-F":  "#9b59ff",
    }

    fig = go.Figure()
    for zone in flow_df["zone"].unique():
        zdf = flow_df[flow_df["zone"] == zone].sort_values("minute")
        color = zone_colors.get(zone, "#00d4ff")
        fig.add_trace(go.Scatter(
            x=zdf["minute"], y=zdf["density"],
            mode="lines", name=zone,
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(").rstrip(")") + ",0.06)"
                if color.startswith("#") else color,
        ))

    # Halftime shading
    fig.add_vrect(x0=43, x1=50,
        fillcolor="rgba(255,204,0,0.08)",
        line=dict(color="#ffcc00", width=1, dash="dot"),
        annotation_text="⏸ Half", annotation_position="top left",
        annotation_font=dict(color="#ffcc00", size=9))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7aa8d4", family="Rajdhani"),
        xaxis=dict(title="Match Minute", showgrid=True,
                   gridcolor="#0e2444", gridwidth=1,
                   zeroline=False, color="#7aa8d4"),
        yaxis=dict(title="Density", showgrid=True,
                   gridcolor="#0e2444", gridwidth=1,
                   zeroline=False, range=[0, 1], color="#7aa8d4",
                   tickformat=".0%"),
        legend=dict(font=dict(color="#7aa8d4", size=9, family="Rajdhani"),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=20, b=40),
        height=260,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0a1628", font_color="#e8f4ff",
                        bordercolor="#0a84ff", font_family="Rajdhani"),
    )
    return fig


# ── Heatmap ───────────────────────────────────────────────────────────────────

def build_heatmap(grid: np.ndarray) -> go.Figure:
    """Render crowd density heatmap from NumPy grid."""
    fig = go.Figure(go.Heatmap(
        z=grid,
        colorscale=[
            [0.0,  "rgba(0,0,0,0)"],
            [0.2,  "rgba(0,255,136,0.3)"],
            [0.5,  "rgba(255,204,0,0.6)"],
            [0.8,  "rgba(255,100,0,0.8)"],
            [1.0,  "rgba(255,0,68,0.95)"],
        ],
        showscale=False,
        hoverongaps=False,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=260,
    )
    return fig


# ── Queue Bar Chart ───────────────────────────────────────────────────────────

def build_queue_chart(queue_df: pd.DataFrame, category: str = "food") -> go.Figure:
    df = queue_df[queue_df["category"] == category].copy()
    df = df.sort_values("wait_min", ascending=True)

    colors = df["status"].map({
        "low": "#00ff88", "medium": "#ffcc00", "high": "#ff3366"
    }).fillna("#0a84ff")

    fig = go.Figure(go.Bar(
        x=df["wait_min"],
        y=df["location_name"],
        orientation="h",
        marker_color=list(colors),
        marker_line_color="rgba(0,0,0,0)",
        text=[f"{w} min" for w in df["wait_min"]],
        textposition="auto",
        textfont=dict(color="white", size=10, family="Rajdhani"),
        hovertemplate="<b>%{y}</b><br>Wait: %{x} min<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#7aa8d4", family="Rajdhani", size=10),
        xaxis=dict(title="Wait (min)", showgrid=True,
                   gridcolor="#0e2444", zeroline=False, color="#7aa8d4"),
        yaxis=dict(showgrid=False, zeroline=False, color="#7aa8d4"),
        margin=dict(l=120, r=20, t=10, b=30),
        height=200,
        bargap=0.3,
        hoverlabel=dict(bgcolor="#0a1628", font_color="#e8f4ff",
                        bordercolor="#0a84ff", font_family="Rajdhani"),
    )
    return fig


# ── Zone Donut Chart ──────────────────────────────────────────────────────────

def build_zone_donut(crowd_df: pd.DataFrame) -> go.Figure:
    """Donut chart showing occupancy distribution across zone categories."""
    cats = {
        "Stands":      ["North Stand", "South Stand", "East Stand", "West Stand"],
        "Food Courts": ["Food Court A", "Food Court B", "Food Court C"],
        "Gates":       ["Gate North", "Gate South", "Gate East", "Gate West"],
        "Other":       ["Medical Bay", "VIP Lounge"],
    }
    labels, values, colors = [], [], []
    cat_colors = {
        "Stands":      "#0a84ff",
        "Food Courts": "#ffcc00",
        "Gates":       "#00ff88",
        "Other":       "#9b59ff",
    }
    for cat, zones in cats.items():
        total = crowd_df[crowd_df["zone_name"].isin(zones)]["occupancy"].sum()
        labels.append(cat); values.append(total)
        colors.append(cat_colors[cat])

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=colors,
                    line=dict(color="#050a14", width=3)),
        textfont=dict(family="Rajdhani", size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,} people<br>%{percent}<extra></extra>",
    ))
    total = int(sum(values))
    fig.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:10px;color:#7aa8d4'>TOTAL</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color="#e8f4ff", size=16, family="Orbitron"),
        align="center",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#7aa8d4", size=9, family="Rajdhani"),
                    bgcolor="rgba(0,0,0,0)", orientation="v"),
        margin=dict(l=0, r=80, t=0, b=0),
        height=220,
        hoverlabel=dict(bgcolor="#0a1628", font_color="#e8f4ff",
                        bordercolor="#0a84ff", font_family="Rajdhani"),
    )
    return fig
