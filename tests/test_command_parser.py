import pytest
from app.engine.command_parser import CommandParser

def test_parse_ticker_sector_function_go():
    cmd = "AAPL US EQUITY GP <GO>"
    res = CommandParser.parse(cmd)
    assert res["valid"] is True
    assert res["ticker"] == "AAPL"
    assert res["sector"] == "EQUITY"
    assert res["function"] == "GP"

def test_parse_standalone_function():
    for fn in ["WEI", "TOP", "YCRV", "ECO", "HELP", "ANR", "FA", "RV", "EE", "WIRP", "WCRS", "FDM", "OMON", "MAPS", "AI", "INSD", "HDS", "POLY"]:
        res = CommandParser.parse(f"{fn} <GO>")
        assert res["valid"] is True
        assert res["function"] == fn
        assert res["ticker"] is None

def test_parse_aliases():
    res_news = CommandParser.parse("NEWS <GO>")
    assert res_news["valid"] is True
    assert res_news["function"] == "TOP"
    assert res_news["ticker"] is None

    res_heat = CommandParser.parse("HEAT <GO>")
    assert res_heat["valid"] is True
    assert res_heat["function"] == "MAPS"

    res_res = CommandParser.parse("RES <GO>")
    assert res_res["valid"] is True
    assert res_res["function"] == "AI"

    res_pred = CommandParser.parse("PRED <GO>")
    assert res_pred["valid"] is True
    assert res_pred["function"] == "POLY"

    res_pm = CommandParser.parse("MACRO PM <GO>")
    assert res_pm["valid"] is True
    assert res_pm["ticker"] == "MACRO"
    assert res_pm["function"] == "POLY"

def test_parse_inferred_sector():
    res_crypto = CommandParser.parse("BTCUSDT L2 <GO>")
    assert res_crypto["valid"] is True
    assert res_crypto["ticker"] == "BTCUSDT"
    assert res_crypto["sector"] == "CRNCY"
    assert res_crypto["function"] == "L2"

    res_index = CommandParser.parse("SPX WEI")
    assert res_index["valid"] is True
    assert res_index["ticker"] == "SPX"
    assert res_index["sector"] == "INDEX"

def test_empty_command():
    res = CommandParser.parse("")
    assert res["valid"] is False

def test_reject_invalid_and_xss_tickers():
    malicious_inputs = [
        "<script>alert(1)</script> GP <GO>",
        "DES <img/src=x/onerror=alert(1)>",
        "AAPL\"onload=\"alert(1) EQUITY GP",
        "THIS_TICKER_IS_WAY_TOO_LONG_FOR_A_SYMBOL GP",
    ]
    for bad_cmd in malicious_inputs:
        res = CommandParser.parse(bad_cmd)
        assert res["valid"] is False, f"Expected malicious/invalid command to be rejected: {bad_cmd}"

def test_valid_special_symbol_formats():
    for sym in ["BRK.B", "^GSPC", "EURUSD=X", "BTC-USD", "US10Y"]:
        res = CommandParser.parse(f"{sym} GP <GO>")
        assert res["valid"] is True
        assert res["ticker"] == sym

