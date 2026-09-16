import pytest
from app.feeds.equities import EquitiesFeed
from app.feeds.yield_curve import YieldCurveFeed
from app.feeds.news import NewsFeed
from app.engine.tick_buffer import TickBuffer

def test_equities_feed():
    feed = EquitiesFeed()
    matrix = feed.get_wei_matrix()
    assert len(matrix) >= 5
    symbols = [item["symbol"] for item in matrix]
    assert "SPX" in symbols
    assert "NDX" in symbols

    desc = feed.get_security_description("AAPL")
    assert desc["symbol"] == "AAPL"
    assert "market_cap" in desc

def test_yield_curve_feed():
    feed = YieldCurveFeed()
    curve = feed.get_curve()
    assert "spread_2_10_bps" in curve
    assert len(curve["tenors"]) >= 5

def test_news_feed():
    feed = NewsFeed()
    news = feed.get_latest_news()
    assert len(news) > 0
    assert "headline" in news[0]

def test_tick_buffer_candles():
    tb = TickBuffer("BTCUSDT", max_ticks=10)
    tb.add_tick(price=100.0, size=1.0, timestamp=1000.0)
    tb.add_tick(price=105.0, size=2.0, timestamp=1010.0)
    tb.add_tick(price=98.0, size=0.5, timestamp=1020.0)
    tb.add_tick(price=102.0, size=1.0, timestamp=1030.0)

    candles = tb.get_candles()
    assert len(candles) == 2
    c1 = candles[0]
    assert c1["open"] == 100.0
    assert c1["high"] == 105.0
    assert c1["close"] == 105.0
    assert c1["volume"] == 3.0

    c2 = candles[1]
    assert c2["open"] == 98.0
    assert c2["high"] == 102.0
    assert c2["close"] == 102.0
    assert c2["volume"] == 1.5

