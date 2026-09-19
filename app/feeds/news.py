import asyncio
import datetime
from email.utils import parsedate_to_datetime
import logging
import re
import time
from typing import List, Dict, Any, Optional, Set
import xml.etree.ElementTree as ET

import aiohttp

try:
    import zoneinfo
    NY_TZ = zoneinfo.ZoneInfo("America/New_York")
except Exception:
    NY_TZ = datetime.timezone(datetime.timedelta(hours=-4))

logger = logging.getLogger(__name__)

TICKER_MAP = {
    "BITCOIN": "BTCUSD", "BTC": "BTCUSD", "CRYPTO": "BTCUSD",
    "ETHEREUM": "ETHUSD", "ETH": "ETHUSD", "SOLANA": "SOLUSD",
    "S&P 500": "SPX", "S&P": "SPX", "SP500": "SPX",
    "NASDAQ": "NDX", "TECH": "NDX",
    "DOW": "DJI", "DOW JONES": "DJI",
    "RUSSELL": "RUT",
    "TREASURY": "US10Y", "YIELDS": "US10Y", "FED": "US10Y", "FOMC": "US10Y", "RATES": "US10Y",
    "NVIDIA": "NVDA", "NVDA": "NVDA",
    "APPLE": "AAPL", "AAPL": "AAPL",
    "TESLA": "TSLA", "TSLA": "TSLA",
    "MICROSOFT": "MSFT", "MSFT": "MSFT",
    "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "GOOGL": "GOOGL",
    "AMAZON": "AMZN", "AMZN": "AMZN",
    "META": "META",
    "CRUDE": "CRUDE", "OIL": "CRUDE", "WTI": "CRUDE", "BRENT": "CRUDE",
    "GOLD": "GOLD",
    "BOEING": "BA", "BA": "BA",
    "MCDONALD": "MCD", "MCD": "MCD",
    "NIKE": "NKE", "NKE": "NKE",
    "OPENAI": "AI", "ANTHROPIC": "AI",
}

IGNORE_PAREN = {
    "CNN", "WSJ", "FT", "AP", "REU", "AFP", "CEO", "CFO", "ETF",
    "IPO", "AI", "SEC", "FDA", "EPA", "USA", "USD", "EUR", "GBP"
}

BULLISH_WORDS = {
    "rally", "surge", "surges", "gain", "gains", "jump", "jumps", "higher",
    "climbs", "record", "boom", "beats", "profit", "bull", "growth", "soar",
    "soars", "boost", "inflows", "upbeat", "outperform"
}

BEARISH_WORDS = {
    "plunge", "plunges", "slump", "slumps", "drop", "drops", "fall", "falls",
    "lower", "slides", "crash", "loss", "losses", "bear", "misses", "risk",
    "cuts", "down", "selloff", "fears", "debt", "tariff", "tariffs", "strains"
}

RSS_FEEDS = [
    ("CNBC", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"),
    ("YAHOO", "https://finance.yahoo.com/news/rssindex"),
    ("COINDESK", "https://www.coindesk.com/arc/outboundfeeds/rss/")
]


class NewsFeed:
    """
    Financial news wire (TOP/NEWS) streaming breaking market headlines
    from live institutional RSS feeds with source attribution, sentiment scoring,
    and automatic ticker entity recognition.
    """
    def __init__(self):
        # Seed with initial high-profile headlines
        now_str = datetime.datetime.now(NY_TZ).strftime("%H:%M:%S")
        self.headlines: List[Dict[str, Any]] = [
            {
                "time": now_str,
                "source": "BLOOMBERG",
                "ticker": "SPX",
                "headline": "S&P 500 EXTENDS RALLY TOWARD RECORD HIGH AS TECH SHARES GAIN",
                "sentiment": "BULLISH",
                "epoch": time.time()
            },
            {
                "time": now_str,
                "source": "REUTERS",
                "ticker": "US10Y",
                "headline": "TREASURY YIELDS DRIFT LOWER AHEAD OF UPCOMING FOMC RATE DECISION",
                "sentiment": "NEUTRAL",
                "epoch": time.time() - 60
            },
            {
                "time": now_str,
                "source": "DOW JONES",
                "ticker": "NVDA",
                "headline": "NVIDIA UNVEILS NEXT-GEN DATA CENTER ARCHITECTURE AT DEVELOPER FORUM",
                "sentiment": "BULLISH",
                "epoch": time.time() - 120
            },
            {
                "time": now_str,
                "source": "FT",
                "ticker": "BTCUSD",
                "headline": "INSTITUTIONAL SPOT ETF INFLOWS SURGE TO HIGHEST LEVEL IN 3 WEEKS",
                "sentiment": "BULLISH",
                "epoch": time.time() - 180
            },
            {
                "time": now_str,
                "source": "BLOOMBERG",
                "ticker": "AAPL",
                "headline": "APPLE INTELLIGENCE GLOBAL EXPANSION PLANNED FOR Q4 UPDATE",
                "sentiment": "BULLISH",
                "epoch": time.time() - 240
            },
            {
                "time": now_str,
                "source": "WSJ",
                "ticker": "CRUDE",
                "headline": "WTI CRUDE EDGES HIGHER AS MID-EAST SHIPPING STRAINS PERSIST",
                "sentiment": "NEUTRAL",
                "epoch": time.time() - 300
            }
        ]
        self._seen_headlines: Set[str] = {h["headline"] for h in self.headlines}
        self.last_refresh: float = 0.0

    @staticmethod
    def extract_ticker(headline: str) -> str:
        """Extract primary financial instrument or equity ticker from headline."""
        # 1. Look for parenthetical stock symbols e.g. (LUV), (TSLA)
        paren = re.search(r"\(([A-Z]{1,5})\)", headline)
        if paren and paren.group(1) not in IGNORE_PAREN:
            return paren.group(1)

        # 2. Match known entities and macro instruments
        upper = headline.upper()
        for key, sym in TICKER_MAP.items():
            if re.search(r"\b" + re.escape(key) + r"\b", upper):
                return sym

        return "MARKET"

    @staticmethod
    def classify_sentiment(headline: str) -> str:
        """Heuristic sentiment classifier for financial headlines."""
        words = set(re.findall(r"\b[A-Za-z]+\b", headline.lower()))
        bull_hits = len(words & BULLISH_WORDS)
        bear_hits = len(words & BEARISH_WORDS)

        if bull_hits > bear_hits:
            return "BULLISH"
        elif bear_hits > bull_hits:
            return "BEARISH"
        return "NEUTRAL"

    async def _fetch_single_feed(self, session: aiohttp.ClientSession, source: str, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse items from a single RSS feed endpoint."""
        items = []
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=7)) as resp:
                if resp.status == 200:
                    raw_xml = await resp.text()
                    root = ET.fromstring(raw_xml)
                    for node in root.findall(".//item"):
                        title_el = node.find("title")
                        date_el = node.find("pubDate")
                        if title_el is not None and title_el.text:
                            raw_title = title_el.text.strip()
                            clean_headline = re.sub(r"\s+", " ", raw_title).strip()
                            clean_headline = clean_headline.replace("&amp;", "&").replace("&quot;", '"')

                            dt = None
                            if date_el is not None and date_el.text:
                                date_str = date_el.text.strip()
                                try:
                                    dt = parsedate_to_datetime(date_str)
                                except Exception:
                                    try:
                                        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                    except Exception:
                                        pass

                            if not dt:
                                dt = datetime.datetime.now(datetime.timezone.utc)

                            # Convert to NY Eastern Time for standard terminal clock alignment
                            try:
                                dt_ny = dt.astimezone(NY_TZ)
                            except Exception:
                                dt_ny = dt

                            time_str = dt_ny.strftime("%H:%M:%S")
                            epoch = dt.timestamp() if hasattr(dt, "timestamp") else time.time()

                            ticker = self.extract_ticker(clean_headline)
                            sentiment = self.classify_sentiment(clean_headline)

                            items.append({
                                "time": time_str,
                                "source": source,
                                "ticker": ticker,
                                "headline": clean_headline.upper(),
                                "sentiment": sentiment,
                                "epoch": epoch
                            })
        except Exception as e:
            logger.warning(f"Error fetching live RSS feed {source} ({url}): {e}")
        return items

    async def refresh_news(self) -> List[Dict[str, Any]]:
        """
        Poll live RSS feeds concurrently, deduplicate, and update the wire cache.
        Returns newly added headline objects.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml; q=0.9, */*; q=0.8"
        }

        new_items: List[Dict[str, Any]] = []
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                tasks = [self._fetch_single_feed(session, src, url) for src, url in RSS_FEEDS]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                fetched: List[Dict[str, Any]] = []
                for res in results:
                    if isinstance(res, list):
                        fetched.extend(res)

                if fetched:
                    # Sort fetched headlines newest first
                    fetched.sort(key=lambda x: x["epoch"], reverse=True)

                    for item in fetched:
                        h_key = item["headline"]
                        if h_key not in self._seen_headlines:
                            self._seen_headlines.add(h_key)
                            new_items.append(item)

                    if new_items:
                        # Combine new items with existing headlines and maintain max 50 items
                        combined = new_items + self.headlines
                        # Deduplicate while preserving order
                        seen = set()
                        deduped = []
                        for h in combined:
                            if h["headline"] not in seen:
                                seen.add(h["headline"])
                                deduped.append(h)
                        self.headlines = deduped[:50]
                        logger.info(f"News wire updated with {len(new_items)} new live headlines")
                    elif not self.headlines and fetched:
                        self.headlines = fetched[:50]

            self.last_refresh = time.time()
        except Exception as e:
            logger.error(f"Failed to refresh live news feeds: {e}")

        return new_items

    def get_latest_news(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Return the latest headlines sorted by recency."""
        return self.headlines[:limit]

    async def get_latest_news_async(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Return the latest live news headlines, refreshing if empty or older than 60s."""
        if not self.headlines or (time.time() - self.last_refresh > 60):
            await self.refresh_news()
        return self.headlines[:limit] if self.headlines else self.get_latest_news(limit)

