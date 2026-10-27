# Context: engine

## Overview
Provides core utility & implementation components for `engine` within the platform ecosystem. Encapsulates specialized logic, interfaces, and operational configurations for this subsystem.

## Key Files & Modules
- `command_parser.py`: Defines class CommandParser
- `orderbook.py`: Defines class OrderLevel, OrderBook
- `tick_buffer.py`: Defines class Tick, Candle

## Architectural Role & Dependencies
- **Layer**: Utility & Implementation
- **Dependencies**: collections, dataclasses, re, time, typing
- **Consumers**: Higher-level orchestration engines, parent modules, and automated cluster workloads.

## AI Agent Guidelines
- Maintain modularity and strict separation of concerns.
- Verify all external inputs and enforce zero-trust security invariants.
