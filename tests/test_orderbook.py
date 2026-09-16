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
