# quant-realtime-analytics
**Quant Realtime Analytics Platform**
Real-Time Market Replay, Statistical Arbitrage Analytics & Research Dashboard
**1. Overview**
This project implements a real-time quantitative analytics platform focused on statistical arbitrage (pairs trading) using replayed cryptocurrency market tick data.

The system ingests raw tick data, aggregates it into OHLC bars, performs statistical analytics (hedge ratio, spread, Z-score, cointegration tests), and visualizes results in an interactive dashboard.

The platform is designed to simulate institutional quant research workflows, separating ingestion, storage, analytics, APIs, and visualization layers.

**2. Features**
Market tick replay engine (NDJSON-based)

Timeframe resampling (1s, 1m, 5m OHLC bars)

Hedge ratio estimation (OLS regression)

Spread & Z-score computation

Rolling correlation analysis

Augmented Dickey-Fuller (ADF) test

Interactive Streamlit dashboard

Replay-mode auto refresh

Production-ready FastAPI backend

DuckDB analytical storage

**3. Technology Stack**
Backend
Python 3.13

FastAPI

DuckDB

Pandas / NumPy

Statsmodels

Frontend
Streamlit

Plotly

Requests

Infrastructure
Backend hosting: Render

Frontend hosting: Streamlit Cloud

Version control: Git + GitHub

Quant Realtime Analytics Platform
Real-Time Market Replay, Statistical Arbitrage Analytics & Research Dashboard
1. Overview
This project implements a real-time quantitative analytics platform focused on statistical arbitrage (pairs trading) using replayed cryptocurrency market tick data.

The system ingests raw tick data, aggregates it into OHLC bars, performs statistical analytics (hedge ratio, spread, Z-score, cointegration tests), and visualizes results in an interactive dashboard.

The platform is designed to simulate institutional quant research workflows, separating ingestion, storage, analytics, APIs, and visualization layers.

2. Features
Market tick replay engine (NDJSON-based)

Timeframe resampling (1s, 1m, 5m OHLC bars)

Hedge ratio estimation (OLS regression)

Spread & Z-score computation

Rolling correlation analysis

Augmented Dickey-Fuller (ADF) test

Interactive Streamlit dashboard

Replay-mode auto refresh

Production-ready FastAPI backend

DuckDB analytical storage

3. Technology Stack
Backend
Python 3.13

FastAPI

DuckDB

Pandas / NumPy

Statsmodels

Frontend
Streamlit

Plotly

Requests

Infrastructure
Backend hosting: Render

Frontend hosting: Streamlit Cloud

Version control: Git + GitHub

4. Project Structure
   quant-realtime-analytics/
│
├── backend/
│   ├── app.py                  # FastAPI application
│   ├── replay_engine.py        # Tick replay logic
│   ├── storage.py              # DuckDB interface
│   ├── analytics/              # Quant analytics modules
│   │   ├── hedge_ratio.py
│   │   ├── spread.py
│   │   ├── zscore.py
│   │   ├── adf.py
│   │   └── correlation.py
│   ├── data/
│   │   └── sample_ticks.ndjson # Market replay dataset
│   └── requirements.txt
│
├── frontend/
│   ├── app.py                  # Streamlit dashboard
│   └── requirements.txt
│
├── architecture/
│   ├── quant_architecture.drawio
│   └── quant_architecture.png
│
└── README.md

**5. Setup Instructions**
5.1 Backend (Local)
cd backend
pip install -r requirements.txt
uvicorn backend.app:app --reload
Backend runs at:

http://127.0.0.1:8000
5.2 Ingest Market Data
After backend starts:

POST /ingest-replay?limit=70000
Use Swagger UI:

http://127.0.0.1:8000/docs
5.3 Frontend (Local)
cd frontend
pip install -r requirements.txt
streamlit run app.py
Frontend runs at:

http://localhost:8501
**6. Methodology**
6.1 Data Ingestion
Market tick data is provided in NDJSON format.

Each tick contains:

Symbol

Price

Quantity

Timestamp

A replay engine sequentially processes ticks and inserts them into DuckDB.

**6.2 OHLC Resampling**
Ticks are resampled into bars using time-based aggregation:

Open: first price

High: max price

Low: min price

Close: last price

Volume: sum of sizes

Supported timeframes:

1 second

1 minute

5 minutes

**6.3 Hedge Ratio Estimation**
The hedge ratio (β) is estimated using Ordinary Least Squares (OLS):

X
t
=
α
+
β
Y
t
+
ϵ
t
X 
t
​
 =α+βY 
t
​
 +ϵ 
t
​
 
Where:

X
t
X 
t
​
  = price of Asset X

Y
t
Y 
t
​
  = price of Asset Y

The estimated 
β
β minimizes residual variance.

**6.4 Spread & Z-Score**
Spread:

S
p
r
e
a
d
t
=
X
t
−
β
Y
t
Spread 
t
​
 =X 
t
​
 −βY 
t
​
 
Z-Score:

Z
t
=
S
p
r
e
a
d
t
−
μ
σ
Z 
t
​
 = 
σ
Spread 
t
​
 −μ
​
 
Computed over a rolling window.

**6.5 Cointegration Test (ADF)**
An Augmented Dickey-Fuller test is applied to the spread to test stationarity.

If:

p-value < 0.05 → spread is stationary → mean reversion likely

**6.6 Rolling Correlation**
Pearson correlation is computed over a rolling window to measure short-term co-movement stability.

**7. Analytics Output**
The dashboard displays:

Hedge ratio

ADF test statistics

OHLC price chart

Spread time series

Z-score with thresholds

Rolling correlation

The system intentionally blocks analytics if insufficient data is available to avoid misleading outputs.

**8. Deployment**
Backend
Hosted on Render

Runs FastAPI with Uvicorn

Public API endpoint exposed

Frontend
Hosted on Streamlit Cloud

Connects to deployed backend via REST APIs

**9. Disclaimer**
This project is for research and educational purposes only.
It does not place live trades or connect to real trading accounts.

**10. Author**
Ashutosh Thakre
