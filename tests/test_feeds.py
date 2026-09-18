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
    assert "ticker" in news[0]
    assert "sentiment" in news[0]

    # Test ticker extraction heuristics
    assert feed.extract_ticker("Bitcoin jumps past 76k") == "BTCUSD"
    assert feed.extract_ticker("Nvidia unveils new Blackwell chip") == "NVDA"
    assert feed.extract_ticker("Fed rate cuts expected in December") == "US10Y"
    assert feed.extract_ticker("Southwest (LUV) reports earnings") == "LUV"

    # Test sentiment heuristics
    assert feed.classify_sentiment("S&P 500 surges to record highs") == "BULLISH"
    assert feed.classify_sentiment("Tech stocks plunge amid market selloff") == "BEARISH"
    assert feed.classify_sentiment("Central bank announces meeting date") == "NEUTRAL"

def test_news_feed_refresh():
    import asyncio
    feed = NewsFeed()
    new_items = asyncio.run(feed.refresh_news())
    assert isinstance(new_items, list)
    latest = feed.get_latest_news(5)
    assert len(latest) > 0
    assert "epoch" in latest[0]

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
    assert 200.0 < mcd_price < 400.0

    spx_des = feed.get_security_description("SPX")
    assert spx_des["symbol"] == "SPX"
    assert spx_des["name"] == "S&P 500 INDEX"
    assert "benchmark" in spx_des["description"].lower() or "benchmark" in spx_des["name"].lower()
    assert spx_des["exchange"] == "CBOE / NYSE / NASDAQ"

def test_options_feed():
    from app.feeds.options import OptionsFeed
    feed = OptionsFeed()
    omon = feed.get_options_chain("SPX")
    assert omon["symbol"] == "SPX"
    assert omon["spot_price"] > 5000
    assert "chain" in omon
    assert len(omon["chain"]) >= 7
    assert omon["max_pain_strike"] > 0
    # verify Greeks are calculated and populated
    atm_row = [r for r in omon["chain"] if r["is_atm"]][0]
    assert 0.4 <= atm_row["call_delta"] <= 0.6
    assert -0.6 <= atm_row["put_delta"] <= -0.4
    assert atm_row["call_gamma"] > 0
    assert atm_row["call_vega"] > 0

def test_market_heatmap_feed():
    from app.feeds.market_heatmap import MarketHeatmapFeed
    feed = MarketHeatmapFeed()
    heatmap = feed.get_sp500_heatmap()
    assert heatmap["index"] == "S&P 500"
    assert heatmap["total_symbols"] >= 20
    assert len(heatmap["sectors"]) >= 6
    tech_sector = [s for s in heatmap["sectors"] if "tech" in s["sector"].lower()][0]
    assert len(tech_sector["constituents"]) >= 4
    symbols = [c["symbol"] for c in tech_sector["constituents"]]
    assert "AAPL" in symbols
    assert "NVDA" in symbols

def test_insider_holdings_feed():
    from app.feeds.insider_holdings import InsiderHoldingsFeed
    feed = InsiderHoldingsFeed()
    insd = feed.get_insider_transactions("AAPL")
    assert insd["symbol"] == "AAPL"
    assert len(insd["transactions"]) >= 3
    assert "sentiment" in insd

    hds = feed.get_institutional_holders("AAPL")
    assert hds["symbol"] == "AAPL"
    assert len(hds["holders"]) >= 5
    assert hds["holders"][0]["rank"] == 1
    assert "Vanguard" in hds["holders"][0]["name"] or "BlackRock" in hds["holders"][0]["name"]

def test_ai_research_feed():
    from app.feeds.ai_research import AIResearchFeed
    feed = AIResearchFeed()
    memo = feed.generate_research_memo("NVDA")
    assert memo["symbol"] == "NVDA"
    assert "rating" in memo
    assert memo["target_price"] > memo["spot_price"]
    assert len(memo["competitive_moat"]) >= 3
    assert len(memo["growth_catalysts"]) >= 3
    assert len(memo["downside_risks"]) >= 3
    assert "fwd_pe" in memo["valuation_assessment"]

def test_market_sessions_and_hours():
    from app.feeds.equities import EquitiesFeed
    feed = EquitiesFeed()
    sessions = feed.get_market_sessions()
    assert "NYSE" in sessions
    assert "LSE" in sessions
    assert "TSE" in sessions
    assert sessions["CRNCY"] == "OPEN"
    assert sessions["NYSE"] in ("OPEN", "CLOSED", "AFTER-HOURS", "PRE-MARKET")

    # Crypto is always open 24/7
    assert feed.is_symbol_market_open("BTC") is True
    assert feed.is_symbol_market_open("ETHUSDT") is True
    # Private equity unlisted is always closed
    assert feed.is_symbol_market_open("SPACEX") is False

def test_crypto_excluded_from_synthetic_ticks():
    from app.feeds.equities import EquitiesFeed
    feed = EquitiesFeed()
    updates = feed.update_ticks()
    symbols = [u["symbol"].upper() for u in updates]
    crypto_symbols = {"BTC", "ETH", "SOL", "BTCUSD", "BTCUSDT", "ETHUSD", "ETHUSDT", "SOLUSD", "SOLUSDT"}
    assert not any(s in crypto_symbols for s in symbols)

def test_tick_buffer_pruning():
    from app.engine.tick_buffer import TickBuffer
    tb = TickBuffer("TEST", max_ticks=2000)
    # Add ticks across 3100 minutes to trigger circular buffer pruning
    for m in range(3100):
        tb.add_tick(price=100.0 + (m % 50), size=1.0, timestamp=float(m * 60))
    candles = tb.get_candles(limit=3000)
    assert len(tb.candles) <= 3000
    assert len(tb.candles) >= 2500
    assert len(candles) <= 3000

def test_equities_brownian_tick_walk():
    from app.feeds.equities import EquitiesFeed
    feed = EquitiesFeed()
    feed.indices["SPX"]["price"] = 7636.00
    # Simulate ticks
    feed.is_symbol_market_open = lambda s: True
    updates = feed.update_ticks()
    assert isinstance(updates, list)
    if "SPX" in feed.simulated_prices:
        sim_price = feed.simulated_prices["SPX"]
        # Ensure simulated price is within 1% of baseline 7636.00
        assert abs(sim_price - 7636.00) / 7636.00 < 0.01

def test_indices_baseline_prices():
    from app.feeds.equities import EquitiesFeed
    feed = EquitiesFeed()
    assert feed.indices["SPX"]["price"] >= 7000.0
    assert feed.indices["NDX"]["price"] >= 20000.0
    assert feed.indices["DJI"]["price"] >= 45000.0
    assert feed.get_security_price("SPX") >= 7000.0



