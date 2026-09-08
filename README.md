# AI Workflow Orchestrator

V7 of an AI system that converts natural-language automation requests into structured, dependency-aware workflow plans, selects an automation provider, validates integration capabilities, generates provider-specific artifacts, and safely executes workflows in a deterministic local runtime.

## V1 foundation

- Parse a user request into a workflow plan.
- Represent triggers, actions, and workflow metadata.
- Validate workflow structure.
- Execute a provider-independent workflow simulation.
- Keep n8n, Make, and Zapier integrations isolated.

## V2 provider layer

- Detect an explicit n8n, Make, or Zapier provider from the request.
- Fall back to a generic provider when no provider is requested.
- Route provider deployments through a central registry.
- Support safe dry-run deployment without external API calls or credentials.
- Keep real provider API deployment deferred to a later version.

## V3 intelligence layer

- Normalize natural-language requests into structured workflow intent.
- Detect triggers and multiple actions in a single request.
- Preserve action order and add explicit step dependencies.
- Detect simple conditional language such as `if ... then ...`.
- Add intent confidence scoring.
- Support additional common actions such as Notion and Discord message creation.
- Expose intent analysis through the CLI and orchestrator.
- Validate dependency references and reject self-dependencies.
- Remain deterministic, offline, and safe-by-default with no API credentials required.

## V4 workflow generation layer

- Convert validated workflow plans into provider-specific artifacts.
- Generate an n8n-style node and connection representation.
- Generate a Make-style module representation with dependency numbers.
- Generate a Zapier-style ordered step representation.
- Preserve conditions, configuration, and dependencies in generated artifacts.
- Keep generation deterministic and credential-free.
- Expose generated artifacts through the orchestrator and CLI.
- Keep generated workflows inactive/dry-run only; no external provider API is called.

## V5 AI decision layer

- Understand workflow intent and requirements.
- Detect missing information that may need clarification.
- Choose an automation provider based on workflow complexity.
- Preserve an explicit user provider preference over automatic optimization.
- Feed the decision back into workflow generation.
- Keep the decision engine deterministic and credential-free.

## V6 execution layer

- Add a deterministic local workflow runtime.
- Execute validated steps in dependency order.
- Record per-step execution status and outputs.
- Evaluate simple workflow conditions and safely skip steps when conditions are not met.
- Produce an execution ID and structured execution report.
- Reject live execution explicitly; V6 remains dry-run only.
- Expose runtime execution through the orchestrator and CLI.

## V7 integration expansion layer

- Add a central, credential-free integration capability catalog.
- Validate every workflow step against a known app/action capability.
- Support expanded capabilities for Gmail, Slack, Discord, Notion, Google Sheets, Airtable, Telegram, webhooks, forms, schedules, and generic HTTP requests.
- Track capability categories and required configuration fields.
- Allow safe `configure_*` placeholders until a future configuration/credential layer exists.
- Expose integration inspection and the complete capability map through the orchestrator.
- Reject unsupported application capabilities before execution or generation.
- Keep all integration intelligence deterministic and offline; no external API calls are made.

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

V7 expands the integration intelligence layer while remaining credential-free and dry-run only. Real provider credentials, live API calls, and production deployment remain future work.
