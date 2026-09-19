import re
from typing import Dict, Any, Optional

SECTORS = {"EQUITY", "CRNCY", "INDEX", "GOVT", "CMDTY"}
FUNCTIONS = {
    "GP", "GIP", "L2", "DES", "WEI", "TOP", "YCRV", "ECO", "HELP",
    "ANR", "FA", "RV", "EE", "WIRP", "WCRS", "FDM",
    "OMON", "MAPS", "HEAT", "AI", "RES", "INSD", "HDS"
}

# Aliases
FUNCTION_ALIASES = {
    "HEAT": "MAPS",
    "RES": "AI"
}

class CommandParser:
    """
    Parses Bloomberg-style terminal commands:
    Pattern: <TICKER> [SECTOR] [FUNCTION] <GO>
    Or standalone functions: <FUNCTION> <GO>
    Or prefix functions: <FUNCTION> <TICKER> <GO>
    """

    @staticmethod
    def parse(raw_command: str) -> Dict[str, Any]:
        if not raw_command:
            return {"valid": False, "error": "Empty command"}

        # Strip whitespace, uppercase, and remove optional trailing <GO> or GO
        clean = raw_command.strip().upper()
        clean = re.sub(r"<\s*GO\s*>$", "", clean).strip()
        clean = re.sub(r"\s+GO$", "", clean).strip()

        tokens = clean.split()
        if not tokens:
            return {"valid": False, "error": "No tokens found"}

        # Check for standalone functions (e.g. WEI, TOP, YCRV, ECO, HELP, MAPS, HEAT, WIRP, WCRS, FDM)
        if len(tokens) == 1 and tokens[0] in FUNCTIONS:
            fn = tokens[0]
            fn = FUNCTION_ALIASES.get(fn, fn)
            return {
                "valid": True,
                "ticker": None,
                "sector": None,
                "function": fn,
                "raw": raw_command
            }

        # Check for prefix function syntax (e.g. "FA AAPL", "DES ETHUSDT", "OMON NVDA")
        if len(tokens) >= 2 and tokens[0] in FUNCTIONS and tokens[1] not in FUNCTIONS and tokens[1] not in SECTORS:
            fn = FUNCTION_ALIASES.get(tokens[0], tokens[0])
            ticker = tokens[1]
            sector = None
            if len(tokens) >= 3 and tokens[2] in SECTORS:
                sector = tokens[2]

            if not sector:
                if ticker in {"SPX", "NDX", "DJI", "VIX", "RUT"}:
                    sector = "INDEX"
                elif any(c in ticker for c in ["USDT", "BTC", "ETH", "SOL", "USD"]):
                    sector = "CRNCY"
                elif ticker.startswith("US") and ticker.endswith("Y"):
                    sector = "GOVT"
                else:
                    sector = "EQUITY"

            return {
                "valid": True,
                "ticker": ticker,
                "sector": sector,
                "function": fn,
                "raw": raw_command
            }

        ticker = tokens[0]
        sector = None
        function = "GP"  # Default function is Price Graph

        # Inspect remaining tokens
        for token in tokens[1:]:
            if token in SECTORS:
                sector = token
            elif token in FUNCTIONS:
                function = FUNCTION_ALIASES.get(token, token)

        # Infer sector if omitted
        if not sector:
            if ticker in {"SPX", "NDX", "DJI", "VIX", "RUT"}:
                sector = "INDEX"
            elif any(c in ticker for c in ["USDT", "BTC", "ETH", "SOL", "USD"]):
                sector = "CRNCY"
            elif ticker.startswith("US") and ticker.endswith("Y"):
                sector = "GOVT"
            else:
                sector = "EQUITY"

        return {
            "valid": True,
            "ticker": ticker,
            "sector": sector,
            "function": function,
            "raw": raw_command
        }
