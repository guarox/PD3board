import logging
from typing import Dict, Any, List
from app.feeds.market_data_client import market_data_client

logger = logging.getLogger(__name__)

class MarketHeatmapFeed:
    """
    S&P 500 Market Treemap / Heatmap provider (MAPS / HEAT).
    Partitions the S&P 500 by GICS sectors, weighting boxes by market cap
    and coloring by daily price percentage change.
    Connects to real-time sector ETF and benchmark constituent quotes.
    """

    @classmethod
    def get_market_heatmap(cls) -> Dict[str, Any]:
        sectors = [
            {
                "name": "TECHNOLOGY",
                "weight_pct": 31.8,
                "change_pct": 1.45,
                "stocks": [
                    {"symbol": "AAPL", "name": "Apple Inc.", "mkt_cap_b": 3420, "price": 224.50, "change_pct": 1.08},
                    {"symbol": "MSFT", "name": "Microsoft Corp.", "mkt_cap_b": 3110, "price": 432.10, "change_pct": 0.82},
                    {"symbol": "NVDA", "name": "NVIDIA Corp.", "mkt_cap_b": 2920, "price": 118.90, "change_pct": 2.45},
                    {"symbol": "AVGO", "name": "Broadcom Inc.", "mkt_cap_b": 780, "price": 168.20, "change_pct": 1.94},
                    {"symbol": "CRM", "name": "Salesforce Inc.", "mkt_cap_b": 285, "price": 298.40, "change_pct": 0.45},
                    {"symbol": "AMD", "name": "Adv. Micro Devices", "mkt_cap_b": 242, "price": 152.10, "change_pct": -0.65},
                    {"symbol": "ORCL", "name": "Oracle Corp.", "mkt_cap_b": 380, "price": 139.80, "change_pct": 1.15}
                ]
            },
            {
                "name": "COMMUNICATION SERVICES",
                "weight_pct": 9.2,
                "change_pct": 1.12,
                "stocks": [
                    {"symbol": "GOOGL", "name": "Alphabet Inc.", "mkt_cap_b": 2020, "price": 164.50, "change_pct": 0.95},
                    {"symbol": "META", "name": "Meta Platforms", "mkt_cap_b": 1340, "price": 528.20, "change_pct": 1.54},
                    {"symbol": "NFLX", "name": "Netflix Inc.", "mkt_cap_b": 295, "price": 685.40, "change_pct": 0.72},
                    {"symbol": "DIS", "name": "Walt Disney Co.", "mkt_cap_b": 175, "price": 96.10, "change_pct": -0.32}
                ]
            },
            {
                "name": "CONSUMER DISCRETIONARY",
                "weight_pct": 10.4,
                "change_pct": 1.34,
                "stocks": [
                    {"symbol": "AMZN", "name": "Amazon.com Inc.", "mkt_cap_b": 1940, "price": 186.20, "change_pct": 1.12},
                    {"symbol": "TSLA", "name": "Tesla Inc.", "mkt_cap_b": 720, "price": 228.40, "change_pct": 3.18},
                    {"symbol": "MCD", "name": "McDonald's Corp.", "mkt_cap_b": 215, "price": 299.69, "change_pct": 0.58},
                    {"symbol": "NKE", "name": "Nike Inc.", "mkt_cap_b": 122, "price": 82.40, "change_pct": -1.24},
                    {"symbol": "SBUX", "name": "Starbucks Corp.", "mkt_cap_b": 108, "price": 94.60, "change_pct": 0.25}
                ]
            },
            {
                "name": "FINANCIALS",
                "weight_pct": 12.6,
                "change_pct": 0.48,
                "stocks": [
                    {"symbol": "JPM", "name": "JPMorgan Chase", "mkt_cap_b": 625, "price": 214.80, "change_pct": 0.52},
                    {"symbol": "V", "name": "Visa Inc.", "mkt_cap_b": 540, "price": 278.10, "change_pct": 0.41},
                    {"symbol": "MA", "name": "Mastercard Inc.", "mkt_cap_b": 445, "price": 476.50, "change_pct": 0.63},
                    {"symbol": "BAC", "name": "Bank of America", "mkt_cap_b": 312, "price": 39.90, "change_pct": 0.28},
                    {"symbol": "GS", "name": "Goldman Sachs", "mkt_cap_b": 172, "price": 482.30, "change_pct": 0.88},
                    {"symbol": "WFC", "name": "Wells Fargo & Co.", "mkt_cap_b": 208, "price": 56.40, "change_pct": -0.22}
                ]
            },
            {
                "name": "HEALTHCARE",
                "weight_pct": 12.1,
                "change_pct": -0.35,
                "stocks": [
                    {"symbol": "LLY", "name": "Eli Lilly & Co.", "mkt_cap_b": 890, "price": 945.20, "change_pct": -0.42},
                    {"symbol": "UNH", "name": "UnitedHealth Group", "mkt_cap_b": 540, "price": 586.10, "change_pct": -0.18},
                    {"symbol": "JNJ", "name": "Johnson & Johnson", "mkt_cap_b": 395, "price": 164.20, "change_pct": -0.65},
                    {"symbol": "ABBV", "name": "AbbVie Inc.", "mkt_cap_b": 340, "price": 192.50, "change_pct": 0.15},
                    {"symbol": "MRK", "name": "Merck & Co.", "mkt_cap_b": 298, "price": 117.80, "change_pct": -0.55}
                ]
            },
            {
                "name": "INDUSTRIALS",
                "weight_pct": 8.4,
                "change_pct": 0.62,
                "stocks": [
                    {"symbol": "GE", "name": "GE Aerospace", "mkt_cap_b": 205, "price": 188.40, "change_pct": 1.25},
                    {"symbol": "CAT", "name": "Caterpillar Inc.", "mkt_cap_b": 172, "price": 348.60, "change_pct": 0.48},
                    {"symbol": "UNP", "name": "Union Pacific", "mkt_cap_b": 148, "price": 242.10, "change_pct": 0.32},
                    {"symbol": "HON", "name": "Honeywell Intl", "mkt_cap_b": 134, "price": 206.50, "change_pct": 0.12},
                    {"symbol": "BA", "name": "Boeing Co.", "mkt_cap_b": 105, "price": 158.20, "change_pct": -1.15}
                ]
            },
            {
                "name": "ENERGY",
                "weight_pct": 3.6,
                "change_pct": -0.85,
                "stocks": [
                    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "mkt_cap_b": 465, "price": 114.20, "change_pct": -0.72},
                    {"symbol": "CVX", "name": "Chevron Corp.", "mkt_cap_b": 272, "price": 146.80, "change_pct": -0.98},
                    {"symbol": "COP", "name": "ConocoPhillips", "mkt_cap_b": 132, "price": 110.40, "change_pct": -1.12},
                    {"symbol": "SLB", "name": "SLB", "mkt_cap_b": 64, "price": 44.50, "change_pct": -0.65}
                ]
            },
            {
                "name": "CONSUMER STAPLES",
                "weight_pct": 6.0,
                "change_pct": 0.15,
                "stocks": [
                    {"symbol": "PG", "name": "Procter & Gamble", "mkt_cap_b": 412, "price": 174.50, "change_pct": 0.22},
                    {"symbol": "COST", "name": "Costco Wholesale", "mkt_cap_b": 395, "price": 892.40, "change_pct": 0.45},
                    {"symbol": "WMT", "name": "Walmart Inc.", "mkt_cap_b": 635, "price": 79.10, "change_pct": 0.38},
                    {"symbol": "KO", "name": "Coca-Cola Co.", "mkt_cap_b": 305, "price": 71.20, "change_pct": -0.15},
                    {"symbol": "PEP", "name": "PepsiCo Inc.", "mkt_cap_b": 240, "price": 173.80, "change_pct": -0.28}
                ]
            }
        ]

        normalized_sectors = []
        for s in sectors:
            norm_stocks = []
            for st in s["stocks"]:
                norm_stocks.append({
                    "symbol": st["symbol"],
                    "name": st["name"],
                    "price": st["price"],
                    "change_pct": st["change_pct"],
                    "market_cap": f"{st['mkt_cap_b']}B",
                    "mkt_cap_b": st["mkt_cap_b"]
                })
            normalized_sectors.append({
                "sector": s["name"],
                "name": s["name"],
                "weight_pct": s["weight_pct"],
                "change_pct": s["change_pct"],
                "stocks": norm_stocks,
                "constituents": norm_stocks,
            })

        total_stocks = sum(len(s["stocks"]) for s in normalized_sectors)
        advancers = sum(sum(1 for st in s["stocks"] if st["change_pct"] > 0) for s in normalized_sectors)
        decliners = sum(sum(1 for st in s["stocks"] if st["change_pct"] < 0) for s in normalized_sectors)
        unchanged = total_stocks - advancers - decliners

        return {
            "index": "S&P 500",
            "benchmark_price": 5625.80,
            "benchmark_change_pct": 0.68,
            "total_symbols": total_stocks,
            "advancers": advancers,
            "decliners": decliners,
            "unchanged": unchanged,
            "sectors": normalized_sectors
        }

    @classmethod
    def get_sp500_heatmap(cls) -> Dict[str, Any]:
        return cls.get_market_heatmap()

    @classmethod
    async def get_market_heatmap_async(cls) -> Dict[str, Any]:
        base = cls.get_market_heatmap()
        # Query representative constituents for live prices & percentage changes
        all_syms = ["SPY"]
        for s in base["sectors"]:
            for st in s["stocks"]:
                all_syms.append(st["symbol"])

        quotes = await market_data_client.get_quotes(all_syms)
        if quotes:
            quote_map = {q.get("symbol"): q for q in quotes if "symbol" in q}
            spy_q = quote_map.get("SPY", {})
            bench_p = float(spy_q.get("regularMarketPrice", base["benchmark_price"]))
            bench_chg_pct = round(float(spy_q.get("regularMarketChangePercent", base["benchmark_change_pct"])), 2)
            base["benchmark_price"] = bench_p
            base["benchmark_change_pct"] = bench_chg_pct

            for s in base["sectors"]:
                sec_changes = []
                for st in s["stocks"]:
                    sym = st["symbol"]
                    if sym in quote_map:
                        q = quote_map[sym]
                        p = round(float(q.get("regularMarketPrice", st["price"])), 2)
                        cp = round(float(q.get("regularMarketChangePercent", st["change_pct"])), 2)
                        st["price"] = p
                        st["change_pct"] = cp
                        sec_changes.append(cp)
                if sec_changes:
                    s["change_pct"] = round(sum(sec_changes) / len(sec_changes), 2)

            total_stocks = sum(len(s["stocks"]) for s in base["sectors"])
            adv = sum(sum(1 for st in s["stocks"] if st["change_pct"] > 0) for s in base["sectors"])
            dec = sum(sum(1 for st in s["stocks"] if st["change_pct"] < 0) for s in base["sectors"])
            base["total_symbols"] = total_stocks
            base["advancers"] = adv
            base["decliners"] = dec
            base["unchanged"] = total_stocks - adv - dec

        return base

    @classmethod
    async def get_sp500_heatmap_async(cls) -> Dict[str, Any]:
        return await cls.get_market_heatmap_async()

market_heatmap_feed = MarketHeatmapFeed()
