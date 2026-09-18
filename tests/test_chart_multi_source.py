import pytest
from app.feeds.equities import EquitiesFeed, SYMBOL_MAP, PRIVATE_SECURITIES
from app.main import get_or_create_tick_buffer, get_or_create_orderbook

def test_symbol_mappings_across_all_asset_classes():
    # Verify equities, crypto, forex, commodities, yields, and indices are in SYMBOL_MAP
    assert "EURUSD" in SYMBOL_MAP
    assert "GBPUSD" in SYMBOL_MAP
    assert "USDJPY" in SYMBOL_MAP
    assert "CL1" in SYMBOL_MAP
    assert "GC1" in SYMBOL_MAP
    assert "SI1" in SYMBOL_MAP
    assert "US10Y" in SYMBOL_MAP
    assert "US2Y" in SYMBOL_MAP
    assert "DOGE" in SYMBOL_MAP
    assert "SPX" in SYMBOL_MAP
    assert "NDX" in SYMBOL_MAP

def test_multi_source_candles_and_precision():
    test_symbols = [
        "AAPL", "NVDA", "MCD",          # Equities
        "SPX", "NDX", "DJI",            # Indices
        "BTCUSDT", "DOGE", "SOLUSDT",   # Crypto
        "EURUSD", "GBPUSD", "USDJPY",   # Currencies / Forex
        "CL1", "GC1", "SI1", "NG1",     # Commodities
        "US10Y", "US2Y",                # Rates / Yields
        "SPACEX", "OPENAI",             # Private Securities
    ]

    for sym in test_symbols:
        tb = get_or_create_tick_buffer(sym)
        assert tb.candles, f"Expected candles for {sym}"
        candles = list(tb.candles.values())
        assert len(candles) >= 5, f"Expected at least 5 candles for {sym}"

        # Verify candles have valid positive OHLCV values without NaNs
        for c in candles:
            assert c.open > 0, f"Invalid open for {sym}: {c.open}"
            assert c.high >= c.open, f"High must be >= open for {sym}"
            assert c.high >= c.close, f"High must be >= close for {sym}"
            assert c.low <= c.open, f"Low must be <= open for {sym}"
            assert c.low <= c.close, f"Low must be <= close for {sym}"
            assert c.volume > 0, f"Volume must be positive for {sym}"

        # Verify orderbook generation for the symbol
        ob = get_or_create_orderbook(sym)
        assert len(ob.bids) > 0, f"Expected bids for {sym}"
        assert len(ob.asks) > 0, f"Expected asks for {sym}"
        assert ob.bids[0].price < ob.asks[0].price, f"Spread inverted for {sym}: {ob.bids[0].price} vs {ob.asks[0].price}"

def test_multi_timeframe_historical_candles():
    feed = EquitiesFeed()
    for interval in ["1M", "5M", "15M", "1H", "1D"]:
        candles = feed.fetch_historical_candles("AAPL", interval=interval)
        assert len(candles) >= 30, f"Expected at least 30 candles for AAPL {interval}, got {len(candles)}"
        # Verify timestamps are in strictly ascending order
        for i in range(1, len(candles)):
            assert candles[i]["time"] > candles[i - 1]["time"], f"Timestamps out of order for {interval}"
            assert candles[i]["high"] >= candles[i]["low"]
            assert candles[i]["open"] > 0
            assert candles[i]["close"] > 0

    # 1D should have at least 200 daily bars (1+ to 5 years of daily history)
    daily_candles = feed.fetch_historical_candles("AAPL", interval="1D")
    assert len(daily_candles) >= 200, f"Expected >= 200 daily bars, got {len(daily_candles)}"

    # 1M should have multiple days of intraday minute bars (>= 300 bars)
    min_candles = feed.fetch_historical_candles("AAPL", interval="1M")
    assert len(min_candles) >= 300, f"Expected >= 300 minute bars, got {len(min_candles)}"
