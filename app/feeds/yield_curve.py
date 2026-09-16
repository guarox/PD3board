from typing import Dict, Any, List

class YieldCurveFeed:
    """
    US Treasury Yield Curve (YCRV) service providing benchmark rates
    from 1M through 30Y, along with 2Y/10Y spread and inversion detection.
    """
    def __init__(self):
        self.tenors = [
            {"tenor": "1M", "yield": 5.34, "change": -0.01},
            {"tenor": "3M", "yield": 5.18, "change": -0.02},
            {"tenor": "6M", "yield": 4.92, "change": -0.03},
            {"tenor": "1Y", "yield": 4.45, "change": -0.04},
            {"tenor": "2Y", "yield": 3.62, "change": -0.05},
            {"tenor": "3Y", "yield": 3.51, "change": -0.04},
            {"tenor": "5Y", "yield": 3.48, "change": -0.03},
            {"tenor": "7Y", "yield": 3.55, "change": -0.02},
            {"tenor": "10Y", "yield": 3.65, "change": -0.01},
            {"tenor": "20Y", "yield": 4.02, "change": 0.00},
            {"tenor": "30Y", "yield": 3.98, "change": +0.01},
        ]

    def get_curve(self) -> Dict[str, Any]:
        y2 = next(t["yield"] for t in self.tenors if t["tenor"] == "2Y")
        y10 = next(t["yield"] for t in self.tenors if t["tenor"] == "10Y")
        spread_2_10 = round((y10 - y2) * 100, 1)  # Basis points

        return {
            "curve_name": "US TREASURY BENCHMARK YIELD CURVE",
            "tenors": self.tenors,
            "y2": y2,
            "y10": y10,
            "spread_2_10_bps": spread_2_10,
            "inverted": spread_2_10 < 0
        }
