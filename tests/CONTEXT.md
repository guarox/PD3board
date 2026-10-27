# Context: tests

## Overview
Provides core quality assurance & testing components for `tests` within the platform ecosystem. Encapsulates specialized logic, interfaces, and operational configurations for this subsystem.

## Key Files & Modules
- `test_chart_multi_source.py`: Exports test_symbol_mappings_across_all_asset_classes, test_multi_source_candles_and_precision, test_multi_timeframe_historical_candles()
- `test_command_parser.py`: Exports test_parse_ticker_sector_function_go, test_parse_standalone_function, test_parse_aliases()
- `test_feeds.py`: Exports test_equities_feed, test_world_macro_feed, test_yield_curve_feed()
- `test_langfuse_integration.py`: Exports test_command_parser_lang, test_ai_research_memo_tracing()
- `test_live_commands.py`: Script / utility module
- `test_orderbook.py`: Exports test_orderbook_sorting_and_totals()
- `test_ui_contracts.py`: Tests for PD3board UI Contracts and Normalization Layer.

## Architectural Role & Dependencies
- **Layer**: Quality Assurance & Testing
- **Dependencies**: app, asyncio, pytest, time
- **Consumers**: Higher-level orchestration engines, parent modules, and automated cluster workloads.

## AI Agent Guidelines
- Maintain modularity and strict separation of concerns.
- Verify all external inputs and enforce zero-trust security invariants.
