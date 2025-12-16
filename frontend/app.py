import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

API_BASE = "http://127.0.0.1:8000"

# -----------------------------
# Page config & global styling
# -----------------------------
st.set_page_config(page_title="Quant Realtime Analytics", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}
[data-testid="stMetric"] {
    background: #020617;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #0f172a;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Hero Header
# -----------------------------
st.markdown(
    """
    <div style="padding: 1.2rem 1.5rem; background:#020617;
                border-radius: 12px; margin-bottom: 1.5rem;">
        <h1 style="margin-bottom: 0.2rem;">📊 Quant Realtime Analytics</h1>
        <p style="color:#94a3b8; margin:0;">
            Statistical Arbitrage Research Dashboard • Real-time Market Replay
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.markdown("## Strategy Controls")

with st.sidebar.expander("Assets", expanded=True):
    symbol_x = st.selectbox("Asset X", ["BTCUSDT", "ETHUSDT"])
    symbol_y = st.selectbox("Asset Y", ["ETHUSDT", "BTCUSDT"])

with st.sidebar.expander("Parameters", expanded=True):
    timeframe = st.selectbox("Timeframe", ["1s", "1m", "5m"], index=1)
    window = st.slider("Rolling Window", 10, 100, 30, step=5)

with st.sidebar.expander("Backtest Settings", expanded=True):
    entry_z = st.slider("Entry Z-Score", 1.0, 3.0, 2.0, 0.1)
    exit_z = st.slider("Exit Z-Score", 0.0, 1.5, 0.0, 0.1)
    position_size = st.number_input("Position Size ($)", 100, 100000, 1000, step=100)


st.sidebar.markdown("---")
run = st.sidebar.button("▶ Run Analytics", width="stretch")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto refresh (replay mode)")
refresh_sec = st.sidebar.slider("Refresh interval (sec)", 1, 10, 3)

# -----------------------------
# Main Panel
# -----------------------------
if run:

    with st.spinner("Fetching analytics..."):
        resp = requests.get(
            f"{API_BASE}/analytics/pairs",
            params={
                "symbol_x": symbol_x,
                "symbol_y": symbol_y,
                "timeframe": timeframe,
                "window": window,
            },
        )

    if resp.status_code != 200:
        st.error("Backend error")
        st.stop()

    result = resp.json()

    # -----------------------------
    # Load analytics data FIRST
    # -----------------------------
    df = pd.DataFrame(result["data"])
    adf = result["adf"]
    hedge = result["hedge_ratio"]

    if df.empty:
        st.warning("Not enough data to display analytics.")
        st.stop()
    # -----------------------------
# Backtest Logic
# -----------------------------
    df_bt = df.copy()
    df_bt["position"] = 0
    df_bt["pnl"] = 0.0

    position = 0

    for i in range(1, len(df_bt)):
        z = df_bt.loc[i, "zscore"]
        spread = df_bt.loc[i, "spread"]
        prev_spread = df_bt.loc[i - 1, "spread"]

    # Entry
        if position == 0:
            if z > entry_z:
                position = -1
            elif z < -entry_z:
                position = 1

    # Exit
        elif abs(z) <= exit_z:
            position = 0

        df_bt.loc[i, "position"] = position
        df_bt.loc[i, "pnl"] = position * (spread - prev_spread)

    df_bt["cum_pnl"] = df_bt["pnl"].cumsum() * position_size

    st.subheader("Backtest Performance")

    total_pnl = df_bt["cum_pnl"].iloc[-1]
    max_dd = (df_bt["cum_pnl"].cummax() - df_bt["cum_pnl"]).max()
    trades = (df_bt["position"].diff().abs() == 1).sum()

    # Performance Metrics
    returns = df_bt["pnl"]
    sharpe = (
        returns.mean() / returns.std() * (252 ** 0.5)
        if returns.std() != 0 else 0
    )

    wins = (df_bt["pnl"] > 0).sum()
    win_rate = wins / trades * 100 if trades > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total PnL ($)", f"{total_pnl:,.2f}")
    m2.metric("Max Drawdown ($)", f"{max_dd:,.2f}")
    m3.metric("Sharpe Ratio", f"{sharpe:.2f}")
    m4.metric("Win Rate (%)", f"{win_rate:.1f}")


    fig_pnl = go.Figure()
    fig_pnl.add_trace(
        go.Scatter(
            x=df_bt["bar_ts"],
            y=df_bt["cum_pnl"],
            mode="lines",
            name="Cumulative PnL"
        )
    )

    fig_pnl.update_layout(
        template="plotly_dark",
        height=350,
        yaxis_title="PnL ($)"
    )

    st.plotly_chart(fig_pnl, width="stretch", key="pnl_chart")

    st.download_button(
        "📥 Download Backtest Results",
        df_bt.to_csv(index=False),
        file_name="backtest_results.csv",
        mime="text/csv"
    )

    # -----------------------------
    # Resolve hedge ratio
    # -----------------------------
    if isinstance(hedge, dict):
        if hedge.get("status") != "ok":
            st.info(
                f"⏳ Waiting for sufficient data "
                f"({hedge.get('n_obs', 0)} / {hedge.get('min_required', '?')} bars collected)"
            )
            st.stop()
        hedge_value = hedge["hedge_ratio"]
    else:
        hedge_value = hedge

    latest_z = df["zscore"].iloc[-1]

    # -----------------------------
    # Key Metrics
    # -----------------------------
    st.markdown("### Key Metrics")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Hedge Ratio", round(hedge_value, 4))

    with c2:
        if adf["status"] == "ok":
            st.metric("ADF p-value", f"{adf['p_value']:.4f}")
        else:
            st.metric("ADF Test", "Waiting")

    with c3:
        st.metric("Bars Used", len(df))

    with c4:
        st.metric("Latest Z-Score", f"{latest_z:.2f}")

    # -----------------------------
    # Market Regime & Signal
    # -----------------------------
    st.markdown("### Market Regime & Trade Signal")

    if adf["status"] == "ok" and adf["p_value"] < 0.05:
        st.success("🟢 Mean-Reverting Regime (Cointegrated)")
    elif adf["status"] == "ok":
        st.warning("🟡 Weak Mean Reversion / Trending")
    else:
        st.info("⏳ Regime Unknown")

    if latest_z > 2:
        st.error("🔴 Trade Signal: SHORT Spread (Z > +2)")
    elif latest_z < -2:
        st.success("🟢 Trade Signal: LONG Spread (Z < −2)")
    else:
        st.info("⚪ No Trade Zone")

    # -----------------------------
    # Fetch OHLC bars
    # -----------------------------
    bars_resp = requests.get(
        f"{API_BASE}/bars/{timeframe}",
        params={"symbol": symbol_x},
    )

    bars_df = pd.DataFrame(bars_resp.json())
    ohlc = bars_df[["bar_ts", "open", "high", "low", "close"]].dropna()

    # -----------------------------
    # Charts (Expandable)
    # -----------------------------
    with st.expander("📈 Price (OHLC)", expanded=True):
        fig_candle = go.Figure(
            data=[go.Candlestick(
                x=ohlc["bar_ts"],
                open=ohlc["open"],
                high=ohlc["high"],
                low=ohlc["low"],
                close=ohlc["close"],
            )]
        )
        fig_candle.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=420,
        )
        st.plotly_chart(fig_candle, width="stretch", key="ohlc")

    with st.expander("📉 Spread"):
        fig_spread = go.Figure()
        fig_spread.add_trace(go.Scatter(
            x=df["bar_ts"],
            y=df["spread"],
            mode="lines",
            name="Spread",
        ))
        st.plotly_chart(fig_spread, width="stretch", key="spread")

    with st.expander("📊 Z-Score + Trade Signals"):
        fig_z = go.Figure()

    # Z-score line
        fig_z.add_trace(go.Scatter(
            x=df["bar_ts"],
            y=df["zscore"],
            mode="lines",
            name="Z-Score",
            line=dict(color="#60a5fa")
        ))

    # Entry markers
        entries_long = df_bt[df_bt["position"].diff() == 1]
        entries_short = df_bt[df_bt["position"].diff() == -1]

        fig_z.add_trace(go.Scatter(
            x=entries_long["bar_ts"],
            y=entries_long["zscore"],
            mode="markers",
            marker=dict(color="green", size=8),
            name="Long Entry"
        ))

        fig_z.add_trace(go.Scatter(
            x=entries_short["bar_ts"],
            y=entries_short["zscore"],
            mode="markers",
            marker=dict(color="red", size=8),
            name="Short Entry"
        ))

    # Thresholds
        fig_z.add_hline(y=entry_z, line_dash="dash", line_color="red")
        fig_z.add_hline(y=-entry_z, line_dash="dash", line_color="green")
        fig_z.add_hline(y=0, line_dash="dot")

        fig_z.update_layout(
            template="plotly_dark",
            height=350
        )

        st.plotly_chart(fig_z, width="stretch", key="zscore_signals")


    with st.expander("🔗 Rolling Correlation"):
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(
            x=df["bar_ts"],
            y=df["rolling_corr"],
            mode="lines",
            name="Correlation",
        ))
        fig_corr.update_yaxes(range=[-1, 1])
        st.plotly_chart(fig_corr, width="stretch", key="corr")

    # -----------------------------
    # Footer
    # -----------------------------
    st.markdown("---")
    st.caption("🟢 Backend: FastAPI • Storage: DuckDB • Mode: Market Replay • UI: Streamlit")

    # -----------------------------
    # Auto refresh
    # -----------------------------
    if auto_refresh:
        time.sleep(refresh_sec)
        st.rerun()
