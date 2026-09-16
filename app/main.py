import asyncio
import json
import logging
import os
import time
from typing import Set, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import Config
from app.engine.command_parser import CommandParser
from app.engine.orderbook import OrderBook
from app.engine.tick_buffer import TickBuffer
from app.feeds.binance import BinanceFeed
from app.feeds.coinbase import CoinbaseFeed
from app.feeds.equities import EquitiesFeed
from app.feeds.news import NewsFeed
from app.feeds.yield_curve import YieldCurveFeed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pd3board")

app = FastAPI(title="PD3board Financial Workstation", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global In-Memory State
orderbooks: Dict[str, OrderBook] = {
    Config.DEFAULT_CRYPTO: OrderBook(Config.DEFAULT_CRYPTO),
}
tick_buffers: Dict[str, TickBuffer] = {
    Config.DEFAULT_CRYPTO: TickBuffer(Config.DEFAULT_CRYPTO),
    Config.DEFAULT_EQUITY: TickBuffer(Config.DEFAULT_EQUITY),
}

# Seed initial ticks for default equity
base_price = 224.50
now = time.time()
for i in range(60):
    t_time = now - (60 - i) * 60
    base_price += (hash(str(i)) % 20 - 10) * 0.1
    tick_buffers[Config.DEFAULT_EQUITY].add_tick(
        price=round(base_price, 2),
        size=100.0,
        side="buy" if i % 2 == 0 else "sell",
        timestamp=t_time
    )

equities_feed = EquitiesFeed()
news_feed = NewsFeed()
yield_curve_feed = YieldCurveFeed()

active_connections: Set[WebSocket] = set()

class CommandRequest(BaseModel):
    command: str

async def broadcast(message: Dict[str, Any]):
    if not active_connections:
        return
    payload = json.dumps(message)
    dead_connections = set()
    for ws in list(active_connections):
        try:
            await ws.send_text(payload)
        except Exception:
            dead_connections.add(ws)
    for ws in dead_connections:
        active_connections.discard(ws)

async def on_binance_tick(symbol: str, price: float, size: float, side: str):
    if symbol not in tick_buffers:
        tick_buffers[symbol] = TickBuffer(symbol)
    tick = tick_buffers[symbol].add_tick(price, size, side)
    await broadcast({
        "type": "tick",
        "symbol": symbol,
        "price": price,
        "size": size,
        "side": side,
        "timestamp": tick.timestamp
    })

async def on_binance_depth(symbol: str, bids: list, asks: list, update_id: int):
    if symbol not in orderbooks:
        orderbooks[symbol] = OrderBook(symbol)
    ob = orderbooks[symbol]
    ob.update_levels(bids, asks, update_id)
    await broadcast({
        "type": "depth",
        "symbol": symbol,
        "data": ob.get_snapshot()
    })

binance_feed = BinanceFeed(
    symbol=Config.DEFAULT_CRYPTO,
    on_tick=on_binance_tick,
    on_depth=on_binance_depth
)

coinbase_feed = CoinbaseFeed(
    symbol="BTC-USD",
    on_tick=on_binance_tick,
    on_depth=on_binance_depth
)

async def equities_broadcaster():
    """Background task to broadcast equities/indices updates periodically."""
    while True:
        try:
            updates = equities_feed.update_ticks()
            if updates:
                await broadcast({
                    "type": "equities_update",
                    "data": updates
                })
        except Exception as e:
            logger.error(f"Error in equities broadcaster: {e}")
        await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting PD3board feeds...")
    await binance_feed.start()
    await coinbase_feed.start()
    asyncio.create_task(equities_broadcaster())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping PD3board feeds...")
    await binance_feed.stop()
    await coinbase_feed.stop()

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "PD3board API Running", "ui": "Compiling static bundle..."})

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PD3board",
        "connections": len(active_connections),
        "timestamp": time.time()
    }

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    parsed = CommandParser.parse(req.command)
    if not parsed["valid"]:
        return JSONResponse({"success": False, "error": parsed["error"]}, status_code=400)

    fn = parsed["function"]
    ticker = parsed["ticker"] or Config.DEFAULT_EQUITY

    data: Dict[str, Any] = {}
    if fn in {"GP", "GIP"}:
        tb = tick_buffers.get(ticker) or tick_buffers.get(Config.DEFAULT_CRYPTO)
        data = {
            "symbol": ticker,
            "candles": tb.get_candles() if tb else [],
            "ticks": tb.get_recent_ticks() if tb else []
        }
    elif fn == "L2":
        ob = orderbooks.get(ticker) or orderbooks.get(Config.DEFAULT_CRYPTO)
        data = ob.get_snapshot() if ob else {}
    elif fn == "WEI":
        data = {"indices": equities_feed.get_wei_matrix()}
    elif fn == "TOP":
        data = {"news": news_feed.get_latest_news()}
    elif fn == "YCRV":
        data = yield_curve_feed.get_curve()
    elif fn == "DES":
        data = equities_feed.get_security_description(ticker)
    elif fn == "HELP":
        data = {
            "help": [
                {"mnemonic": "GP", "desc": "Price Graph (Interactive candlestick & tick chart)"},
                {"mnemonic": "L2", "desc": "Level 2 Order Book Depth Ladder"},
                {"mnemonic": "WEI", "desc": "World Equity Indices & Macro Rates"},
                {"mnemonic": "DES", "desc": "Security Description & Capital Structure"},
                {"mnemonic": "TOP", "desc": "Top Financial Market News Wire"},
                {"mnemonic": "YCRV", "desc": "US Treasury Benchmark Yield Curve"}
            ]
        }

    return {
        "success": True,
        "parsed": parsed,
        "data": data
    }

@app.get("/api/wei")
async def get_wei():
    return equities_feed.get_wei_matrix()

@app.get("/api/yield_curve")
async def get_yield_curve():
    return yield_curve_feed.get_curve()

@app.get("/api/news")
async def get_news():
    return news_feed.get_latest_news()

@app.get("/api/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    sym = symbol.upper()
    ob = orderbooks.get(sym) or orderbooks.get(Config.DEFAULT_CRYPTO)
    return ob.get_snapshot() if ob else {}

@app.get("/api/ticks/{symbol}")
async def get_ticks(symbol: str):
    sym = symbol.upper()
    tb = tick_buffers.get(sym) or tick_buffers.get(Config.DEFAULT_CRYPTO)
    if tb:
        return {
            "symbol": sym,
            "candles": tb.get_candles(),
            "ticks": tb.get_recent_ticks()
        }
    return {"symbol": sym, "candles": [], "ticks": []}

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        # Send initial snapshot upon connection
        ob = orderbooks.get(Config.DEFAULT_CRYPTO)
        if ob:
            await websocket.send_text(json.dumps({
                "type": "depth",
                "symbol": Config.DEFAULT_CRYPTO,
                "data": ob.get_snapshot()
            }))

        await websocket.send_text(json.dumps({
            "type": "wei",
            "data": equities_feed.get_wei_matrix()
        }))

        await websocket.send_text(json.dumps({
            "type": "news",
            "data": news_feed.get_latest_news()
        }))

        await websocket.send_text(json.dumps({
            "type": "yield_curve",
            "data": yield_curve_feed.get_curve()
        }))

        while True:
            raw_text = await websocket.receive_text()
            try:
                msg = json.loads(raw_text)
                if msg.get("action") == "command":
                    parsed = CommandParser.parse(msg.get("command", ""))
                    await websocket.send_text(json.dumps({
                        "type": "command_result",
                        "parsed": parsed
                    }))
            except Exception as e:
                logger.error(f"Error processing client message: {e}")

    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        active_connections.discard(websocket)
