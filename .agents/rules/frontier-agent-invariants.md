# Frontier Agent Architecture & Operational Rules

## Strict Communication & Output Rule
* **No Emojis:** Do NOT use emojis anywhere in markdown responses, terminal outputs, code, comments, commits, or documentation files. All communication and generated artifacts must remain strictly professional, technical, and clean.

## Frontier Agent Architecture & Long-Horizon Task Invariants

To effectively build, optimize, and execute frontier AI agents (such as Gemini 4 / 3.8 / 3.6) across complex and long-horizon tasks, all workloads must adhere to these four architectural invariants:

1. **Strategic Reasoning Effort (Low vs. High):**
    * *Low Reasoning Effort (`thinkingBudget: 0` or Low):* Mandated for clear, explicit UI/design specifications, fast chat, structured JSON formatting, and status lookups to minimize cost, bandwidth, and latency.
    * *High Reasoning Effort (High / Full Budget):* Reserved specifically for tasks requiring complex algorithmic logic, deep multi-file debugging, architecture analysis, and sandbox execution to resolve tricky edge cases.

2. **Token Budget Sizing & Anti-Rationing Directives:**
    * *Max Output Token Ceiling:* When using High reasoning, scale `maxOutputTokens` up to `65,536` to account for internal model "thinking" consumption. Setting low caps (e.g., 2,048 or 4,096) causes output budget exhaustion and truncated solutions before completion.
    * *Context Anti-Rationing Prompting:* For massive long-horizon tasks, explicitly state the available 1,000,000 token context budget in the system prompt. This prevents the model from prematurely rationing or compressing its analysis and ensures full, unabridged code implementations.

3. **Interaction API Server-Side State Management:**
    * *Session State Persistence:* Employ the Gemini Interaction API (`previous_interaction_id`) for multi-turn conversations and multimodal workflows.
    * *Asset Re-Upload Prevention:* Avoid the inefficiency of repeatedly re-uploading large assets (such as Playwright DOM screenshots, PDF runbooks, or terminal dumps) turn after turn. Let server-side state maintain history cleanly and reduce round-trip payload size.

4. **AI Agent Sandbox & Evaluation Boundary Isolation (Out-of-Band Grading):**
    * *Rule:* Never place grading scripts, evaluation assertions, or benchmark capture timestamps within the agent's accessible workspace (sandbox).
    * *Technical Reason:* Frontier agents optimize for whatever objectives and files are visible in their environment. To guarantee rigorous, uncompromised verification, the evaluation harness must remain strictly blind and inaccessible to the agent.
    * *Operational Standards:*
        * Run grading harnesses and score evaluators out-of-band via parent orchestrators or external CI containers.
        * If test fixtures must be evaluated against agent outputs, mount them read-only after the agent terminates.
        * Maintain zero tampering surface within the agent's writable workspace.
