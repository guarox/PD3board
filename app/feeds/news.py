import time
from typing import List, Dict, Any

class NewsFeed:
    """
    Financial news wire (TOP/NEWS) streaming breaking market headlines
    with source attribution, sentiment scoring, and ticker tagging.
    """
    def __init__(self):
        self.headlines = [
            {
                "time": "13:28:15",
                "source": "BLOOMBERG",
                "ticker": "SPX",
                "headline": "S&P 500 EXTENDS RALLY TOWARD RECORD HIGH AS TECH SHARES GAIN",
                "sentiment": "BULLISH"
            },
            {
                "time": "13:25:40",
                "source": "REUTERS",
                "ticker": "US10Y",
                "headline": "TREASURY YIELDS DRIFT LOWER AHEAD OF UPCOMING FOMC RATE DECISION",
                "sentiment": "NEUTRAL"
            },
            {
                "time": "13:22:11",
                "source": "DOW JONES",
                "ticker": "NVDA",
                "headline": "NVIDIA UNVEILS NEXT-GEN DATA CENTER ARCHITECTURE AT DEVELOPER FORUM",
                "sentiment": "BULLISH"
            },
            {
                "time": "13:19:02",
                "source": "FT",
                "ticker": "BTCUSD",
                "headline": "INSTITUTIONAL SPOT ETF INFLOWS SURGE TO HIGHEST LEVEL IN 3 WEEKS",
                "sentiment": "BULLISH"
            },
            {
                "time": "13:15:55",
                "source": "BLOOMBERG",
                "ticker": "AAPL",
                "headline": "APPLE INTELLIGENCE GLOBAL EXPANSION PLANNED FOR Q4 UPDATE",
                "sentiment": "BULLISH"
            },
            {
                "time": "13:10:30",
                "source": "WSJ",
                "ticker": "CRUDE",
                "headline": "WTI CRUDE EDGES HIGHER AS MID-EAST SHIPPING STRAINS PERSIST",
                "sentiment": "NEUTRAL"
            }
        ]

    def get_latest_news(self, limit: int = 15) -> List[Dict[str, Any]]:
        return self.headlines[:limit]
