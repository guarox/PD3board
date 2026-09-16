import asyncio
import json
import logging
import random
import time
from typing import Callable, Optional
import websockets

logger = logging.getLogger(__name__)

class BinanceFeed:
    """
    Subscribes to Binance public WebSocket streams:
    - Real-time trade ticks: <symbol>@trade
    - 20-level order book depth: <symbol>@depth20@100ms
    Includes resilient auto-reconnect and synthetic fallback.
    """
    def __init__(self, symbol: str = "BTCUSDT", on_tick: Optional[Callable] = None, on_depth: Optional[Callable] = None):
        self.symbol = symbol.lower()
        self.raw_symbol = symbol.upper()
        self.on_tick = on_tick
        self.on_depth = on_depth
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.last_price = 64250.00 if "BTC" in self.raw_symbol else 3450.00

    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self._run_loop())

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        stream_url = f"wss://stream.binance.com:9443/stream?streams={self.symbol}@trade/{self.symbol}@depth20@100ms"
        backoff = 2

        while self.running:
            try:
                logger.info(f"Connecting to Binance WebSocket: {stream_url}")
                async with websockets.connect(stream_url, ping_interval=20, ping_timeout=10) as ws:
                    backoff = 2
                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        stream = data.get("stream", "")
                        payload = data.get("data", {})

                        if "trade" in stream:
                            price = float(payload.get("p", 0.0))
                            size = float(payload.get("q", 0.0))
                            is_buyer_maker = payload.get("m", False)
                            side = "sell" if is_buyer_maker else "buy"
                            self.last_price = price
                            if self.on_tick:
                                await self.on_tick(self.raw_symbol, price, size, side)

                        elif "depth" in stream:
                            bids = payload.get("bids", [])
                            asks = payload.get("asks", [])
                            update_id = payload.get("lastUpdateId", 0)
                            if self.on_depth:
                                await self.on_depth(self.raw_symbol, bids, asks, update_id)

            except Exception as e:
                logger.warning(f"Binance WebSocket error: {e}. Falling back to internal engine for {backoff}s...")
                await self._fallback_drift(duration=backoff)
                backoff = min(backoff * 2, 30)

    async def _fallback_drift(self, duration: int):
        """Simulates micro-ticks if network is unreachable or rate-limited."""
        end_time = time.time() + duration
        while time.time() < end_time and self.running:
            change = (random.random() - 0.49) * (self.last_price * 0.0003)
            self.last_price = round(self.last_price + change, 2)
            size = round(random.uniform(0.01, 1.5), 4)
            side = "buy" if change >= 0 else "sell"

            if self.on_tick:
                await self.on_tick(self.raw_symbol, self.last_price, size, side)

            if self.on_depth:
                bids = [[round(self.last_price - (i * 0.5) - 0.25, 2), round(random.uniform(0.1, 4.0), 3)] for i in range(1, 21)]
                asks = [[round(self.last_price + (i * 0.5) + 0.25, 2), round(random.uniform(0.1, 4.0), 3)] for i in range(1, 21)]
                await self.on_depth(self.raw_symbol, bids, asks, int(time.time() * 1000))

            await asyncio.sleep(0.5)
