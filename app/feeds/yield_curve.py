import asyncio
import datetime
import json
import logging
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from app.feeds.market_data_client import market_data_client

logger = logging.getLogger(__name__)

TENOR_SPEC = [
    ("1M", "BC_1MONTH"),
    ("3M", "BC_3MONTH"),
    ("6M", "BC_6MONTH"),
    ("1Y", "BC_1YEAR"),
    ("2Y", "BC_2YEAR"),
    ("3Y", "BC_3YEAR"),
    ("5Y", "BC_5YEAR"),
    ("7Y", "BC_7YEAR"),
    ("10Y", "BC_10YEAR"),
    ("20Y", "BC_20YEAR"),
    ("30Y", "BC_30YEAR"),
]

YAHOO_RATE_MAP = {
    "3M": "^IRX",   # 13-Week Treasury Bill Yield
    "5Y": "^FVX",   # 5-Year Treasury Note Yield
    "10Y": "^TNX",  # 10-Year Treasury Note Yield
    "30Y": "^TYX",  # 30-Year Treasury Bond Yield
}

class YieldCurveFeed:
    """
    Live US Treasury Benchmark Yield Curve (YCRV) service.
    Pulls official daily constant maturity Treasury rates from the US Department
    of the Treasury and enriches benchmark tenors (3M, 5Y, 10Y, 30Y) with live
    intraday ticks from Yahoo Finance.
    """

    def __init__(self):
        # Default baseline yields (used on cold starts and offline tests)
        self.tenors: List[Dict[str, Any]] = [
            {"tenor": "1M", "yield": 3.96, "change": +0.03},
            {"tenor": "3M", "yield": 4.14, "change": +0.03},
            {"tenor": "6M", "yield": 4.22, "change": +0.05},
            {"tenor": "1Y", "yield": 4.45, "change": +0.06},
            {"tenor": "2Y", "yield": 4.74, "change": +0.07},
            {"tenor": "3Y", "yield": 4.82, "change": +0.06},
            {"tenor": "5Y", "yield": 4.86, "change": +0.03},
            {"tenor": "7Y", "yield": 4.94, "change": +0.03},
            {"tenor": "10Y", "yield": 5.01, "change": +0.01},
            {"tenor": "20Y", "yield": 5.39, "change": -0.01},
            {"tenor": "30Y", "yield": 5.35, "change": -0.01},
        ]
        self.last_fetch: float = 0.0
        self.cache_ttl: float = 60.0  # 1 minute cache
        self.as_of_date: str = "LIVE"

    def fetch_live_treasury_curve(self) -> Optional[List[Dict[str, Any]]]:
        """Fetches the official Daily Treasury Yield Curve XML from home.treasury.gov."""
        now = datetime.datetime.now(datetime.timezone.utc)
        months_to_try = [
            now.strftime("%Y%m"),
            (now.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")
        ]

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for m in months_to_try:
            url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month={m}"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=1.5) as res:
                    xml_text = res.read().decode("utf-8")
                    root = ET.fromstring(xml_text)
                    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                    if not entries:
                        continue

                    latest_entry = entries[-1]
                    prev_entry = entries[-2] if len(entries) > 1 else None

                    def parse_entry(entry) -> Dict[str, str]:
                        c = entry.find("{http://www.w3.org/2005/Atom}content")
                        if c is None:
                            return {}
                        p = c.find("{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties")
                        if p is None:
                            return {}
                        res_dict = {}
                        for child in p:
                            tag = child.tag.split("}")[-1]
                            if child.text:
                                res_dict[tag] = child.text
                        return res_dict

                    latest_props = parse_entry(latest_entry)
                    prev_props = parse_entry(prev_entry) if prev_entry else {}
                    if not latest_props:
                        continue

                    date_val = latest_props.get("NEW_DATE", "")
                    if date_val:
                        self.as_of_date = date_val.split("T")[0]

                    tenors_out = []
                    for label, xml_key in TENOR_SPEC:
                        raw_val = latest_props.get(xml_key)
                        if raw_val is not None:
                            curr_yield = round(float(raw_val), 2)
                            prev_raw = prev_props.get(xml_key, raw_val)
                            prev_yield = float(prev_raw) if prev_raw is not None else curr_yield
                            chg = round(curr_yield - prev_yield, 2)
                            tenors_out.append({"tenor": label, "yield": curr_yield, "change": chg})

                    if len(tenors_out) >= 7:
                        return tenors_out
            except Exception as e:
                logger.debug(f"Failed to fetch Treasury yield curve for {m}: {e}")
                continue

        return None

    def enrich_with_intraday_ticks(self, tenors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optionally pulls live intraday Treasury yields from Yahoo Finance for 3M, 5Y, 10Y, 30Y."""
        headers = {"User-Agent": "Mozilla/5.0"}
        for t in tenors:
            tenor_code = t["tenor"]
            ticker = YAHOO_RATE_MAP.get(tenor_code)
            if not ticker:
                continue
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=0.8) as res:
                    payload = json.loads(res.read().decode())
                    meta = payload.get("chart", {}).get("result", [{}])[0].get("meta", {})
                    live_p = meta.get("regularMarketPrice")
                    prev_p = meta.get("chartPreviousClose") or meta.get("previousClose") or live_p
                    if live_p is not None:
                        t["yield"] = round(float(live_p), 2)
                        t["change"] = round(float(live_p) - float(prev_p), 2)
            except Exception:
                pass
        return tenors

    def refresh_curve_sync(self):
        """Synchronous refresh method."""
        now = time.time()
        self.last_fetch = now

        try:
            live_tenors = self.fetch_live_treasury_curve()
            if live_tenors:
                self.tenors = self.enrich_with_intraday_ticks(live_tenors)
        except Exception as e:
            logger.debug(f"Failed to refresh curve sync: {e}")

    def _build_curve_response(self) -> Dict[str, Any]:
        y2 = next((t["yield"] for t in self.tenors if t["tenor"] == "2Y"), 4.74)
        y10 = next((t["yield"] for t in self.tenors if t["tenor"] == "10Y"), 5.01)
        spread_2_10 = round((y10 - y2) * 100, 1)  # Basis points

        return {
            "curve_name": "US TREASURY BENCHMARK YIELD CURVE",
            "as_of_date": self.as_of_date,
            "tenors": self.tenors,
            "y2": y2,
            "y10": y10,
            "spread_2_10_bps": spread_2_10,
            "inverted": spread_2_10 < 0
        }

    def get_curve(self) -> Dict[str, Any]:
        # Non-blocking check: if cache expired, trigger background refresh
        now = time.time()
        if now - self.last_fetch >= self.cache_ttl:
            self.last_fetch = now
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.get_curve_async())
            except RuntimeError:
                try:
                    self.refresh_curve_sync()
                except Exception as e:
                    logger.debug(f"Error during curve refresh: {e}")

        return self._build_curve_response()

    async def get_curve_async(self) -> Dict[str, Any]:
        now = time.time()
        if now - self.last_fetch >= self.cache_ttl:
            self.last_fetch = now
            try:
                treasury_data = await market_data_client.get_treasury_yield_curve()
                if treasury_data:
                    tenor_change_map = {t["tenor"]: t.get("change", 0.0) for t in self.tenors}
                    updated_tenors = []
                    for t in treasury_data:
                        tenor_code = t["tenor"]
                        y_val = t["yield"]
                        chg = tenor_change_map.get(tenor_code, 0.0)
                        updated_tenors.append({"tenor": tenor_code, "yield": y_val, "change": chg})
                    if updated_tenors:
                        self.tenors = updated_tenors
                        self.as_of_date = datetime.date.today().isoformat()
            except Exception as e:
                logger.debug(f"Async curve refresh error: {e}")
        return self._build_curve_response()

    async def refresh_curve(self) -> Dict[str, Any]:
        """Asynchronous refresh task."""
        return await self.get_curve_async()

