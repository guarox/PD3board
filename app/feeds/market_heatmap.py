from typing import Dict, Any, List

class MarketHeatmapFeed:
    """
    S&P 500 Market Treemap / Heatmap provider (MAPS / HEAT).
    Partitions the S&P 500 by GICS sectors, weighting boxes by market cap
    and coloring by daily price percentage change.
    """

    @staticmethod
    def get_market_heatmap() -> Dict[str, Any]:
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
                "weight_pct": 11.8,
                "change_pct": 0.35,
                "stocks": [
                    {"symbol": "LLY", "name": "Eli Lilly & Co.", "mkt_cap_b": 860, "price": 912.40, "change_pct": 1.78},
                    {"symbol": "UNH", "name": "UnitedHealth Group", "mkt_cap_b": 525, "price": 574.10, "change_pct": 0.38},
                    {"symbol": "JNJ", "name": "Johnson & Johnson", "mkt_cap_b": 392, "price": 162.80, "change_pct": -0.12},
                    {"symbol": "ABBV", "name": "AbbVie Inc.", "mkt_cap_b": 345, "price": 194.20, "change_pct": 0.65},
                    {"symbol": "MRK", "name": "Merck & Co.", "mkt_cap_b": 292, "price": 115.30, "change_pct": -0.48}
                ]
            },
            {
                "name": "INDUSTRIALS",
                "weight_pct": 8.5,
                "change_pct": 0.62,
                "stocks": [
                    {"symbol": "GE", "name": "GE Aerospace", "mkt_cap_b": 205, "price": 188.50, "change_pct": 1.42},
                    {"symbol": "CAT", "name": "Caterpillar Inc.", "mkt_cap_b": 174, "price": 348.60, "change_pct": 0.68},
                    {"symbol": "UNP", "name": "Union Pacific", "mkt_cap_b": 152, "price": 248.90, "change_pct": 0.32},
                    {"symbol": "BA", "name": "Boeing Co.", "mkt_cap_b": 108, "price": 156.40, "change_pct": -1.45}
                ]
            },
            {
                "name": "ENERGY",
                "weight_pct": 3.8,
                "change_pct": -0.84,
                "stocks": [
                    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "mkt_cap_b": 462, "price": 116.20, "change_pct": -0.88},
                    {"symbol": "CVX", "name": "Chevron Corp.", "mkt_cap_b": 272, "price": 145.80, "change_pct": -0.72},
                    {"symbol": "COP", "name": "ConocoPhillips", "mkt_cap_b": 132, "price": 112.40, "change_pct": -1.05}
                ]
            },
            {
                "name": "CONSUMER STAPLES",
                "weight_pct": 6.1,
                "change_pct": 0.42,
                "stocks": [
                    {"symbol": "WMT", "name": "Walmart Inc.", "mkt_cap_b": 565, "price": 79.80, "change_pct": 0.64},
                    {"symbol": "PG", "name": "Procter & Gamble", "mkt_cap_b": 402, "price": 172.50, "change_pct": 0.22},
                    {"symbol": "COST", "name": "Costco Wholesale", "mkt_cap_b": 395, "price": 894.20, "change_pct": 0.78},
                    {"symbol": "KO", "name": "Coca-Cola Co.", "mkt_cap_b": 296, "price": 68.90, "change_pct": 0.31}
                ]
            }
        ]

        # Normalize sectors with sector/name and constituents/stocks for UI compatibility
        normalized_sectors = []
        for s in sectors:
            norm_stocks = []
            for st in s["stocks"]:
                norm_stocks.append({
                    "symbol": st["symbol"],
                    "name": st["name"],
                    "mkt_cap_b": st["mkt_cap_b"],
                    "price": st["price"],
                    "change_pct": st["change_pct"],
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
