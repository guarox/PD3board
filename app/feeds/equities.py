import asyncio
import random
import time
from typing import Dict, Any, List

class EquitiesFeed:
    """
    World Equity Indices (WEI) and US Equities data provider.
    Streams intraday ticks, net change, and percentage change.
    Provides fundamental institutional descriptions (DES).
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
            "AAPL": {
                "name": "APPLE INC",
                "sector": "EQUITY",
                "industry": "Consumer Electronics / Hardware",
                "exchange": "NASDAQ",
                "price": 224.50,
                "prev_close": 222.10,
                "pe": 33.8,
                "fwd_pe": 29.5,
                "eps": 6.64,
                "mkt_cap": "3.42T",
                "shares_out": "15.34B",
                "div_yield": "0.45%",
                "ex_div_date": "2026-08-12",
                "beta": 1.08,
                "range_52w": "164.08 - 237.23",
                "ceo": "Tim Cook",
                "hq": "Cupertino, CA",
                "revenue": "385.7B",
                "net_income": "100.4B"
            },
            "NVDA": {
                "name": "NVIDIA CORP",
                "sector": "EQUITY",
                "industry": "Semiconductors / AI Compute",
                "exchange": "NASDAQ",
                "price": 118.90,
                "prev_close": 116.40,
                "pe": 45.2,
                "fwd_pe": 32.1,
                "eps": 2.63,
                "mkt_cap": "2.92T",
                "shares_out": "24.56B",
                "div_yield": "0.03%",
                "ex_div_date": "2026-09-04",
                "beta": 1.68,
                "range_52w": "40.35 - 140.76",
                "ceo": "Jensen Huang",
                "hq": "Santa Clara, CA",
                "revenue": "120.9B",
                "net_income": "68.2B"
            },
            "MSFT": {
                "name": "MICROSOFT CORP",
                "sector": "EQUITY",
                "industry": "Systems Software & Cloud Infrastructure",
                "exchange": "NASDAQ",
                "price": 435.20,
                "prev_close": 432.80,
                "pe": 35.1,
                "fwd_pe": 30.4,
                "eps": 12.40,
                "mkt_cap": "3.23T",
                "shares_out": "7.43B",
                "div_yield": "0.69%",
                "ex_div_date": "2026-08-14",
                "beta": 0.89,
                "range_52w": "309.45 - 468.35",
                "ceo": "Satya Nadella",
                "hq": "Redmond, WA",
                "revenue": "245.1B",
                "net_income": "88.1B"
            },
            "TSLA": {
                "name": "TESLA INC",
                "sector": "EQUITY",
                "industry": "Automotive & Clean Energy",
                "exchange": "NASDAQ",
                "price": 230.15,
                "prev_close": 226.70,
                "pe": 62.4,
                "fwd_pe": 55.2,
                "eps": 3.69,
                "mkt_cap": "735.8B",
                "shares_out": "3.19B",
                "div_yield": "N/A",
                "ex_div_date": "N/A",
                "beta": 2.42,
                "range_52w": "138.80 - 271.00",
                "ceo": "Elon Musk",
                "hq": "Austin, TX",
                "revenue": "96.8B",
                "net_income": "14.9B"
            },
            "GOOGL": {
                "name": "ALPHABET INC",
                "sector": "EQUITY",
                "industry": "Internet Media & Cloud Platforms",
                "exchange": "NASDAQ",
                "price": 162.40,
                "prev_close": 160.85,
                "pe": 24.3,
                "fwd_pe": 20.8,
                "eps": 6.68,
                "mkt_cap": "2.01T",
                "shares_out": "12.38B",
                "div_yield": "0.49%",
                "ex_div_date": "2026-09-09",
                "beta": 1.05,
                "range_52w": "129.40 - 191.75",
                "ceo": "Sundar Pichai",
                "hq": "Mountain View, CA",
                "revenue": "307.4B",
                "net_income": "73.8B"
            },
            "MCD": {
                "name": "MCDONALD'S CORP",
                "sector": "EQUITY",
                "industry": "Fast Food & Quick Service Restaurants",
                "exchange": "NYSE",
                "price": 298.50,
                "prev_close": 296.80,
                "pe": 26.4,
                "fwd_pe": 23.9,
                "eps": 11.31,
                "mkt_cap": "214.5B",
                "shares_out": "718.5M",
                "div_yield": "2.28%",
                "ex_div_date": "2026-08-30",
                "beta": 0.65,
                "range_52w": "243.50 - 302.20",
                "ceo": "Christopher J. Kempczinski",
                "hq": "Chicago, IL",
                "revenue": "25.49B",
                "net_income": "8.47B"
            },
            "BTCUSDT": {
                "name": "BITCOIN / TETHER",
                "sector": "CRNCY",
                "industry": "Decentralized Digital Asset / Layer 1",
                "exchange": "COINBASE",
                "price": 64500.00,
                "prev_close": 63900.00,
                "pe": "N/A",
                "fwd_pe": "N/A",
                "eps": "N/A",
                "mkt_cap": "1.27T",
                "shares_out": "19.75M BTC",
                "div_yield": "N/A",
                "ex_div_date": "N/A",
                "beta": 2.85,
                "range_52w": "26,500 - 73,750",
                "ceo": "Satoshi Nakamoto",
                "hq": "Decentralized / P2P",
                "revenue": "N/A",
                "net_income": "N/A"
            }
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
                "industry": eq.get("industry", "Financial & Tech Services"),
                "exchange": eq.get("exchange", "NASDAQ"),
                "price": eq["price"],
                "change": chg,
                "change_pct": chg_pct,
                "pe": eq.get("pe", "N/A"),
                "fwd_pe": eq.get("fwd_pe", "N/A"),
                "eps": eq.get("eps", "N/A"),
                "market_cap": eq.get("mkt_cap", "N/A"),
                "shares_out": eq.get("shares_out", "N/A"),
                "div_yield": eq.get("div_yield", "N/A"),
                "ex_div_date": eq.get("ex_div_date", "N/A"),
                "beta": eq.get("beta", 1.0),
                "range_52w": eq.get("range_52w", "N/A"),
                "ceo": eq.get("ceo", "N/A"),
                "hq": eq.get("hq", "N/A"),
                "revenue": eq.get("revenue", "N/A"),
                "net_income": eq.get("net_income", "N/A"),
                "currency": "USD"
            }
        return {
            "symbol": sym,
            "name": f"{sym} CORP",
            "sector": "EQUITY",
            "industry": "Diversified Commercial Enterprise",
            "exchange": "NYSE",
            "price": 100.00,
            "change": 0.0,
            "change_pct": 0.0,
            "pe": 20.0,
            "fwd_pe": 18.5,
            "eps": 5.0,
            "market_cap": "50.0B",
            "shares_out": "500M",
            "div_yield": "1.50%",
            "ex_div_date": "N/A",
            "beta": 1.0,
            "range_52w": "85.00 - 115.00",
            "ceo": "Executive Leadership",
            "hq": "New York, NY",
            "revenue": "10.0B",
            "net_income": "1.5B",
            "currency": "USD"
        }
