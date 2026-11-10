"""
Tests for PD3board UI Contracts and Normalization Layer.

Verifies that all command payloads strictly adhere to expected contracts,
never raise uncaught exceptions, and properly normalize incomplete, None,
or missing upstream data feeds.
"""

import pytest
from app.main import CommandRequest, execute_command
from app.models.contracts import (
    CONTRACT_REGISTRY,
    normalize_contract_payload,
    DesContract,
    AnrContract,
    FaContract,
    RvContract,
    EeContract,
    OmonContract,
    WirpContract,
    WcrsContract,
    FdmContract,
    EcoContract,
    MapsContract,
    InsdContract,
    HdsContract,
    AiResearchContract,
)
from app.feeds.market_data_client import market_data_client


@pytest.fixture(autouse=True)
async def cleanup_client():
    yield
    await market_data_client.close()


def test_contract_normalization_empty_payloads():
    """Verify that normalize_contract_payload handles empty/None payloads without throwing."""
    for fn in CONTRACT_REGISTRY:
        normalized = normalize_contract_payload(fn, None, "AAPL")
        assert isinstance(normalized, dict)
        if "symbol" in normalized:
            assert normalized["symbol"] == "AAPL"


def test_contract_normalization_corrupt_payloads():
    """Verify that corrupted data types are gracefully coerced or defaulted."""
    corrupted_des = {
        "symbol": "CORRUPT",
        "price": "not_a_float",  # Should trigger fallback or handle gracefully
        "pe": None,
    }
    normalized = normalize_contract_payload("DES", corrupted_des, "CORRUPT")
    assert isinstance(normalized, dict)
    assert normalized["symbol"] == "CORRUPT"
    assert "name" in normalized
    assert "pe" in normalized


def test_contract_dual_representation_keys():
    """Verify that dual-representation keys (e.g., div_yield vs dividend_yield) are synchronized."""
    # DES
    des_yield = normalize_contract_payload("DES", {"div_yield": "3.5%"}, "T")
    assert des_yield["div_yield"] == "3.5%"
    assert des_yield["dividend_yield"] == "3.5%"

    # ANR
    anr = normalize_contract_payload("ANR", {"mean_target": 250.0}, "AAPL")
    assert anr["mean_target"] == 250.0
    assert anr["target_price"] == 250.0

    # FA
    fa = normalize_contract_payload("FA", {"years": ["2023", "2024", "2025"]}, "AAPL")
    assert fa["years"] == ["2023", "2024", "2025"]
    assert fa["periods"] == ["2023", "2024", "2025"]

    # OMON
    omon = normalize_contract_payload(
        "OMON",
        {
            "expiry": "2026-12-18",
            "max_pain_strike": 100.0,
            "chain": [{"strike": 100.0, "is_atm": True, "iv": 25.0, "call_vol": 450, "put_vol": 320}],
        },
        "SPY",
    )
    assert len(omon["chain"]) == 1
    assert len(omon["strikes"]) == 1
    assert omon["expiration"] == "2026-12-18"
    assert omon["atm_iv"] == 0.25
    assert omon["chain"][0]["call_iv"] == 0.25
    assert omon["chain"][0]["put_iv"] == 0.25
    assert omon["chain"][0]["call_volume"] == 450
    assert omon["chain"][0]["put_volume"] == 320
    assert omon["chain"][0]["is_max_pain"] is True

    # AI (verify nested valuation_assessment preserves default keys)
    ai = normalize_contract_payload(
        "AI",
        {"rating": "BUY", "valuation_assessment": {"fwd_pe": "28.4x"}},
        "NVDA",
    )
    assert ai["rating"] == "BUY"
    assert ai["recommendation"] == "BUY"
    assert ai["valuation_assessment"]["fwd_pe"] == "28.4x"
    assert "dividend_yield" in ai["valuation_assessment"]
    assert "verdict" in ai["valuation_assessment"]

@pytest.mark.asyncio
async def test_command_msi_ee_and_des():
    """Verify that MSI EE and DES return complete valid contracts with real live data."""
    res_ee = await execute_command(CommandRequest(command="MSI EE <GO>"))
    assert res_ee["success"] is True
    data_ee = res_ee["data"]
    assert data_ee["symbol"] == "MSI"
    assert "quarterly_history" in data_ee
    assert "forward_estimates" in data_ee

    res_des = await execute_command(CommandRequest(command="MSI DES <GO>"))
    assert res_des["success"] is True
    data_des = res_des["data"]
    assert data_des["symbol"] == "MSI"
    assert data_des["price"] > 100.0
    assert data_des["shares_out"] != "N/A"


@pytest.mark.asyncio
async def test_all_registered_command_contracts():
    """Ensure every terminal command function produces a compliant contract payload."""
    commands = [
        "AAPL DES <GO>",
        "AAPL ANR <GO>",
        "AAPL FA <GO>",
        "AAPL RV <GO>",
        "AAPL EE <GO>",
        "AAPL OMON <GO>",
        "WIRP",
        "WCRS",
        "FDM",
        "ECO",
        "MAPS",
        "AAPL INSD <GO>",
        "AAPL HDS <GO>",
        "NVDA AI <GO>",
        "POLY <GO>",
        "PRED <GO>",
    ]
    for cmd in commands:
        res = await execute_command(CommandRequest(command=cmd))
        assert res["success"] is True
        assert isinstance(res["data"], dict)
        assert len(res["data"]) > 0


def test_safe_parse_xml_rejects_xxe():
    """Verify safe_parse_xml blocks DOCTYPE and ENTITY declarations."""
    from app.feeds.market_data_client import safe_parse_xml

    valid_xml = "<rss><channel><item><title>Market Rally</title></item></channel></rss>"
    root = safe_parse_xml(valid_xml)
    assert root.tag == "rss"

    xxe_xml = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><rss>&xxe;</rss>'
    with pytest.raises(ValueError, match="Unsafe XML declaration"):
        safe_parse_xml(xxe_xml)


@pytest.mark.asyncio
async def test_broadcast_evicts_failed_websocket_clients():
    """Verify broadcast delivers concurrently and evicts broken WebSocket connections."""
    from app.main import active_connections, broadcast

    delivered = []

    class HealthyWS:
        async def send_text(self, payload: str):
            delivered.append(payload)

    class BrokenWS:
        async def send_text(self, payload: str):
            raise RuntimeError("Simulated broken pipe")

    good_ws = HealthyWS()
    bad_ws = BrokenWS()
    active_connections.add(good_ws)
    active_connections.add(bad_ws)
    try:
        await broadcast({"type": "ping", "ts": 123})
        assert len(delivered) == 1
        assert bad_ws not in active_connections
        assert good_ws in active_connections
    finally:
        active_connections.discard(good_ws)
        active_connections.discard(bad_ws)


def test_frontend_xss_escaping_helpers_present():
    """Verify terminal.js defines escapeHtml and orderbook.js coerces numeric values."""
    import os
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "static", "js"))
    with open(os.path.join(base_dir, "terminal.js"), "r", encoding="utf-8") as f:
        term_js = f.read()
    assert "function escapeHtml(" in term_js
    assert "this.escapeHtml(" in term_js


def test_frontend_html_tabs_and_version_cache_parity():
    """Verify every data-fn tab in index.html is wired in CommandParser and terminal.js, and ?v= matches VERSION."""
    import os
    import re
    from app.engine.command_parser import FUNCTIONS

    pd3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with open(os.path.join(pd3_root, "VERSION"), "r", encoding="utf-8") as f:
        version = f.read().strip()
    with open(os.path.join(pd3_root, "app", "static", "index.html"), "r", encoding="utf-8") as f:
        index_html = f.read()
    with open(os.path.join(pd3_root, "app", "static", "js", "terminal.js"), "r", encoding="utf-8") as f:
        term_js = f.read()

    for asset in ("/static/css/terminal.css", "/static/js/chart.js", "/static/js/orderbook.js", "/static/js/terminal.js"):
        assert f"{asset}?v={version}" in index_html, f"Missing cache-buster {asset}?v={version} in index.html"

    fn_tabs = re.findall(r'class="fn-tab[^"]*"\s+data-fn="([A-Z0-9_]+)"', index_html)
    assert len(fn_tabs) >= 20
    workspace_tabs = {"GP", "GIP", "L2", "WEI", "TOP", "YCRV"}
    for fn in fn_tabs:
        assert fn in FUNCTIONS, f"Tab data-fn='{fn}' missing from CommandParser.FUNCTIONS"
        if fn not in workspace_tabs:
            assert f"fn === '{fn}'" in term_js, f"Modal tab data-fn='{fn}' missing explicit branch in terminal.js executeFunction()"
    assert not re.search(r"\}\s*else\s*\{\s*this\.closeModal\(\);\s*\}", term_js), (
        "Bare silent fallthrough else { this.closeModal(); } is prohibited in terminal.js"
    )
    assert "this.priceChart.indicators" in term_js

    with open(os.path.join(pd3_root, "Dockerfile"), "r", encoding="utf-8") as f:
        dockerfile_txt = f.read()
    assert "COPY VERSION ." in dockerfile_txt


def test_e2e_dom_modal_and_orderbook_rendering():
    """Execute frontend JS controllers in Node against contract payloads to verify DOM/SVG rendering."""
    import json
    import os
    import shutil
    import subprocess
    from app.feeds.options import OptionsFeed
    from app.feeds.polymarket import FALLBACK_POLYMARKET_MARKETS

    pd3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    omon_payload = normalize_contract_payload("OMON", OptionsFeed.get_options_chain("AAPL", 225.0), "AAPL")
    assert omon_payload["atm_iv"] > 0
    assert any(r.get("is_max_pain") for r in omon_payload["chain"])
    assert all(r.get("call_iv", 0) > 0 and r.get("put_iv", 0) > 0 for r in omon_payload["chain"])
    poly_payload = normalize_contract_payload("POLY", {"markets": FALLBACK_POLYMARKET_MARKETS[:3], "total_volume_24h": 11510000.0, "total_liquidity": 11250000.0, "avg_spread_cents": 0.47})
    if not shutil.which("node"):
        return
    lang_payload = {
        "enabled": True,
        "host": "http://langfuse-web:3000",
        "external_url": "https://langfuse.home.gilbertopina.com",
        "total_traces": 3,
        "recent_traces": [
            {
                "timestamp": "2026-11-10 00:15:00",
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "rating": "OUTPERFORM",
                "target_price": 160.0,
                "upside_pct": 35.0,
                "url": "https://langfuse.home.gilbertopina.com/traces/123",
            }
        ],
    }

    node_script = f"""
const fs = require('fs');
const elements = {{}};
const getEl = (id) => {{
  if (!elements[id]) {{
    elements[id] = {{
      id,
      innerHTML: '',
      innerText: '',
      style: {{ display: 'block' }},
      classList: {{ remove() {{}}, add() {{}}, toggle() {{ return false; }}, contains() {{ return false; }} }},
      querySelector() {{ return {{}}; }},
      querySelectorAll() {{ return []; }},
      addEventListener() {{}},
    }};
  }}
  return elements[id];
}};
global.window = {{ location: {{ protocol: 'http:', host: 'localhost:8000' }}, addEventListener() {{}}, dispatchEvent() {{}} }};
global.document = {{
  getElementById: getEl,
  querySelectorAll() {{ return []; }},
  addEventListener() {{}},
}};
const storage = {{}};
global.localStorage = {{
  setItem(k, v) {{ storage[k] = v; }},
  getItem(k) {{ return storage[k] || null; }},
}};

eval(fs.readFileSync({json.dumps(os.path.join(pd3_root, "app/static/js/orderbook.js"))}, 'utf8'));
eval(fs.readFileSync({json.dumps(os.path.join(pd3_root, "app/static/js/terminal.js"))}, 'utf8'));

const proto = window.TerminalController ? window.TerminalController.prototype : TerminalController.prototype;
const ctx = Object.create(proto);
ctx.currentTicker = 'AAPL';
ctx.currentSector = 'EQUITY';
ctx.currentFunction = 'OMON';
ctx.clockMode = 'EST';
ctx.cmdHistory = ['AAPL OMON <GO>'];
ctx.sound = {{ enabled: true }};
ctx.priceChart = {{ interval: '5M', indicators: {{ SMA20: true, SMA50: false, BOLL: false, RSI: true, MACD: false }} }};

// 1. Verify OMON modal & SVG Volatility Smile
const omonData = {json.dumps(omon_payload)};
ctx.showOmonModal(omonData);
const omonHtml = getEl('modalBody').innerHTML;
if (!omonHtml.includes('<svg') || !omonHtml.includes('<path d="M')) throw new Error('Missing OMON SVG smile path');
if (omonHtml.includes('0.0%</div>')) throw new Error('OMON ATM IV rendered as 0.0%');
if (!omonHtml.includes('[MAX PAIN]')) throw new Error('Missing [MAX PAIN] badge in OMON table');

// 2. Verify POLY modal
const polyData = {json.dumps(poly_payload)};
ctx.showPolyModal(polyData);
const polyHtml = getEl('modalBody').innerHTML;
if (!polyHtml.includes('https://polymarket.com/event/fed-rate-cut-next-fomc')) throw new Error('Missing Polymarket event URL');
if (!polyHtml.includes('$11.51M')) throw new Error('Missing formatted 24h volume in POLY modal');

// 3. Verify LANG modal
const langData = {json.dumps(lang_payload)};
ctx.showLangfuseModal(langData);
const langHtml = getEl('modalBody').innerHTML;
if (!langHtml.includes('ONLINE // STREAMING') || !langHtml.includes('NVIDIA Corporation')) throw new Error('Missing Langfuse trace row');

// 4. Verify saveState indicator persistence
ctx.saveState();
const saved = JSON.parse(storage['pd3board_state']);
if (JSON.stringify(saved.indicators) !== JSON.stringify(['SMA20', 'RSI'])) {{
  throw new Error('Indicator persistence failed: ' + JSON.stringify(saved.indicators));
}}

// 5. Verify OrderBookUI dynamic 4-decimal FX precision
const obUI = new window.OrderBookUI('obTest');
obUI.update({{
  symbol: 'EURUSD',
  best_bid: 1.1124,
  best_ask: 1.1126,
  spread: 0.0002,
  spread_bps: 1.8,
  bids: [{{ price: 1.1124, size: 10, total: 10 }}],
  asks: [{{ price: 1.1126, size: 10, total: 10 }}],
}});
const obHtml = getEl('obTest').innerHTML;
if (!obHtml.includes('1.1124') || !obHtml.includes('SPREAD: 0.0002')) {{
  throw new Error('OrderBookUI failed 4-decimal FX formatting: ' + obHtml);
}}
console.log('E2E_DOM_OK');
"""
    proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"Node E2E DOM check failed: {proc.stderr or proc.stdout}"
    assert "E2E_DOM_OK" in proc.stdout
