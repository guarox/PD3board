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
from app.engine.tick_buffer import TickBuffer, Tick, Candle
from app.feeds.binance import BinanceFeed
from app.feeds.coinbase import CoinbaseFeed
from app.feeds.equities import EquitiesFeed
from app.feeds.news import NewsFeed
from app.feeds.yield_curve import YieldCurveFeed
from app.feeds.eco import EcoFeed

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

# Global Feeds
equities_feed = EquitiesFeed()
news_feed = NewsFeed()
yield_curve_feed = YieldCurveFeed()
eco_feed = EcoFeed()

# Global In-Memory State
orderbooks: Dict[str, OrderBook] = {
    Config.DEFAULT_CRYPTO: OrderBook(Config.DEFAULT_CRYPTO),
}
tick_buffers: Dict[str, TickBuffer] = {
    Config.DEFAULT_CRYPTO: TickBuffer(Config.DEFAULT_CRYPTO),
}

def get_or_create_tick_buffer(sym: str) -> TickBuffer:
    sym = sym.upper()
    expected_price = equities_feed.get_security_price(sym)
    if sym in tick_buffers:
        tb = tick_buffers[sym]
        recent = tb.get_recent_ticks(1)
        # Check if buffer was corrupted with old default 150.0 value when expected price differs significantly
        if recent and abs(recent[0]["price"] - expected_price) > (expected_price * 0.35):
            tb.candles.clear()
            tb.ticks.clear()
        else:
            return tb
    else:
        tb = TickBuffer(sym)
        tick_buffers[sym] = tb

    base_price = expected_price
    now_ts = time.time()
    current_minute = int(now_ts // 60) * 60
    step = max(0.02, round(base_price * 0.0004, 2))

    # Generate 60 historical minute candles ending at base_price
    price_walk = [base_price]
    curr = base_price
    for i in range(1, 60):
        drift = (hash(f"{sym}_{i}") % 21 - 10) * step * 0.35
        reversion = (base_price - curr) * 0.05
        curr = round(curr + drift + reversion, 2)
        price_walk.append(curr)

    price_walk.reverse()

    for idx, close_p in enumerate(price_walk):
        bucket_time = current_minute - (59 - idx) * 60
        prev_p = price_walk[idx - 1] if idx > 0 else close_p
        open_p = prev_p
        high_p = round(max(open_p, close_p) + abs(hash(f"{sym}_h_{idx}") % 10) * step * 0.2, 2)
        low_p = round(min(open_p, close_p) - abs(hash(f"{sym}_l_{idx}") % 10) * step * 0.2, 2)
        vol = round(100.0 + (hash(f"{sym}_v_{idx}") % 100), 1)

        tb.candles[bucket_time] = Candle(
            time=bucket_time,
            open=open_p,
            high=high_p,
            low=low_p,
            close=close_p,
            volume=vol
        )

        tb.ticks.append(Tick(timestamp=bucket_time + 10, price=open_p, size=vol * 0.25, side="buy"))
        tb.ticks.append(Tick(timestamp=bucket_time + 25, price=high_p, size=vol * 0.25, side="buy"))
        tb.ticks.append(Tick(timestamp=bucket_time + 40, price=low_p, size=vol * 0.25, side="sell"))
        tb.ticks.append(Tick(timestamp=bucket_time + 55, price=close_p, size=vol * 0.25, side="buy" if close_p >= open_p else "sell"))

    return tb

def get_or_create_orderbook(sym: str) -> OrderBook:
    sym = sym.upper()
    if sym == Config.DEFAULT_CRYPTO and sym in orderbooks and orderbooks[sym].bids:
        return orderbooks[sym]

    if sym not in orderbooks or not orderbooks[sym].bids:
        orderbooks[sym] = OrderBook(sym)

    ob = orderbooks[sym]
    if not ob.bids or sym != Config.DEFAULT_CRYPTO:
        price = equities_feed.get_security_price(sym)
        if price >= 10000:
            tick = 0.50
        elif price >= 1000:
            tick = 0.25
        elif price >= 100:
            tick = 0.05
        else:
            tick = 0.01

        raw_bids = []
        raw_asks = []
        for i in range(1, 11):
            bid_p = round(price - i * tick, 2)
            ask_p = round(price + i * tick, 2)
            bid_sz = round(10.0 + (hash(f"{sym}_b_{i}") % 80) * 1.5, 2)
            ask_sz = round(10.0 + (hash(f"{sym}_a_{i}") % 80) * 1.5, 2)
            raw_bids.append([bid_p, bid_sz])
            raw_asks.append([ask_p, ask_sz])
        ob.update_levels(raw_bids, raw_asks, update_id=int(time.time() * 1000))
    return ob

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
                # Update in-memory tick buffers and order books for active equities & indices
                for item in updates:
                    sym = item["symbol"]
                    price = item["price"]
                    chg = item["change"]
                    if sym in tick_buffers:
                        tick_buffers[sym].add_tick(
                            price=price,
                            size=round(50.0 + (hash(f"{sym}_{price}") % 50), 1),
                            side="buy" if chg >= 0 else "sell"
                        )
                    if sym in orderbooks and sym != Config.DEFAULT_CRYPTO:
                        ob = orderbooks[sym]
                        tick = 0.50 if price >= 10000 else (0.25 if price >= 1000 else (0.05 if price >= 100 else 0.01))
                        raw_bids = []
                        raw_asks = []
                        for i in range(1, 11):
                            b_sz = round(15.0 + (hash(f"{sym}_b_{i}_{price}") % 75), 2)
                            a_sz = round(15.0 + (hash(f"{sym}_a_{i}_{price}") % 75), 2)
                            raw_bids.append([round(price - i * tick, 2), b_sz])
                            raw_asks.append([round(price + i * tick, 2), a_sz])
                        ob.update_levels(raw_bids, raw_asks, update_id=int(time.time() * 1000))
                        await broadcast({
                            "type": "depth",
                            "symbol": sym,
                            "data": ob.get_snapshot()
                        })
        except Exception as e:
            logger.error(f"Error in equities broadcaster: {e}")
        await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting PD3board feeds...")
    for sym in list(equities_feed.equities.keys()) + list(equities_feed.indices.keys()):
        get_or_create_tick_buffer(sym)
        get_or_create_orderbook(sym)
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
        tb = get_or_create_tick_buffer(ticker)
        data = {
            "symbol": ticker,
            "candles": tb.get_candles(),
            "ticks": tb.get_recent_ticks()
        }
    elif fn == "L2":
        ob = get_or_create_orderbook(ticker)
        data = ob.get_snapshot() if ob else {}
    elif fn == "WEI":
        data = {"indices": equities_feed.get_wei_matrix()}
    elif fn == "TOP":
        data = {"news": news_feed.get_latest_news()}
    elif fn == "YCRV":
        data = yield_curve_feed.get_curve()
    elif fn == "DES":
        data = equities_feed.get_security_description(ticker)
    elif fn == "ECO":
        data = {"events": eco_feed.get_events()}
    elif fn == "HELP":
        data = {
            "help": [
                {"mnemonic": "GP", "desc": "Price Graph (Interactive candlestick & tick chart with 60 FPS Canvas)"},
                {"mnemonic": "L2", "desc": "Level 2 Order Book Depth Ladder with Spread in BPS"},
                {"mnemonic": "WEI", "desc": "World Equity Indices & Macro Rates (SPX, NDX, DJI, etc.)"},
                {"mnemonic": "DES", "desc": "Security Description, Fundamentals & Capital Structure"},
                {"mnemonic": "TOP", "desc": "Top Financial Market News Wire with Ticker Tagging"},
                {"mnemonic": "YCRV", "desc": "US Treasury Benchmark Yield Curve (1M to 30Y)"},
                {"mnemonic": "ECO", "desc": "Economic Calendar & Global Macroeconomic Indicators"}
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

@app.get("/api/eco")
async def get_eco():
    return eco_feed.get_events()

@app.get("/api/des/{symbol}")
async def get_des(symbol: str):
    return equities_feed.get_security_description(symbol)

@app.get("/api/help")
async def get_help():
    return {
        "functions": [
            {"mnemonic": "GP", "desc": "Price Graph (Interactive candlestick & tick chart with 60 FPS Canvas)"},
            {"mnemonic": "L2", "desc": "Level 2 Order Book Depth Ladder with Spread in BPS"},
            {"mnemonic": "WEI", "desc": "World Equity Indices & Macro Rates (SPX, NDX, DJI, etc.)"},
            {"mnemonic": "DES", "desc": "Security Description, Fundamentals & Capital Structure"},
            {"mnemonic": "TOP", "desc": "Top Financial Market News Wire with Ticker Tagging"},
            {"mnemonic": "YCRV", "desc": "US Treasury Benchmark Yield Curve (1M to 30Y)"},
            {"mnemonic": "ECO", "desc": "Economic Calendar & Global Macroeconomic Indicators"}
        ],
        "sectors": ["EQUITY", "CRNCY", "INDEX", "GOVT", "CMDTY"],
        "shortcuts": [
            {"key": "/", "action": "Focus Bloomberg command line"},
            {"key": "Esc", "action": "Clear command input buffer"},
            {"key": "<GO>", "action": "Execute entered command"},
            {"key": "<CNCL>", "action": "Cancel current command input"}
        ]
    }

@app.get("/api/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    sym = symbol.upper()
    ob = get_or_create_orderbook(sym)
    return ob.get_snapshot() if ob else {}

@app.get("/api/ticks/{symbol}")
async def get_ticks(symbol: str):
    sym = symbol.upper()
    tb = get_or_create_tick_buffer(sym)
    return {
        "symbol": sym,
        "candles": tb.get_candles(),
        "ticks": tb.get_recent_ticks()
    }

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
