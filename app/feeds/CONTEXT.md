# Context: feeds

## Overview
Provides core api & ingestion components for `feeds` within the platform ecosystem. Encapsulates specialized logic, interfaces, and operational configurations for this subsystem.

## Key Files & Modules
- `ai_research.py`: Defines class AIResearchFeed
- `binance.py`: Defines class BinanceFeed
- `coinbase.py`: Defines class CoinbaseFeed
- `eco.py`: Defines class EcoFeed
- `equities.py`: Defines class EquitiesFeed
- `insider_holdings.py`: Defines class InsiderHoldingsFeed
- `market_data_client.py`: Defines class MarketDataClient
- `market_heatmap.py`: Defines class MarketHeatmapFeed
- `news.py`: Defines class NewsFeed
- `options.py`: Defines class OptionsFeed
- `polymarket.py`: Defines class PolymarketFeed
- `world_macro.py`: Defines class WorldMacroFeed
- `yield_curve.py`: Defines class YieldCurveFeed

## Architectural Role & Dependencies
- **Layer**: API & Ingestion
- **Dependencies**: aiohttp, app, asyncio, base64, copy, datetime
- **Consumers**: Higher-level orchestration engines, parent modules, and automated cluster workloads.

## AI Agent Guidelines
- Maintain modularity and strict separation of concerns.
- Verify all external inputs and enforce zero-trust security invariants.
