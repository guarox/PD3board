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
    assert "price" in des and "change" in des and "change_pct" in des
    assert "pe" in des and "fwd_pe" in des and "eps" in des
    assert "shares_out" in des and "range_52w" in des and "div_yield" in des

    # Verify MSI DES specific field resolution
    res_msi = await execute_command(CommandRequest(command="MSI DES <GO>"))
    assert res_msi["success"] is True
    des_msi = res_msi["data"]
    assert des_msi["symbol"] == "MSI"
    assert "Motorola" in des_msi["name"] or "MOTOROLA" in des_msi["name"].upper()
    assert des_msi["price"] > 300.0
    assert des_msi["exchange"] in ("NYSE", "NYQ", "NYSE/NASDAQ")
    assert des_msi["shares_out"] != "N/A"
    assert des_msi["revenue"] != "N/A"

@pytest.mark.asyncio
async def test_command_des_crypto():
    res = await execute_command(CommandRequest(command="ETHUSDT DES <GO>"))
    assert res["success"] is True
    des = res["data"]
    assert des["symbol"] == "ETHUSDT"
    assert des["sector"] == "CRNCY"
    assert "exchange" in des and "change" in des and "revenue" in des

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
async def test_command_anr():
    res = await execute_command(CommandRequest(command="AAPL ANR <GO>"))
    assert res["success"] is True
    anr = res["data"]
    assert anr["symbol"] == "AAPL"
    assert "consensus" in anr
    assert "mean_target" in anr
    assert anr["ratings_breakdown"]["Buy"] > 0
    assert len(anr["recent_actions"]) >= 1
    assert "target" in anr["recent_actions"][0]

@pytest.mark.asyncio
async def test_command_ee():
    res = await execute_command(CommandRequest(command="AAPL EE <GO>"))
    assert res["success"] is True
    ee = res["data"]
    assert ee["symbol"] == "AAPL"
    assert "quarterly_history" in ee
    assert len(ee["quarterly_history"]) >= 2
    assert "reported_eps" in ee["quarterly_history"][0]
    assert "revenue_reported" in ee["quarterly_history"][0]
    assert "rev_surprise_pct" in ee["quarterly_history"][0]
    assert "forward_estimates" in ee

    msi_res = await execute_command(CommandRequest(command="MSI EE <GO>"))
    assert msi_res["success"] is True
    msi_ee = msi_res["data"]
    assert msi_ee["symbol"] == "MSI"
    assert len(msi_ee["quarterly_history"]) >= 2
    assert "revenue_reported" in msi_ee["quarterly_history"][0]

    eth_res = await execute_command(CommandRequest(command="ETHUSDT EE <GO>"))
    assert eth_res["success"] is True
    eth_ee = eth_res["data"]
    assert eth_ee["symbol"] == "ETHUSDT"
    assert eth_ee.get("asset_type") == "DIGITAL_ASSET"
    assert len(eth_ee["quarterly_history"]) >= 2

@pytest.mark.asyncio
async def test_command_world_macro():
    wirp = await execute_command(CommandRequest(command="WIRP"))
    assert wirp["success"] is True
    assert "meetings" in wirp["data"]
    assert wirp["data"]["current_target_rate"] == "4.75% - 5.00%"
    assert "%" in wirp["data"]["effective_fed_funds_rate"]

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

    # Verify crypto options dynamic spot price anchoring
    res_eth = await execute_command(CommandRequest(command="ETHUSDT OMON <GO>"))
    assert res_eth["success"] is True
    opts_eth = res_eth["data"]
    assert opts_eth["spot_price"] > 2000.0
    assert opts_eth["chain"][0]["strike"] > 1500.0

    # Verify equity with asymmetric call/put strikes (MSI)
    res_msi = await execute_command(CommandRequest(command="MSI OMON <GO>"))
    assert res_msi["success"] is True
    opts_msi = res_msi["data"]
    assert opts_msi["symbol"] == "MSI"
    assert opts_msi["spot_price"] > 300.0
    assert len(opts_msi["chain"]) >= 5

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
async def test_command_rv():
    res = await execute_command(CommandRequest(command="MCD RV <GO>"))
    assert res["success"] is True
    rv = res["data"]
    assert rv["symbol"] == "MCD"
    assert len(rv["peers"]) >= 3
    # Verify peer metrics are distinct and not all identical
    op_margins = [p["op_margin"] for p in rv["peers"] if p.get("op_margin") != "N/A"]
    assert len(set(op_margins)) > 1, f"Operating margins should be distinct, got {op_margins}"
    ev_ebitdas = [p["ev_ebitda"] for p in rv["peers"] if p.get("ev_ebitda") != "N/A"]
    assert len(set(ev_ebitdas)) > 1, f"EV/EBITDA values should be distinct, got {ev_ebitdas}"

    # Verify crypto RV
    res_crypto = await execute_command(CommandRequest(command="ETHUSDT RV <GO>"))
    assert res_crypto["success"] is True
    assert len(res_crypto["data"]["peers"]) >= 3
    assert res_crypto["data"]["peers"][0]["price"] > 0


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
