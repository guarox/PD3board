import time
from typing import Dict, Any, List

class WorldMacroFeed:
    """
    World Macro & Multi-Asset Data Provider.
    Covers:
      - WIRP: World Interest Rate Probabilities (FOMC Rate Probabilities)
      - WCRS: World Currency Ranker (G10 & Major Currencies vs USD)
      - FDM: Commodity Futures & Energy Dashboard
    """

    def __init__(self):
        pass

    def get_wirp(self) -> Dict[str, Any]:
        """
        World Interest Rate Probabilities (WIRP).
        Derived from Fed Funds Futures pricing across upcoming FOMC meetings.
        """
        return {
            "current_target_rate": "5.25% - 5.50%",
            "effective_fed_funds_rate": "5.33%",
            "calculation_date": time.strftime("%Y-%m-%d"),
            "meetings": [
                {
                    "date": "2026-09-18",
                    "days_forward": 2,
                    "implied_rate": "5.08%",
                    "prob_cut_25bp": 85.0,
                    "prob_cut_50bp": 15.0,
                    "prob_hold": 0.0,
                    "prob_hike": 0.0,
                    "bias": "EASING (25-50 BPS)"
                },
                {
                    "date": "2026-11-06",
                    "days_forward": 51,
                    "implied_rate": "4.82%",
                    "prob_cut_25bp": 68.4,
                    "prob_cut_50bp": 31.6,
                    "prob_hold": 0.0,
                    "prob_hike": 0.0,
                    "bias": "EASING (50-75 BPS CUMULATIVE)"
                },
                {
                    "date": "2026-12-18",
                    "days_forward": 93,
                    "implied_rate": "4.55%",
                    "prob_cut_25bp": 58.0,
                    "prob_cut_50bp": 42.0,
                    "prob_hold": 0.0,
                    "prob_hike": 0.0,
                    "bias": "EASING (100 BPS CUMULATIVE)"
                },
                {
                    "date": "2027-01-29",
                    "days_forward": 135,
                    "implied_rate": "4.30%",
                    "prob_cut_25bp": 52.5,
                    "prob_cut_50bp": 47.5,
                    "prob_hold": 0.0,
                    "prob_hike": 0.0,
                    "bias": "TERMINAL RATE PROJECTION"
                }
            ],
            "terminal_rate": "3.85% (Q3 2027)"
        }

    def get_wcrs(self) -> List[Dict[str, Any]]:
        """
        World Currency Ranker (WCRS).
        Ranks global currencies by intraday performance relative to USD.
        """
        currencies = [
            {"code": "JPY", "name": "Japanese Yen", "spot": 140.62, "change": -1.18, "change_pct": -0.83, "range_52w": "140.25 - 161.95", "bias": "STRONGEST (CARRY UNWIND)"},
            {"code": "GBP", "name": "British Pound", "spot": 1.3214, "change": 0.0058, "change_pct": 0.44, "range_52w": "1.2037 - 1.3266", "bias": "OUTPERFORMING"},
            {"code": "EUR", "name": "Euro Currency", "spot": 1.1128, "change": 0.0034, "change_pct": 0.31, "range_52w": "1.0448 - 1.1201", "bias": "STABLE"},
            {"code": "AUD", "name": "Australian Dollar", "spot": 0.6754, "change": 0.0019, "change_pct": 0.28, "range_52w": "0.6270 - 0.6871", "bias": "COMMODITY BID"},
            {"code": "CHF", "name": "Swiss Franc", "spot": 0.8465, "change": -0.0021, "change_pct": -0.25, "range_52w": "0.8375 - 0.9245", "bias": "SAFE HAVEN"},
            {"code": "CAD", "name": "Canadian Dollar", "spot": 1.3582, "change": 0.0012, "change_pct": 0.09, "range_52w": "1.3177 - 1.3946", "bias": "NEUTRAL"},
            {"code": "CNH", "name": "Offshore Chinese Yuan", "spot": 7.0985, "change": -0.0090, "change_pct": -0.13, "range_52w": "7.0850 - 7.3440", "bias": "CENTRAL BANK FIX"},
            {"code": "MXN", "name": "Mexican Peso", "spot": 19.2450, "change": 0.1850, "change_pct": 0.97, "range_52w": "16.2600 - 20.1500", "bias": "EM VOLATILE"}
        ]
        # Sort by performance
        return sorted(currencies, key=lambda x: x["change_pct"], reverse=True)

    def get_fdm(self) -> List[Dict[str, Any]]:
        """
        Global Commodities & Energy Matrix (FDM).
        Energy, Precious Metals, Industrial Metals, and Agriculture.
        """
        return [
            {"symbol": "CL1", "name": "WTI CRUDE OIL", "category": "ENERGY", "price": 70.18, "change": 1.14, "change_pct": 1.65, "unit": "USD/bbl"},
            {"symbol": "CO1", "name": "BRENT CRUDE", "category": "ENERGY", "price": 73.65, "change": 1.05, "change_pct": 1.45, "unit": "USD/bbl"},
            {"symbol": "NG1", "name": "NATURAL GAS", "category": "ENERGY", "price": 2.375, "change": -0.045, "change_pct": -1.86, "unit": "USD/MMBtu"},
            {"symbol": "GC1", "name": "GOLD (100 OZ)", "category": "PRECIOUS", "price": 2584.40, "change": 12.80, "change_pct": 0.50, "unit": "USD/t oz"},
            {"symbol": "SI1", "name": "SILVER (5000 OZ)", "category": "PRECIOUS", "price": 31.05, "change": 0.42, "change_pct": 1.37, "unit": "USD/t oz"},
            {"symbol": "HG1", "name": "COPPER HIGH GRADE", "category": "METALS", "price": 4.268, "change": 0.052, "change_pct": 1.23, "unit": "USD/lb"},
            {"symbol": "W1", "name": "CHICAGO WHEAT", "category": "AGRI", "price": 578.50, "change": -3.25, "change_pct": -0.56, "unit": "USd/bu"},
            {"symbol": "C1", "name": "CORN FUTURES", "category": "AGRI", "price": 412.25, "change": 1.75, "change_pct": 0.43, "unit": "USd/bu"}
        ]
