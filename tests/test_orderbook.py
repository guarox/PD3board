import pytest
from app.engine.orderbook import OrderBook

def test_orderbook_sorting_and_totals():
    ob = OrderBook("BTCUSDT", max_depth=5)
    bids = [[60000.0, 1.0], [60100.0, 0.5], [59900.0, 2.0]]
    asks = [[60200.0, 1.5], [60150.0, 0.8], [60300.0, 3.0]]

    ob.update_levels(bids, asks, update_id=101)
    snapshot = ob.get_snapshot()

    assert snapshot["symbol"] == "BTCUSDT"
    assert snapshot["best_bid"] == 60100.0
    assert snapshot["best_ask"] == 60150.0
    assert snapshot["spread"] == 50.0

    # Ensure bids are sorted descending
    assert snapshot["bids"][0]["price"] == 60100.0
    assert snapshot["bids"][1]["price"] == 60000.0
    assert snapshot["bids"][2]["price"] == 59900.0
    assert snapshot["bids"][0]["total"] == 0.5
    assert snapshot["bids"][1]["total"] == 1.5

    # Ensure asks are sorted ascending
    assert snapshot["asks"][0]["price"] == 60150.0
    assert snapshot["asks"][1]["price"] == 60200.0
    assert snapshot["asks"][2]["price"] == 60300.0


def test_thread_safe_orderbook_and_tick_buffer():
    import threading
    from app.engine.tick_buffer import TickBuffer

    ob = OrderBook("BTCUSDT", max_depth=10)
    tb = TickBuffer("BTCUSDT", max_ticks=500)
    errors = []

    def writer():
        try:
            for i in range(200):
                p = 60000.0 + (i % 50)
                tb.add_tick(price=p, size=1.25, side="buy", timestamp=1700000000.0 + i * 15)
                ob.update_levels([[p - 1.0, 1.0], [p - 2.0, 2.0]], [[p + 1.0, 1.5], [p + 2.0, 2.5]], update_id=i)
        except Exception as e:
            errors.append(e)

    def reader():
        try:
            for _ in range(200):
                _ = tb.get_candles(limit=100)
                _ = tb.get_recent_ticks(count=20)
                _ = ob.get_snapshot()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer) for _ in range(3)] + [threading.Thread(target=reader) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Thread-safety errors encountered: {errors}"

