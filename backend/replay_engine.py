import json
import time
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict

from backend.config import TICK_REPLAY_SPEED


class TickReplayEngine:
    """
    Replays NDJSON tick data as a simulated real-time stream.
    """

    def __init__(self, ndjson_path: Path):
        self.ndjson_path = ndjson_path
        self._validate_file()

    def _validate_file(self):
        if not self.ndjson_path.exists():
            raise FileNotFoundError(f"NDJSON file not found: {self.ndjson_path}")

    def _read_ticks(self) -> Iterator[Dict]:
        """
        Reads ticks line-by-line from NDJSON.
        """
        with open(self.ndjson_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def replay(self) -> Iterator[Dict]:
        """
        Generator that yields ticks respecting original timestamps.
        Supports epoch-ms and ISO-8601 timestamps.
        """
        prev_event_time = None

        for tick in self._read_ticks():

            # --- Timestamp normalization ---
            if "E" in tick or "T" in tick:
                event_time = datetime.utcfromtimestamp(
                    (tick.get("E") or tick.get("T")) / 1000
                )

            elif "ts" in tick:
                event_time = datetime.fromisoformat(
                    tick["ts"].replace("Z", "+00:00")
                )

            else:
                continue

            # --- Timing control ---
            if prev_event_time is not None:
                delta = (event_time - prev_event_time).total_seconds()
                sleep_time = max(delta / TICK_REPLAY_SPEED, 0)
                time.sleep(sleep_time)

            prev_event_time = event_time
            yield tick
