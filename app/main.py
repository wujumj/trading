import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta
from strategies import sma, rsi, macd
from backtest.engine import run, INITIAL_CAPITAL, WATCHLIST

st.set_page_config(page_title="Trading Dashboard", layout="wide", page_icon="📈")

st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 18px !important; }
    .stMetric label { font-size: 16px !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 28px !important; }
    .stSelectbox label, .stSelectbox div { font-size: 18px !important; }
    thead tr th { font-size: 16px !important; }
    tbody tr td { font-size: 16px !important; }

    /* Time range buttons */
    div[data-testid="column"] button {
        width: 100%;
        border-radius: 6px;
        font-size: 14px !important;
        padding: 4px 0px;
        border: 1px solid #3b4263;
        background: #1e2130;
        color: #94a3b8;
    }
    div[data-testid="column"] button:hover {
        border-color: #6366f1;
        color: #fff;
    }
    div[data-testid="column"] button[kind="primary"] {
        background: #6366f1 !important;
        color: white !important;
        border-color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("📈 Trading Dashboard")

ticker = st.sidebar.selectbox("Ticker", WATCHLIST)

strategy_name = st.sidebar.selectbox(
    "Strategy",
    ["SMA (20/50)", "RSI (14)", "MACD (12/26/9)"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Yahoo Finance via yfinance · DB: TimescaleDB")

# ── Load signals ───────────────────────────────────────────────────────────────
@st.cache_data
def load(ticker, strategy):
    if strategy == "SMA (20/50)":
        return sma.get_signals(ticker)
    elif strategy == "RSI (14)":
        return rsi.get_signals(ticker)
    else:
        return macd.get_signals(ticker)

df = load(ticker, strategy_name)
metrics = run(df)

# ── KPI cards ──────────────────────────────────────────────────────────────────
st.title(f"{ticker} — {strategy_name}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Return", f"{metrics['total_return_pct']}%",
          delta=f"{metrics['total_return_pct']}%")
c2.metric("Max Drawdown", f"{metrics['max_drawdown_pct']}%")
c3.metric("Sharpe Ratio", metrics['sharpe_ratio'])
c4.metric("Trades", metrics['num_trades'])
c5.metric("Win Rate", f"{metrics['win_rate_pct']}%")

st.markdown("---")

# ── Time range selector ────────────────────────────────────────────────────────
RANGES = {
    "1D":  1,
    "3D":  3,
    "1W":  7,
    "2W":  14,
    "1M":  30,
    "3M":  90,
    "6M":  180,
    "1Y":  365,
    "2Y":  730,
    "3Y":  1095,
    "All": None,
}

selected_range = st.selectbox(
    "Time Range",
    list(RANGES.keys()),
    index=list(RANGES.keys()).index("1Y"),
    key="range",
)

# Filter df to selected range (trading days only)
end_date = df["time"].max()
selected_days = RANGES[selected_range]

if selected_days is None:
    df_view = df.copy()
else:
    # Count back N trading days (rows) rather than calendar days
    df_view = df.tail(selected_days).copy()

buys  = df_view[df_view["signal"] == "BUY"]
sells = df_view[df_view["signal"] == "SELL"]

# ── Price chart with signals ───────────────────────────────────────────────────
fig = go.Figure()

if "open" in df_view.columns:
    fig.add_trace(go.Candlestick(
        x=df_view["time"], open=df_view["open"], high=df_view["high"],
        low=df_view["low"], close=df_view["close"],
        name="Price", increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    ))
else:
    fig.add_trace(go.Scatter(
        x=df_view["time"], y=df_view["close"], name="Close",
        line=dict(color="#6366f1", width=1.5),
    ))

# Strategy overlays
if strategy_name == "SMA (20/50)":
    fig.add_trace(go.Scatter(x=df_view["time"], y=df_view["sma_fast"],
                             name="SMA 20", line=dict(color="#f59e0b", width=1.2)))
    fig.add_trace(go.Scatter(x=df_view["time"], y=df_view["sma_slow"],
                             name="SMA 50", line=dict(color="#8b5cf6", width=1.2)))

elif strategy_name == "RSI (14)":
    fig.add_trace(go.Scatter(x=df_view["time"], y=df_view["rsi"],
                             name="RSI", line=dict(color="#f59e0b", width=1.5),
                             yaxis="y2"))
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444",
                  annotation_text="Overbought 70")
    fig.add_hline(y=30, line_dash="dash", line_color="#22c55e",
                  annotation_text="Oversold 30")
    fig.update_layout(
        yaxis2=dict(title="RSI", overlaying="y", side="right",
                    range=[0, 100], showgrid=False)
    )

elif strategy_name == "MACD (12/26/9)":
    fig.add_trace(go.Scatter(x=df_view["time"], y=df_view["macd"],
                             name="MACD", line=dict(color="#f59e0b", width=1.2),
                             yaxis="y2"))
    fig.add_trace(go.Scatter(x=df_view["time"], y=df_view["macd_signal"],
                             name="Signal", line=dict(color="#8b5cf6", width=1.2),
                             yaxis="y2"))
    fig.update_layout(
        yaxis2=dict(title="MACD", overlaying="y", side="right", showgrid=False)
    )

# Buy / Sell markers
fig.add_trace(go.Scatter(
    x=buys["time"], y=buys["close"], mode="markers", name="BUY",
    marker=dict(symbol="triangle-up", size=12, color="#22c55e"),
))
fig.add_trace(go.Scatter(
    x=sells["time"], y=sells["close"], mode="markers", name="SELL",
    marker=dict(symbol="triangle-down", size=12, color="#ef4444"),
))

fig.update_layout(
    template="plotly_dark",
    height=540,
    xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", y=1.02, x=0),
    margin=dict(l=0, r=0, t=40, b=0),
    xaxis=dict(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
        ]
    ),
)

st.plotly_chart(fig, use_container_width=True)

# ── All strategies comparison table ───────────────────────────────────────────
st.markdown("### All Strategies — Backtest Comparison")

STRATEGIES = {
    "SMA(20/50)":    sma.get_signals,
    "RSI(14)":       rsi.get_signals,
    "MACD(12/26/9)": macd.get_signals,
}

@st.cache_data
def load_all():
    rows = []
    for t in WATCHLIST:
        for sname, fn in STRATEGIES.items():
            m = run(fn(t))
            rows.append({
                "Ticker":     t,
                "Strategy":   sname,
                "Return %":   m["total_return_pct"],
                "Max DD %":   m["max_drawdown_pct"],
                "Sharpe":     m["sharpe_ratio"],
                "Trades":     m["num_trades"],
                "Win Rate %": m["win_rate_pct"],
                "Final $":    m["final_capital"],
            })
    return pd.DataFrame(rows)

results = load_all()

st.dataframe(
    results.style
        .background_gradient(subset=["Return %"], cmap="RdYlGn")
        .background_gradient(subset=["Sharpe"], cmap="RdYlGn")
        .background_gradient(subset=["Max DD %"], cmap="RdYlGn_r")
        .format({
            "Return %": "{:.2f}%",
            "Max DD %": "{:.2f}%",
            "Sharpe":   "{:.2f}",
            "Win Rate %": "{:.1f}%",
            "Final $":  "${:,.2f}",
        }),
    use_container_width=True,
    height=460,
)
