from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Candle data schema
class CandleData(BaseModel):
    open: float
    high: float
    low: float
    close: float

class RequestBody(BaseModel):
    candles: List[CandleData]

# 📊 Candlestick pattern recognition
def detect_pattern(candles: List[CandleData]):
    if len(candles) < 2:
        return "Not enough data", "Unknown"

    prev = candles[-2]
    last = candles[-1]

    # Bullish Engulfing
    if prev.close < prev.open and last.close > last.open and last.close > prev.open and last.open < prev.close:
        return "Bullish Engulfing", "Up"

    # Bearish Engulfing
    if prev.close > prev.open and last.close < last.open and last.close < prev.open and last.open > prev.close:
        return "Bearish Engulfing", "Down"

    # Doji
    if abs(last.open - last.close) <= (last.high - last.low) * 0.1:
        return "Doji", "Uncertain"

    # Hammer
    if (last.high - last.low) > 2 * abs(last.open - last.close) and last.close > last.open:
        return "Hammer", "Up"

    return "None", "Unknown"

# 🧠 Count how often price touched the zone
def count_zone_touches(candles: List[CandleData], zone: float, buffer: float = 0.0007):
    count = 0
    for c in candles:
        if zone - buffer <= c.low <= zone + buffer or zone - buffer <= c.high <= zone + buffer:
            count += 1
    return count

# 📌 Count rejections based on large wicks near the zone
def count_rejection_wicks(candles: List[CandleData], zone: float, buffer: float = 0.0007):
    rejections = 0
    for c in candles:
        wick_size = (c.high - max(c.open, c.close)) + (min(c.open, c.close) - c.low)
        body_size = abs(c.close - c.open)
        if wick_size > 1.5 * body_size:
            if zone - buffer <= c.low <= zone + buffer or zone - buffer <= c.high <= zone + buffer:
                rejections += 1
    return rejections

# 🚀 Main AI logic
@app.post("/ai/zones")
async def detect_zones(data: RequestBody):
    highs = [c.high for c in data.candles]
    lows = [c.low for c in data.candles]

    resistance = round(np.percentile(highs, 95), 5)
    support = round(np.percentile(lows, 5), 5)

    # Support/Resistance touches
    support_touches = count_zone_touches(data.candles, support)
    resistance_touches = count_zone_touches(data.candles, resistance)

    # Wick rejections
    support_rejections = count_rejection_wicks(data.candles, support)
    resistance_rejections = count_rejection_wicks(data.candles, resistance)

    # Candle pattern detection
    pattern, prediction = detect_pattern(data.candles)

    # 🔢 Scoring
    touch_factor = (support_touches + resistance_touches) * 5
    rejection_factor = (support_rejections + resistance_rejections) * 4
    pattern_factor = 10 if pattern in ["Hammer", "Bullish Engulfing", "Bearish Engulfing"] else 0

    range_span = max(highs) - min(lows)
    base_strength = max(0, 100 - (range_span / max(highs)) * 100)
    final_strength = min(100, base_strength + touch_factor + rejection_factor + pattern_factor)

    # Zones
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
        "stop": stop,
        "strength": round(final_strength, 2),
        "pattern": pattern,
        "prediction": prediction,
        "touches": {
            "support": support_touches,
            "resistance": resistance_touches
        },
        "rejections": {
            "support": support_rejections,
            "resistance": resistance_rejections
        }
    }
