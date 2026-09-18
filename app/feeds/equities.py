import asyncio
import copy
import json
import datetime
import logging
import random
import time
import urllib.request
from typing import Dict, Any, List, Optional

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
            "1M": ("1m", "1d", 20.0),
            "5M": ("5m", "5d", 60.0),
            "15M": ("15m", "1mo", 180.0),
            "1H": ("60m", "3mo", 300.0),
            "1D": ("1d", "1y", 1800.0),
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
