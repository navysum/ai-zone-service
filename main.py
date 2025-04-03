from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
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

class Candle(BaseModel):
    open: float
    high: float
    low: float
    close: float

class CandleData(BaseModel):
    candles: List[Candle]

# === Full Pattern Recognition Function ===
def detect_pattern(candles: List[Candle]):
    if len(candles) < 5:
        return {"name": "None", "direction": "None", "confidence": 0.0}
    c = candles[-5:]

    # Define patterns (include all from your full pattern recognition block)
    def hammer(c): return (abs(c.close - c.open) < 0.5 * (c.high - c.low) and min(c.open, c.close) - c.low > 2 * abs(c.close - c.open))
    def inverted_hammer(c): return (abs(c.close - c.open) < 0.5 * (c.high - c.low) and c.high - max(c.open, c.close) > 2 * abs(c.close - c.open))
    def bullish_engulfing(p1, p2): return p1.close < p1.open and p2.close > p2.open and p2.open < p1.close and p2.close > p1.open
    def bearish_engulfing(p1, p2): return p1.close > p1.open and p2.close < p2.open and p2.open > p1.close and p2.close < p1.open
    def morning_star(p1, p2, p3): return p1.close < p1.open and p2.close < p2.open and p3.close > p3.open and p3.close > ((p1.open + p1.close)/2)
    def evening_star(p1, p2, p3): return p1.close > p1.open and p2.close > p2.open and p3.close < p3.open and p3.close < ((p1.open + p1.close)/2)
    def piercing_pattern(p1, p2): return p1.close < p1.open and p2.open < p1.low and p2.close > ((p1.open + p1.close)/2)
    def dark_cloud_cover(p1, p2): return p1.close > p1.open and p2.open > p1.high and p2.close < ((p1.open + p1.close)/2)
    def bullish_harami(p1, p2): return p1.close < p1.open and p2.close > p2.open and p2.open > p1.close and p2.close < p1.open
    def bearish_harami(p1, p2): return p1.close > p1.open and p2.close < p2.open and p2.open < p1.close and p2.close > p1.open
    def tweezer_bottom(p1, p2): return abs(p1.low - p2.low) <= 0.0002 and p1.close < p1.open and p2.close > p2.open
    def tweezer_top(p1, p2): return abs(p1.high - p2.high) <= 0.0002 and p1.close > p1.open and p2.close < p2.open
    def three_inside_up(p1, p2, p3): return bearish_engulfing(p1, p2) and p3.close > p2.close
    def three_inside_down(p1, p2, p3): return bullish_engulfing(p1, p2) and p3.close < p2.close
    def three_outside_up(p1, p2, p3): return bullish_engulfing(p1, p2) and p3.close > p2.close
    def three_outside_down(p1, p2, p3): return bearish_engulfing(p1, p2) and p3.close < p2.close
    def on_neck(p1, p2): return p1.close > p1.open and p2.open < p1.low and abs(p2.close - p1.low) <= 0.0002
    def counterattack_bull(p1, p2): return p1.close < p1.open and p2.close > p2.open and abs(p1.close - p2.close) <= 0.0002
    def counterattack_bear(p1, p2): return p1.close > p1.open and p2.close < p2.open and abs(p1.close - p2.close) <= 0.0002
    def white_marubozu(c): return c.open == c.low and c.close == c.high
    def black_marubozu(c): return c.open == c.high and c.close == c.low

    # === Continuation Patterns ===
    def doji(c): return abs(c.open - c.close) <= (c.high - c.low) * 0.1
    def spinning_top(c): return abs(c.close - c.open) <= (c.high - c.low) * 0.3 and c.high - max(c.open, c.close) > 0 and min(c.open, c.close) - c.low > 0
    def three_white_soldiers(candles): return all(c.close > c.open for c in candles)
    def three_black_crows(candles): return all(c.close < c.open for c in candles)

    # Pattern Checks
    if hammer(c[-1]): return {"name": "Hammer", "direction": "Bullish", "confidence": 0.85}
    if inverted_hammer(c[-1]): return {"name": "Inverted Hammer", "direction": "Bullish", "confidence": 0.85}
    if bullish_engulfing(c[-2], c[-1]): return {"name": "Bullish Engulfing", "direction": "Bullish", "confidence": 0.9}
    if bearish_engulfing(c[-2], c[-1]): return {"name": "Bearish Engulfing", "direction": "Bearish", "confidence": 0.9}
    if morning_star(c[-3], c[-2], c[-1]): return {"name": "Morning Star", "direction": "Bullish", "confidence": 0.9}
    if evening_star(c[-3], c[-2], c[-1]): return {"name": "Evening Star", "direction": "Bearish", "confidence": 0.9}
    if piercing_pattern(c[-2], c[-1]): return {"name": "Piercing Pattern", "direction": "Bullish", "confidence": 0.85}
    if dark_cloud_cover(c[-2], c[-1]): return {"name": "Dark Cloud Cover", "direction": "Bearish", "confidence": 0.85}
    if bullish_harami(c[-2], c[-1]): return {"name": "Bullish Harami", "direction": "Bullish", "confidence": 0.8}
    if bearish_harami(c[-2], c[-1]): return {"name": "Bearish Harami", "direction": "Bearish", "confidence": 0.8}
    if tweezer_bottom(c[-2], c[-1]): return {"name": "Tweezer Bottom", "direction": "Bullish", "confidence": 0.8}
    if tweezer_top(c[-2], c[-1]): return {"name": "Tweezer Top", "direction": "Bearish", "confidence": 0.8}
    if three_inside_up(c[-3], c[-2], c[-1]): return {"name": "Three Inside Up", "direction": "Bullish", "confidence": 0.9}
    if three_inside_down(c[-3], c[-2], c[-1]): return {"name": "Three Inside Down", "direction": "Bearish", "confidence": 0.9}
    if three_outside_up(c[-3], c[-2], c[-1]): return {"name": "Three Outside Up", "direction": "Bullish", "confidence": 0.9}
    if three_outside_down(c[-3], c[-2], c[-1]): return {"name": "Three Outside Down", "direction": "Bearish", "confidence": 0.9}
    if on_neck(c[-2], c[-1]): return {"name": "On-Neck Pattern", "direction": "Bearish", "confidence": 0.75}
    if counterattack_bull(c[-2], c[-1]): return {"name": "Bullish Counterattack", "direction": "Bullish", "confidence": 0.75}
    if counterattack_bear(c[-2], c[-1]): return {"name": "Bearish Counterattack", "direction": "Bearish", "confidence": 0.75}
    if white_marubozu(c[-1]): return {"name": "White Marubozu", "direction": "Bullish", "confidence": 0.8}
    if black_marubozu(c[-1]): return {"name": "Black Marubozu", "direction": "Bearish", "confidence": 0.8}
    if doji(c[-1]): return {"name": "Doji", "direction": "Neutral", "confidence": 0.6}
    if spinning_top(c[-1]): return {"name": "Spinning Top", "direction": "Neutral", "confidence": 0.6}
    if three_white_soldiers(c[-3:]): return {"name": "Three White Soldiers", "direction": "Bullish", "confidence": 0.95}
    if three_black_crows(c[-3:]): return {"name": "Three Black Crows", "direction": "Bearish", "confidence": 0.95}

    return {"name": "None", "direction": "None", "confidence": 0.0}

# === AI Endpoint ===
@app.post("/ai/zones")
async def ai_zones(data: CandleData):
    candles = data.candles
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]

    # Support/Resistance (basic logic)
    support = min(lows[-10:])
    resistance = max(highs[-10:])

    # RSI
    delta = np.diff(closes)
    gain = np.mean([d for d in delta if d > 0]) if any(d > 0 for d in delta) else 0
    loss = np.mean([-d for d in delta if d < 0]) if any(d < 0 for d in delta) else 0
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs != 0 else 100

    # EMAs
    ema50 = np.mean(closes[-50:]) if len(closes) >= 50 else None
    ema100 = np.mean(closes[-100:]) if len(closes) >= 100 else None

    # Bollinger Bands
    bb_close = closes[-20:] if len(closes) >= 20 else closes
    ma = np.mean(bb_close)
    std = np.std(bb_close)
    upper_band = ma + 2 * std
    lower_band = ma - 2 * std

    # Pattern Detection
    pattern = detect_pattern(candles)

    # Signal Logic
    signal_confirmed = pattern["direction"] in ["Bullish", "Bearish"] and pattern["confidence"] > 0.8
    direction = pattern["direction"] if signal_confirmed else "N/A"

    return {
        "support": f"{support:.5f}",
        "resistance": f"{resistance:.5f}",
        "entry": f"{'Buy' if direction == 'Bullish' else 'Sell'} @ {closes[-1]:.5f}" if direction != "N/A" else "N/A",
        "target": f"{closes[-1] + 0.0020:.5f}" if direction == "Bullish" else (f"{closes[-1] - 0.0020:.5f}" if direction == "Bearish" else "N/A"),
        "stop": f"{closes[-1] - 0.0010:.5f}" if direction == "Bullish" else (f"{closes[-1] + 0.0010:.5f}" if direction == "Bearish" else "N/A"),
        "signal": signal_confirmed,
        "direction": direction,
        "pattern": pattern,
        "rsi": rsi,
        "trend": "Uptrend" if ema50 and ema100 and ema50 > ema100 else ("Downtrend" if ema50 and ema100 and ema50 < ema100 else "N/A"),
        "ema50": ema50,
        "ema100": ema100,
        "bollinger_upper": upper_band,
        "bollinger_lower": lower_band,
        "take_profit_ratio": 2
    }

# === Run app locally for testing ===
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
