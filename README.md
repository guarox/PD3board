# PD3board: Real-Time Financial Workstation & Bloomberg Terminal Emulator

## Executive Overview
PD3board is an open-source, high-throughput financial workstation emulator designed to replicate the workflow, density, and command-driven UX of the Bloomberg Professional Service (Terminal). It pairs an authentic amber/phosphor CRT aesthetic and tiled window manager with low-latency streaming market data feeds, L1/L2 order book ladders, macroeconomic calendars, technical analysis overlays, and financial news pipelines.

---

## Core System Architecture

```
+-----------------------------------------------------------------------------------------+
|                                       PD3board UI                                       |
|   - Tiled 4-Quadrant Workspace Grid (GP Chart, L2 Depth Ladder, WEI Indices, YCRV/TOP)  |
|   - Terminal Command Line Parser (Mnemonic Dispatch: TICKER + SECTOR + FUNCTION <GO>)   |
|   - TradingView Lightweight Charts (Standalone v4.2.1, 60 FPS Candlestick & Overlays)   |
|   - Amber Monospace Font Stack (#FFB000 on #0A0A0A Pitch Black CRT Simulation)          |
|   - Vintage Mechanical Keyboard Audio Synthesizer (Web Audio API)                       |
+-----------------------------------------------------------------------------------------+
                                             ^
                                             | WebSockets / REST API (Sub-50ms)
                                             v
+-----------------------------------------------------------------------------------------+
|                           PD3board Streaming Ingestion Engine                           |
|   - FastAPI / Uvicorn Asynchronous Non-Blocking Server Architecture                     |
|   - In-Memory Circular Order Book & Tick Buffer (L1/L2 Depth Ladder Reconstruction)     |
|   - Pub/Sub Market Feed Dispatcher & WebSocket Broadcaster                              |
|   - Langfuse LLM Observability & OpenTelemetry Trace Engine                             |
+-----------------------------------------------------------------------------------------+
        |                  |                   |                  |               |
        v                  v                   v                  v               v
+---------------+  +---------------+  +----------------+  +-------------+  +---------------+
| Market Data   |  | Crypto L2     |  | Macro Rates    |  | News / SEC  |  | Polymarket    |
| (Alpaca /     |  | (Binance /    |  | & Treasury     |  | (EDGAR RSS, |  | CLOB / Gamma  |
| Finnhub /     |  | Coinbase      |  | Yield Curves   |  | Financial   |  | Prediction    |
| Yahoo WSS)    |  | WebSockets)   |  | FRED API)      |  | Headlines)  |  | Markets)      |
+---------------+  +---------------+  +----------------+  +-------------+  +---------------+
        |                                                                         |
        +-----------------------------> [ Langfuse ] <----------------------------+
                                  (LLM Traces & Observability)
```

---

## Workstation Controls & Productivity Features

* **Hotkeys (F1 - F12)**:
  * `F1`: `HELP <GO>` - Workstation directory, keyboard shortcuts, and syntax guide.
  * `F2`: `WEI <GO>` - World Equity Indices multi-market tabular overview.
  * `F3`: `YCRV <GO>` - US Treasury sovereign yield curve (1M to 30Y).
  * `F4`: `ECO <GO>` - Economic release calendar with consensus vs actual numbers.
  * `F5`: `TOP <GO>` - Financial news wire with ticker attribution.
  * `F6`: `GP <GO>` - Graphical Price chart (candlestick and volume).
  * `F7`: `L2 <GO>` - Level 2 order book depth ladder and bid/ask liquidity.
  * `F8`: `DES <GO>` - Fundamental security description, valuation multiples, capital structure.
  * `F9`: `FA <GO>` - Financial analysis 5-year income statement and balance sheet breakdown.
  * `F10`: `ANR <GO>` - Analyst recommendations, consensus breakdown, price targets.
  * `F11`: `EE <GO>` - Quarterly earnings reports, consensus estimates, and surprise margins.
  * `F12`: `OMON <GO>` - Options chains, Black-Scholes Greeks, implied volatility smiles.

* **Quadrant Maximization (`[MAX]` / `[RST]`)**:
  * Any of the 4 workspace quadrants (Chart `GP`, Order Book `L2`, Indices `WEI`, News Wire `TOP`) can be maximized to full workstation dimensions by clicking the `[MAX]` button on its header bar.
  * Pressing `<ESC>` or clicking `[RST]` instantly restores the standard 4-pane tiled grid.

* **Tabular Data Exporter (`[EXPORT CSV]`)**:
  * All tabular analysis modal screens (`WEI`, `OMON`, `FA`, `EE`, `ANR`, `INSD`, `HDS`, `POLY`, `WCRS`, `FDM`, `ECO`) feature an active `[EXPORT CSV]` action.
  * Clicking `[EXPORT CSV]` compiles the active table into RFC 4180-compliant CSV and prompts an immediate client-side download timestamped to current market time.

* **Technical Indicators (TradingView Lightweight Charts)**:
  * Selectable from the chart header toolbar:
    * `SMA 20`: 20-period simple moving average overlay.
    * `SMA 50`: 50-period simple moving average overlay.
    * `BOLL`: Bollinger Bands (20-period SMA with +/- 2 standard deviations).
    * `RSI`: Relative Strength Index (14-period momentum oscillator with 30/70 thresholds).
    * `MACD`: Moving Average Convergence Divergence (12/26 EMA line, 9 EMA signal line, histogram).

* **Timezone Switching (`ET/UTC`)**:
  * Toggle between New York Market Time (`EST` / `EDT`) and Coordinated Universal Time (`UTC`) via the footer control or by clicking the live digital clock in the header.
  * Synchronizes both timestamp displays and charting x-axis time scales across all open panels.

* **Audio & Phosphor CRT Simulation**:
  * Mechanical switch audio feedback synthesized in real time via the Web Audio API (toggleable via `AUDIO: ON/OFF`).
  * Retro amber phosphor scanline simulation with subtle glass curvature overlay (toggleable via `CRT: ON/OFF`).

---

## Supported Function Mnemonics (All 22 Functions)

PD3board supports full Bloomberg-style syntax (`<TICKER> [SECTOR] [FUNCTION] <GO>`), prefix syntax (`[FUNCTION] <TICKER> <GO>`), and standalone global dispatch (`[FUNCTION] <GO>`).

| # | Mnemonic | Syntax Example | Description |
|---|---|---|---|
| 1 | `GP` | `AAPL US EQUITY GP <GO>` | Graphical Price Candlestick Chart rendered via TradingView Lightweight Charts with volume bars. |
| 2 | `GIP` | `NVDA GIP <GO>` | Graphical Intraday Price action tick chart with 1-minute VWAP bands. |
| 3 | `L2` | `BTCUSD CRNCY L2 <GO>` | Level 2 Order Book Depth Ladder with live bid/ask spreads calculated in basis points (BPS). |
| 4 | `WEI` | `WEI <GO>` | World Equity Indices real-time tracking matrix (S&P 500, Nasdaq 100, Dow Jones, FTSE 100, DAX, Nikkei 225). |
| 5 | `TOP` / `NEWS` | `TOP <GO>` or `NEWS <GO>` | Breaking financial market headlines wire with clickable ticker routing. |
| 6 | `YCRV` | `YCRV <GO>` | US Treasury Sovereign Benchmark Yield Curve (1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y) with spread differentials. |
| 7 | `DES` | `MSFT DES <GO>` | Comprehensive Security Description, market capitalization, P/E, beta, 52-week range, and capital structure. |
| 8 | `ANR` | `AMZN ANR <GO>` | Analyst Recommendations consensus breakdown (Buy/Hold/Sell count), average price target, and upside potential. |
| 9 | `FA` | `TSLA FA <GO>` | Financial Analysis 5-year historical statements (Revenue, Gross Profit, Operating Margin, Net Income, Operating Cash Flow). |
| 10 | `RV` | `GOOGL RV <GO>` | Relative Valuation matrix comparing target security against industry peer group across multiples (P/E, P/S, EV/EBITDA, Margins). |
| 11 | `EE` | `META EE <GO>` | Earnings and Estimates quarterly EPS surprises, revenue forecasts, and historical beats/misses. |
| 12 | `WIRP` | `WIRP <GO>` | World Interest Rate Probabilities (FOMC meeting rate hike/cut probabilities derived from Fed Funds Futures). |
| 13 | `WCRS` | `WCRS <GO>` | World Currency Ranker tracking global G10 and emerging market FX pairs relative to USD. |
| 14 | `FDM` | `FDM <GO>` | Global Commodities & Energy Matrix (Crude Oil, Brent, Natural Gas, Gold, Silver, Copper, Agricultural futures). |
| 15 | `OMON` | `AAPL OMON <GO>` | Options Chain Monitor with Black-Scholes Greeks (Delta, Gamma, Theta, Vega), Max Pain strike, and Volatility Smile curve. |
| 16 | `MAPS` / `HEAT` | `MAPS <GO>` or `HEAT <GO>` | S&P 500 Market Treemap and sector heatmap grouped by GICS industry classification. |
| 17 | `AI` / `RES` | `NVDA AI <GO>` or `RES <GO>` | Autonomous AI Equity Research Analyst Investment Memo synthesizing valuation, thesis, risks, and price target. |
| 18 | `POLY` / `PRED` / `PM` | `POLY <GO>` or `MACRO POLY <GO>` | Polymarket Prediction Markets and Binary Event Contracts (CLOB prices, implied probabilities, 24h volume, open interest). |
| 19 | `LANG` / `TRACE` | `LANG <GO>` or `TRACE <GO>` | Langfuse LLM Observability and trace telemetry console displaying active sessions, generation spans, token usage, and latency. |
| 20 | `INSD` | `AAPL INSD <GO>` | SEC Form 4 Insider Trading Ledger tracking recent purchases and sales by corporate executives, officers, and directors. |
| 21 | `HDS` | `NVDA HDS <GO>` | SEC 13F Institutional Holders ownership breakdown, institutional float percentage, and top institutional asset managers. |
| 22 | `ECO` | `ECO <GO>` | Macroeconomic Event Calendar detailing global releases (CPI, Non-Farm Payrolls, FOMC Decisions, GDP) with consensus vs actual prints. |
| 23 | `HELP` | `HELP <GO>` | Workstation Directory, available mnemonic inventory, keyboard shortcuts, and syntax specification guide. |

---

## Market Data Feed Connectors

| Feed Type | Provider Options | Update Protocol | Latency Target |
| :--- | :--- | :--- | :--- |
| **US Equities (L1 Quotes & Trades)** | Alpaca Markets, Finnhub, Yahoo Finance WSS | WebSocket | < 100ms |
| **Crypto (L2 Order Book & Depth)** | Binance, Coinbase Exchange, Kraken | WebSocket | < 25ms |
| **Forex & FX Pairs** | Finnhub FX, TwelveData | WebSocket / SSE | < 200ms |
| **Macro & Yield Curves** | Federal Reserve Economic Data (FRED) API | REST Poll (Daily/Hourly) | Batch |
| **Corporate News & SEC Filings** | SEC EDGAR Atom/RSS Feed, Finnhub News | SSE / Polling | < 5s |
| **Prediction Markets & Event Contracts** | Polymarket Gamma + CLOB API (`POLYGON / QCX US DCM`) | REST / 30s Cache | < 150ms |
| **LLM Observability & Tracing** | Langfuse Tracing API Engine | Async Trace Export | Sub-second |

---

## Command Syntax Rules

1. **Standard Bloomberg Command**:
   ```
   <TICKER> [SECTOR] [FUNCTION] <GO>
   ```
   * Example: `AAPL US EQUITY GP <GO>`
   * Example: `BTCUSD CRNCY L2 <GO>`
   * Example: `US10Y GOVT YCRV <GO>`

2. **Prefix Shortcut**:
   ```
   [FUNCTION] <TICKER> <GO>
   ```
   * Example: `DES MSFT <GO>`
   * Example: `ANR NVDA <GO>`
   * Example: `OMON TSLA <GO>`

3. **Standalone Global Mnemonics**:
   ```
   [FUNCTION] <GO>
   ```
   * Example: `WEI <GO>`, `ECO <GO>`, `TOP <GO>`, `YCRV <GO>`, `WIRP <GO>`, `WCRS <GO>`, `FDM <GO>`, `MAPS <GO>`, `POLY <GO>`, `LANG <GO>`, `HELP <GO>`
