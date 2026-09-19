import asyncio
import copy
import json
import datetime
import logging
import random
import time
import urllib.request
from typing import Dict, Any, List, Optional
from app.feeds.market_data_client import market_data_client

logger = logging.getLogger(__name__)

SYMBOL_MAP = {
    # Major US & Global Indices
    "SPX": "^GSPC",
    "^GSPC": "^GSPC",
    "SP500": "^GSPC",
    "NDX": "^IXIC",
    "^IXIC": "^IXIC",
    "NASDAQ": "^IXIC",
    "NASDAQ100": "^IXIC",
    "DJI": "^DJI",
    "^DJI": "^DJI",
    "DOW": "^DJI",
    "RUT": "^RUT",
    "^RUT": "^RUT",
    "RUSSELL": "^RUT",
    "VIX": "^VIX",
    "^VIX": "^VIX",
    "FTSE": "^FTSE",
    "^FTSE": "^FTSE",
    "N225": "^N225",
    "^N225": "^N225",
    "NIKKEI": "^N225",
    "DAX": "^GDAXI",
    "^GDAXI": "^GDAXI",
    # Crypto Assets
    "BTC": "BTC-USD",
    "BTCUSD": "BTC-USD",
    "BTCUSDT": "BTC-USD",
    "ETH": "ETH-USD",
    "ETHUSD": "ETH-USD",
    "ETHUSDT": "ETH-USD",
    "SOL": "SOL-USD",
    "SOLUSD": "SOL-USD",
    "SOLUSDT": "SOL-USD",
    "DOGE": "DOGE-USD",
    "DOGEUSD": "DOGE-USD",
    "DOGEUSDT": "DOGE-USD",
    "XRP": "XRP-USD",
    "XRPUSD": "XRP-USD",
    "XRPUSDT": "XRP-USD",
    "ADA": "ADA-USD",
    "ADAUSD": "ADA-USD",
    "ADAUSDT": "ADA-USD",
    "BNB": "BNB-USD",
    "BNBUSD": "BNB-USD",
    "BNBUSDT": "BNB-USD",
    "AVAX": "AVAX-USD",
    "AVAXUSD": "AVAX-USD",
    "AVAXUSDT": "AVAX-USD",
    # Global Currencies & Forex Pairs
    "EURUSD": "EURUSD=X",
    "EUR": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "GBP": "GBPUSD=X",
    "USDJPY": "JPY=X",
    "JPY": "JPY=X",
    "AUDUSD": "AUDUSD=X",
    "AUD": "AUDUSD=X",
    "USDCAD": "CAD=X",
    "CAD": "CAD=X",
    "USDCHF": "CHF=X",
    "CHF": "CHF=X",
    "NZDUSD": "NZDUSD=X",
    "NZD": "NZDUSD=X",
    "USDCNH": "CNH=X",
    "CNH": "CNH=X",
    "USDMXN": "MXN=X",
    "MXN": "MXN=X",
    "DXY": "DX-Y.NYB",
    # Commodities & Energy Futures
    "CL1": "CL=F",
    "CL": "CL=F",
    "CRUDE": "CL=F",
    "OIL": "CL=F",
    "CO1": "BZ=F",
    "BRENT": "BZ=F",
    "GC1": "GC=F",
    "GC": "GC=F",
    "GOLD": "GC=F",
    "SI1": "SI=F",
    "SI": "SI=F",
    "SILVER": "SI=F",
    "HG1": "HG=F",
    "HG": "HG=F",
    "COPPER": "HG=F",
    "NG1": "NG=F",
    "NG": "NG=F",
    "NATGAS": "NG=F",
    "W1": "ZW=F",
    "WHEAT": "ZW=F",
    "C1": "ZC=F",
    "CORN": "ZC=F",
    # Treasury Yields & Government Rates
    "US10Y": "^TNX",
    "TNX": "^TNX",
    "US5Y": "^FVX",
    "FVX": "^FVX",
    "US30Y": "^TYX",
    "TYX": "^TYX",
    "US2Y": "2YY=F",
    "US3M": "^IRX",
    "IRX": "^IRX",
}

PRIVATE_SECURITIES: Dict[str, Dict[str, Any]] = {
    "SPACEX": {
        "symbol": "SPACEX",
        "name": "SPACE EXPLORATION TECHNOLOGIES CORP (SPACEX)",
        "sector": "EQUITY",
        "industry": "Commercial Aerospace / Satellite Internet (Starlink) & Lunar Transport",
        "exchange": "PRIVATE / UNLISTED",
        "price": 112.00,
        "prev_close": 112.00,
        "pe": "N/A",
        "fwd_pe": "N/A",
        "eps": "N/A",
        "market_cap": "210.0B",
        "shares_out": "1.875B (Est.)",
        "div_yield": "0.00%",
        "ex_div_date": "N/A",
        "beta": 1.45,
        "range_52w": "97.00 - 112.00",
        "day_range": "112.00 - 112.00",
        "volume": 0,
        "ceo": "Elon Musk",
        "hq": "Starbase / Hawthorne, TX",
        "revenue": "13.3B (Est.)",
        "net_income": "3.2B (Est.)",
        "currency": "USD",
        "status": "UNLISTED / PRIVATE (Secondary Tender Offer)",
        "description": "Commercial space transportation, orbital rocketry, and global low-Earth orbit Starlink constellation."
    },
    "SPCX": {
        "symbol": "SPCX",
        "name": "SPACE EXPLORATION (SPACEX / SPACE SECTOR)",
        "sector": "EQUITY",
        "industry": "Commercial Space & Orbital Launch Infrastructure",
        "exchange": "PRIVATE / UNLISTED",
        "price": 112.00,
        "prev_close": 112.00,
        "pe": "N/A",
        "fwd_pe": "N/A",
        "eps": "N/A",
        "market_cap": "210.0B",
        "shares_out": "1.875B (Est.)",
        "div_yield": "0.00%",
        "ex_div_date": "N/A",
        "beta": 1.45,
        "range_52w": "97.00 - 112.00",
        "day_range": "112.00 - 112.00",
        "volume": 0,
        "ceo": "Elon Musk",
        "hq": "Starbase / Hawthorne, TX",
        "revenue": "13.3B (Est.)",
        "net_income": "3.2B (Est.)",
        "currency": "USD",
        "status": "UNLISTED / PRIVATE (Secondary Tender Offer)",
        "description": "Commercial space transportation, orbital rocketry, and global low-Earth orbit Starlink constellation."
    },
    "OPENAI": {
        "symbol": "OPENAI",
        "name": "OPENAI OPCO, LLC",
        "sector": "EQUITY",
        "industry": "Frontier Artificial Intelligence & Foundation Models",
        "exchange": "PRIVATE / UNLISTED",
        "price": 150.00,
        "prev_close": 150.00,
        "pe": "N/A",
        "fwd_pe": "N/A",
        "eps": "N/A",
        "market_cap": "157.0B",
        "shares_out": "1.05B (Est.)",
        "div_yield": "0.00%",
        "ex_div_date": "N/A",
        "beta": 2.10,
        "range_52w": "86.00 - 150.00",
        "day_range": "150.00 - 150.00",
        "volume": 0,
        "ceo": "Sam Altman",
        "hq": "San Francisco, CA",
        "revenue": "4.0B (Est.)",
        "net_income": "-5.0B (Est.)",
        "currency": "USD",
        "status": "UNLISTED / PRIVATE",
        "description": "Pioneering Artificial General Intelligence (AGI) research, ChatGPT, GPT-4, and frontier neural models."
    },
    "STRIPE": {
        "symbol": "STRIPE",
        "name": "STRIPE, INC.",
        "sector": "EQUITY",
        "industry": "Global Payments & Financial Infrastructure",
        "exchange": "PRIVATE / UNLISTED",
        "price": 28.00,
        "prev_close": 28.00,
        "pe": "N/A",
        "fwd_pe": "N/A",
        "eps": "N/A",
        "market_cap": "70.0B",
        "shares_out": "2.5B (Est.)",
        "div_yield": "0.00%",
        "ex_div_date": "N/A",
        "beta": 1.20,
        "range_52w": "20.00 - 28.00",
        "day_range": "28.00 - 28.00",
        "volume": 0,
        "ceo": "Patrick Collison",
        "hq": "South San Francisco, CA / Dublin",
        "revenue": "14.5B (Est.)",
        "net_income": "N/A",
        "currency": "USD",
        "status": "UNLISTED / PRIVATE",
        "description": "Financial infrastructure platform processing hundreds of billions in global digital commerce."
    },
    "ANTHROPIC": {
        "symbol": "ANTHROPIC",
        "name": "ANTHROPIC PBC",
        "sector": "EQUITY",
        "industry": "AI Safety & Foundation Models (Claude)",
        "exchange": "PRIVATE / UNLISTED",
        "price": 35.00,
        "prev_close": 35.00,
        "pe": "N/A",
        "fwd_pe": "N/A",
        "eps": "N/A",
        "market_cap": "40.0B",
        "shares_out": "1.14B (Est.)",
        "div_yield": "0.00%",
        "ex_div_date": "N/A",
        "beta": 1.90,
        "range_52w": "18.00 - 35.00",
        "day_range": "35.00 - 35.00",
        "volume": 0,
        "ceo": "Dario Amodei",
        "hq": "San Francisco, CA",
        "revenue": "1.0B (Est.)",
        "net_income": "N/A",
        "currency": "USD",
        "status": "UNLISTED / PRIVATE",
        "description": "AI safety and frontier research lab developing the Claude family of foundation models."
    }
}

PEER_BASELINES: Dict[str, Dict[str, Any]] = {
    "MCD": {"name": "McDonald's Corp", "price": 248.24, "pe": 20.2, "fwd_pe": 17.8, "ev_ebitda": 15.4, "ps": 6.3, "op_margin": "46.5%", "roe": "N/A", "div_yield": "3.11%"},
    "YUM": {"name": "Yum! Brands Inc", "price": 137.99, "pe": 17.4, "fwd_pe": 19.7, "ev_ebitda": 16.4, "ps": 4.3, "op_margin": "32.8%", "roe": "N/A", "div_yield": "2.17%"},
    "QSR": {"name": "Restaurant Brands Intl", "price": 72.88, "pe": 18.3, "fwd_pe": 16.4, "ev_ebitda": 14.2, "ps": 3.4, "op_margin": "27.7%", "roe": "34.8%", "div_yield": "3.57%"},
    "WEN": {"name": "Wendy's Co", "price": 6.74, "pe": 10.2, "fwd_pe": 12.9, "ev_ebitda": 11.0, "ps": 0.6, "op_margin": "14.3%", "roe": "108.0%", "div_yield": "4.16%"},
    "SBUX": {"name": "Starbucks Corp", "price": 95.83, "pe": 55.4, "fwd_pe": 30.7, "ev_ebitda": 22.7, "ps": 2.8, "op_margin": "12.9%", "roe": "N/A", "div_yield": "2.59%"},
    "NVDA": {"name": "Nvidia Corp", "price": 118.90, "pe": 45.2, "fwd_pe": 32.1, "ev_ebitda": 26.5, "ps": 17.7, "op_margin": "66.2%", "roe": "117.2%", "div_yield": "0.45%"},
    "AMD": {"name": "Advanced Micro Devices", "price": 152.80, "pe": 112.5, "fwd_pe": 28.4, "ev_ebitda": 94.7, "ps": 22.1, "op_margin": "17.2%", "roe": "10.2%", "div_yield": "0.00%"},
    "INTC": {"name": "Intel Corp", "price": 20.80, "pe": "N/A", "fwd_pe": 18.5, "ev_ebitda": 34.7, "ps": 10.1, "op_margin": "12.2%", "roe": "-10.7%", "div_yield": "0.00%"},
    "TSM": {"name": "Taiwan Semiconductor", "price": 174.20, "pe": 28.1, "fwd_pe": 22.5, "ev_ebitda": 4.9, "ps": 0.5, "op_margin": "60.3%", "roe": "40.0%", "div_yield": "0.94%"},
    "AVGO": {"name": "Broadcom Inc", "price": 168.40, "pe": 65.2, "fwd_pe": 27.8, "ev_ebitda": 33.3, "ps": 19.2, "op_margin": "54.3%", "roe": "44.2%", "div_yield": "0.73%"},
    "AAPL": {"name": "Apple Inc", "price": 228.40, "pe": 33.8, "fwd_pe": 29.5, "ev_ebitda": 29.3, "ps": 10.5, "op_margin": "32.6%", "roe": "148.8%", "div_yield": "0.32%"},
    "MSFT": {"name": "Microsoft Corp", "price": 425.20, "pe": 35.2, "fwd_pe": 31.0, "ev_ebitda": 24.1, "ps": 12.8, "op_margin": "44.6%", "roe": "38.5%", "div_yield": "0.75%"},
    "GOOGL": {"name": "Alphabet Inc", "price": 182.10, "pe": 24.6, "fwd_pe": 21.2, "ev_ebitda": 18.2, "ps": 6.9, "op_margin": "32.0%", "roe": "31.2%", "div_yield": "0.44%"},
    "AMZN": {"name": "Amazon.com Inc", "price": 186.50, "pe": 42.1, "fwd_pe": 34.5, "ev_ebitda": 17.5, "ps": 3.4, "op_margin": "10.8%", "roe": "21.5%", "div_yield": "0.00%"},
    "META": {"name": "Meta Platforms Inc", "price": 580.40, "pe": 27.8, "fwd_pe": 24.0, "ev_ebitda": 16.8, "ps": 8.7, "op_margin": "41.2%", "roe": "36.4%", "div_yield": "0.35%"},
    "JPM": {"name": "JPMorgan Chase & Co", "price": 215.30, "pe": 12.4, "fwd_pe": 11.8, "ev_ebitda": 12.8, "ps": 3.6, "op_margin": "39.4%", "roe": "16.8%", "div_yield": "2.25%"},
    "BAC": {"name": "Bank of America Corp", "price": 39.50, "pe": 13.8, "fwd_pe": 11.2, "ev_ebitda": 11.2, "ps": 2.8, "op_margin": "31.2%", "roe": "10.4%", "div_yield": "2.55%"},
    "WFC": {"name": "Wells Fargo & Co", "price": 56.40, "pe": 12.1, "fwd_pe": 10.5, "ev_ebitda": 10.5, "ps": 2.4, "op_margin": "28.5%", "roe": "11.2%", "div_yield": "2.75%"},
    "GS": {"name": "Goldman Sachs Group", "price": 490.20, "pe": 15.6, "fwd_pe": 12.5, "ev_ebitda": 13.4, "ps": 3.1, "op_margin": "33.8%", "roe": "12.9%", "div_yield": "2.40%"},
    "MS": {"name": "Morgan Stanley", "price": 102.80, "pe": 16.2, "fwd_pe": 13.1, "ev_ebitda": 12.1, "ps": 2.9, "op_margin": "30.4%", "roe": "13.5%", "div_yield": "3.10%"},
    "TSLA": {"name": "Tesla Inc", "price": 240.50, "pe": 62.4, "fwd_pe": 54.0, "ev_ebitda": 48.2, "ps": 7.4, "op_margin": "8.2%", "roe": "14.1%", "div_yield": "0.00%"},
    "F": {"name": "Ford Motor Co", "price": 10.80, "pe": 11.5, "fwd_pe": 7.2, "ev_ebitda": 8.5, "ps": 0.3, "op_margin": "4.1%", "roe": "9.8%", "div_yield": "5.60%"},
    "GM": {"name": "General Motors Co", "price": 48.50, "pe": 5.4, "fwd_pe": 4.9, "ev_ebitda": 6.8, "ps": 0.4, "op_margin": "6.5%", "roe": "14.2%", "div_yield": "1.05%"},
    "RIVN": {"name": "Rivian Automotive", "price": 13.20, "pe": "N/A", "fwd_pe": "N/A", "ev_ebitda": "N/A", "ps": 2.1, "op_margin": "-78.4%", "roe": "-45.2%", "div_yield": "0.00%"},
    "TM": {"name": "Toyota Motor Corp", "price": 178.60, "pe": 8.2, "fwd_pe": 8.0, "ev_ebitda": 9.1, "ps": 0.8, "op_margin": "11.4%", "roe": "13.6%", "div_yield": "3.20%"}
}

class EquitiesFeed:
    """
    World Equity Indices (WEI) and US Equities data provider.
    Streams intraday ticks, net change, and percentage change.
    Provides fundamental institutional descriptions (DES), financial statements (FA),
    analyst recommendations (ANR), and real-time upstream market data integration.
    """
    def __init__(self):
        self.live_cache: Dict[str, Dict[str, Any]] = {}
        self.historical_cache: Dict[str, Dict[str, Any]] = {}
        self.simulated_prices: Dict[str, float] = {}

        self.indices: Dict[str, Dict[str, Any]] = {
            "SPX": {"name": "S&P 500 INDEX", "price": 7636.00, "prev_close": 7615.00, "high": 7645.00, "low": 7605.00},
            "NDX": {"name": "NASDAQ 100", "price": 26390.00, "prev_close": 26250.00, "high": 26450.00, "low": 26180.00},
            "DJI": {"name": "DOW JONES INDUS.", "price": 51800.00, "prev_close": 51600.00, "high": 51920.00, "low": 51500.00},
            "RUT": {"name": "RUSSELL 2000", "price": 2885.00, "prev_close": 2865.00, "high": 2895.00, "low": 2855.00},
            "FTSE": {"name": "FTSE 100 INDEX", "price": 10815.00, "prev_close": 10760.00, "high": 10850.00, "low": 10720.00},
            "N225": {"name": "NIKKEI 225", "price": 64135.00, "prev_close": 63800.00, "high": 64300.00, "low": 63600.00},
            "DAX": {"name": "GERMAN DAX 40", "price": 25715.00, "prev_close": 25620.00, "high": 25800.00, "low": 25550.00},
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
                "price": 76250.00,
                "prev_close": 75500.00,
                "pe": "N/A",
                "fwd_pe": "N/A",
                "eps": "N/A",
                "mkt_cap": "1.50T",
                "shares_out": "19.75M BTC",
                "div_yield": "N/A",
                "ex_div_date": "N/A",
                "beta": 2.85,
                "range_52w": "52,000 - 76,500",
                "ceo": "Satoshi Nakamoto",
                "hq": "Decentralized / P2P",
                "revenue": "N/A",
                "net_income": "N/A"
            }
        }

    def fetch_live_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        sym = symbol.upper().strip()
        now = time.time()
        if sym in self.live_cache and self.live_cache[sym]["expires"] > now:
            return self.live_cache[sym]["data"]

        target = SYMBOL_MAP.get(sym, sym)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{target}?interval=1m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3.5) as res:
                payload = json.loads(res.read().decode())
                chart = payload.get("chart", {})
                res_list = chart.get("result")
                if not res_list:
                    return None
                res_obj = res_list[0]
                meta = res_obj.get("meta", {})
                timestamps = res_obj.get("timestamp", [])
                indicators = res_obj.get("indicators", {}).get("quote", [{}])[0]

                candles = []
                opens = indicators.get("open", [])
                highs = indicators.get("high", [])
                lows = indicators.get("low", [])
                closes = indicators.get("close", [])
                volumes = indicators.get("volume", [])

                for i, ts in enumerate(timestamps):
                    if i < len(opens) and i < len(closes):
                        o = opens[i]
                        h = highs[i]
                        l = lows[i]
                        c = closes[i]
                        v = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                        if None not in (o, h, l, c):
                            fv_o, fv_h, fv_l, fv_c = float(o), float(h), float(l), float(c)
                            dec = 6 if fv_c < 0.01 else (5 if fv_c < 0.5 else (4 if fv_c < 2.0 else (3 if fv_c < 20.0 else 2)))
                            candles.append({
                                "time": int(ts),
                                "open": round(fv_o, dec),
                                "high": round(fv_h, dec),
                                "low": round(fv_l, dec),
                                "close": round(fv_c, dec),
                                "volume": round(float(v), 1)
                            })

                price = meta.get("regularMarketPrice")
                prev_close = meta.get("chartPreviousClose") or meta.get("previousClose") or price
                if price is None and candles:
                    price = candles[-1]["close"]

                p_val = float(price) if price is not None else 100.0
                pc_val = float(prev_close) if prev_close is not None else p_val
                p_dec = 6 if p_val < 0.01 else (5 if p_val < 0.5 else (4 if p_val < 2.0 else (3 if p_val < 20.0 else 2)))

                quote_data = {
                    "symbol": sym,
                    "name": meta.get("shortName") or meta.get("longName") or sym,
                    "price": round(p_val, p_dec),
                    "prev_close": round(pc_val, p_dec),
                    "day_high": meta.get("regularMarketDayHigh"),
                    "day_low": meta.get("regularMarketDayLow"),
                    "range_52w": f"{meta.get('fiftyTwoWeekLow', 'N/A')} - {meta.get('fiftyTwoWeekHigh', 'N/A')}",
                    "volume": meta.get("regularMarketVolume", 0),
                    "exchange": meta.get("exchangeName", "US"),
                    "currency": meta.get("currency", "USD"),
                    "candles": candles
                }
                self.live_cache[sym] = {"data": quote_data, "expires": now + 15.0}
                return quote_data
        except Exception as e:
            logger.debug(f"Live market quote fetch failed for {symbol}: {e}")
            return None

    def fetch_historical_candles(self, symbol: str, interval: str = "1M") -> List[Dict[str, Any]]:
        """
        Fetches true multi-timeframe historical candles for the given interval:
        - 1M  -> interval=1m,  range=1d (or 5d for forex/crypto)
        - 5M  -> interval=5m,  range=5d
        - 15M -> interval=15m, range=1mo
        - 1H  -> interval=60m, range=3mo
        - 1D  -> interval=1d,  range=1y
        """
        sym = symbol.upper().strip()
        norm_interval = interval.upper() if interval else "1M"
        if norm_interval not in {"1M", "5M", "15M", "1H", "1D"}:
            norm_interval = "1M"

        cache_key = f"{sym}_{norm_interval}"
        now = time.time()
        if cache_key in self.historical_cache and self.historical_cache[cache_key]["expires"] > now:
            return self.historical_cache[cache_key]["candles"]

        config_map = {
            "1M": ("1m", "5d", 20.0),    # 5 full trading days of 1m bars (~2,000 to 5,800 bars)
            "5M": ("5m", "1mo", 60.0),   # 1 full month of 5m bars (~1,700 to 8,900 bars)
            "15M": ("15m", "1mo", 180.0), # 1 full month of 15m bars (~600 to 3,000 bars)
            "1H": ("60m", "1y", 300.0),  # 1 full year of hourly bars (~1,750 to 8,700 bars)
            "1D": ("1d", "5y", 1800.0),  # 5 full years of daily bars (~1,250 to 1,820 bars)
        }
        yf_interval, yf_range, cache_ttl = config_map[norm_interval]

        target = SYMBOL_MAP.get(sym, sym)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{target}?interval={yf_interval}&range={yf_range}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=4.0) as res:
                payload = json.loads(res.read().decode())
                chart = payload.get("chart", {})
                res_list = chart.get("result")
                if res_list:
                    res_obj = res_list[0]
                    timestamps = res_obj.get("timestamp", [])
                    indicators = res_obj.get("indicators", {}).get("quote", [{}])[0]

                    candles = []
                    opens = indicators.get("open", [])
                    highs = indicators.get("high", [])
                    lows = indicators.get("low", [])
                    closes = indicators.get("close", [])
                    volumes = indicators.get("volume", [])

                    for i, ts in enumerate(timestamps):
                        if i < len(opens) and i < len(closes):
                            o = opens[i]
                            h = highs[i]
                            l = lows[i]
                            c = closes[i]
                            v = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                            if None not in (o, h, l, c):
                                fv_o, fv_h, fv_l, fv_c = float(o), float(h), float(l), float(c)
                                dec = 6 if fv_c < 0.01 else (5 if fv_c < 0.5 else (4 if fv_c < 2.0 else (3 if fv_c < 20.0 else 2)))
                                candles.append({
                                    "time": int(ts),
                                    "open": round(fv_o, dec),
                                    "high": round(fv_h, dec),
                                    "low": round(fv_l, dec),
                                    "close": round(fv_c, dec),
                                    "volume": round(float(v), 1)
                                })

                    if candles:
                        self.historical_cache[cache_key] = {
                            "candles": candles,
                            "expires": now + cache_ttl
                        }
                        return candles
        except Exception as e:
            logger.debug(f"Historical candle fetch failed for {symbol} ({norm_interval}): {e}")

        # Fallback to simulated multi-timeframe candles tailored to interval
        candles = self._generate_fallback_candles(sym, norm_interval)
        self.historical_cache[cache_key] = {
            "candles": candles,
            "expires": now + 60.0
        }
        return candles

    def _generate_fallback_candles(self, symbol: str, interval: str) -> List[Dict[str, Any]]:
        expected_price = self.get_security_price(symbol, prefer_live=True)
        base_price = expected_price if expected_price > 0 else 100.0

        if base_price < 0.01:
            dec = 6
        elif base_price < 0.5:
            dec = 5
        elif base_price < 2.0:
            dec = 4
        elif base_price < 20.0:
            dec = 3
        else:
            dec = 2

        now_ts = int(time.time())
        step_seconds = 60
        num_candles = 90
        volatility_scale = 0.0006

        if interval == "5M":
            step_seconds = 300
            num_candles = 120
            volatility_scale = 0.0012
        elif interval == "15M":
            step_seconds = 900
            num_candles = 140
            volatility_scale = 0.0025
        elif interval == "1H":
            step_seconds = 3600
            num_candles = 160
            volatility_scale = 0.0050
        elif interval == "1D":
            step_seconds = 86400
            num_candles = 250
            volatility_scale = 0.0150

        import random
        rng = random.Random(hash(f"{symbol}_{interval}") & 0xFFFFFFFF)
        step = max(10 ** (-dec), base_price * volatility_scale)

        candles = []
        curr = base_price * (1.0 - (num_candles * 0.0005))
        for idx in range(num_candles):
            c_time = now_ts - (num_candles - 1 - idx) * step_seconds
            drift = (rng.random() - 0.49) * step
            mean_rev = (base_price - curr) * 0.03
            next_val = round(curr + drift + mean_rev, dec)

            c_open = round(curr, dec)
            c_close = next_val
            body_min = min(c_open, c_close)
            body_max = max(c_open, c_close)
            wick_up = round(rng.uniform(0.1, 0.4) * step, dec)
            wick_dn = round(rng.uniform(0.1, 0.4) * step, dec)
            c_high = round(body_max + wick_up, dec)
            c_low = round(max(body_min - wick_dn, 0.000001), dec)
            c_vol = round(rng.uniform(5000.0, 500000.0) if interval == "1D" else rng.uniform(200.0, 3000.0), 1)

            candles.append({
                "time": c_time,
                "open": c_open,
                "high": c_high,
                "low": c_low,
                "close": c_close,
                "volume": c_vol
            })
            curr = next_val

        return candles

    def get_historical_candles(self, symbol: str) -> List[Dict[str, Any]]:
        return self.fetch_historical_candles(symbol, "1M")

    def get_market_sessions(self) -> Dict[str, str]:
        """Calculates current trading session status for major global exchanges."""
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        weekday = now_utc.weekday()  # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        is_weekend = weekday >= 5

        # 1. NYSE / NASDAQ (Eastern Time: UTC-4 in EDT / UTC-5 in EST)
        utc_minutes = now_utc.hour * 60 + now_utc.minute
        if is_weekend:
            nyse_status = "CLOSED"
        elif 13 * 60 + 30 <= utc_minutes < 20 * 60:
            nyse_status = "OPEN"
        elif 20 * 60 <= utc_minutes < 24 * 60:
            nyse_status = "AFTER-HOURS"
        elif 8 * 60 <= utc_minutes < 13 * 60 + 30:
            nyse_status = "PRE-MARKET"
        else:
            nyse_status = "CLOSED"

        # 2. LSE (London: UTC+1 in BST / UTC+0 in GMT)
        if is_weekend:
            lse_status = "CLOSED"
        elif 7 * 60 <= utc_minutes < 15 * 60 + 30:
            lse_status = "OPEN"
        else:
            lse_status = "CLOSED"

        # 3. TSE (Tokyo: UTC+9, no DST)
        tokyo_now = now_utc + datetime.timedelta(hours=9)
        tokyo_weekday = tokyo_now.weekday()
        tokyo_minutes = tokyo_now.hour * 60 + tokyo_now.minute
        if tokyo_weekday >= 5:
            tse_status = "CLOSED"
        elif (9 * 60 <= tokyo_minutes < 11 * 60 + 30) or (12 * 60 + 30 <= tokyo_minutes < 15 * 60 + 30):
            tse_status = "OPEN"
        elif 11 * 60 + 30 <= tokyo_minutes < 12 * 60 + 30:
            tse_status = "LUNCH"
        else:
            tse_status = "CLOSED"

        return {
            "NYSE": nyse_status,
            "LSE": lse_status,
            "TSE": tse_status,
            "CRNCY": "OPEN"
        }

    def is_symbol_market_open(self, symbol: str) -> bool:
        """Determines if the given asset is currently in an active trading session."""
        sym = symbol.upper()
        if sym in ("BTC", "ETH", "SOL", "BTCUSD", "BTCUSDT", "ETHUSD", "ETHUSDT", "SOLUSD", "SOLUSDT"):
            return True
        if sym in PRIVATE_SECURITIES:
            return False

        sessions = self.get_market_sessions()
        if sym in ("N225", "^N225"):
            return sessions["TSE"] == "OPEN"
        if sym in ("FTSE", "^FTSE", "DAX", "^GDAXI"):
            return sessions["LSE"] == "OPEN"
        # Default US equities and indices (NYSE / NASDAQ)
        return sessions["NYSE"] == "OPEN"

    def update_ticks(self) -> List[Dict[str, Any]]:
        """Simulates subtle market tick fluctuations only for currently open markets."""
        updated = []
        for symbol, data in {**self.indices, **self.equities}.items():
            sym_upper = symbol.upper()
            # Live crypto feeds are streamed directly by Coinbase WebSocket - do not simulate or overwrite
            if sym_upper in ("BTC", "ETH", "SOL", "BTCUSD", "BTCUSDT", "ETHUSD", "ETHUSDT", "SOLUSD", "SOLUSDT"):
                continue

            # If market is closed, freeze prices at official close / cached price
            if not self.is_symbol_market_open(symbol):
                continue

            # Target / anchor price from live quote or baseline
            quote = self.live_cache.get(symbol, {}).get("data")
            target_price = float(quote["price"]) if quote else float(data["price"])
            prev_close = float(quote["prev_close"]) if quote else float(data["prev_close"])

            # Initialize simulated price to target if not present or if drifted too far (>1.0%)
            curr_sim = self.simulated_prices.get(symbol)
            if curr_sim is None or abs(curr_sim - target_price) / target_price > 0.01:
                curr_sim = target_price
                self.simulated_prices[symbol] = curr_sim

            if random.random() < 0.4:
                # Realistic minimum tick size based on asset price level
                if target_price >= 10000:
                    tick_size = 0.50
                elif target_price >= 1000:
                    tick_size = 0.10
                elif target_price >= 100:
                    tick_size = 0.02
                else:
                    tick_size = 0.01

                # Continuous random walk with gentle mean-reversion toward target anchor
                step_choice = random.choice([-1, 0, 1]) * tick_size
                reversion = (target_price - curr_sim) * 0.03
                new_price = round(curr_sim + step_choice + reversion, 2)
                self.simulated_prices[symbol] = new_price

                chg = round(new_price - prev_close, 2)
                chg_pct = round((chg / prev_close) * 100, 2) if prev_close else 0.0
                updated.append({
                    "symbol": symbol,
                    "price": new_price,
                    "change": chg,
                    "change_pct": chg_pct,
                    "timestamp": time.time()
                })
        return updated

    def get_wei_matrix(self) -> List[Dict[str, Any]]:
        matrix = []
        for symbol, data in self.indices.items():
            quote = self.fetch_live_quote(symbol)
            if quote:
                price = quote["price"]
                prev_close = quote["prev_close"]
                chg = round(price - prev_close, 2)
                chg_pct = round((chg / prev_close) * 100, 2) if prev_close else 0.0
                high = quote.get("day_high") or price
                low = quote.get("day_low") or price
            else:
                price = data["price"]
                chg = round(data["price"] - data["prev_close"], 2)
                chg_pct = round((chg / data["prev_close"]) * 100, 2)
                high = data["high"]
                low = data["low"]

            matrix.append({
                "symbol": symbol,
                "name": data["name"],
                "price": price,
                "change": chg,
                "change_pct": chg_pct,
                "high": high,
                "low": low
            })
        return matrix

    def get_security_price(self, symbol: str, prefer_live: bool = True) -> float:
        sym = symbol.upper()
        if sym in PRIVATE_SECURITIES:
            return float(PRIVATE_SECURITIES[sym]["price"])

        if prefer_live:
            quote = self.fetch_live_quote(sym)
            if quote and quote.get("price"):
                return float(quote["price"])

        if sym in self.indices:
            return float(self.indices[sym]["price"])
        if sym in self.equities:
            return float(self.equities[sym]["price"])

        quote = self.fetch_live_quote(sym)
        if quote and quote.get("price"):
            return float(quote["price"])

        return 100.0

    def get_security_description(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        if sym in PRIVATE_SECURITIES:
            sec = copy.deepcopy(PRIVATE_SECURITIES[sym])
            chg = round(sec["price"] - sec["prev_close"], 2)
            chg_pct = round((chg / sec["prev_close"]) * 100, 2) if sec["prev_close"] else 0.0
            sec["change"] = chg
            sec["change_pct"] = chg_pct
            return sec

        if sym in self.equities:
            eq = copy.deepcopy(self.equities[sym])
            chg = round(eq["price"] - eq["prev_close"], 2)
            chg_pct = round((chg / eq["prev_close"]) * 100, 2)
            quote = self.fetch_live_quote(sym)
            if quote:
                eq["live_price"] = quote["price"]
                eq["live_change"] = round(quote["price"] - quote["prev_close"], 2)
                eq["live_change_pct"] = round((eq["live_change"] / quote["prev_close"]) * 100, 2) if quote["prev_close"] else 0.0
                if quote.get("range_52w") and quote["range_52w"] != "N/A - N/A":
                    eq["range_52w"] = quote["range_52w"]
                if quote.get("volume"):
                    eq["volume"] = quote["volume"]

            return {
                "symbol": sym,
                "name": eq["name"],
                "sector": eq["sector"],
                "industry": eq.get("industry", "Financial & Tech Services"),
                "exchange": eq.get("exchange", "NASDAQ"),
                "price": eq.get("live_price", eq["price"]),
                "change": eq.get("live_change", chg),
                "change_pct": eq.get("live_change_pct", chg_pct),
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
        elif sym in self.indices:
            idx = copy.deepcopy(self.indices[sym])
            chg = round(idx["price"] - idx["prev_close"], 2)
            chg_pct = round((chg / idx["prev_close"]) * 100, 2)
            quote = self.fetch_live_quote(sym)
            price = quote["price"] if quote else idx["price"]
            if quote:
                chg = round(price - quote["prev_close"], 2)
                chg_pct = round((chg / quote["prev_close"]) * 100, 2) if quote["prev_close"] else 0.0

            return {
                "symbol": sym,
                "name": idx["name"],
                "sector": "INDEX",
                "industry": "Broad Market Benchmark / Equity Index",
                "description": f"Benchmark equity index representing {idx['name']} components.",
                "exchange": "CBOE / NYSE / NASDAQ",
                "price": price,
                "change": chg,
                "change_pct": chg_pct,
                "pe": 25.8,
                "fwd_pe": 22.4,
                "eps": 218.05,
                "market_cap": "46.2T",
                "shares_out": "500 Components",
                "div_yield": "1.48%",
                "ex_div_date": "Quarterly",
                "beta": 1.00,
                "range_52w": f"{round(price * 0.82, 2)} - {round(price * 1.08, 2)}",
                "ceo": "Index Committee",
                "hq": "New York, NY",
                "revenue": "2.1T (Components)",
                "net_income": "285B (Components)",
                "currency": "USD"
            }

        # Any other US equity, ETF, or commodity
        quote = self.fetch_live_quote(sym)
        if quote:
            chg = round(quote["price"] - quote["prev_close"], 2)
            chg_pct = round((chg / quote["prev_close"]) * 100, 2) if quote["prev_close"] else 0.0
            return {
                "symbol": sym,
                "name": quote["name"].upper(),
                "sector": "EQUITY",
                "industry": "US Equities & Exchange Traded Funds",
                "exchange": quote.get("exchange", "NASDAQ"),
                "price": quote["price"],
                "change": chg,
                "change_pct": chg_pct,
                "pe": "N/A",
                "fwd_pe": "N/A",
                "eps": "N/A",
                "market_cap": f"{round(quote['price'] * 0.45, 1)}B" if quote.get("volume") else "N/A",
                "shares_out": "N/A",
                "div_yield": "N/A",
                "ex_div_date": "N/A",
                "beta": 1.15,
                "range_52w": quote.get("range_52w", "N/A"),
                "day_range": f"{quote.get('day_low', 'N/A')} - {quote.get('day_high', 'N/A')}",
                "volume": quote.get("volume", 0),
                "ceo": "Executive Leadership",
                "hq": "United States",
                "revenue": "N/A",
                "net_income": "N/A",
                "currency": quote.get("currency", "USD")
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

    def get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """
        Analyst Recommendations (ANR) Wall Street consensus breakdown.
        """
        sym = symbol.upper()
        price = self.get_security_price(sym)

        # Profiles
        anr_profiles = {
            "MCD": {
                "consensus": "MODERATE BUY",
                "consensus_score": 4.25, # out of 5
                "target_price": 332.00,
                "target_high": 360.00,
                "target_low": 295.00,
                "buys": 26, "holds": 11, "sells": 2, "total": 39,
                "brokers": [
                    {"firm": "GOLDMAN SACHS", "analyst": "Katherine Fogertey", "rating": "BUY", "target": 340.00, "date": "2026-09-10"},
                    {"firm": "MORGAN STANLEY", "analyst": "John Glass", "rating": "OVERWEIGHT", "target": 335.00, "date": "2026-09-08"},
                    {"firm": "JPMORGAN", "analyst": "John Ivankoe", "rating": "OVERWEIGHT", "target": 330.00, "date": "2026-09-02"},
                    {"firm": "CITIGROUP", "analyst": "Jon Tower", "rating": "NEUTRAL", "target": 310.00, "date": "2026-08-28"},
                    {"firm": "BANK OF AMERICA", "analyst": "Sara Senatore", "rating": "BUY", "target": 345.00, "date": "2026-08-15"}
                ]
            },
            "NVDA": {
                "consensus": "STRONG BUY",
                "consensus_score": 4.82,
                "target_price": 145.00,
                "target_high": 175.00,
                "target_low": 120.00,
                "buys": 58, "holds": 4, "sells": 1, "total": 63,
                "brokers": [
                    {"firm": "GOLDMAN SACHS", "analyst": "Toshiya Hari", "rating": "CONVICTION BUY", "target": 150.00, "date": "2026-09-12"},
                    {"firm": "MORGAN STANLEY", "analyst": "Joseph Moore", "rating": "OVERWEIGHT", "target": 144.00, "date": "2026-09-09"},
                    {"firm": "BERNSTEIN", "analyst": "Stacy Rasgon", "rating": "OUTPERFORM", "target": 155.00, "date": "2026-09-05"},
                    {"firm": "JPMORGAN", "analyst": "Harlan Sur", "rating": "OVERWEIGHT", "target": 140.00, "date": "2026-08-30"}
                ]
            },
            "AAPL": {
                "consensus": "BUY",
                "consensus_score": 4.15,
                "target_price": 255.00,
                "target_high": 275.00,
                "target_low": 210.00,
                "buys": 34, "holds": 12, "sells": 4, "total": 50,
                "brokers": [
                    {"firm": "MORGAN STANLEY", "analyst": "Erik Woodring", "rating": "OVERWEIGHT", "target": 273.00, "date": "2026-09-11"},
                    {"firm": "BANK OF AMERICA", "analyst": "Wamsi Mohan", "rating": "BUY", "target": 256.00, "date": "2026-09-04"},
                    {"firm": "BARCLAYS", "analyst": "Tim Long", "rating": "UNDERWEIGHT", "target": 210.00, "date": "2026-08-25"}
                ]
            }
        }

        profile = anr_profiles.get(sym, {
            "consensus": "MODERATE BUY",
            "consensus_score": 3.90,
            "target_price": round(price * 1.15, 2),
            "target_high": round(price * 1.30, 2),
            "target_low": round(price * 0.95, 2),
            "buys": 18, "holds": 8, "sells": 2, "total": 28,
            "brokers": [
                {"firm": "WALL STREET CONSENSUS", "analyst": "Institutional Research", "rating": "BUY", "target": round(price * 1.15, 2), "date": "2026-09-01"},
                {"firm": "GLOBAL SECURITIES", "analyst": "Equity Desk", "rating": "HOLD", "target": round(price * 1.05, 2), "date": "2026-08-20"}
            ]
        })

        upside = round(((profile["target_price"] - price) / price) * 100, 2) if price else 0.0
        return {
            "symbol": sym,
            "price": price,
            "consensus": profile["consensus"],
            "consensus_score": profile["consensus_score"],
            "target_price": profile["target_price"],
            "target_high": profile["target_high"],
            "target_low": profile["target_low"],
            "upside_pct": upside,
            "buys": profile["buys"],
            "holds": profile["holds"],
            "sells": profile["sells"],
            "total_analysts": profile["total"],
            "brokers": profile["brokers"]
        }

    def get_financial_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Financial Analysis (FA) 5-year multi-period historical statements.
        """
        sym = symbol.upper()
        years = ["2022", "2023", "2024", "2025", "2026E"]

        fa_data = {
            "MCD": {
                "income_statement": [
                    {"metric": "Revenue / Turnover", "vals": ["23.18B", "25.49B", "26.85B", "28.10B", "29.45B"]},
                    {"metric": "Gross Profit", "vals": ["13.21B", "14.56B", "15.30B", "16.12B", "16.90B"]},
                    {"metric": "Operating Income (EBIT)", "vals": ["10.37B", "11.64B", "12.18B", "12.85B", "13.50B"]},
                    {"metric": "EBITDA", "vals": ["12.15B", "13.48B", "14.10B", "14.90B", "15.65B"]},
                    {"metric": "Net Income", "vals": ["6.18B", "8.47B", "8.82B", "9.25B", "9.80B"]},
                    {"metric": "Diluted EPS (USD)", "vals": ["8.33", "11.56", "12.15", "12.80", "13.62"]}
                ],
                "balance_sheet": [
                    {"metric": "Cash & Short Term Inv.", "vals": ["2.58B", "4.57B", "3.20B", "3.85B", "4.10B"]},
                    {"metric": "Property, Plant & Equip.", "vals": ["24.85B", "26.12B", "27.40B", "28.50B", "29.80B"]},
                    {"metric": "Total Assets", "vals": ["50.44B", "56.15B", "58.20B", "60.40B", "62.80B"]},
                    {"metric": "Total Long Term Debt", "vals": ["35.90B", "37.20B", "38.10B", "38.80B", "39.20B"]},
                    {"metric": "Total Liabilities", "vals": ["56.44B", "60.85B", "62.50B", "64.10B", "65.50B"]},
                    {"metric": "Total Equity (Deficit)", "vals": ["-6.00B", "-4.70B", "-4.30B", "-3.70B", "-2.70B"]}
                ],
                "cash_flow": [
                    {"metric": "Cash from Operations", "vals": ["7.39B", "9.61B", "10.15B", "10.80B", "11.40B"]},
                    {"metric": "Capital Expenditures (CapEx)", "vals": ["-1.90B", "-2.36B", "-2.55B", "-2.70B", "-2.85B"]},
                    {"metric": "Free Cash Flow (FCF)", "vals": ["5.49B", "7.25B", "7.60B", "8.10B", "8.55B"]},
                    {"metric": "Dividends Paid", "vals": ["-4.17B", "-4.53B", "-4.80B", "-5.10B", "-5.35B"]},
                    {"metric": "Share Repurchases", "vals": ["-3.90B", "-4.20B", "-4.00B", "-4.20B", "-4.50B"]}
                ]
            },
            "NVDA": {
                "income_statement": [
                    {"metric": "Revenue / Turnover", "vals": ["26.97B", "26.91B", "60.92B", "120.90B", "165.00B"]},
                    {"metric": "Gross Profit", "vals": ["15.36B", "15.36B", "44.30B", "90.67B", "125.40B"]},
                    {"metric": "Operating Income (EBIT)", "vals": ["10.04B", "4.22B", "32.97B", "78.50B", "110.20B"]},
                    {"metric": "EBITDA", "vals": ["11.22B", "5.60B", "34.50B", "82.10B", "115.00B"]},
                    {"metric": "Net Income", "vals": ["9.75B", "4.37B", "29.76B", "68.20B", "98.50B"]},
                    {"metric": "Diluted EPS (USD)", "vals": ["0.39", "0.18", "1.19", "2.63", "3.85"]}
                ],
                "balance_sheet": [
                    {"metric": "Cash & Short Term Inv.", "vals": ["19.90B", "13.30B", "25.98B", "34.80B", "48.50B"]},
                    {"metric": "Property, Plant & Equip.", "vals": ["2.78B", "3.80B", "4.50B", "6.20B", "8.50B"]},
                    {"metric": "Total Assets", "vals": ["44.19B", "41.18B", "65.73B", "102.50B", "145.00B"]},
                    {"metric": "Total Long Term Debt", "vals": ["10.95B", "9.70B", "8.46B", "8.50B", "8.50B"]},
                    {"metric": "Total Liabilities", "vals": ["17.58B", "19.08B", "22.75B", "28.50B", "35.00B"]},
                    {"metric": "Total Equity", "vals": ["26.61B", "22.10B", "42.98B", "74.00B", "110.00B"]}
                ],
                "cash_flow": [
                    {"metric": "Cash from Operations", "vals": ["9.11B", "5.64B", "28.09B", "62.40B", "92.00B"]},
                    {"metric": "Capital Expenditures (CapEx)", "vals": ["-0.98B", "-1.83B", "-2.45B", "-3.80B", "-5.20B"]},
                    {"metric": "Free Cash Flow (FCF)", "vals": ["8.13B", "3.81B", "25.64B", "58.60B", "86.80B"]},
                    {"metric": "Dividends Paid", "vals": ["-0.40B", "-0.40B", "-0.40B", "-0.60B", "-0.80B"]},
                    {"metric": "Share Repurchases", "vals": ["-2.00B", "-10.00B", "-9.50B", "-18.00B", "-25.00B"]}
                ]
            }
        }

        stock_data = fa_data.get(sym, {
            "income_statement": [
                {"metric": "Revenue / Turnover", "vals": ["8.2B", "9.5B", "10.4B", "11.2B", "12.0B"]},
                {"metric": "Gross Profit", "vals": ["4.1B", "4.8B", "5.3B", "5.8B", "6.2B"]},
                {"metric": "Operating Income (EBIT)", "vals": ["1.8B", "2.1B", "2.4B", "2.7B", "3.0B"]},
                {"metric": "EBITDA", "vals": ["2.2B", "2.5B", "2.9B", "3.2B", "3.6B"]},
                {"metric": "Net Income", "vals": ["1.2B", "1.4B", "1.6B", "1.8B", "2.1B"]},
                {"metric": "Diluted EPS (USD)", "vals": ["3.80", "4.25", "4.90", "5.45", "6.10"]}
            ],
            "balance_sheet": [
                {"metric": "Cash & Short Term Inv.", "vals": ["1.5B", "1.8B", "2.1B", "2.4B", "2.8B"]},
                {"metric": "Total Assets", "vals": ["18.0B", "20.2B", "22.5B", "24.8B", "27.0B"]},
                {"metric": "Total Debt", "vals": ["6.5B", "7.0B", "7.2B", "7.5B", "7.8B"]},
                {"metric": "Total Liabilities", "vals": ["10.2B", "11.4B", "12.6B", "13.8B", "14.9B"]},
                {"metric": "Total Equity", "vals": ["7.8B", "8.8B", "9.9B", "11.0B", "12.1B"]}
            ],
            "cash_flow": [
                {"metric": "Cash from Operations", "vals": ["1.9B", "2.2B", "2.5B", "2.8B", "3.2B"]},
                {"metric": "Capital Expenditures (CapEx)", "vals": ["-0.5B", "-0.6B", "-0.7B", "-0.8B", "-0.9B"]},
                {"metric": "Free Cash Flow (FCF)", "vals": ["1.4B", "1.6B", "1.8B", "2.0B", "2.3B"]},
                {"metric": "Dividends Paid", "vals": ["-0.4B", "-0.5B", "-0.5B", "-0.6B", "-0.7B"]}
            ]
        })

        return {
            "symbol": sym,
            "years": years,
            "income_statement": stock_data["income_statement"],
            "balance_sheet": stock_data["balance_sheet"],
            "cash_flow": stock_data["cash_flow"]
        }

    def get_relative_valuation(self, symbol: str) -> Dict[str, Any]:
        """
        Relative Valuation (RV) Peer Comparison Matrix.
        """
        sym = symbol.upper()
        price = self.get_security_price(sym)
        rv_groups = {
            "MCD": {
                "industry": "Quick Service Restaurants & Franchising",
                "peers": [
                    {"symbol": "MCD", "name": "McDonald's Corp", "price": 301.16, "pe": 26.4, "fwd_pe": 23.2, "ev_ebitda": 18.5, "ps": 8.5, "op_margin": "45.8%", "roe": "N/A", "div_yield": "2.22%"},
                    {"symbol": "YUM", "name": "Yum! Brands Inc", "price": 135.40, "pe": 24.1, "fwd_pe": 21.0, "ev_ebitda": 17.2, "ps": 5.4, "op_margin": "32.4%", "roe": "N/A", "div_yield": "1.98%"},
                    {"symbol": "QSR", "name": "Restaurant Brands Intl", "price": 72.85, "pe": 19.8, "fwd_pe": 17.5, "ev_ebitda": 14.6, "ps": 4.8, "op_margin": "29.1%", "roe": "28.5%", "div_yield": "3.18%"},
                    {"symbol": "WEN", "name": "Wendy's Co", "price": 17.20, "pe": 18.2, "fwd_pe": 16.1, "ev_ebitda": 13.8, "ps": 1.7, "op_margin": "17.8%", "roe": "42.1%", "div_yield": "5.81%"},
                    {"symbol": "SBUX", "name": "Starbucks Corp", "price": 96.50, "pe": 28.5, "fwd_pe": 24.8, "ev_ebitda": 16.9, "ps": 3.1, "op_margin": "15.2%", "roe": "N/A", "div_yield": "2.36%"}
                ]
            },
            "NVDA": {
                "industry": "Semiconductors & AI Accelerators",
                "peers": [
                    {"symbol": "NVDA", "name": "Nvidia Corp", "price": 118.90, "pe": 45.2, "fwd_pe": 32.1, "ev_ebitda": 36.4, "ps": 24.1, "op_margin": "64.9%", "roe": "115.6%", "div_yield": "0.03%"},
                    {"symbol": "AMD", "name": "Advanced Micro Devices", "price": 152.80, "pe": 112.5, "fwd_pe": 28.4, "ev_ebitda": 42.1, "ps": 10.4, "op_margin": "11.2%", "roe": "3.8%", "div_yield": "0.00%"},
                    {"symbol": "INTC", "name": "Intel Corp", "price": 20.80, "pe": "N/A", "fwd_pe": 18.5, "ev_ebitda": 9.2, "ps": 1.6, "op_margin": "1.2%", "roe": "-3.2%", "div_yield": "2.40%"},
                    {"symbol": "TSM", "name": "Taiwan Semiconductor", "price": 174.20, "pe": 28.1, "fwd_pe": 22.5, "ev_ebitda": 14.8, "ps": 11.2, "op_margin": "42.5%", "roe": "27.4%", "div_yield": "1.24%"},
                    {"symbol": "AVGO", "name": "Broadcom Inc", "price": 168.40, "pe": 65.2, "fwd_pe": 27.8, "ev_ebitda": 22.4, "ps": 15.6, "op_margin": "38.6%", "roe": "18.2%", "div_yield": "1.26%"}
                ]
            }
        }

        default_group = {
            "industry": "Peer Benchmark Group",
            "peers": [
                {"symbol": sym, "name": f"{sym} Corp", "price": price, "pe": 22.5, "fwd_pe": 19.4, "ev_ebitda": 15.2, "ps": 3.8, "op_margin": "24.5%", "roe": "18.2%", "div_yield": "1.50%"},
                {"symbol": "PEER1", "name": "Industry Peer Alpha", "price": 85.40, "pe": 20.1, "fwd_pe": 18.0, "ev_ebitda": 14.1, "ps": 3.2, "op_margin": "21.0%", "roe": "15.4%", "div_yield": "1.80%"},
                {"symbol": "PEER2", "name": "Industry Peer Beta", "price": 112.20, "pe": 25.4, "fwd_pe": 21.5, "ev_ebitda": 16.8, "ps": 4.5, "op_margin": "26.4%", "roe": "20.1%", "div_yield": "1.20%"}
            ]
        }
        group = rv_groups.get(sym, default_group)
        return {
            "symbol": sym,
            "industry": group["industry"],
            "peers": group["peers"]
        }

    def get_earnings_estimates(self, symbol: str) -> Dict[str, Any]:
        """
        Earnings Estimates (EE) Quarterly Surprises and Forward Guidance.
        """
        sym = symbol.upper()
        return {
            "symbol": sym,
            "quarterly_history": [
                {"quarter": "Q2 2026", "reported_eps": 3.12, "consensus_eps": 3.05, "surprise_pct": 2.30, "revenue_reported": "6.85B", "rev_surprise_pct": 1.15},
                {"quarter": "Q1 2026", "reported_eps": 2.95, "consensus_eps": 2.90, "surprise_pct": 1.72, "revenue_reported": "6.40B", "rev_surprise_pct": 0.85},
                {"quarter": "Q4 2025", "reported_eps": 2.82, "consensus_eps": 2.80, "surprise_pct": 0.71, "revenue_reported": "6.25B", "rev_surprise_pct": -0.40},
                {"quarter": "Q3 2025", "reported_eps": 3.18, "consensus_eps": 3.00, "surprise_pct": 6.00, "revenue_reported": "6.69B", "rev_surprise_pct": 2.10}
            ],
            "forward_estimates": [
                {"quarter": "Q3 2026E", "consensus_eps": 3.35, "high_eps": 3.50, "low_eps": 3.20, "est_revenue": "7.10B"},
                {"quarter": "Q4 2026E", "consensus_eps": 3.20, "high_eps": 3.38, "low_eps": 3.10, "est_revenue": "6.95B"}
            ]
        }

    def _is_crypto(self, symbol: str) -> bool:
        sym = symbol.upper()
        return (
            any(sym.endswith(s) for s in ["USDT", "BTC", "ETH", "SOL", "USD"])
            or sym in ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA"]
        ) and not sym.startswith("^")

    async def get_wei_matrix_async(self) -> List[Dict[str, Any]]:
        indices_to_fetch = ["^GSPC", "^IXIC", "^DJI", "^RUT", "^VIX", "BTC-USD", "ETH-USD"]
        quotes = await market_data_client.get_quotes(indices_to_fetch)
        results = []
        if quotes:
            quote_map = {q["symbol"]: q for q in quotes}
            for item in self.get_wei_matrix():
                sym = item["symbol"]
                mapped = SYMBOL_MAP.get(sym, sym)
                orig_price = item.get("price", item.get("value", 0.0))
                orig_chg = item.get("change", item.get("net_change", 0.0))
                orig_pct = item.get("change_pct", item.get("pct_change", 0.0))
                if mapped in quote_map:
                    q = quote_map[mapped]
                    price = round(float(q.get("regularMarketPrice", orig_price)), 2)
                    chg = round(float(q.get("regularMarketChange", orig_chg)), 2)
                    pct = round(float(q.get("regularMarketChangePercent", orig_pct)), 2)
                    high = round(float(q.get("regularMarketDayHigh", price)), 2)
                    low = round(float(q.get("regularMarketDayLow", price)), 2)
                else:
                    price = orig_price
                    chg = orig_chg
                    pct = orig_pct
                    high = item.get("high", price)
                    low = item.get("low", price)

                results.append({
                    "name": item["name"],
                    "symbol": sym,
                    "price": price,
                    "value": price,
                    "change": chg,
                    "net_change": chg,
                    "change_pct": pct,
                    "pct_change": pct,
                    "high": high,
                    "low": low,
                    "time": datetime.datetime.now().strftime("%H:%M:%S")
                })
            return results

        for item in self.get_wei_matrix():
            res = dict(item)
            p = res.get("price", res.get("value", 0.0))
            c = res.get("change", res.get("net_change", 0.0))
            cp = res.get("change_pct", res.get("pct_change", 0.0))
            res["price"] = p
            res["value"] = p
            res["change"] = c
            res["net_change"] = c
            res["change_pct"] = cp
            res["pct_change"] = cp
            results.append(res)
        return results

    async def get_security_price_async(self, symbol: str) -> float:
        sym = symbol.upper()
        mapped = SYMBOL_MAP.get(sym, sym)
        if self._is_crypto(sym):
            cb_sym = sym.replace("USDT", "-USD")
            if not "-" in cb_sym:
                cb_sym = f"{cb_sym}-USD"
            cb_candles = await market_data_client.get_coinbase_candles(cb_sym)
            if cb_candles:
                return cb_candles[-1]["close"]

        quotes = await market_data_client.get_quotes([mapped])
        if quotes and quotes[0].get("regularMarketPrice") is not None:
            return round(float(quotes[0]["regularMarketPrice"]), 2)
        return self.get_security_price(sym)

    async def get_security_description_async(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        mapped = SYMBOL_MAP.get(sym, sym)

        if self._is_crypto(sym):
            coin_id = "ethereum" if "ETH" in sym else ("bitcoin" if "BTC" in sym else "solana")
            tokenomics = await market_data_client.get_crypto_tokenomics(coin_id)
            if tokenomics:
                mkt_cap_b = f"${round(tokenomics.get('market_cap', 0) / 1e9, 2)}B"
                vol_b = f"${round(tokenomics.get('total_volume_24h', 0) / 1e9, 2)}B"
                supply = f"{tokenomics.get('circulating_supply', 0):,.0f}"
                return {
                    "symbol": sym,
                    "name": tokenomics.get("name", sym),
                    "sector": "CRNCY",
                    "industry": "Decentralized Smart Contract Protocol",
                    "price": tokenomics.get("price_usd", 2600.0),
                    "market_cap": mkt_cap_b,
                    "pe_ratio": "N/A",
                    "dividend_yield": "3.2% (Staking APR)",
                    "beta": 1.45,
                    "summary": f"{tokenomics.get('name', sym)} is a decentralized, open-source blockchain network supporting smart contracts and autonomous applications.",
                    "stats": {
                        "Open": tokenomics.get("price_usd", 2600.0),
                        "High": tokenomics.get("high_24h", 2650.0),
                        "Low": tokenomics.get("low_24h", 2580.0),
                        "Volume (24h)": vol_b,
                        "Circulating Supply": supply,
                        "ATH (USD)": f"${tokenomics.get('ath_usd', 0):,.2f}"
                    }
                }

        summary = await market_data_client.get_quote_summary(mapped)
        if summary:
            profile = summary.get("assetProfile", {})
            f_data = summary.get("financialData", {})
            d_data = summary.get("defaultKeyStatistics", {})
            p_data = summary.get("price", {})

            price = round(float(p_data.get("regularMarketPrice", {}).get("raw", 100.0)), 2)
            mkt_cap = p_data.get("marketCap", {}).get("fmt", "N/A")
            pe = round(float(d_data.get("trailingPE", {}).get("raw", 25.0)), 1) if d_data.get("trailingPE", {}).get("raw") else "N/A"
            div_yield = f_data.get("dividendYield", {}).get("fmt", "0.00%")
            beta = round(float(d_data.get("beta", {}).get("raw", 1.0)), 2) if d_data.get("beta", {}).get("raw") else 1.0
            descr = profile.get("longBusinessSummary", "")

            return {
                "symbol": sym,
                "name": p_data.get("shortName", sym),
                "sector": profile.get("sector", "TECHNOLOGY").upper(),
                "industry": profile.get("industry", "Consumer Tech & Software"),
                "price": price,
                "market_cap": mkt_cap,
                "pe_ratio": pe,
                "dividend_yield": div_yield,
                "beta": beta,
                "summary": descr if descr else f"{sym} Corporation is a leading publicly traded technology enterprise.",
                "stats": {
                    "Open": round(float(p_data.get("regularMarketOpen", {}).get("raw", price)), 2),
                    "High": round(float(p_data.get("regularMarketDayHigh", {}).get("raw", price)), 2),
                    "Low": round(float(p_data.get("regularMarketDayLow", {}).get("raw", price)), 2),
                    "Volume": p_data.get("regularMarketVolume", {}).get("fmt", "N/A"),
                    "52w High": round(float(summary.get("summaryDetail", {}).get("fiftyTwoWeekHigh", {}).get("raw", price)), 2),
                    "52w Low": round(float(summary.get("summaryDetail", {}).get("fiftyTwoWeekLow", {}).get("raw", price)), 2)
                }
            }

        return self.get_security_description(sym)

    async def get_analyst_recommendations_async(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        mapped = SYMBOL_MAP.get(sym, sym)
        if self._is_crypto(sym):
            return self.get_analyst_recommendations(sym)

        summary = await market_data_client.get_quote_summary(mapped)
        if summary:
            f_data = summary.get("financialData", {})
            curr_price = await self.get_security_price_async(sym)
            target_mean = round(float(f_data.get("targetMeanPrice", {}).get("raw", curr_price * 1.15)), 2)
            target_high = round(float(f_data.get("targetHighPrice", {}).get("raw", curr_price * 1.30)), 2)
            target_low = round(float(f_data.get("targetLowPrice", {}).get("raw", curr_price * 0.90)), 2)
            rec_key = f_data.get("recommendationKey", "buy").upper().replace("_", " ")

            return {
                "symbol": sym,
                "consensus": rec_key,
                "mean_target": target_mean,
                "high_target": target_high,
                "low_target": target_low,
                "current_price": curr_price,
                "ratings_breakdown": {
                    "Buy": 26,
                    "Hold": 9,
                    "Sell": 2
                },
                "recent_actions": [
                    {"firm": "Morgan Stanley", "analyst": "E. Woodring", "action": "OVERWEIGHT", "target": target_high, "date": "LIVE"},
                    {"firm": "Goldman Sachs", "analyst": "M. Ng", "action": "BUY", "target": target_mean, "date": "LIVE"},
                    {"firm": "JPMorgan", "analyst": "S. Chatterjee", "action": "OVERWEIGHT", "target": round(target_mean * 1.05, 2), "date": "LIVE"}
                ]
            }

        return self.get_analyst_recommendations(sym)

    async def get_financial_analysis_async(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        if self._is_crypto(sym):
            coin_id = "ethereum" if "ETH" in sym else ("bitcoin" if "BTC" in sym else "solana")
            tokenomics = await market_data_client.get_crypto_tokenomics(coin_id)
            tvl = await market_data_client.get_crypto_tvl(tokenomics.get("name", "Ethereum"))
            if tokenomics:
                mkt_cap_b = f"${round(tokenomics.get('market_cap', 0) / 1e9, 2)}B"
                vol_b = f"${round(tokenomics.get('total_volume_24h', 0) / 1e9, 2)}B"
                tvl_b = f"${round(tvl / 1e9, 2)}B" if tvl else "N/A"
                supply = f"{tokenomics.get('circulating_supply', 0):,.0f} {tokenomics.get('symbol', '')}"
                ath = f"${tokenomics.get('ath_usd', 0):,.2f}"
                rng = f"${tokenomics.get('low_24h', 0):,.2f} - ${tokenomics.get('high_24h', 0):,.2f}"

                return {
                    "symbol": sym,
                    "asset_type": "DIGITAL_ASSET / PROTOCOL",
                    "protocol_name": tokenomics.get("name", sym),
                    "years": ["2022", "2023", "2024", "2025", "2026 YTD"],
                    "income_statement": [
                        {"metric": "Market Capitalization", "vals": ["145.2B", "275.4B", "310.8B", "345.0B", mkt_cap_b]},
                        {"metric": "Total Value Locked (TVL)", "vals": ["24.5B", "38.2B", "46.1B", "55.8B", tvl_b]},
                        {"metric": "24h Trading Volume", "vals": ["8.5B", "14.2B", "18.5B", "24.1B", vol_b]},
                        {"metric": "24h High/Low Range", "vals": ["N/A", "N/A", "N/A", "N/A", rng]},
                        {"metric": "All-Time High (ATH)", "vals": ["N/A", "N/A", "N/A", "N/A", ath]}
                    ],
                    "balance_sheet": [
                        {"metric": "Circulating Supply", "vals": ["120.4M", "120.2M", "120.1M", "121.5M", supply]},
                        {"metric": "Total Supply", "vals": ["120.4M", "120.2M", "120.1M", "121.5M", supply]},
                        {"metric": "Max Supply", "vals": ["Dynamic", "Dynamic", "Dynamic", "Dynamic", "Burn Dynamic"]},
                        {"metric": "Staking Participation Ratio", "vals": ["13.1%", "20.1%", "26.2%", "28.6%", "28.8%"]}
                    ],
                    "cash_flow": [
                        {"metric": "Annualized Fee Burn (EIP-1559)", "vals": ["-850M", "-1.42B", "-1.85B", "-2.20B", "-1.95B"]},
                        {"metric": "Net Issuance Dynamic", "vals": ["+1.2%", "-0.22%", "-0.18%", "+0.05%", "-0.08%"]},
                        {"metric": "Staking Real Yield APR", "vals": ["4.85%", "4.12%", "3.65%", "3.40%", "3.24%"]}
                    ]
                }

        mapped = SYMBOL_MAP.get(sym, sym)
        summary = await market_data_client.get_quote_summary(mapped)
        if summary:
            inc_history = summary.get("incomeStatementHistory", {}).get("incomeStatementHistory", [])
            bal_history = summary.get("balanceSheetHistory", {}).get("balanceSheetStatements", [])
            cf_history = summary.get("cashflowStatementHistory", {}).get("cashflowStatements", [])

            if inc_history:
                years = [stmt.get("endDate", {}).get("fmt", "").split("-")[0] for stmt in reversed(inc_history)]
                if not years or not any(years):
                    years = ["2022", "2023", "2024", "2025"]

                inc_list = list(reversed(inc_history))
                bal_list = list(reversed(bal_history))
                cf_list = list(reversed(cf_history))

                def get_vals(history: List[Dict[str, Any]], field: str) -> List[str]:
                    vals = []
                    for h in history:
                        val = h.get(field, {}).get("fmt")
                        if not val:
                            raw = h.get(field, {}).get("raw")
                            if raw is not None:
                                val = f"{round(raw / 1e9, 2)}B" if abs(raw) >= 1e9 else f"{round(raw / 1e6, 2)}M"
                            else:
                                val = "N/A"
                        vals.append(val)
                    while len(vals) < len(years):
                        vals.append("EST")
                    return vals

                inc_metrics = [
                    {"metric": "Revenue / Turnover", "vals": get_vals(inc_list, "totalRevenue")},
                    {"metric": "Gross Profit", "vals": get_vals(inc_list, "grossProfit")},
                    {"metric": "Operating Income (EBIT)", "vals": get_vals(inc_list, "operatingIncome")},
                    {"metric": "EBITDA", "vals": get_vals(inc_list, "ebit")},
                    {"metric": "Net Income", "vals": get_vals(inc_list, "netIncome")},
                    {"metric": "Diluted EPS (USD)", "vals": get_vals(inc_list, "dilutedEps" if inc_list and "dilutedEps" in inc_list[0] else "netIncome")}
                ]

                bal_metrics = [
                    {"metric": "Cash & Short Term Inv.", "vals": get_vals(bal_list, "cash")},
                    {"metric": "Property, Plant & Equip.", "vals": get_vals(bal_list, "propertyPlantEquipment")},
                    {"metric": "Total Assets", "vals": get_vals(bal_list, "totalAssets")},
                    {"metric": "Total Debt", "vals": get_vals(bal_list, "longTermDebt")},
                    {"metric": "Total Liabilities", "vals": get_vals(bal_list, "totalLiab")},
                    {"metric": "Total Stockholder Equity", "vals": get_vals(bal_list, "totalStockholderEquity")}
                ]

                cf_metrics = [
                    {"metric": "Cash from Operations", "vals": get_vals(cf_list, "totalCashFromOperatingActivities")},
                    {"metric": "Capital Expenditures (CapEx)", "vals": get_vals(cf_list, "capitalExpenditures")},
                    {"metric": "Free Cash Flow (FCF)", "vals": get_vals(cf_list, "freeCashFlow" if cf_list and "freeCashFlow" in cf_list[0] else "totalCashFromOperatingActivities")},
                    {"metric": "Dividends Paid", "vals": get_vals(cf_list, "dividendsPaid")}
                ]

                return {
                    "symbol": sym,
                    "years": years,
                    "income_statement": inc_metrics,
                    "balance_sheet": bal_metrics,
                    "cash_flow": cf_metrics
                }

        return self.get_financial_analysis(sym)

    async def get_relative_valuation_async(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        if self._is_crypto(sym):
            crypto_peers = ["ETHUSDT", "BTCUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT"]
            peers = []
            for cp in crypto_peers:
                coin_id = "ethereum" if "ETH" in cp else ("bitcoin" if "BTC" in cp else ("solana" if "SOL" in cp else ("binancecoin" if "BNB" in cp else "avalanche-2")))
                tokenomics = await market_data_client.get_crypto_tokenomics(coin_id)
                price = tokenomics.get("price_usd", 0.0) if tokenomics else 0.0
                staking_apr = "3.2% (Staking)" if "ETH" in cp else ("6.8% (Staking)" if "SOL" in cp else ("5.5% (Staking)" if "AVAX" in cp else "N/A"))
                mkt_cap_b = f"${round(tokenomics.get('market_cap', 0) / 1e9, 1)}B" if tokenomics else "N/A"
                peers.append({
                    "symbol": cp,
                    "name": tokenomics.get("name", cp) if tokenomics else cp,
                    "price": round(float(price), 2),
                    "pe": "N/A",
                    "fwd_pe": "N/A",
                    "ev_ebitda": mkt_cap_b,
                    "ps": "N/A",
                    "op_margin": "N/A",
                    "roe": staking_apr,
                    "div_yield": staking_apr if "Staking" in staking_apr else "0.00%"
                })
            return {
                "symbol": sym,
                "industry": "Layer 1 Smart Contract Protocols & Digital Assets",
                "peers": peers
            }

        tech_peers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        qsr_peers = ["MCD", "YUM", "QSR", "WEN", "SBUX"]
        semi_peers = ["NVDA", "AMD", "INTC", "TSM", "AVGO"]
        fin_peers = ["JPM", "BAC", "WFC", "GS", "MS"]
        auto_peers = ["TSLA", "F", "GM", "RIVN", "TM"]
        health_peers = ["LLY", "UNH", "JNJ", "ABBV", "MRK"]
        energy_peers = ["XOM", "CVX", "COP", "SLB", "EOG"]
        retail_peers = ["WMT", "COST", "TGT", "HD", "LOW"]

        if sym in qsr_peers:
            peer_syms = qsr_peers
            industry = "Quick Service Restaurants & Franchising"
        elif sym in semi_peers:
            peer_syms = semi_peers
            industry = "Semiconductors & AI Compute"
        elif sym in tech_peers:
            peer_syms = tech_peers
            industry = "Mega-Cap Technology & Platforms"
        elif sym in fin_peers:
            peer_syms = fin_peers
            industry = "Diversified Banking & Financial Services"
        elif sym in auto_peers:
            peer_syms = auto_peers
            industry = "Automotive & Electric Vehicles"
        elif sym in health_peers:
            peer_syms = health_peers
            industry = "Pharmaceuticals & Healthcare"
        elif sym in energy_peers:
            peer_syms = energy_peers
            industry = "Integrated Oil, Gas & Energy"
        elif sym in retail_peers:
            peer_syms = retail_peers
            industry = "Consumer Retail & Merchandising"
        else:
            peer_syms = [sym, "AAPL", "MSFT", "NVDA", "AMZN"]
            industry = "Comparative Benchmark Group"

        if sym not in peer_syms:
            peer_syms = [sym] + peer_syms[:4]

        quotes_task = market_data_client.get_quotes(peer_syms)
        summaries_tasks = [
            market_data_client.get_quote_summary(
                s, ["financialData", "defaultKeyStatistics", "summaryDetail"]
            )
            for s in peer_syms
        ]

        gathered = await asyncio.gather(quotes_task, *summaries_tasks, return_exceptions=True)
        quotes = gathered[0] if len(gathered) > 0 and isinstance(gathered[0], list) else []
        summaries = gathered[1:] if len(gathered) > 1 else []

        quote_map = {}
        for q in quotes:
            if isinstance(q, dict):
                quote_map[q.get("symbol", "").upper()] = q

        summary_map = {}
        for s_sym, summary in zip(peer_syms, summaries):
            if isinstance(summary, dict):
                summary_map[s_sym.upper()] = summary

        if not quote_map and not summary_map:
            return self.get_relative_valuation(sym)

        peers = []
        for p_sym in peer_syms:
            q = quote_map.get(p_sym.upper(), {})
            s = summary_map.get(p_sym.upper(), {})
            fd = s.get("financialData", {})
            ks = s.get("defaultKeyStatistics", {})
            sd = s.get("summaryDetail", {})
            base = PEER_BASELINES.get(p_sym.upper(), {})

            p_name = q.get("shortName") or q.get("longName") or base.get("name", f"{p_sym} Corp")
            price = round(float(q.get("regularMarketPrice", base.get("price", 100.0))), 2)
            
            pe_val = q.get("trailingPE") or sd.get("trailingPE", {}).get("raw") or base.get("pe")
            pe = round(float(pe_val), 1) if pe_val is not None and pe_val != "N/A" else "N/A"
            
            fwd_pe_val = q.get("forwardPE") or sd.get("forwardPE", {}).get("raw") or base.get("fwd_pe")
            fwd_pe = round(float(fwd_pe_val), 1) if fwd_pe_val is not None and fwd_pe_val != "N/A" else "N/A"

            ev_val = ks.get("enterpriseToEbitda", {}).get("raw") or base.get("ev_ebitda")
            ev_ebitda = round(float(ev_val), 1) if ev_val is not None and ev_val != "N/A" else "N/A"

            ps_val = sd.get("priceToSalesTrailing12Months", {}).get("raw") or ks.get("priceToSalesTrailing12Months", {}).get("raw") or q.get("priceToSalesTrailing12Months") or base.get("ps")
            ps = round(float(ps_val), 1) if ps_val is not None and ps_val != "N/A" else "N/A"

            op_m_val = fd.get("operatingMargins", {}).get("raw")
            if op_m_val is not None:
                op_margin = f"{round(float(op_m_val) * 100, 1)}%"
            else:
                op_margin = base.get("op_margin", "N/A")

            roe_val = fd.get("returnOnEquity", {}).get("raw")
            if roe_val is not None:
                roe = f"{round(float(roe_val) * 100, 1)}%"
            else:
                roe = base.get("roe", "N/A")

            div_val = sd.get("dividendYield", {}).get("raw") or q.get("dividendYield")
            if div_val is not None:
                div_float = float(div_val)
                if div_float > 1.0:
                    div_yield = f"{round(div_float, 2)}%"
                else:
                    div_yield = f"{round(div_float * 100, 2)}%"
            else:
                div_yield = base.get("div_yield", "0.00%")

            peers.append({
                "symbol": p_sym,
                "name": p_name,
                "price": price,
                "pe": pe,
                "fwd_pe": fwd_pe,
                "ev_ebitda": ev_ebitda,
                "ps": ps,
                "op_margin": op_margin,
                "roe": roe,
                "div_yield": div_yield
            })

        return {
            "symbol": sym,
            "industry": industry,
            "peers": peers
        }

    async def get_earnings_estimates_async(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        mapped = SYMBOL_MAP.get(sym, sym)
        if self._is_crypto(sym):
            return self.get_earnings_estimates(sym)

        summary = await market_data_client.get_quote_summary(mapped)
        if summary:
            earnings_trend = summary.get("earningsTrend", {}).get("trend", [])
            forward = []
            for t in earnings_trend[:2]:
                period = t.get("period", "")
                est_eps = t.get("earningsEstimate", {}).get("avg", {}).get("raw", 3.0)
                high_eps = t.get("earningsEstimate", {}).get("high", {}).get("raw", 3.2)
                low_eps = t.get("earningsEstimate", {}).get("low", {}).get("raw", 2.8)
                rev_est = t.get("revenueEstimate", {}).get("avg", {}).get("fmt", "7.0B")
                forward.append({
                    "quarter": f"{period.upper()}E",
                    "consensus_eps": round(float(est_eps), 2),
                    "high_eps": round(float(high_eps), 2),
                    "low_eps": round(float(low_eps), 2),
                    "est_revenue": rev_est
                })

            base = self.get_earnings_estimates(sym)
            if forward:
                base["forward_estimates"] = forward
            return base

        return self.get_earnings_estimates(sym)

