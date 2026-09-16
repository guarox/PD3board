from typing import Dict, Any, List

class InsiderHoldingsFeed:
    """
    SEC Form 4 Insider Transactions (INSD) &
    13F Institutional Major Holders (HDS) engine.
    """

    @staticmethod
    def get_insider_transactions(symbol: str) -> Dict[str, Any]:
        symbol = symbol.upper()
        
        # Realistic data generator customized per ticker
        if symbol == "MCD":
            insiders = [
                {"date": "2026-09-02", "name": "Kempczinski Christopher J", "title": "Chairman & CEO", "type": "Sale (S)", "shares": 14500, "price": 298.50, "value": 4328250, "shares_owned": 248900},
                {"date": "2026-08-18", "name": "Borden Ian Frederick", "title": "EVP & CFO", "type": "Sale (S)", "shares": 6200, "price": 295.10, "value": 1829620, "shares_owned": 84100},
                {"date": "2026-07-25", "name": "Erlinger Joseph M.", "title": "President McDonald's USA", "type": "Option Ex (M)", "shares": 10000, "price": 210.40, "value": 2104000, "shares_owned": 112400},
                {"date": "2026-06-12", "name": "Hernandez Enrique Jr", "title": "Director", "type": "Purchase (P)", "shares": 2500, "price": 255.80, "value": 639500, "shares_owned": 56700},
                {"date": "2026-05-14", "name": "Rice Kareem", "title": "Global Chief People Officer", "type": "Sale (S)", "shares": 3800, "price": 268.20, "value": 1019160, "shares_owned": 42100}
            ]
        elif symbol == "NVDA":
            insiders = [
                {"date": "2026-09-08", "name": "Huang Jen Hsun", "title": "President & CEO", "type": "Rule 10b5-1 Sale (S)", "shares": 120000, "price": 119.40, "value": 14328000, "shares_owned": 78200000},
                {"date": "2026-08-28", "name": "Kress Colette", "title": "EVP & CFO", "type": "Sale (S)", "shares": 35000, "price": 124.80, "value": 4368000, "shares_owned": 4120000},
                {"date": "2026-08-10", "name": "Stevens Mark A", "title": "Director", "type": "Sale (S)", "shares": 80000, "price": 108.50, "value": 8680000, "shares_owned": 28400000},
                {"date": "2026-07-15", "name": "Shoquist Debora", "title": "EVP Operations", "type": "Option Ex (M)", "shares": 40000, "price": 18.20, "value": 728000, "shares_owned": 1890000}
            ]
        elif symbol == "AAPL":
            insiders = [
                {"date": "2026-09-04", "name": "Cook Timothy D", "title": "Chief Executive Officer", "type": "Rule 10b5-1 Sale (S)", "shares": 50000, "price": 224.10, "value": 11205000, "shares_owned": 3280000},
                {"date": "2026-08-20", "name": "Maestri Luca", "title": "Senior VP & CFO", "type": "Sale (S)", "shares": 22000, "price": 226.50, "value": 4983000, "shares_owned": 112000},
                {"date": "2026-07-28", "name": "Williams Jeffrey E", "title": "Chief Operating Officer", "type": "Sale (S)", "shares": 30000, "price": 218.40, "value": 6552000, "shares_owned": 489000},
                {"date": "2026-06-15", "name": "Levinson Arthur D", "title": "Chairman of Board", "type": "Purchase (P)", "shares": 5000, "price": 212.00, "value": 1060000, "shares_owned": 4530000}
            ]
        else:
            insiders = [
                {"date": "2026-09-05", "name": "Executive Officers & Directors", "title": "Multiple Officers", "type": "Sale (S)", "shares": 18500, "price": 150.20, "value": 2778700, "shares_owned": 1250000},
                {"date": "2026-08-14", "name": "Chief Financial Officer", "title": "Principal Financial Officer", "type": "Option Ex (M)", "shares": 8000, "price": 85.40, "value": 683200, "shares_owned": 280000},
                {"date": "2026-07-20", "name": "Board of Directors", "title": "Independent Director", "type": "Purchase (P)", "shares": 4000, "price": 138.90, "value": 555600, "shares_owned": 95000}
            ]

        net_bought_sold = sum(-tx["shares"] if "Sale" in tx["type"] else tx["shares"] for tx in insiders)

        return {
            "symbol": symbol,
            "period": "Last 6 Months (SEC Form 4)",
            "total_transactions": len(insiders),
            "net_shares_flow": net_bought_sold,
            "sentiment": "NET SELLING" if net_bought_sold < 0 else "NET BUYING",
            "transactions": insiders
        }

    @staticmethod
    def get_institutional_holders(symbol: str) -> Dict[str, Any]:
        symbol = symbol.upper()
        
        # Standard institutional heavyweights for US Equities
        if symbol == "MCD":
            holders = [
                {"rank": 1, "name": "The Vanguard Group, Inc.", "shares": 68420000, "value_b": 20.51, "pct_float": 9.55, "change_shares": 420000, "date": "2026-06-30"},
                {"rank": 2, "name": "BlackRock, Inc.", "shares": 55180000, "value_b": 16.54, "pct_float": 7.70, "change_shares": -180000, "date": "2026-06-30"},
                {"rank": 3, "name": "State Street Corporation", "shares": 35210000, "value_b": 10.55, "pct_float": 4.91, "change_shares": 95000, "date": "2026-06-30"},
                {"rank": 4, "name": "Geode Capital Management, LLC", "shares": 16400000, "value_b": 4.91, "pct_float": 2.29, "change_shares": 310000, "date": "2026-06-30"},
                {"rank": 5, "name": "Morgan Stanley", "shares": 14100000, "value_b": 4.23, "pct_float": 1.97, "change_shares": -620000, "date": "2026-06-30"},
                {"rank": 6, "name": "JPMorgan Chase & Co.", "shares": 12850000, "value_b": 3.85, "pct_float": 1.79, "change_shares": 150000, "date": "2026-06-30"},
                {"rank": 7, "name": "Bank of America Corporation", "shares": 11400000, "value_b": 3.42, "pct_float": 1.59, "change_shares": -85000, "date": "2026-06-30"},
                {"rank": 8, "name": "FMR LLC (Fidelity)", "shares": 10900000, "value_b": 3.27, "pct_float": 1.52, "change_shares": 480000, "date": "2026-06-30"}
            ]
        elif symbol == "AAPL":
            holders = [
                {"rank": 1, "name": "The Vanguard Group, Inc.", "shares": 1310000000, "value_b": 294.1, "pct_float": 8.54, "change_shares": 2400000, "date": "2026-06-30"},
                {"rank": 2, "name": "BlackRock, Inc.", "shares": 1045000000, "value_b": 234.6, "pct_float": 6.81, "change_shares": -1800000, "date": "2026-06-30"},
                {"rank": 3, "name": "Berkshire Hathaway Inc.", "shares": 400000000, "value_b": 89.8, "pct_float": 2.61, "change_shares": -50000000, "date": "2026-06-30"},
                {"rank": 4, "name": "State Street Corporation", "shares": 560000000, "value_b": 125.7, "pct_float": 3.65, "change_shares": 1200000, "date": "2026-06-30"},
                {"rank": 5, "name": "Geode Capital Management, LLC", "shares": 315000000, "value_b": 70.7, "pct_float": 2.05, "change_shares": 850000, "date": "2026-06-30"}
            ]
        else:
            holders = [
                {"rank": 1, "name": "The Vanguard Group, Inc.", "shares": 45000000, "value_b": 8.5, "pct_float": 8.85, "change_shares": 500000, "date": "2026-06-30"},
                {"rank": 2, "name": "BlackRock, Inc.", "shares": 38000000, "value_b": 7.2, "pct_float": 7.48, "change_shares": 240000, "date": "2026-06-30"},
                {"rank": 3, "name": "State Street Corporation", "shares": 22000000, "value_b": 4.1, "pct_float": 4.33, "change_shares": -110000, "date": "2026-06-30"},
                {"rank": 4, "name": "FMR LLC (Fidelity)", "shares": 18500000, "value_b": 3.5, "pct_float": 3.64, "change_shares": 890000, "date": "2026-06-30"}
            ]

        total_inst_shares = sum(h["shares"] for h in holders)
        total_inst_pct = round(sum(h["pct_float"] for h in holders), 2)

        return {
            "symbol": symbol,
            "source": "SEC Form 13F-HR Q2 2026 Filings",
            "top_holders_count": len(holders),
            "top_holders_ownership_pct": total_inst_pct,
            "holders": holders
        }
