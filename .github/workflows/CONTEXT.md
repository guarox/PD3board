# Context: workflows

## Overview
Provides core ci/cd & automation components for `workflows` within the platform ecosystem. Encapsulates specialized logic, interfaces, and operational configurations for this subsystem.

## Key Files & Modules
- `ci.yml`: CI/CD workflow: PD3board CI

## Architectural Role & Dependencies
- **Layer**: CI/CD & Automation
- **Dependencies**: Forgejo/GitHub Actions
- **Consumers**: Higher-level orchestration engines, parent modules, and automated cluster workloads.

## AI Agent Guidelines
- Verify runner compatibility and ensure secrets are securely injected via vault/secrets.
- Enforce pre-merge manifest validation and smoke testing steps.
- Maintain automated push webhooks for sub-second GitOps synchronization.
