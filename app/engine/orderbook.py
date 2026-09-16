from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class OrderLevel:
    price: float
    size: float
    total: float = 0.0

class OrderBook:
    """
    Maintains a Level 2 Bid/Ask order book ladder with sorted levels
    and cumulative depth volume profiles.
    """
    def __init__(self, symbol: str, max_depth: int = 20):
        self.symbol = symbol
        self.max_depth = max_depth
        self.bids: List[OrderLevel] = []
        self.asks: List[OrderLevel] = []
        self.last_update_id: int = 0

    def update_levels(self, raw_bids: List[List[Any]], raw_asks: List[List[Any]], update_id: int = 0):
        self.last_update_id = update_id

        # Convert and sort bids (highest price first)
        bids = [OrderLevel(price=float(p), size=float(s)) for p, s in raw_bids[:self.max_depth]]
        bids.sort(key=lambda x: x.price, reverse=True)
        running_total = 0.0
        for b in bids:
            running_total += b.size
            b.total = round(running_total, 4)
        self.bids = bids

        # Convert and sort asks (lowest price first)
        asks = [OrderLevel(price=float(p), size=float(s)) for p, s in raw_asks[:self.max_depth]]
        asks.sort(key=lambda x: x.price)
        running_total = 0.0
        for a in asks:
            running_total += a.size
            a.total = round(running_total, 4)
        self.asks = asks

    def get_snapshot(self) -> Dict[str, Any]:
        best_bid = self.bids[0].price if self.bids else 0.0
        best_ask = self.asks[0].price if self.asks else 0.0
        spread = round(best_ask - best_bid, 4) if (best_bid and best_ask) else 0.0
        spread_bps = round((spread / best_bid) * 10000, 2) if best_bid else 0.0

        return {
            "symbol": self.symbol,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "spread_bps": spread_bps,
            "bids": [{"price": b.price, "size": b.size, "total": b.total} for b in self.bids],
            "asks": [{"price": a.price, "size": a.size, "total": a.total} for a in self.asks],
            "update_id": self.last_update_id
        }
