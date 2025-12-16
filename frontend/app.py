import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE = "http://127.0.0.1:8000"

# -----------------------------
# Page config & styling
# -----------------------------
st.set_page_config(page_title="Quant Realtime Analytics", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { font-weight: 600; }
    .stMetric {
        background-color: #111827;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Quant Realtime Analytics")
st.markdown(
    """
    **Statistical Arbitrage Research Dashboard**  
    Powered by real-time replayed market data.
    """
)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("Controls")

symbol_x = st.sidebar.selectbox("Asset X", ["BTCUSDT", "ETHUSDT"])
symbol_y = st.sidebar.selectbox("Asset Y", ["ETHUSDT", "BTCUSDT"])

timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1m", "5m"], index=0)

window = st.sidebar.slider(
    "Rolling Window", min_value=10, max_value=100, value=30, step=5
)

run = st.sidebar.button("Run Analytics")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto refresh (replay mode)")
refresh_sec = st.sidebar.slider("Refresh interval (sec)", 1, 10, 3)

# -----------------------------
# Main Panel
# -----------------------------
if run:
    chart_container = st.container()
    chart_container.empty()

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
    # Fetch OHLC bars
    # -----------------------------
    bars_resp = requests.get(
        f"{API_BASE}/bars/{timeframe}",
        params={"symbol": symbol_x},
    )

    if bars_resp.status_code != 200:
        st.error("Failed to fetch OHLC bars")
        st.stop()

    bars_df = pd.DataFrame(bars_resp.json())

    # -----------------------------
    # Hedge Ratio
    # -----------------------------
    st.subheader("Hedge Ratio")

    hedge = result["hedge_ratio"]

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

    st.metric("Hedge Ratio", round(hedge_value, 4))

    # -----------------------------
    # ADF Test
    # -----------------------------
    st.subheader("ADF Test")
    adf = result["adf"]

    if adf["status"] != "ok":
        st.info("ADF test skipped (waiting for sufficient data)")
    else:
        st.write(f"ADF Statistic: {adf['adf_stat']:.4f}")
        st.write(f"P-Value: {adf['p_value']:.4f}")

    # -----------------------------
    # Analytics Data
    # -----------------------------
    df = pd.DataFrame(result["data"])
    if df.empty:
        st.warning("Not enough data to display analytics.")
        st.stop()

    # -----------------------------
    # Charts
    # -----------------------------
    with chart_container:

        # OHLC Candles
        st.subheader("Price (OHLC)")
        ohlc = bars_df[["bar_ts", "open", "high", "low", "close"]].dropna()

        fig_candle = go.Figure(
            data=[
                go.Candlestick(
                    x=ohlc["bar_ts"],
                    open=ohlc["open"],
                    high=ohlc["high"],
                    low=ohlc["low"],
                    close=ohlc["close"],
                    name="OHLC",
                )
            ]
        )
        fig_candle.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=420,
        )
        st.plotly_chart(fig_candle,  width="stretch", key="ohlc_chart")

        # Spread
        st.subheader("Spread")
        fig_spread = go.Figure()
        fig_spread.add_trace(
            go.Scatter(
                x=df["bar_ts"],
                y=df["spread"],
                mode="lines",
                name="Spread",
            )
        )
        st.plotly_chart(fig_spread,  width="stretch", key="spread_chart")

        # Z-score
        st.subheader("Z-Score")
        fig_z = go.Figure()
        fig_z.add_trace(
            go.Scatter(
                x=df["bar_ts"],
                y=df["zscore"],
                mode="lines",
                name="Z-Score",
            )
        )
        fig_z.add_hline(y=2, line_dash="dash")
        fig_z.add_hline(y=-2, line_dash="dash")
        st.plotly_chart(fig_z,  width="stretch", key="zscore_chart")

        # Rolling Correlation
        st.subheader("Rolling Correlation")
        fig_corr = go.Figure()
        fig_corr.add_trace(
            go.Scatter(
                x=df["bar_ts"],
                y=df["rolling_corr"],
                mode="lines",
                name="Correlation",
            )
        )
        fig_corr.update_yaxes(range=[-1, 1])
        st.plotly_chart(fig_corr,  width="stretch", key="corr_chart")

    # -----------------------------
    # Auto refresh
    # -----------------------------
    if auto_refresh:
        import time
        time.sleep(refresh_sec)
        st.rerun()

