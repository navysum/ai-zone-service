from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Candle format
class CandleData(BaseModel):
    open: float
    high: float
    low: float
    close: float

class RequestBody(BaseModel):
    candles: List[CandleData]

# Pattern recognition
def detect_pattern(candles: List[CandleData]):
    if len(candles) < 2:
        return "Not enough data", "Unknown"

    prev = candles[-2]
    last = candles[-1]

    # Bullish engulfing
    if prev.close < prev.open and last.close > last.open and last.close > prev.open and last.open < prev.close:
        return "Bullish Engulfing", "Up"

    # Bearish engulfing
    if prev.close > prev.open and last.close < last.open and last.close < prev.open and last.open > prev.close:
        return "Bearish Engulfing", "Down"

    # Doji
    if abs(last.open - last.close) <= (last.high - last.low) * 0.1:
        return "Doji", "Uncertain"

    # Hammer
    if (last.high - last.low) > 2 * abs(last.open - last.close) and (last.close > last.open):
        return "Hammer", "Up"

    return "None", "Unknown"

@app.post("/ai/zones")
async def detect_zones(data: RequestBody):
    highs = [c.high for c in data.candles]
    lows = [c.low for c in data.candles]

    resistance = round(np.percentile(highs, 95), 5)
    support = round(np.percentile(lows, 5), 5)

    # 🔥 Add strength estimation (based on range tightness)
    range_span = max(highs) - min(lows)
    strength_score = round(100 - (range_span / max(highs)) * 100, 2)
    strength_score = max(min(strength_score, 100), 0)

    support_zone = f"{support - 0.0005:.5f} - {support + 0.0005:.5f}"
    resistance_zone = f"{resistance - 0.0005:.5f} - {resistance + 0.0005:.5f}"
    entry = f"Buy @ {support + 0.0003:.5f}"
    target = f"{resistance:.5f}"
    stop = f"{support - 0.0010:.5f}"

    pattern, prediction = detect_pattern(data.candles)

    return {
        "support": support_zone,
        "resistance": resistance_zone,
        "strength": strength_score,
        "entry": entry,
        "target": target,
        "stop": stop,
        "pattern": pattern,
        "prediction": prediction
    }
