"""
SmartVenue AI — Stadium Map Visualization
Renders the top-down stadium overview using Plotly.
"""

import plotly.graph_objects as go
from typing import Dict, Optional
from utils.config import COLORS, PLOTLY_THEME


def density_to_color(density: float, alpha: float = 0.75) -> str:
    """Map 0‒1 density to a neon color."""
    if density >= 0.75:
        return f"rgba(255, 51, 102, {alpha})"   # red
    if density >= 0.45:
        return f"rgba(255, 204, 0, {alpha})"    # yellow
    return f"rgba(0, 255, 136, {alpha})"         # green


def density_to_glow(density: float) -> str:
    if density >= 0.75: return "#ff3366"
    if density >= 0.45: return "#ffcc00"
    return "#00ff88"


def build_stadium_map(
    zone_densities: Optional[Dict[str, float]] = None,
    show_heatmap: bool = False,
    highlight_route: Optional[list] = None,
) -> go.Figure:
    """
    Build the interactive stadium top-view map.
    zone_densities: dict of zone_name → 0‒1 density.
    """
    if zone_densities is None:
        zone_densities = {}

    fig = go.Figure()

    # ── Background pitch ──────────────────────────────────────────────────────
    # Outer stadium ring (use circle type — ellipse not supported in this Plotly version)
    fig.add_shape(type="circle",
        x0=0.02, y0=0.02, x1=0.98, y1=0.98,
        fillcolor="rgba(5,20,40,0.9)", line=dict(color="#0a84ff", width=2))

    # Playing field (green)
    fig.add_shape(type="rect",
        x0=0.27, y0=0.28, x1=0.73, y1=0.72,
        fillcolor="rgba(0,80,30,0.85)",
        line=dict(color="#00ff88", width=1.5))

    # Field markings
    # Center circle
    fig.add_shape(type="circle",
        x0=0.43, y0=0.43, x1=0.57, y1=0.57,
        fillcolor="rgba(0,0,0,0)",
        line=dict(color="rgba(255,255,255,0.35)", width=1))
    # Center line
    fig.add_shape(type="line", x0=0.5, y0=0.28, x1=0.5, y1=0.72,
        line=dict(color="rgba(255,255,255,0.3)", width=1))
    # Goal boxes
    for y0, y1 in [(0.28, 0.37), (0.63, 0.72)]:
        fig.add_shape(type="rect",
            x0=0.40, y0=y0, x1=0.60, y1=y1,
            fillcolor="rgba(0,0,0,0)",
            line=dict(color="rgba(255,255,255,0.25)", width=1))
    # Center spot
    fig.add_trace(go.Scatter(
        x=[0.5], y=[0.5], mode="markers",
        marker=dict(size=6, color="rgba(255,255,255,0.4)"),
        showlegend=False, hoverinfo="skip"
    ))

    # ── Stands ────────────────────────────────────────────────────────────────
    stands = [
        ("North Stand",  0.27, 0.73, 0.77, 0.92),
        ("South Stand",  0.27, 0.73, 0.08, 0.23),
        ("East Stand",   0.76, 0.91, 0.28, 0.72),
        ("West Stand",   0.09, 0.24, 0.28, 0.72),
    ]
    for name, x0, x1, y0, y1 in stands:
        density = zone_densities.get(name, 0.5)
        color = density_to_color(density, 0.65)
        border = density_to_glow(density)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=color, line=dict(color=border, width=1.5))
        # Label
        mx, my = (x0+x1)/2, (y0+y1)/2
        pct = int(density * 100)
        fig.add_annotation(x=mx, y=my, text=f"<b>{name.split()[0]}</b><br>{pct}%",
            showarrow=False, font=dict(size=9, color="white", family="Rajdhani"),
            align="center")

    # ── Corner facilities ─────────────────────────────────────────────────────
    corners = [
        ("Food Court A", 0.09, 0.22, 0.09, 0.22, "🍔"),
        ("Food Court B", 0.78, 0.91, 0.09, 0.22, "🍔"),
        ("Food Court C", 0.78, 0.91, 0.78, 0.91, "🍔"),
        ("Medical Bay",  0.09, 0.22, 0.78, 0.91, "🏥"),
    ]
    for name, x0, x1, y0, y1, icon in corners:
        density = zone_densities.get(name, 0.3)
        color = density_to_color(density, 0.7)
        border = density_to_glow(density)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=color, line=dict(color=border, width=1.5))
        mx, my = (x0+x1)/2, (y0+y1)/2
        short = name.replace("Food Court ", "FC-")
        fig.add_annotation(x=mx, y=my, text=f"{icon}<br><b>{short}</b>",
            showarrow=False, font=dict(size=8, color="white", family="Rajdhani"),
            align="center")

    # ── Gates ─────────────────────────────────────────────────────────────────
    gates = [
        ("Gate North", 0.46, 0.54, 0.93, 0.99, "▲"),
        ("Gate South", 0.46, 0.54, 0.01, 0.07, "▼"),
        ("Gate East",  0.93, 0.99, 0.46, 0.54, "▶"),
        ("Gate West",  0.01, 0.07, 0.46, 0.54, "◀"),
    ]
    for name, x0, x1, y0, y1, arrow in gates:
        density = zone_densities.get(name, 0.4)
        color = density_to_color(density, 0.8)
        border = density_to_glow(density)
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=color, line=dict(color=border, width=2))
        mx, my = (x0+x1)/2, (y0+y1)/2
        fig.add_annotation(x=mx, y=my, text=f"{arrow}<br><b>G{name[-1]}</b>",
            showarrow=False, font=dict(size=8, color="white", family="Rajdhani"),
            align="center")

    # ── VIP Lounge ────────────────────────────────────────────────────────────
    density = zone_densities.get("VIP Lounge", 0.5)
    color = density_to_color(density, 0.75)
    fig.add_shape(type="rect", x0=0.39, y0=0.84, x1=0.61, y1=0.92,
        fillcolor="rgba(155, 89, 255, 0.5)",
        line=dict(color="#9b59ff", width=1.5))
    fig.add_annotation(x=0.5, y=0.88, text="⭐ VIP",
        showarrow=False, font=dict(size=8, color="#e0ccff", family="Rajdhani"))

    # ── Route highlight ───────────────────────────────────────────────────────
    if highlight_route:
        from utils.config import STADIUM_ZONES
        route_x, route_y = [], []
        for node in highlight_route:
            if node in STADIUM_ZONES:
                b = STADIUM_ZONES[node]
                route_x.append((b["x"][0] + b["x"][1]) / 2)
                route_y.append((b["y"][0] + b["y"][1]) / 2)
        if len(route_x) > 1:
            fig.add_trace(go.Scatter(
                x=route_x, y=route_y, mode="lines+markers",
                line=dict(color="#00ff88", width=3, dash="dot"),
                marker=dict(size=10, color="#00ff88",
                            line=dict(color="white", width=2)),
                showlegend=False, hoverinfo="skip"
            ))

    # ── Pulse nodes (animated via size wobble hack) ───────────────────────────
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    all_zones = {**{s[0]: ((s[1]+s[2])/2, (s[3]+s[4])/2) for s in stands},
                 **{c[0]: ((c[1]+c[2])/2, (c[3]+c[4])/2) for c in corners},
                 **{g[0]: ((g[1]+g[2])/2, (g[3]+g[4])/2) for g in gates}}
    for zname, (zx, zy) in all_zones.items():
        d = zone_densities.get(zname, 0.3)
        node_x.append(zx); node_y.append(zy)
        node_text.append(f"<b>{zname}</b><br>Density: {d:.0%}")
        node_color.append(density_to_glow(d))
        node_size.append(10 + d * 14)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers",
        marker=dict(size=node_size, color=node_color,
                    line=dict(color="rgba(255,255,255,0.6)", width=1),
                    opacity=0.7),
        text=node_text, hovertemplate="%{text}<extra></extra>",
        showlegend=False
    ))

    # ── Legend ────────────────────────────────────────────────────────────────
    for level, color, label in [
        ("low",    "#00ff88", "Low (<45%)"),
        ("medium", "#ffcc00", "Medium (45–75%)"),
        ("high",   "#ff3366", "High (>75%)"),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=color),
            name=label, showlegend=True
        ))

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,10,20,0.95)",
        xaxis=dict(range=[0, 1], showgrid=False, zeroline=False,
                   showticklabels=False, constrain="domain"),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False,
                   showticklabels=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        legend=dict(
            orientation="h", x=0, y=-0.02,
            font=dict(color="#7aa8d4", size=10, family="Rajdhani"),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#0a1628", font_color="#e8f4ff",
            bordercolor="#0a84ff", font_family="Rajdhani"
        ),
    )
    return fig
