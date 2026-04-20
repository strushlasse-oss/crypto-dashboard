"""Plotly charts for local indicator views."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def indicator_figure(df: pd.DataFrame, title: str = "") -> go.Figure:
    """3-row figure: price + SMAs + Bollinger, RSI, MACD."""
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.22, 0.23],
        vertical_spacing=0.04,
        subplot_titles=("Preis + SMA + Bollinger", "RSI(14)", "MACD"),
    )

    x = df["time"]

    fig.add_trace(go.Scatter(x=x, y=df["close"], name="Close",
                             line=dict(color="#F7931A", width=2)), row=1, col=1)
    if "sma_50" in df:
        fig.add_trace(go.Scatter(x=x, y=df["sma_50"], name="SMA 50",
                                 line=dict(color="#4EA8DE", width=1)), row=1, col=1)
    if "sma_200" in df:
        fig.add_trace(go.Scatter(x=x, y=df["sma_200"], name="SMA 200",
                                 line=dict(color="#B983FF", width=1)), row=1, col=1)
    if "bb_upper" in df:
        fig.add_trace(go.Scatter(x=x, y=df["bb_upper"], name="BB Upper",
                                 line=dict(color="rgba(200,200,200,0.4)", width=1)),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["bb_lower"], name="BB Lower",
                                 line=dict(color="rgba(200,200,200,0.4)", width=1),
                                 fill="tonexty", fillcolor="rgba(120,120,120,0.08)"),
                      row=1, col=1)

    if "rsi_14" in df:
        fig.add_trace(go.Scatter(x=x, y=df["rsi_14"], name="RSI",
                                 line=dict(color="#E9C46A", width=1.5)),
                      row=2, col=1)
        fig.add_hline(y=70, line=dict(color="#E63946", dash="dot", width=1), row=2, col=1)
        fig.add_hline(y=30, line=dict(color="#2A9D8F", dash="dot", width=1), row=2, col=1)

    if "macd" in df:
        colors = ["#2A9D8F" if v >= 0 else "#E63946" for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=x, y=df["macd_hist"], name="Hist",
                             marker_color=colors, opacity=0.6), row=3, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["macd"], name="MACD",
                                 line=dict(color="#4EA8DE", width=1.2)), row=3, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["macd_signal"], name="Signal",
                                 line=dict(color="#F4A261", width=1.2)), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=720,
        margin=dict(l=10, r=10, t=50, b=10),
        title=title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    return fig
