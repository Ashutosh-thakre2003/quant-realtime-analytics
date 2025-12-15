import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Quant Realtime Analytics",
    layout="wide",
)
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
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

symbol_x = st.sidebar.selectbox(
    "Asset X",
    ["BTCUSDT", "ETHUSDT"]
)

symbol_y = st.sidebar.selectbox(
    "Asset Y",
    ["ETHUSDT", "BTCUSDT"]
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1s", "1m", "5m"],
    index=1
)

window = st.sidebar.slider(
    "Rolling Window",
    min_value=10,
    max_value=100,
    value=30,
    step=5
)

run = st.sidebar.button("Run Analytics")

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
            }
        )

    if resp.status_code != 200:
        st.error("Backend error")
        st.stop()

    result = resp.json()

    # Hedge Ratio Status
    st.subheader("Hedge Ratio")

    hedge = result["hedge_ratio"]

    st.subheader("Hedge Ratio")

# Case 1: backend returned structured status
    if isinstance(hedge, dict):
        if hedge.get("status") != "ok":
            st.info(
                f"⏳ Waiting for sufficient data "
                f"({hedge.get('n_obs', 0)} / {hedge.get('min_required', '?')} bars collected)"
            )
            st.stop()

        hedge_value = hedge["hedge_ratio"]

# Case 2: backend returned raw float (legacy / fallback)
    else:
        hedge_value = hedge

    st.metric("Hedge Ratio", round(hedge_value, 4))


    # ADF Status
    st.subheader("ADF Test")
    adf = result["adf"]

    if adf["status"] != "ok":
        st.info("ADF test skipped (waiting for sufficient data)")
    else:
        st.write(f"ADF Statistic: {adf['adf_stat']:.4f}")
        st.write(f"P-Value: {adf['p_value']:.4f}")

    # Time Series Data
    df = pd.DataFrame(result["data"])

    if df.empty:
        st.warning("Not enough data to display spread & Z-score.")
        st.stop()
    
    st.subheader("Price (Close)")

    price_df = pd.DataFrame(result["data"])

    fig_price = go.Figure()
    fig_price.add_trace(
        go.Scatter(
            x=price_df["bar_ts"],
            y=price_df["spread"],
            mode="lines",
            name="Price (Close)"
        )
    )

    st.plotly_chart(fig_price, use_container_width=True)
    

    # -----------------------------
    # Spread Plot
    # -----------------------------
    st.subheader("Spread")

    fig_spread = go.Figure()
    fig_spread.add_trace(
        go.Scatter(
            x=df["bar_ts"],
            y=df["spread"],
            mode="lines",
            name="Spread"
        )
    )

    st.plotly_chart(fig_spread, use_container_width=True)

    # -----------------------------
    # Z-Score Plot
    # -----------------------------
    st.subheader("Z-Score")

    fig_z = go.Figure()
    fig_z.add_trace(
        go.Scatter(
            x=df["bar_ts"],
            y=df["zscore"],
            mode="lines",
            name="Z-Score"
        )
    )

    fig_z.add_hline(y=2, line_dash="dash")
    fig_z.add_hline(y=-2, line_dash="dash")

    st.plotly_chart(fig_z, use_container_width=True)

    st.subheader("Rolling Correlation")

    fig_corr = go.Figure()
    fig_corr.add_trace(
        go.Scatter(
            x=df["bar_ts"],
            y=df["rolling_corr"],
            mode="lines",
            name="Correlation"
        )
    )

    fig_corr.update_yaxes(range=[-1, 1])
    st.plotly_chart(fig_corr, use_container_width=True)

