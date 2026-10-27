# Context: models

## Overview
Provides core data & storage components for `models` within the platform ecosystem. Encapsulates specialized logic, interfaces, and operational configurations for this subsystem.

## Key Files & Modules
- `__init__.py`: PD3board data contracts and validation models.
- `contracts.py`: PD3board Strict UI Contract DTOs & Normalization Layer.

## Architectural Role & Dependencies
- **Layer**: Data & Storage
- **Dependencies**: pydantic, typing
- **Consumers**: Higher-level orchestration engines, parent modules, and automated cluster workloads.

## AI Agent Guidelines
- Maintain modularity and strict separation of concerns.
- Verify all external inputs and enforce zero-trust security invariants.
