# PD3board: Real-Time Financial Workstation & Bloomberg Terminal Emulator

## Executive Overview
PD3board is an open-source, high-throughput financial workstation emulator designed to replicate the workflow, density, and command-driven UX of the Bloomberg Professional Service (Terminal). It pairs an authentic amber/phosphor CRT aesthetic and tiled window manager with low-latency streaming market data feeds, L1/L2 order book ladders, macroeconomic calendars, and financial news pipelines.

---

## Core System Architecture

```
+-----------------------------------------------------------------------+
|                             PD3board UI                               |
|   - Tiled Grid Workspace (Dockable Panes, Multi-Monitor Support)      |
|   - Terminal Command Line Parser (Mnemonic Dispatch: TICKER + CMND)   |
|   - Canvas/WebGL Tick Charts (60 FPS Hardware-Accelerated Rendering)  |
|   - Amber Monospace Font Stack (#FFB000 on #0A0A0A Pitch Black)       |
+-----------------------------------------------------------------------+
                                   ^
                                   | WebSockets / SSE (Sub-50ms)
                                   v
+-----------------------------------------------------------------------+
|                    PD3board Streaming Ingestion Engine                |
|   - Async Market Feed Connectors (WebSockets / REST Polling)          |
|   - In-Memory Circular Order Book & Tick Buffer (L1/L2 Reconstruction)|
|   - Fast Pub/Sub Message Broker                                       |
|   - Feed Handlers: Stocks, Crypto, Forex, Yield Curves, Macro Data    |
+-----------------------------------------------------------------------+
        |                  |                   |                  |
        v                  v                   v                  v
+---------------+  +---------------+  +----------------+  +-------------+
| Market Data   |  | Crypto L2     |  | Macro Rates    |  | News / SEC  |
| (Alpaca /     |  | (Binance /    |  | (Federal       |  | (EDGAR RSS, |
| Finnhub /     |  | Coinbase      |  | Reserve FRED   |  | Financial   |
| Yahoo WSS)    |  | WebSockets)   |  | API)           |  | Headlines)  |
+---------------+  +---------------+  +----------------+  +-------------+
```

---

## Visual & Interface Paradigm

1. **Terminal Command Line**:
   * Global command line accessible via keyboard shortcut `/` or direct typing.
   * Input pattern: `<TICKER> <SECTOR> <FUNCTION> <GO>`
     * Example: `AAPL US EQUITY GP <GO>` (Interactive intraday chart)
     * Example: `SPX INDEX WEI <GO>` (World Equity Indices heatmap)
     * Example: `US10Y GOVT YCRV <GO>` (Treasury Yield Curve)
     * Example: `TOP <GO>` or `NEWS <GO>` (Real-time financial news stream)
     * Example: `BTCUSD CRNCY L2 <GO>` (Live Order Book depth)

2. **Bloomberg Key Color Coding**:
   * Sector Keys: Yellow (`CMDTY`, `INDEX`, `CRNCY`, `EQUITY`, `GOVT`).
   * Action Keys: Green (`<GO>`, Enter), Red (`<CANCEL>`, Esc), White (Navigation).

3. **High-Density Data Grid**:
   * Monospace tabular numbers with zero font jitter.
   * Flashing tick price updates (green for tick up, red for tick down, fading over 300ms).
   * Fixed 80-column / 160-column terminal grid or flexible CSS Grid layout.

---

## Market Data Feed Connectors

| Feed Type | Provider Options | Update Protocol | Latency Target |
| :--- | :--- | :--- | :--- |
| **US Equities (L1 Quotes & Trades)** | Alpaca Markets, Finnhub, Yahoo Finance WSS | WebSocket | < 100ms |
| **Crypto (L2 Order Book & Depth)** | Binance, Coinbase Exchange, Kraken | WebSocket | < 25ms |
| **Forex & FX Pairs** | Finnhub FX, TwelveData | WebSocket / SSE | < 200ms |
| **Macro & Yield Curves** | Federal Reserve Economic Data (FRED) API | REST Poll (Daily/Hourly) | Batch |
| **Corporate News & SEC Filings** | SEC EDGAR Atom/RSS Feed, Finnhub News | SSE / Polling | < 5s |

---

## Supported Function Mnemonics

* `DES`: Security Description, P/E, Market Cap, Beta, 52-Week Range, and Capital Structure.
* `GP`: Interactive Candlestick / Bar Chart with Volume Profile and Moving Averages.
* `GIP`: Intraday Tick Chart with 1m/5m VWAP bands.
* `WEI`: World Equity Indices (S&P 500, Nasdaq 100, Dow Jones, FTSE 100, Nikkei 225, DAX).
* `L2`: Level 2 Order Book Depth ladder with cumulative volume visualizer.
* `YCRV`: US Treasury Yield Curve (3M, 2Y, 5Y, 10Y, 30Y) with inversion alerts.
* `TOP`: Top global financial market headlines with live ticker tagging.
* `ECO`: Macroeconomic calendar (CPI, NFP, FOMC rate decisions, GDP releases).
* `PORT`: Portfolio monitor, position weights, real-time unrealized P&L.
