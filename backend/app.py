from fastapi import FastAPI
from datetime import datetime, timezone
from pathlib import Path
from backend.replay_engine import TickReplayEngine
from backend.config import DATA_DIR
from backend.storage import DuckDBStorage
from backend.config import DB_PATH


app = FastAPI(
    title="Quant Realtime Analytics Engine",
    description="Realtime tick ingestion, resampling, and quantitative analytics",
    version="0.1.0",
)

storage = DuckDBStorage(DB_PATH)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "quant-realtime-analytics",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/replay-test")
def replay_test(limit: int = 5):
    """
    Simple endpoint to test tick replay.
    """
    ndjson_file = DATA_DIR / "sample_ticks.ndjson"

    engine = TickReplayEngine(ndjson_file)

    ticks = []
    for i, tick in enumerate(engine.replay()):
        ticks.append({
            "symbol": tick.get("symbol") or tick.get("s"),
            "price": tick.get("price") or tick.get("p"),
            "size": tick.get("size") or tick.get("q"),
            "timestamp": tick.get("ts") or tick.get("E") or tick.get("T"),
        })

        if i + 1 >= limit:
            break

    return {
        "ticks_replayed": len(ticks),
        "data": ticks
    }


@app.post("/ingest-replay")
def ingest_replay(limit: int = 1000):
    """
    Replays NDJSON ticks and stores them in DuckDB.
    """
    ndjson_file = DATA_DIR / "sample_ticks.ndjson"
    engine = TickReplayEngine(ndjson_file)

    count = 0

    for tick in engine.replay():

        # --- Symbol ---
        symbol = tick.get("symbol") or tick.get("s")
        if symbol is None:
            continue

        # --- Timestamp (already normalized to naive UTC) ---
        if "ts" in tick:
            ts = (
                datetime
                .fromisoformat(tick["ts"].replace("Z", "+00:00"))
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
        elif "E" in tick or "T" in tick:
            ts = datetime.utcfromtimestamp(
                (tick.get("E") or tick.get("T")) / 1000
            )
        else:
            continue

        # --- Price ---
        if "price" in tick and tick["price"] is not None:
            price = float(tick["price"])
        elif "p" in tick and tick["p"] is not None:
            price = float(tick["p"])
        else:
            continue

        # --- Size / Quantity ---
        if "size" in tick and tick["size"] is not None:
            size = float(tick["size"])
        elif "q" in tick and tick["q"] is not None:
            size = float(tick["q"])
        else:
            continue

        storage.insert_tick({
            "symbol": symbol,
            "ts": ts,
            "price": price,
            "size": size,
        })

        count += 1
        if count >= limit:
            break

    return {"ticks_ingested": count}



@app.get("/bars/{timeframe}")
def get_bars(timeframe: str):
    """
    Returns OHLCV bars for the given timeframe.
    """
    df = storage.resample_ohlcv(timeframe)
    return df.to_dict(orient="records")

