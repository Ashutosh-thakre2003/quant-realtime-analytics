from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Quant Realtime Analytics Engine",
    description="Realtime tick ingestion, resampling, and quantitative analytics",
    version="0.1.0",
)

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "quant-realtime-analytics",
        "timestamp": datetime.utcnow().isoformat()
    }
