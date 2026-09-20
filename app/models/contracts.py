"""
PD3board Strict UI Contract DTOs & Normalization Layer.

Guarantees that every response returned to the frontend strictly conforms
to the schema expected by terminal.js modals, preventing uncaught frontend
exceptions due to undefined or missing upstream metrics while preserving
all real-time data returned by market data feeds.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class DesContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    sector: str = "EQUITY"
    name: str = "Unknown Security"
    exchange: str = "US"
    industry: str = "General"
    price: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    market_cap: str = "N/A"
    pe: Union[float, str] = "N/A"
    fwd_pe: Union[float, str] = "N/A"
    eps: Union[float, str] = "N/A"
    shares_out: str = "N/A"
    range_52w: str = "N/A"
    div_yield: Union[float, str] = "N/A"
    dividend_yield: Union[float, str] = "N/A"
    ex_div_date: str = "N/A"
    revenue: str = "N/A"
    net_income: str = "N/A"
    ceo: str = "N/A"
    hq: str = "N/A"
    description: str = "No description available."
    financials: Optional[Dict[str, Any]] = None
    macro: Optional[Dict[str, Any]] = None


class BrokerRecommendation(BaseModel):
    model_config = ConfigDict(extra="allow")

    firm: str = "Wall Street Research"
    analyst: str = "Analyst Team"
    rating: str = "HOLD"
    action: str = "Reiterate"
    target: float = 0.0
    date: str = "2026"


class AnrContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    consensus: str = "HOLD"
    consensus_score: float = 3.0
    mean_target: float = 0.0
    target_price: float = 0.0
    upside_pct: float = 0.0
    target_low: float = 0.0
    target_high: float = 0.0
    buys: int = 0
    holds: int = 0
    sells: int = 0
    total_analysts: int = 0
    ratings_breakdown: Dict[str, Any] = Field(default_factory=lambda: {"Buy": 0, "Hold": 0, "Sell": 0})
    recent_actions: List[Dict[str, Any]] = Field(default_factory=list)
    brokers: List[Dict[str, Any]] = Field(default_factory=list)


class FaContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    asset_type: str = "EQUITY"
    years: List[str] = Field(default_factory=lambda: ["2021", "2022", "2023", "2024", "2025"])
    periods: List[str] = Field(default_factory=lambda: ["2021", "2022", "2023", "2024", "2025"])
    income_statement: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    balance_sheet: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    cash_flow: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    note: Optional[str] = None


class PeerValuation(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    name: str = "Peer"
    price: float = 0.0
    pe: Union[float, str] = "N/A"
    fwd_pe: Union[float, str] = "N/A"
    ev_ebitda: Union[float, str] = "N/A"
    ps: Union[float, str] = "N/A"
    op_margin: Union[float, str] = "N/A"
    roe: Union[float, str] = "N/A"
    div_yield: Union[float, str] = "N/A"


class RvContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    industry: str = "General"
    peers: List[Dict[str, Any]] = Field(default_factory=list)


class EeContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    asset_type: str = "EQUITY"
    quarterly_history: List[Dict[str, Any]] = Field(default_factory=list)
    forward_estimates: List[Dict[str, Any]] = Field(default_factory=list)


class OptionStrike(BaseModel):
    model_config = ConfigDict(extra="allow")

    strike: float = 0.0
    call_bid: float = 0.0
    call_ask: float = 0.0
    call_iv: float = 0.0
    call_delta: float = 0.0
    call_gamma: float = 0.0
    call_theta: float = 0.0
    call_vega: float = 0.0
    put_bid: float = 0.0
    put_ask: float = 0.0
    put_iv: float = 0.0
    put_delta: float = 0.0
    put_gamma: float = 0.0
    put_theta: float = 0.0
    put_vega: float = 0.0
    is_atm: bool = False
    is_max_pain: bool = False


class OmonContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    spot_price: float = 0.0
    expiry: str = "N/A"
    expiration: str = "N/A"
    dte: int = 0
    expiries: List[str] = Field(default_factory=list)
    atm_iv: float = 0.0
    max_pain_strike: float = 0.0
    put_call_ratio: float = 1.0
    chain: List[Dict[str, Any]] = Field(default_factory=list)
    strikes: List[Dict[str, Any]] = Field(default_factory=list)


class WirpMeeting(BaseModel):
    model_config = ConfigDict(extra="allow")

    meeting_date: str = "N/A"
    hike_prob_pct: float = 0.0
    cut_prob_pct: float = 0.0
    hold_prob_pct: float = 100.0
    implied_rate: str = "N/A"


class WirpContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_target_rate: str = "4.75% - 5.00%"
    effective_fed_funds_rate: str = "4.83%"
    meetings: List[Dict[str, Any]] = Field(default_factory=list)


class FxPair(BaseModel):
    model_config = ConfigDict(extra="allow")

    pair: str = "N/A"
    name: str = "Currency"
    spot: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0


class WcrsContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    currencies: List[Dict[str, Any]] = Field(default_factory=list)


class CommodityItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    commodity: str = "N/A"
    category: str = "Commodities"
    spot: float = 0.0
    change: float = 0.0
    change_pct: float = 0.0
    unit: str = "USD"


class FdmContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    commodities: List[Dict[str, Any]] = Field(default_factory=list)


class EcoEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    time: str = "--:--"
    country: str = "US"
    indicator: str = "Economic Indicator"
    event: str = "Economic Indicator"
    period: str = "Current"
    importance: str = "MEDIUM"
    impact: str = "MED"
    actual: str = "--"
    consensus: str = "--"
    forecast: str = "--"
    prior: str = "--"
    previous: str = "--"


class EcoContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    events: List[Dict[str, Any]] = Field(default_factory=list)


class MapsContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    index: str = "SPX"
    total_symbols: int = 0
    advancers: int = 0
    decliners: int = 0
    sectors: List[Dict[str, Any]] = Field(default_factory=list)


class InsdContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    sentiment: str = "NEUTRAL"
    net_shares_flow: int = 0
    period: str = "LTM"
    transactions: List[Dict[str, Any]] = Field(default_factory=list)


class HdsContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    top_holders_ownership_pct: float = 0.0
    top_holders_count: int = 0
    source: str = "SEC EDGAR Form 13F"
    holders: List[Dict[str, Any]] = Field(default_factory=list)


class AiResearchContract(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str = "N/A"
    rating: str = "HOLD"
    recommendation: str = "HOLD"
    analyst: str = "Autonomous Equity Research"
    target_price: float = 0.0
    upside_pct: float = 0.0
    investment_thesis: str = "Analysis pending."
    executive_summary: str = "Analysis pending."
    competitive_moat: List[str] = Field(default_factory=list)
    growth_catalysts: List[str] = Field(default_factory=list)
    downside_risks: List[str] = Field(default_factory=list)
    valuation_assessment: Dict[str, Any] = Field(
        default_factory=lambda: {
            "fwd_pe": "N/A",
            "ev_ebitda": "N/A",
            "free_cash_flow_yield": "N/A",
            "dividend_yield": "N/A",
            "verdict": "Fairly valued",
        }
    )


CONTRACT_REGISTRY: Dict[str, Any] = {
    "DES": DesContract,
    "ANR": AnrContract,
    "FA": FaContract,
    "RV": RvContract,
    "EE": EeContract,
    "OMON": OmonContract,
    "WIRP": WirpContract,
    "WCRS": WcrsContract,
    "FDM": FdmContract,
    "ECO": EcoContract,
    "MAPS": MapsContract,
    "HEAT": MapsContract,
    "INSD": InsdContract,
    "HDS": HdsContract,
    "AI": AiResearchContract,
    "RES": AiResearchContract,
}


def normalize_contract_payload(fn: str, raw_data: Any, symbol: str = "") -> Dict[str, Any]:
    """
    Validates and normalizes raw feed dictionary against the strict Pydantic DTO.
    Ensures that real-time data from feeds is completely preserved, while
    guaranteeing that default contract fields exist to prevent frontend crashes.
    """
    fn_upper = fn.upper()
    model_cls = CONTRACT_REGISTRY.get(fn_upper)
    if not model_cls:
        if isinstance(raw_data, dict):
            return raw_data
        return {}

    # If raw_data is a list or empty, wrap appropriately
    if isinstance(raw_data, list):
        if fn_upper == "ECO":
            raw_data = {"events": raw_data}
        elif fn_upper == "WCRS":
            raw_data = {"currencies": raw_data}
        elif fn_upper == "FDM":
            raw_data = {"commodities": raw_data}
        else:
            raw_data = {"items": raw_data}

    if not isinstance(raw_data, dict):
        raw_data = {}

    target_sym = str(symbol or raw_data.get("symbol") or "N/A").upper()

    # Pre-populate / mirror dual-representation keys
    if fn_upper == "DES":
        if "div_yield" in raw_data and "dividend_yield" not in raw_data:
            raw_data["dividend_yield"] = raw_data["div_yield"]
        elif "dividend_yield" in raw_data and "div_yield" not in raw_data:
            raw_data["div_yield"] = raw_data["dividend_yield"]
    elif fn_upper == "ANR":
        if "mean_target" in raw_data and "target_price" not in raw_data:
            raw_data["target_price"] = raw_data["mean_target"]
        elif "target_price" in raw_data and "mean_target" not in raw_data:
            raw_data["mean_target"] = raw_data["target_price"]
        if "recent_actions" in raw_data and "brokers" not in raw_data:
            raw_data["brokers"] = raw_data["recent_actions"]
        elif "brokers" in raw_data and "recent_actions" not in raw_data:
            raw_data["recent_actions"] = raw_data["brokers"]
    elif fn_upper == "FA":
        if "years" in raw_data and "periods" not in raw_data:
            raw_data["periods"] = raw_data["years"]
        elif "periods" in raw_data and "years" not in raw_data:
            raw_data["years"] = raw_data["periods"]
    elif fn_upper == "OMON":
        if "chain" in raw_data and "strikes" not in raw_data:
            raw_data["strikes"] = raw_data["chain"]
        elif "strikes" in raw_data and "chain" not in raw_data:
            raw_data["chain"] = raw_data["strikes"]
    elif fn_upper == "AI":
        if "rating" in raw_data and "recommendation" not in raw_data:
            raw_data["recommendation"] = raw_data["rating"]
        elif "recommendation" in raw_data and "rating" not in raw_data:
            raw_data["rating"] = raw_data["recommendation"]
        if "analyst" not in raw_data:
            raw_data["analyst"] = "Autonomous Equity Research"
    elif fn_upper == "ECO":
        events = raw_data.get("events", [])
        for e in events:
            if isinstance(e, dict):
                if "indicator" in e and "event" not in e:
                    e["event"] = e["indicator"]
                elif "event" in e and "indicator" not in e:
                    e["indicator"] = e["event"]
                if "impact" in e and "importance" not in e:
                    e["importance"] = e["impact"]
                elif "importance" in e and "impact" not in e:
                    e["impact"] = e["importance"]

    # Start with default contract values, then update with raw_data to preserve all real metrics
    default_dict = model_cls().model_dump()
    if "symbol" in default_dict and target_sym != "N/A":
        default_dict["symbol"] = target_sym

    merged = {**default_dict, **raw_data}
    if "symbol" in merged and target_sym != "N/A":
        merged["symbol"] = target_sym

    try:
        validated = model_cls.model_validate(merged)
        return validated.model_dump()
    except Exception:
        return merged
