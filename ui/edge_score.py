"""Plotly donut for the Edge Factor score."""
from __future__ import annotations

import plotly.graph_objects as go

from analysis.edge_factor import EdgeResult


def donut(edge: EdgeResult, size: int = 170) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                values=[edge.score, max(0, 100 - edge.score)],
                hole=0.78,
                sort=False,
                direction="clockwise",
                rotation=-90,
                marker=dict(colors=[edge.color, "rgba(255,255,255,0.06)"],
                            line=dict(width=0)),
                textinfo="none",
                hoverinfo="skip",
            )
        ]
    )
    fig.add_annotation(
        text=f"<b style='font-size:1.9rem'>{edge.score}</b><br>"
             f"<span style='font-size:0.7rem;opacity:0.7'>EDGE FACTOR</span>",
        showarrow=False, x=0.5, y=0.5, font=dict(color=edge.color),
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=size,
        width=size,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def gauge(value: int, label: str, color: str, height: int = 170) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number=dict(font=dict(size=34, color=color)),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=0, tickcolor="rgba(0,0,0,0)",
                          showticklabels=False),
                bar=dict(color=color, thickness=0.25),
                bgcolor="rgba(255,255,255,0.04)",
                borderwidth=0,
                steps=[
                    dict(range=[0, 25], color="rgba(255,68,102,0.18)"),
                    dict(range=[25, 45], color="rgba(255,140,80,0.16)"),
                    dict(range=[45, 55], color="rgba(255,204,0,0.16)"),
                    dict(range=[55, 75], color="rgba(120,220,140,0.14)"),
                    dict(range=[75, 100], color="rgba(0,255,136,0.18)"),
                ],
            ),
        )
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f7"),
    )
    return fig
