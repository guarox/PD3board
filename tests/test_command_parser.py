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
    for fn in ["WEI", "TOP", "YCRV", "ECO", "HELP", "ANR", "FA", "RV", "EE", "WIRP", "WCRS", "FDM"]:
        res = CommandParser.parse(f"{fn} <GO>")
        assert res["valid"] is True
        assert res["function"] == fn
        assert res["ticker"] is None

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
