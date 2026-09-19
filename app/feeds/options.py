import logging
import math
import time
from typing import Dict, Any, List, Optional
from app.feeds.market_data_client import market_data_client

logger = logging.getLogger(__name__)

class OptionsFeed:
    """
    Options chain & Greeks engine (OMON).
    Calculates strike chains, Greeks (Delta, Gamma, Theta, Vega),
    implied volatility, and Max Pain strike using live market feeds.
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

            # Baseline implied volatility: 25% with skew (puts higher than calls)
            skew = (1.0 - moneyness) * 0.15
            iv = max(0.12, min(0.85, 0.25 + skew))

            # Black-Scholes Greeks calculation
            d1 = (math.log(spot_price / strike) + (r + 0.5 * iv ** 2) * t) / (iv * math.sqrt(t))
            d2 = d1 - iv * math.sqrt(t)

            call_delta = cls._norm_cdf(d1)
            put_delta = call_delta - 1.0

            gamma = cls._norm_pdf(d1) / (spot_price * iv * math.sqrt(t))
            vega = (spot_price * cls._norm_pdf(d1) * math.sqrt(t)) / 100.0

            # Theta (1-day decay)
            theta_term1 = -(spot_price * cls._norm_pdf(d1) * iv) / (2.0 * math.sqrt(t))
            theta_term2 = -r * strike * math.exp(-r * t) * cls._norm_cdf(d2)
            call_theta = (theta_term1 + theta_term2) / 365.0
            put_theta = (theta_term1 + r * strike * math.exp(-r * t) * cls._norm_cdf(-d2)) / 365.0

            # Synthetic pricing
            intrinsic_call = max(0.0, diff)
            intrinsic_put = max(0.0, -diff)
            time_val = spot_price * iv * math.sqrt(t) * 0.4
            call_mid = round(intrinsic_call + time_val, 2)
            put_mid = round(intrinsic_put + time_val, 2)

            call_spread = max(0.05, round(call_mid * 0.02, 2))
            put_spread = max(0.05, round(put_mid * 0.02, 2))

            # Realistic Open Interest & Volume distribution
            distance = abs(strike - base_strike) / interval
            decay = max(0.1, 1.0 - (distance * 0.15))
            call_oi = int((1250 + (hash(f"{symbol}_coi_{strike}") % 800)) * decay)
            put_oi = int((1100 + (hash(f"{symbol}_poi_{strike}") % 950)) * decay)
            call_vol = int(call_oi * (0.2 + (hash(f"{symbol}_cv_{strike}") % 30) / 100.0))
            put_vol = int(put_oi * (0.25 + (hash(f"{symbol}_pv_{strike}") % 30) / 100.0))

            total_call_oi += call_oi
            total_put_oi += put_oi
            total_call_vol += call_vol
            total_put_vol += put_vol

            is_atm = strike == base_strike

            chain.append({
                "strike": strike,
                "is_atm": is_atm,
                "iv": round(iv * 100, 1),
                "call_bid": round(max(0.01, call_mid - call_spread), 2),
                "call_ask": round(call_mid + call_spread, 2),
                "call_last": call_mid,
                "call_vol": call_vol,
                "call_oi": call_oi,
                "call_delta": round(call_delta, 3),
                "call_gamma": round(gamma, 4),
                "call_theta": round(call_theta, 3),
                "call_vega": round(vega, 3),
                "put_bid": round(max(0.01, put_mid - put_spread), 2),
                "put_ask": round(put_mid + put_spread, 2),
                "put_last": put_mid,
                "put_vol": put_vol,
                "put_oi": put_oi,
                "put_delta": round(put_delta, 3),
                "put_gamma": round(gamma, 4),
                "put_theta": round(put_theta, 3),
                "put_vega": round(vega, 3),
            })

        # Max Pain calculation: strike minimizing total option payout
        pain_values = []
        for test_strike in strikes:
            loss = 0.0
            for row in chain:
                k = row["strike"]
                if test_strike > k:
                    loss += (test_strike - k) * row["call_oi"]
                elif test_strike < k:
                    loss += (k - test_strike) * row["put_oi"]
            pain_values.append((test_strike, loss))

        max_pain = min(pain_values, key=lambda x: x[1])[0]
        pc_ratio_oi = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 1.0
        pc_ratio_vol = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else 1.0

        return {
            "symbol": symbol,
            "spot_price": spot_price,
            "dte": dte,
            "expiry": "30D Forward",
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "put_call_ratio_oi": pc_ratio_oi,
            "put_call_ratio_vol": pc_ratio_vol,
            "max_pain_strike": max_pain,
            "chain": chain
        }

    @classmethod
    async def get_options_chain_async(cls, symbol: str, spot_price: float = None) -> Dict[str, Any]:
        symbol = symbol.upper()
        live_data = await market_data_client.get_options_chain(symbol)
        if live_data and "options" in live_data and live_data["options"]:
            opt = live_data["options"][0]
            exp_date = opt.get("expirationDate", int(time.time() + 30 * 86400))
            dte = max(1, int((exp_date - time.time()) / 86400))
            t = dte / 365.0
            r = 0.0525

            calls = {c["strike"]: c for c in opt.get("calls", []) if "strike" in c}
            puts = {p["strike"]: p for p in opt.get("puts", []) if "strike" in p}
            all_strikes = sorted(list(set(calls.keys()) | set(puts.keys())))

            if all_strikes:
                curr_spot = float(spot_price) if spot_price and spot_price > 0 else (
                    float(calls[all_strikes[0]].get("strike", 100.0))
                )
                quotes = await market_data_client.get_quotes([symbol])
                if quotes:
                    curr_spot = float(quotes[0].get("regularMarketPrice", curr_spot))

                # Select 11 strikes around spot price
                closest_idx = min(range(len(all_strikes)), key=lambda i: abs(all_strikes[i] - curr_spot))
                start_idx = max(0, closest_idx - 5)
                end_idx = min(len(all_strikes), start_idx + 11)
                selected_strikes = all_strikes[start_idx:end_idx]

                chain = []
                total_call_oi = 0
                total_put_oi = 0
                total_call_vol = 0
                total_put_vol = 0

                for strike in selected_strikes:
                    c = calls.get(strike, {})
                    p = puts.get(strike, {})

                    iv = float(c.get("impliedVolatility") or p.get("impliedVolatility") or 0.25)
                    iv = max(0.05, min(2.0, iv))

                    d1 = (math.log(curr_spot / strike) + (r + 0.5 * iv ** 2) * t) / (iv * math.sqrt(t))
                    d2 = d1 - iv * math.sqrt(t)

                    call_delta = cls._norm_cdf(d1)
                    put_delta = call_delta - 1.0
                    gamma = cls._norm_pdf(d1) / (curr_spot * iv * math.sqrt(t))
                    vega = (curr_spot * cls._norm_pdf(d1) * math.sqrt(t)) / 100.0
                    theta_term1 = -(curr_spot * cls._norm_pdf(d1) * iv) / (2.0 * math.sqrt(t))
                    theta_term2 = -r * strike * math.exp(-r * t) * cls._norm_cdf(d2)
                    call_theta = (theta_term1 + theta_term2) / 365.0
                    put_theta = (theta_term1 + r * strike * math.exp(-r * t) * cls._norm_cdf(-d2)) / 365.0

                    c_oi = int(c.get("openInterest", 0) or 0)
                    p_oi = int(p.get("openInterest", 0) or 0)
                    c_vol = int(c.get("volume", 0) or 0)
                    p_vol = int(p.get("volume", 0) or 0)

                    total_call_oi += c_oi
                    total_put_oi += p_oi
                    total_call_vol += c_vol
                    total_put_vol += p_vol

                    is_atm = (strike == all_strikes[closest_idx])

                    chain.append({
                        "strike": strike,
                        "is_atm": is_atm,
                        "iv": round(iv * 100, 1),
                        "call_bid": float(c.get("bid", 0.0) or 0.0),
                        "call_ask": float(c.get("ask", 0.0) or 0.0),
                        "call_last": float(c.get("lastPrice", 0.0) or 0.0),
                        "call_vol": c_vol,
                        "call_oi": c_oi,
                        "call_delta": round(call_delta, 3),
                        "call_gamma": round(gamma, 4),
                        "call_theta": round(call_theta, 3),
                        "call_vega": round(vega, 3),
                        "put_bid": float(p.get("bid", 0.0) or 0.0),
                        "put_ask": float(p.get("ask", 0.0) or 0.0),
                        "put_last": float(p.get("lastPrice", 0.0) or 0.0),
                        "put_vol": p_vol,
                        "put_oi": p_oi,
                        "put_delta": round(put_delta, 3),
                        "put_gamma": round(gamma, 4),
                        "put_theta": round(put_theta, 3),
                        "put_vega": round(vega, 3),
                    })

                pain_values = []
                for test_strike in selected_strikes:
                    loss = sum((test_strike - r_item["strike"]) * r_item["call_oi"] for r_item in chain if test_strike > r_item["strike"])
                    loss += sum((r_item["strike"] - test_strike) * r_item["put_oi"] for r_item in chain if test_strike < r_item["strike"])
                    pain_values.append((test_strike, loss))

                max_pain = min(pain_values, key=lambda x: x[1])[0] if pain_values else curr_spot
                pc_ratio_oi = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 1.0
                pc_ratio_vol = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else 1.0

                return {
                    "symbol": symbol,
                    "spot_price": round(curr_spot, 2),
                    "dte": dte,
                    "expiry": time.strftime("%Y-%m-%d", time.gmtime(exp_date)),
                    "total_call_oi": total_call_oi,
                    "total_put_oi": total_put_oi,
                    "put_call_ratio_oi": pc_ratio_oi,
                    "put_call_ratio_vol": pc_ratio_vol,
                    "max_pain_strike": max_pain,
                    "chain": chain
                }

        return cls.get_options_chain(symbol, spot_price)

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Standard normal cumulative distribution function."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    @staticmethod
    def _norm_pdf(x: float) -> float:
        """Standard normal probability density function."""
        return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x ** 2)

options_feed = OptionsFeed()
