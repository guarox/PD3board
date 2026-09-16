import pytest
from app.feeds.equities import EquitiesFeed
from app.feeds.yield_curve import YieldCurveFeed
from app.feeds.news import NewsFeed
from app.feeds.eco import EcoFeed
from app.engine.tick_buffer import TickBuffer

def test_equities_feed():
    feed = EquitiesFeed()
    matrix = feed.get_wei_matrix()
    assert len(matrix) >= 5
    symbols = [item["symbol"] for item in matrix]
    assert "SPX" in symbols
    assert "NDX" in symbols

    desc_aapl = feed.get_security_description("AAPL")
    assert desc_aapl["symbol"] == "AAPL"
    assert "market_cap" in desc_aapl
    assert desc_aapl["pe"] == 33.8
    assert desc_aapl["ceo"] == "Tim Cook"

    desc_mcd = feed.get_security_description("MCD")
    assert desc_mcd["symbol"] == "MCD"
    assert desc_mcd["name"] == "MCDONALD'S CORP"
    assert desc_mcd["pe"] == 26.4
    assert desc_mcd["market_cap"] == "214.5B"
    assert desc_mcd["exchange"] == "NYSE"

    anr = feed.get_analyst_recommendations("MCD")
    assert anr["symbol"] == "MCD"
    assert anr["consensus"] == "MODERATE BUY"
    assert anr["total_analysts"] >= 20
    assert len(anr["brokers"]) >= 3

    fa = feed.get_financial_analysis("MCD")
    assert fa["symbol"] == "MCD"
    assert len(fa["years"]) == 5
    assert len(fa["income_statement"]) >= 5

    rv = feed.get_relative_valuation("MCD")
    assert rv["symbol"] == "MCD"
    assert len(rv["peers"]) >= 4

    ee = feed.get_earnings_estimates("MCD")
    assert ee["symbol"] == "MCD"
    assert len(ee["quarterly_history"]) >= 4

def test_world_macro_feed():
    from app.feeds.world_macro import WorldMacroFeed
    feed = WorldMacroFeed()
    
    wirp = feed.get_wirp()
    assert "current_target_rate" in wirp
    assert len(wirp["meetings"]) >= 3

    wcrs = feed.get_wcrs()
    assert len(wcrs) >= 6
    assert any(c["code"] == "JPY" for c in wcrs)

    fdm = feed.get_fdm()
    assert len(fdm) >= 6
    assert any(c["symbol"] == "CL1" for c in fdm)

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

def test_eco_feed():
    feed = EcoFeed()
    events = feed.get_events()
    assert len(events) >= 5
    event = events[0]
    assert "indicator" in event
    assert "actual" in event
    assert "impact" in event

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

def test_coinbase_feed_instantiation():
    from app.feeds.coinbase import CoinbaseFeed
    feed = CoinbaseFeed(symbol="BTC-USD")
    assert feed.unified_symbol == "BTCUSD"
    assert feed.running is False

def test_index_security_price_and_des():
    feed = EquitiesFeed()
    spx_price = feed.get_security_price("SPX")
    assert spx_price > 5000.0

    ndx_price = feed.get_security_price("NDX")
    assert ndx_price > 18000.0

    mcd_price = feed.get_security_price("MCD")
    assert 280.0 < mcd_price < 350.0

    spx_des = feed.get_security_description("SPX")
    assert spx_des["symbol"] == "SPX"
    assert spx_des["name"] == "S&P 500 INDEX"
    assert "benchmark" in spx_des["description"].lower() or "benchmark" in spx_des["name"].lower()
    assert spx_des["exchange"] == "CBOE / NYSE / NASDAQ"

