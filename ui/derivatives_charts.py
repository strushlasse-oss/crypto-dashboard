"""CVD, Open Interest and Funding Rate charts."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import derivatives as deriv
from ui.styles import GREEN, RED, YELLOW, TEXT_DIM, TEXT_MUTED, ACCENT, BG

_PAPER = "rgba(0,0,0,0)"
_PLOT  = "rgba(0,0,0,0)"
_GRID  = "rgba(255,255,255,0.06)"
_FONT  = dict(color=TEXT_DIM, size=11)

INTERVAL_OPTS = {"1h": "1H", "4h": "4H", "1d": "1D"}


def _base_layout(title: str, height: int = 220) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT_DIM, size=11), x=0, xanchor="left"),
        height=height,
        margin=dict(l=0, r=0, t=28, b=0),
        paper_bgcolor=_PAPER,
        plot_bgcolor=_PLOT,
        font=_FONT,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color=TEXT_MUTED),
            showline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=_GRID, zeroline=False,
            tickfont=dict(size=10, color=TEXT_MUTED),
            showline=False,
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111", bordercolor=_GRID, font_size=11),
        legend=dict(font=dict(size=10, color=TEXT_DIM), bgcolor="rgba(0,0,0,0)"),
    )


# ── CVD ────────────────────────────────────────────────────────────────────────

def _cvd_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    last_cvd = float(df["cvd"].iloc[-1])
    cvd_color = GREEN if last_cvd >= 0 else RED

    # Delta bars (buy/sell pressure per candle)
    fig = go.Figure()
    bar_colors = [GREEN if d >= 0 else RED for d in df["delta"]]
    fig.add_trace(go.Bar(
        x=df["time"], y=df["delta"],
        marker_color=bar_colors,
        opacity=0.45,
        name="Delta",
        showlegend=True,
    ))
    # CVD line
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["cvd"],
        mode="lines",
        line=dict(color=cvd_color, width=2),
        name="CVD",
        yaxis="y2",
    ))
    # Zero line
    fig.add_hline(y=0, line_color=_GRID, line_width=1, yref="y")

    layout = _base_layout("CVD — Cumulative Volume Delta")
    layout["yaxis2"] = dict(
        overlaying="y", side="right",
        showgrid=False, zeroline=False,
        tickfont=dict(size=10, color=TEXT_MUTED),
    )
    layout["legend"] = dict(
        orientation="h", y=1.02, x=1, xanchor="right",
        font=dict(size=10, color=TEXT_DIM), bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**layout)
    return fig


# ── Open Interest ──────────────────────────────────────────────────────────────

def _oi_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    oi_change = float(df["oi"].iloc[-1]) - float(df["oi"].iloc[0])
    area_color = GREEN if oi_change >= 0 else RED

    def _rgb(c: str) -> str:
        h = c.lstrip("#")
        return f"{int(h[:2],16)},{int(h[2:4],16)},{int(h[4:],16)}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["oi"],
        mode="lines",
        line=dict(color=area_color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({_rgb(area_color)},0.12)",
        name="OI (Contracts)",
    ))
    # OI USD on secondary axis
    fig.add_trace(go.Scatter(
        x=df["time"], y=df["oi_usd"] / 1e6,
        mode="lines",
        line=dict(color=ACCENT, width=1.5, dash="dot"),
        name="OI (Mio USD)",
        yaxis="y2",
    ))

    layout = _base_layout("Open Interest")
    layout["yaxis2"] = dict(
        overlaying="y", side="right",
        showgrid=False, zeroline=False,
        tickformat=".0f", ticksuffix="M",
        tickfont=dict(size=10, color=TEXT_MUTED),
    )
    layout["legend"] = dict(
        orientation="h", y=1.02, x=1, xanchor="right",
        font=dict(size=10, color=TEXT_DIM), bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(**layout)
    return fig


# ── Funding Rate ───────────────────────────────────────────────────────────────

def _funding_fig(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()

    bar_colors = [GREEN if r >= 0 else RED for r in df["rate"]]
    current = float(df["rate"].iloc[-1])
    annualized = current * 3 * 365  # 3 payments/day

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["time"], y=df["rate"],
        marker_color=bar_colors,
        name="Funding %",
    ))
    fig.add_hline(y=0, line_color=_GRID, line_width=1)

    layout = _base_layout("Funding Rate")
    layout["yaxis"]["tickformat"] = ".4f"
    layout["yaxis"]["ticksuffix"] = "%"
    layout["annotations"] = [dict(
        x=1, y=1.08, xref="paper", yref="paper",
        text=f"Aktuell: <b>{current:+.4f}%</b> · Annualisiert: <b>{annualized:+.1f}%</b>",
        showarrow=False, font=dict(size=11, color=TEXT_DIM),
        xanchor="right",
    )]
    fig.update_layout(**layout)
    return fig


# ── Public renderer ────────────────────────────────────────────────────────────

def render(coin_id: str) -> None:
    """Render CVD, OI and Funding Rate section for a coin."""
    interval_label = st.session_state.get(f"deriv_interval_{coin_id}", "1h")

    col_ctrl, _ = st.columns([2, 5])
    with col_ctrl:
        chosen = st.segmented_control(
            "Intervall",
            options=list(INTERVAL_OPTS.keys()),
            default=interval_label,
            key=f"deriv_interval_{coin_id}",
            label_visibility="collapsed",
        )
    interval = chosen or interval_label

    cvd_df = deriv.get_cvd(coin_id, interval=interval)
    oi_df  = deriv.get_open_interest(coin_id)
    fr_df  = deriv.get_funding_rate(coin_id)

    no_futures = oi_df.empty and fr_df.empty

    # CVD (always — from spot)
    with st.container(border=True):
        if cvd_df.empty:
            st.markdown(
                f"<div class='pcard-title'>CVD</div>"
                f"<div class='pcard-sub'>Kein CVD für diesen Coin verfügbar.</div>",
                unsafe_allow_html=True,
            )
        else:
            last_cvd = float(cvd_df["cvd"].iloc[-1])
            cvd_color = GREEN if last_cvd >= 0 else RED
            direction = "Käufer dominieren" if last_cvd >= 0 else "Verkäufer dominieren"
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"margin-bottom:0.3rem'>"
                f"<div class='pcard-title' style='margin:0'>CVD — Cumulative Volume Delta</div>"
                f"<span style='font-size:0.82rem;font-weight:700;color:{cvd_color}'>"
                f"{direction}</span></div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(_cvd_fig(cvd_df), width="stretch",
                            config={"displayModeBar": False}, key=f"cvd_{coin_id}_{interval}")

    # OI + Funding (futures — may not be available for all coins)
    if no_futures:
        st.markdown(
            f"<div class='pcard-sub' style='margin-top:0.5rem'>"
            f"OI & Funding Rate: Kein Futures-Markt auf Binance für diesen Coin.</div>",
            unsafe_allow_html=True,
        )
        return

    oi_col, fr_col = st.columns(2)

    with oi_col:
        with st.container(border=True):
            if oi_df.empty:
                st.markdown(
                    "<div class='pcard-title'>Open Interest</div>"
                    "<div class='pcard-sub'>Nicht verfügbar.</div>",
                    unsafe_allow_html=True,
                )
            else:
                oi_change = float(oi_df["oi"].iloc[-1]) - float(oi_df["oi"].iloc[0])
                oi_color = GREEN if oi_change >= 0 else RED
                trend_txt = f"{'▲' if oi_change >= 0 else '▼'} {oi_change:+,.0f} Contracts"
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;align-items:center;"
                    f"margin-bottom:0.3rem'>"
                    f"<div class='pcard-title' style='margin:0'>Open Interest</div>"
                    f"<span style='font-size:0.82rem;font-weight:700;color:{oi_color}'>"
                    f"{trend_txt}</span></div>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(_oi_fig(oi_df), width="stretch",
                                config={"displayModeBar": False}, key=f"oi_{coin_id}")

    with fr_col:
        with st.container(border=True):
            if fr_df.empty:
                st.markdown(
                    "<div class='pcard-title'>Funding Rate</div>"
                    "<div class='pcard-sub'>Nicht verfügbar.</div>",
                    unsafe_allow_html=True,
                )
            else:
                current_fr = float(fr_df["rate"].iloc[-1])
                fr_color = GREEN if current_fr >= 0 else RED
                sentiment = "Longs zahlen (Bearish-Druck)" if current_fr >= 0 else "Shorts zahlen (Bullish-Druck)"
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;align-items:center;"
                    f"margin-bottom:0.3rem'>"
                    f"<div class='pcard-title' style='margin:0'>Funding Rate</div>"
                    f"<span style='font-size:0.78rem;color:{fr_color}'>{sentiment}</span></div>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(_funding_fig(fr_df), width="stretch",
                                config={"displayModeBar": False}, key=f"fr_{coin_id}")
