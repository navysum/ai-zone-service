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
    allow_origins=["*"],  # Allow all origins or specify your frontend URL
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

@app.post("/ai/zones")
async def ai_zones(data: CandleData):
    candles = data.candles
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    
    # Your logic for technical analysis (RSI, EMA, support/resistance)
    
    # Sample response (replace with actual analysis)
    return {
        "support": f"{min(lows):.5f}",
        "resistance": f"{max(highs):.5f}",
        "entry": f"{closes[-1]:.5f}",
        "signal": True,  # Example signal
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
