import os

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DEFAULT_CRYPTO = os.getenv("DEFAULT_CRYPTO", "BTCUSDT")
    DEFAULT_EQUITY = os.getenv("DEFAULT_EQUITY", "AAPL")
    BINANCE_WS_URL = "wss://stream.binance.com:9443/ws"
    MAX_TICKS_BUFFER = 500
    MAX_ORDERBOOK_DEPTH = 20
