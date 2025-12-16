import duckdb
from pathlib import Path
from typing import Dict
from datetime import datetime


class DuckDBStorage:
    """
    Handles persistent storage of raw ticks and OHLCV bars.
    """

    def __init__(self, db_path: Path):
        self.conn = duckdb.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        # Raw tick table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ticks (
                symbol TEXT,
                ts TIMESTAMP,
                price DOUBLE,
                size DOUBLE
            )
        """)

    def insert_tick(self, tick: Dict):
        self.conn.execute(
            "INSERT INTO ticks VALUES (?, ?, ?, ?)",
            (
                tick["symbol"],
                tick["ts"],
                tick["price"],
                tick["size"]
            )
        )

    def resample_ohlcv(self, timeframe: str):
        """
        Resample raw ticks into OHLCV bars.
        timeframe: '1s', '1m', '5m'
        """
        interval_map = {
            "1s": "1 second",
            "1m": "1 minute",
            "5m": "5 minutes"
        }

        if timeframe not in interval_map:
            raise ValueError("Invalid timeframe")

        interval = interval_map[timeframe]

        query = f"""
            SELECT
                symbol,
                time_bucket(INTERVAL '{interval}', ts) AS bar_ts,
                FIRST(price) AS open,
                MAX(price) AS high,
                MIN(price) AS low,
                LAST(price) AS close,
                SUM(size) AS volume
            FROM ticks
            GROUP BY symbol, bar_ts
            ORDER BY bar_ts
        """

        return self.conn.execute(query).fetchdf()
