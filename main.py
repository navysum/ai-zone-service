from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (change this in production!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandleData(BaseModel):
    high: float
    low: float
    close: float
    open: float

class RequestBody(BaseModel):
    candles: List[CandleData]

@app.post("/ai/zones")
async def detect_zones(data: RequestBody):
    highs = [candle.high for candle in data.candles]
    lows = [candle.low for candle in data.candles]

    resistance = round(np.percentile(highs, 95), 5)
    support = round(np.percentile(lows, 5), 5)

    support_zone = f"{support - 0.0005:.5f} - {support + 0.0005:.5f}"
    resistance_zone = f"{resistance - 0.0005:.5f} - {resistance + 0.0005:.5f}"
    entry = f"Buy @ {support + 0.0003:.5f}"
    target = f"{resistance:.5f}"
    stop = f"{support - 0.0010:.5f}"

    return {
        "support": support_zone,
        "resistance": resistance_zone,
        "entry": entry,
        "target": target,
        "stop": stop
    }
