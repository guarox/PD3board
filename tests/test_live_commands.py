import pytest
from app.main import (
    CommandRequest,
    execute_command,
    health_check,
    get_wei,
    get_yield_curve,
    get_news,
    get_eco,
    get_des,
    get_fa,
    get_wirp,
    get_wcrs,
    get_fdm,
    get_options,
    get_heatmap,
    get_insiders,
    get_holders,
    get_research,
)
from app.feeds.market_data_client import market_data_client

@pytest.fixture(autouse=True)
async def cleanup_client():
    yield
    await market_data_client.close()

@pytest.mark.asyncio
async def test_health():
    res = await health_check()
    assert res["status"] == "healthy"
    assert res["service"] == "PD3board"

@pytest.mark.asyncio
async def test_command_wei():
    res = await execute_command(CommandRequest(command="WEI"))
    assert res["success"] is True
    indices = res["data"]["indices"]
    assert len(indices) >= 5
    symbols = [i["symbol"] for i in indices]
    assert "SPX" in symbols

@pytest.mark.asyncio
async def test_command_fa_equities():
    res = await execute_command(CommandRequest(command="AAPL FA <GO>"))
    assert res["success"] is True
    fa = res["data"]
    assert fa["symbol"] == "AAPL"
    assert len(fa["years"]) >= 4
    metrics = [r["metric"] for r in fa["income_statement"]]
    assert any("Revenue" in m for m in metrics)
    assert any("Net Income" in m for m in metrics)

@pytest.mark.asyncio
async def test_command_fa_crypto_no_corporate_statements():
    res = await execute_command(CommandRequest(command="ETHUSDT FA <GO>"))
    assert res["success"] is True
    fa = res["data"]
    assert fa["symbol"] == "ETHUSDT"
    assert "DIGITAL_ASSET" in fa.get("asset_type", "") or "CRYPTOCURRENCY" in fa.get("asset_type", "")
    metrics = [r["metric"] for r in fa["income_statement"]]
    # Verify corporate Diluted EPS is NOT present for Ethereum
    assert not any("Diluted EPS" in m for m in metrics)
    assert any("Market Capitalization" in m for m in metrics)
    assert any("Total Value Locked (TVL)" in m for m in metrics)

@pytest.mark.asyncio
async def test_command_des():
    res = await execute_command(CommandRequest(command="AAPL DES <GO>"))
    assert res["success"] is True
    des = res["data"]
    assert des["symbol"] == "AAPL"
    assert "Apple" in des["name"] or "APPLE" in des["name"].upper()

@pytest.mark.asyncio
async def test_command_des_crypto():
    res = await execute_command(CommandRequest(command="ETHUSDT DES <GO>"))
    assert res["success"] is True
    des = res["data"]
    assert des["symbol"] == "ETHUSDT"
    assert des["sector"] == "CRNCY"

@pytest.mark.asyncio
async def test_command_ycrv():
    res = await execute_command(CommandRequest(command="YCRV"))
    assert res["success"] is True
    curve = res["data"]
    assert "tenors" in curve
    assert len(curve["tenors"]) >= 7
    assert "spread_2_10_bps" in curve

@pytest.mark.asyncio
async def test_command_top_news():
    res = await execute_command(CommandRequest(command="TOP"))
    assert res["success"] is True
    news = res["data"]["news"]
    assert len(news) >= 3
    assert "headline" in news[0]

@pytest.mark.asyncio
async def test_command_eco():
    res = await execute_command(CommandRequest(command="ECO"))
    assert res["success"] is True
    events = res["data"]["events"]
    assert len(events) >= 3
    assert "indicator" in events[0]

@pytest.mark.asyncio
async def test_command_world_macro():
    wirp = await execute_command(CommandRequest(command="WIRP"))
    assert wirp["success"] is True
    assert "meetings" in wirp["data"]

    wcrs = await execute_command(CommandRequest(command="WCRS"))
    assert wcrs["success"] is True
    assert len(wcrs["data"]["currencies"]) >= 5

    fdm = await execute_command(CommandRequest(command="FDM"))
    assert fdm["success"] is True
    assert len(fdm["data"]["commodities"]) >= 5

@pytest.mark.asyncio
async def test_command_omon():
    res = await execute_command(CommandRequest(command="AAPL OMON <GO>"))
    assert res["success"] is True
    opts = res["data"]
    assert opts["symbol"] == "AAPL"
    assert "chain" in opts
    assert len(opts["chain"]) >= 5
    assert "max_pain_strike" in opts

@pytest.mark.asyncio
async def test_command_maps():
    res = await execute_command(CommandRequest(command="MAPS"))
    assert res["success"] is True
    heatmap = res["data"]
    assert "sectors" in heatmap
    assert len(heatmap["sectors"]) >= 6

@pytest.mark.asyncio
async def test_command_insd_and_hds():
    insd = await execute_command(CommandRequest(command="AAPL INSD <GO>"))
    assert insd["success"] is True
    assert len(insd["data"]["transactions"]) >= 1

    hds = await execute_command(CommandRequest(command="AAPL HDS <GO>"))
    assert hds["success"] is True
    assert len(hds["data"]["holders"]) >= 3

@pytest.mark.asyncio
async def test_command_ai():
    res = await execute_command(CommandRequest(command="NVDA AI <GO>"))
    assert res["success"] is True
    memo = res["data"]
    assert memo["symbol"] == "NVDA"
    assert "analyst" in memo
    assert "target_price" in memo
    assert len(memo["competitive_moat"]) >= 1

@pytest.mark.asyncio
async def test_prefix_syntax_support():
    # Verify prefix syntax: "FA AAPL"
    res = await execute_command(CommandRequest(command="FA AAPL"))
    assert res["success"] is True
    assert res["data"]["symbol"] == "AAPL"

    # Verify prefix syntax: "DES ETHUSDT"
    res2 = await execute_command(CommandRequest(command="DES ETHUSDT"))
    assert res2["success"] is True
    assert res2["data"]["symbol"] == "ETHUSDT"

@pytest.mark.asyncio
async def test_rest_endpoints():
    wei = await get_wei()
    assert len(wei) >= 5

    curve = await get_yield_curve()
    assert "tenors" in curve

    news = await get_news()
    assert len(news) >= 3

    eco = await get_eco()
    assert len(eco) >= 3

    des = await get_des("AAPL")
    assert des["symbol"] == "AAPL"

    fa = await get_fa("ETHUSDT")
    assert "DIGITAL_ASSET" in fa.get("asset_type", "") or "CRYPTOCURRENCY" in fa.get("asset_type", "")

    heatmap = await get_heatmap()
    assert "sectors" in heatmap

    wirp = await get_wirp()
    assert "meetings" in wirp

    wcrs = await get_wcrs()
    assert len(wcrs) >= 5

    fdm = await get_fdm()
    assert len(fdm) >= 5
