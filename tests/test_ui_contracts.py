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
    omon = normalize_contract_payload("OMON", {"chain": [{"strike": 100.0}]}, "SPY")
    assert len(omon["chain"]) == 1
    assert len(omon["strikes"]) == 1

    # AI
    ai = normalize_contract_payload("AI", {"rating": "BUY"}, "NVDA")
    assert ai["rating"] == "BUY"
    assert ai["recommendation"] == "BUY"


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
    ]

    for cmd in commands:
        res = await execute_command(CommandRequest(command=cmd))
        assert res["success"] is True
        assert isinstance(res["data"], dict)
        assert len(res["data"]) > 0
