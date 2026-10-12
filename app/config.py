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
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://langfuse-web.apps.svc.cluster.local:3000")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-51aafcd7-eb78-43ec-9a61-91c6ae2a8f6c")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-cd2590d4-2d1e-48cf-b3cc-cb3f6ffd8157")
    LANGFUSE_EXTERNAL_URL = os.getenv("LANGFUSE_EXTERNAL_URL", "https://langfuse.home.gilbertopina.com")

