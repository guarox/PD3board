import asyncio
import random
import time
from typing import Dict, Any, List

class EquitiesFeed:
    """
    World Equity Indices (WEI) and US Equities data provider.
    Streams intraday ticks, net change, and percentage change.
    """
    def __init__(self):
        self.indices: Dict[str, Dict[str, Any]] = {
            "SPX": {"name": "S&P 500 INDEX", "price": 5625.80, "prev_close": 5595.75, "high": 5638.10, "low": 5588.20},
            "NDX": {"name": "NASDAQ 100", "price": 19680.40, "prev_close": 19520.10, "high": 19740.00, "low": 19480.50},
            "DJI": {"name": "DOW JONES INDUS.", "price": 41390.25, "prev_close": 41240.80, "high": 41450.00, "low": 41180.10},
            "RUT": {"name": "RUSSELL 2000", "price": 2210.60, "prev_close": 2195.40, "high": 2225.00, "low": 2190.20},
            "FTSE": {"name": "FTSE 100 INDEX", "price": 8280.15, "prev_close": 8245.50, "high": 8295.00, "low": 8230.00},
            "N225": {"name": "NIKKEI 225", "price": 36580.00, "prev_close": 36210.00, "high": 36720.00, "low": 36150.00},
            "DAX": {"name": "GERMAN DAX 40", "price": 18630.70, "prev_close": 18580.20, "high": 18680.00, "low": 18540.00},
        }

        self.equities: Dict[str, Dict[str, Any]] = {
            "AAPL": {"name": "APPLE INC", "sector": "EQUITY", "price": 224.50, "prev_close": 222.10, "pe": 33.8, "mkt_cap": "3.42T"},
            "NVDA": {"name": "NVIDIA CORP", "sector": "EQUITY", "price": 118.90, "prev_close": 116.40, "pe": 45.2, "mkt_cap": "2.92T"},
            "MSFT": {"name": "MICROSOFT CORP", "sector": "EQUITY", "price": 435.20, "prev_close": 432.80, "pe": 35.1, "mkt_cap": "3.23T"},
            "TSLA": {"name": "TESLA INC", "sector": "EQUITY", "price": 230.15, "prev_close": 226.70, "pe": 62.4, "mkt_cap": "735.8B"},
            "GOOGL": {"name": "ALPHABET INC", "sector": "EQUITY", "price": 162.40, "prev_close": 160.85, "pe": 24.3, "mkt_cap": "2.01T"},
            "MCD": {"name": "MCDONALD'S CORP", "sector": "EQUITY", "price": 298.50, "prev_close": 296.80, "pe": 26.4, "mkt_cap": "214.5B"},
        }

    def update_ticks(self) -> List[Dict[str, Any]]:
        """Simulates subtle market tick fluctuations."""
        updated = []
        for symbol, data in {**self.indices, **self.equities}.items():
            if random.random() < 0.4:
                drift = (random.random() - 0.48) * (data["price"] * 0.0004)
                data["price"] = round(data["price"] + drift, 2)
                chg = round(data["price"] - data["prev_close"], 2)
                chg_pct = round((chg / data["prev_close"]) * 100, 2)
                updated.append({
                    "symbol": symbol,
                    "price": data["price"],
                    "change": chg,
                    "change_pct": chg_pct,
                    "timestamp": time.time()
                })
        return updated

    def get_wei_matrix(self) -> List[Dict[str, Any]]:
        matrix = []
        for symbol, data in self.indices.items():
            chg = round(data["price"] - data["prev_close"], 2)
            chg_pct = round((chg / data["prev_close"]) * 100, 2)
            matrix.append({
                "symbol": symbol,
                "name": data["name"],
                "price": data["price"],
                "change": chg,
                "change_pct": chg_pct,
                "high": data["high"],
                "low": data["low"]
            })
        return matrix

    def get_security_description(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        if sym in self.equities:
            eq = self.equities[sym]
            chg = round(eq["price"] - eq["prev_close"], 2)
            chg_pct = round((chg / eq["prev_close"]) * 100, 2)
            return {
                "symbol": sym,
                "name": eq["name"],
                "sector": eq["sector"],
                "price": eq["price"],
                "change": chg,
                "change_pct": chg_pct,
                "pe": eq["pe"],
                "market_cap": eq["mkt_cap"],
                "currency": "USD",
                "exchange": "NASDAQ"
            }
        return {
            "symbol": sym,
            "name": f"{sym} FINANCIAL CORP",
            "sector": "EQUITY",
            "price": 100.00,
            "change": 0.0,
            "change_pct": 0.0,
            "pe": 20.0,
            "market_cap": "50.0B",
            "currency": "USD",
            "exchange": "NYSE"
        }
