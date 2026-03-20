"""
Chart Utility — Standardized Plotly chart builders.

Consistent styling across all dashboard pages.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Brand colors ──
COLORS = {
    "primary": "#2E6DA4",
    "secondary": "#1B2A4A",
    "accent": "#00C9A7",
    "warning": "#F5A623",
    "danger": "#E74C3C",
    "light": "#F5F7FA",
    "text": "#333333",
}

CATEGORY_COLORS = {
    "Technology": "#2E6DA4",
    "Furniture": "#00C9A7",
    "Office Supplies": "#F5A623",
}

REGION_COLORS = {
    "West": "#2E6DA4",
    "East": "#00C9A7",
    "Central": "#F5A623",
    "South": "#E74C3C",
}

SEGMENT_COLORS = {
    "Consumer": "#2E6DA4",
    "Corporate": "#00C9A7",
    "Home Office": "#F5A623",
}


def apply_layout(fig, title: str = "", height: int = 400):
    """Apply consistent layout to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=COLORS["secondary"])),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color=COLORS["text"]),
        height=height,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0")
    fig.update_yaxes(showgrid=True, gridcolor="#F0F0F0", linecolor="#E0E0E0")
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
               color: str = None, y2: str = None, height: int = 400) -> go.Figure:
    """Create a line chart with optional dual axis."""
    if color:
        fig = px.line(df, x=x, y=y, color=color, markers=True)
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[x], y=df[y], mode="lines+markers",
            name=y.replace("_", " ").title(),
            line=dict(color=COLORS["primary"], width=2),
            marker=dict(size=5),
        ))

    if y2 and not color:
        fig.add_trace(go.Scatter(
            x=df[x], y=df[y2], mode="lines+markers",
            name=y2.replace("_", " ").title(),
            line=dict(color=COLORS["accent"], width=2, dash="dash"),
            marker=dict(size=5),
            yaxis="y2",
        ))
        fig.update_layout(
            yaxis2=dict(
                title=y2.replace("_", " ").title(),
                overlaying="y", side="right",
                showgrid=False,
            )
        )

    return apply_layout(fig, title, height)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
              color: str = None, orientation: str = "v",
              color_map: dict = None, height: int = 400) -> go.Figure:
    """Create a bar chart."""
    if orientation == "h":
        fig = px.bar(df, x=y, y=x, orientation="h", color=color,
                     color_discrete_map=color_map)
    else:
        fig = px.bar(df, x=x, y=y, color=color,
                     color_discrete_map=color_map)

    if not color:
        fig.update_traces(marker_color=COLORS["primary"])

    return apply_layout(fig, title, height)


def pie_chart(df: pd.DataFrame, values: str, names: str,
              title: str = "", color_map: dict = None, height: int = 400) -> go.Figure:
    """Create a donut chart."""
    fig = px.pie(df, values=values, names=names, hole=0.45,
                 color=names, color_discrete_map=color_map)
    fig.update_traces(textposition="outside", textinfo="label+percent")
    return apply_layout(fig, title, height)


def scatter_chart(df: pd.DataFrame, x: str, y: str, size: str = None,
                  text: str = None, title: str = "", height: int = 400) -> go.Figure:
    """Create a scatter plot."""
    fig = px.scatter(df, x=x, y=y, size=size, text=text,
                     color_discrete_sequence=[COLORS["primary"]])
    if text:
        fig.update_traces(textposition="top center", textfont_size=10)
    return apply_layout(fig, title, height)


def heatmap(df: pd.DataFrame, x: str, y: str, values: str,
            title: str = "", height: int = 400) -> go.Figure:
    """Create a heatmap from long-format data."""
    pivot = df.pivot_table(index=y, columns=x, values=values, aggfunc="sum").fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#F5F7FA"], [0.5, "#2E6DA4"], [1, "#1B2A4A"]],
        texttemplate="%{z:,.0f}",
        textfont={"size": 11},
        hovertemplate="Segment: %{y}<br>Region: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
    ))

    return apply_layout(fig, title, height)


def stacked_bar(df: pd.DataFrame, x: str, y: str, color: str,
                title: str = "", color_map: dict = None, height: int = 400) -> go.Figure:
    """Create a stacked bar chart."""
    fig = px.bar(df, x=x, y=y, color=color, barmode="stack",
                 color_discrete_map=color_map)
    return apply_layout(fig, title, height)
