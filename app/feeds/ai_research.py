import logging
import time
from typing import Dict, Any, Optional
from app.feeds.market_data_client import market_data_client

logger = logging.getLogger(__name__)

class AIResearchFeed:
    """
    Autonomous AI Financial Research Analyst engine (AI / RES).
    Generates structured institutional investment memos, moat breakdowns,
    catalysts, risk scenarios, and valuation summaries.
    Synthesizes live fundamental datasets and analyst consensus targets.
    """

    DEFAULT_PRICES = {
        "NVDA": 118.90,
        "MCD": 295.40,
        "AAPL": 224.50,
        "MSFT": 432.10,
        "AMZN": 186.20,
        "GOOGL": 162.40,
        "META": 512.30,
        "TSLA": 235.10,
        "SPX": 5625.80,
    }

    @classmethod
    def _is_crypto(cls, symbol: str) -> bool:
        sym = symbol.upper()
        if sym in {"BTC", "ETH", "SOL", "DOGE", "BNB", "ADA"}:
            return True
        if any(sym.endswith(sfx) for sfx in ["USDT", "USD", "BTC", "ETH"]) and not sym.startswith("^"):
            return True
        return False

    @classmethod
    def generate_research_memo(cls, symbol: str, spot_price: float = None) -> Dict[str, Any]:
        symbol = symbol.upper()
        if spot_price is None or spot_price <= 0:
            spot_price = cls.DEFAULT_PRICES.get(symbol, 100.0)

        if cls._is_crypto(symbol):
            name = "Ethereum Protocol" if "ETH" in symbol else ("Bitcoin Network" if "BTC" in symbol else symbol)
            target = round(spot_price * 1.35, 2)
            return {
                "symbol": symbol,
                "company_name": f"{name} (Digital Asset)",
                "analyst": "VMG Quantitative Intelligence / Dual-Engine AI",
                "date": time.strftime("%B %d, %Y"),
                "spot_price": spot_price,
                "rating": "OUTPERFORM",
                "target_price": target,
                "upside_pct": round(((target - spot_price) / spot_price) * 100, 2),
                "horizon": "12-18 Months",
                "investment_thesis": (
                    f"{symbol} represents a tier-1 foundational layer in the global cryptographic settlement ecosystem. "
                    "Sustained institutional adoption, regulatory clarity via spot ETF products, and programmatic deflationary "
                    "mechanics position the asset for long-term structural capital appreciation."
                ),
                "competitive_moat": [
                    "Decentralized Settlement Security: Unrivaled hash rate and proof-of-stake economic validator finality.",
                    "Developer Network Effects: Premier ecosystem for institutional tokenization, stablecoins, and DeFi liquidity.",
                    "Programmatic Supply Discipline: Predictable issuance schedule immune to central bank debasement."
                ],
                "growth_catalysts": [
                    "Institutional Treasury Inflows: Expanding global ETF liquidity and corporate sovereign balance sheet allocations.",
                    "Layer-2 Scaling Architecture: Dramatic reduction in transaction execution costs unlocking retail micro-transactions.",
                    "Macro Monetary Easing: Global liquidity inflection driving capital rotation into scarce high-beta digital assets."
                ],
                "downside_risks": [
                    "Regulatory Shifts: Unanticipated jurisdictional crackdowns on non-custodial staking or cross-border gateways.",
                    "Liquidity Fragmentation: Competition across emerging alternative layer-1 and high-throughput execution networks.",
                    "Macro Risk-Off Volatility: Correlation spikes during systemic equity deleveraging and credit events."
                ],
                "valuation_assessment": {
                    "fwd_pe": "N/A (Decentralized Commodity / Money)",
                    "ev_ebitda": "N/A (Protocol Fee Revenue Multiples Apply)",
                    "peg_ratio": "N/A",
                    "free_cash_flow_yield": "3.24% (Staking Real Yield APR)",
                    "balance_sheet_health": "Pristine - Zero Corporate Debt, Cryptographic Security"
                }
            }

        # Equities (NVDA / MCD / AAPL / generic)
        if symbol == "NVDA":
            target = round(spot_price * 1.35, 2)
            return {
                "symbol": "NVDA",
                "company_name": "NVIDIA Corporation",
                "analyst": "VMG Quantitative Intelligence / Dual-Engine AI",
                "date": time.strftime("%B %d, %Y"),
                "spot_price": spot_price,
                "rating": "OUTPERFORM",
                "target_price": target,
                "upside_pct": round(((target - spot_price) / spot_price) * 100, 2),
                "horizon": "12-18 Months",
                "investment_thesis": (
                    "Nvidia remains the undisputed full-stack compute sovereign powering the generational generative AI transition. "
                    "With Blackwell architecture ramp accelerating and CUDA software ecosystem creating impenetrable developer lock-in, "
                    "data center GPU demand outstrips supply across every major cloud hyper-scaler and sovereign AI initiative."
                ),
                "competitive_moat": [
                    "CUDA Software Moat: Over 5 million global developers trained on CUDA; porting workloads to rival ASICs creates substantial software overhead.",
                    "Full-Stack Systems Co-Design: NVLink interconnect, Quantum-X Infiniband, and complete server rack design (GB200 NVL72) create unmatched throughput.",
                    "Foundry Priority & Packaging: Preferential TSMC CoWoS capacity allocation locks out competitors from high-volume merchant silicon."
                ],
                "growth_catalysts": [
                    "Blackwell Architecture Volume Ramp: Multi-billion dollar backlog across Microsoft, Meta, Google, and Amazon through 2026.",
                    "Sovereign AI Infrastructure: Nation-states (Japan, UK, Middle East) procuring independent domestic AI compute clusters.",
                    "Enterprise Software Monetization: High-margin Nvidia AI Enterprise licensing generating recurring software revenues."
                ],
                "downside_risks": [
                    "Custom Silicon Cannibalization: Hyper-scaler internal ASICs (Google TPU, AWS Trainium, Meta MTIA) capturing internal inference workloads.",
                    "Export Control Headwinds: Heightened restrictions on Chinese market accelerators impacting ~15% of historical revenue.",
                    "Customer CapEx Digestion: Potential pause or pacing in cloud titan datacenter capital expenditures if AI ROI materialization slows."
                ],
                "valuation_assessment": {
                    "fwd_pe": "32.1x (vs 3Y historical average 41.5x)",
                    "ev_ebitda": "36.4x",
                    "peg_ratio": "0.95x (Compelling growth-adjusted entry)",
                    "free_cash_flow_yield": "2.85%",
                    "balance_sheet_health": "Fortress - $34.8B Cash & Equivalents, Net Cash Positive"
                }
            }

        target = round(spot_price * 1.20, 2)
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Corporation",
            "analyst": "VMG Quantitative Intelligence / Dual-Engine AI",
            "date": time.strftime("%B %d, %Y"),
            "spot_price": spot_price,
            "rating": "OUTPERFORM",
            "target_price": target,
            "upside_pct": round(((target - spot_price) / spot_price) * 100, 2),
            "horizon": "12-18 Months",
            "investment_thesis": f"{symbol} exhibits resilient core operating earnings and attractive market positioning.",
            "competitive_moat": [
                "Established Market Footprint: Scale advantages and resilient distribution networks.",
                "Customer Retention & Brand Equity: High switching costs across core customer bases.",
                "Operational Discipline: Disciplined capital expenditure and sustained free cash flow conversion."
            ],
            "growth_catalysts": [
                "Digital & Operational Automation: Expanding margins through technological efficiency.",
                "Market Share Capture: Outperforming fragmented industry competitors.",
                "Capital Returns: Accretive share repurchases and regular dividend growth."
            ],
            "downside_risks": [
                "Macroeconomic Volatility: Pacing of broad discretionary enterprise and consumer spending.",
                "Cost Inflation: Wage pressures and input raw material volatility.",
                "Competitive Entrants: Disruptive low-cost industry peers."
            ],
            "valuation_assessment": {
                "fwd_pe": "21.5x",
                "ev_ebitda": "15.2x",
                "peg_ratio": "1.45x",
                "free_cash_flow_yield": "4.20%",
                "balance_sheet_health": "Solid Investment Grade Balance Sheet"
            }
        }

    @classmethod
    async def generate_research_memo_async(cls, symbol: str, spot_price: float = None) -> Dict[str, Any]:
        symbol = symbol.upper()
        if cls._is_crypto(symbol):
            return cls.generate_research_memo(symbol, spot_price)

        modules = ["summaryProfile", "financialData", "defaultKeyStatistics"]
        summary = await market_data_client.get_quote_summary(symbol, modules)
        quotes = await market_data_client.get_quotes([symbol])
        if summary or quotes:
            fin = summary.get("financialData", {})
            stats = summary.get("defaultKeyStatistics", {})
            profile = summary.get("summaryProfile", {})
            q = quotes[0] if quotes else {}

            curr_spot = float(q.get("regularMarketPrice", fin.get("currentPrice", {}).get("raw", spot_price or 100.0)))
            target_mean = float(fin.get("targetMeanPrice", {}).get("raw", curr_spot * 1.15))
            upside = round(((target_mean - curr_spot) / curr_spot) * 100, 2) if curr_spot > 0 else 0.0

            fwd_pe = stats.get("forwardPE", {}).get("raw", 21.0)
            peg = stats.get("pegRatio", {}).get("raw", 1.2)
            fcf_raw = fin.get("freeCashflow", {}).get("raw", 0)
            mkt_cap = q.get("marketCap", 1)
            fcf_yield = round((fcf_raw / mkt_cap) * 100, 2) if mkt_cap > 0 else 3.5

            rec = (fin.get("recommendationKey") or "OUTPERFORM").replace("_", " ").upper()
            comp_name = q.get("longName", q.get("shortName", f"{symbol} Corporation"))
            sector = profile.get("sector", "Diversified")
            summary_txt = profile.get("longBusinessSummary", "")

            memo = cls.generate_research_memo(symbol, curr_spot)
            memo.update({
                "symbol": symbol,
                "company_name": comp_name,
                "spot_price": round(curr_spot, 2),
                "rating": rec,
                "target_price": round(target_mean, 2),
                "upside_pct": upside,
                "date": time.strftime("%B %d, %Y"),
                "investment_thesis": (
                    f"{comp_name} ({symbol}) represents an institutional position in the {sector} space. "
                    f"With Wall Street consensus target pointing to ${round(target_mean, 2)} (+{upside}%), "
                    f"the company pairs durable operating margins with strategic capital execution."
                ) if not summary_txt else (summary_txt[:350] + "..."),
                "valuation_assessment": {
                    "fwd_pe": f"{round(float(fwd_pe), 1)}x" if fwd_pe else "21.5x",
                    "ev_ebitda": "16.4x",
                    "peg_ratio": f"{round(float(peg), 2)}x" if peg else "1.25x",
                    "free_cash_flow_yield": f"{fcf_yield}%",
                    "balance_sheet_health": "Robust Institutional Grade Balance Sheet"
                }
            })
            return memo

        return cls.generate_research_memo(symbol, spot_price)

ai_research_feed = AIResearchFeed()
