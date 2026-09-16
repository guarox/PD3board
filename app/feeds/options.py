import math
from typing import Dict, Any, List

class OptionsFeed:
    """
    Options chain & Greeks engine (OMON).
    Calculates strike chains, Greeks (Delta, Gamma, Theta, Vega),
    implied volatility, and Max Pain strike.
    """

    DEFAULT_PRICES = {
        "SPX": 5880.0,
        "NDX": 20250.0,
        "AAPL": 228.5,
        "NVDA": 124.0,
        "MSFT": 432.0,
        "AMZN": 186.0,
        "GOOGL": 162.0,
        "META": 512.0,
        "TSLA": 235.0,
        "MCD": 295.0,
    }

    @classmethod
    def get_options_chain(cls, symbol: str, spot_price: float = None) -> Dict[str, Any]:
        symbol = symbol.upper()
        if spot_price is None or spot_price <= 0:
            spot_price = cls.DEFAULT_PRICES.get(symbol, 100.0)
        # Round spot price to nearest dollar for strike baseline
        base_strike = round(spot_price)
        
        # Determine strike interval based on price magnitude
        if spot_price > 1000:
            interval = 50.0
        elif spot_price > 500:
            interval = 25.0
        elif spot_price > 100:
            interval = 5.0
        elif spot_price > 25:
            interval = 2.5
        else:
            interval = 1.0

        # Generate 11 strikes centered around ATM
        strikes = [round(base_strike + (i * interval), 2) for i in range(-5, 6)]
        
        chain = []
        total_call_oi = 0
        total_put_oi = 0
        total_call_vol = 0
        total_put_vol = 0

        # Expiry: 30 days DTE baseline (T = 30/365)
        dte = 30
        t = dte / 365.0
        r = 0.0525  # 5.25% risk-free rate

        for strike in strikes:
            moneyness = spot_price / strike
            diff = spot_price - strike
            
            # Implied Volatility skew (smile)
            iv = 0.22 + 0.15 * ((strike - spot_price) / spot_price) ** 2
            iv = max(0.12, min(0.65, iv))

            # Approximation for d1 and d2
            sig_sqrt_t = iv * math.sqrt(t)
            d1 = (math.log(spot_price / strike) + (r + 0.5 * iv * iv) * t) / sig_sqrt_t
            d2 = d1 - sig_sqrt_t

            # Standard normal CDF approx
            norm_cdf_d1 = 0.5 * (1.0 + math.erf(d1 / math.sqrt(2.0)))
            norm_cdf_d2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2.0)))
            norm_pdf_d1 = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * d1 * d1)

            # Call Greeks & Pricing
            call_delta = round(norm_cdf_d1, 3)
            call_gamma = round(norm_pdf_d1 / (spot_price * sig_sqrt_t), 4)
            call_vega = round((spot_price * norm_pdf_d1 * math.sqrt(t)) / 100.0, 3)
            call_theta = round((-(spot_price * norm_pdf_d1 * iv) / (2.0 * math.sqrt(t)) - r * strike * math.exp(-r * t) * norm_cdf_d2) / 365.0, 3)
            
            call_intrinsic = max(0.0, diff)
            call_extrinsic = max(0.15, spot_price * 0.04 * (1.0 - abs(1.0 - moneyness)))
            call_last = round(call_intrinsic + call_extrinsic, 2)
            call_bid = round(max(0.01, call_last - 0.08), 2)
            call_ask = round(call_last + 0.08, 2)

            # Put Greeks & Pricing
            put_delta = round(call_delta - 1.0, 3)
            put_gamma = call_gamma
            put_vega = call_vega
            put_theta = round((-(spot_price * norm_pdf_d1 * iv) / (2.0 * math.sqrt(t)) + r * strike * math.exp(-r * t) * (1.0 - norm_cdf_d2)) / 365.0, 3)

            put_intrinsic = max(0.0, -diff)
            put_extrinsic = call_extrinsic
            put_last = round(put_intrinsic + put_extrinsic, 2)
            put_bid = round(max(0.01, put_last - 0.08), 2)
            put_ask = round(put_last + 0.08, 2)

            # Synthetic volume & Open Interest with peak at ATM/near-OTM
            dist_factor = math.exp(-0.5 * (((strike - spot_price) / (2 * interval)) ** 2))
            call_oi = int(1200 + 4500 * dist_factor)
            put_oi = int(900 + 3800 * dist_factor)
            call_vol = int(call_oi * 0.35)
            put_vol = int(put_oi * 0.32)

            total_call_oi += call_oi
            total_put_oi += put_oi
            total_call_vol += call_vol
            total_put_vol += put_vol

            chain.append({
                "strike": strike,
                "is_atm": (strike == base_strike),
                "is_max_pain": False,
                "call_bid": call_bid,
                "call_ask": call_ask,
                "call_last": call_last,
                "call_vol": call_vol,
                "call_oi": call_oi,
                "call_iv": round(iv, 3),
                "call_delta": call_delta,
                "call_gamma": call_gamma,
                "call_theta": call_theta,
                "call_vega": call_vega,
                "put_bid": put_bid,
                "put_ask": put_ask,
                "put_last": put_last,
                "put_vol": put_vol,
                "put_oi": put_oi,
                "put_iv": round(iv + 0.01, 3),
                "put_delta": put_delta,
                "put_gamma": put_gamma,
                "put_theta": put_theta,
                "put_vega": put_vega,
                "call": {
                    "bid": call_bid,
                    "ask": call_ask,
                    "last": call_last,
                    "volume": call_vol,
                    "oi": call_oi,
                    "iv": round(iv * 100, 1),
                    "delta": call_delta,
                    "gamma": call_gamma,
                    "theta": call_theta,
                    "vega": call_vega
                },
                "put": {
                    "bid": put_bid,
                    "ask": put_ask,
                    "last": put_last,
                    "volume": put_vol,
                    "oi": put_oi,
                    "iv": round((iv + 0.01) * 100, 1),
                    "delta": put_delta,
                    "gamma": put_gamma,
                    "theta": put_theta,
                    "vega": put_vega
                }
            })

        # Calculate Max Pain Strike (strike with minimum cash payout to option buyers)
        pain_values = {}
        for test_strike in strikes:
            call_loss = sum(c["call"]["oi"] * max(0.0, test_strike - c["strike"]) for c in chain)
            put_loss = sum(c["put"]["oi"] * max(0.0, c["strike"] - test_strike) for c in chain)
            pain_values[test_strike] = call_loss + put_loss

        max_pain_strike = min(pain_values, key=pain_values.get) if pain_values else base_strike
        for c in chain:
            if c["strike"] == max_pain_strike:
                c["is_max_pain"] = True

        pc_ratio_oi = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 1.0
        pc_ratio_vol = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else 1.0

        return {
            "symbol": symbol,
            "spot_price": spot_price,
            "dte": dte,
            "atm_iv": 0.22,
            "expiration": "2026-10-16",
            "expirations_available": ["2026-09-18 (2 DTE)", "2026-10-16 (30 DTE)", "2026-11-20 (65 DTE)", "2027-01-15 (121 DTE)"],
            "max_pain": max_pain_strike,
            "max_pain_strike": max_pain_strike,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "put_call_ratio_oi": pc_ratio_oi,
            "put_call_ratio_vol": pc_ratio_vol,
            "chain": chain
        }
