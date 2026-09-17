import time
from collections import deque
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class Tick:
    timestamp: float
    price: float
    size: float
    side: str  # "buy" or "sell"

@dataclass
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class TickBuffer:
    """
    Circular tick buffer storing high-frequency trade ticks
    and synthesizing minute-based OHLCV candles.
    """
    def __init__(self, symbol: str, max_ticks: int = 500):
        self.symbol = symbol
        self.max_ticks = max_ticks
        self.ticks = deque(maxlen=max_ticks)
        self.candles: Dict[int, Candle] = {}

    def add_tick(self, price: float, size: float, side: str = "buy", timestamp: Optional[float] = None) -> Tick:
        ts = timestamp if timestamp is not None else time.time()
        tick = Tick(timestamp=ts, price=price, size=size, side=side)
        self.ticks.append(tick)

        # Aggregate into 1-minute candle
        minute_bucket = int(ts // 60) * 60
        if minute_bucket not in self.candles:
            self.candles[minute_bucket] = Candle(
                time=minute_bucket,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=size
            )
        else:
            c = self.candles[minute_bucket]
            c.high = max(c.high, price)
            c.low = min(c.low, price)
            c.close = price
            c.volume += size

        if len(self.candles) > 300:
            oldest_keys = sorted(self.candles.keys())[:-200]
            for old_k in oldest_keys:
                del self.candles[old_k]

        return tick

    def get_recent_ticks(self, count: int = 50) -> List[Dict[str, Any]]:
        return [asdict(t) for t in list(self.ticks)[-count:]]

    def get_candles(self, limit: int = 60) -> List[Dict[str, Any]]:
        sorted_times = sorted(self.candles.keys())[-limit:]
        return [asdict(self.candles[t]) for t in sorted_times]
