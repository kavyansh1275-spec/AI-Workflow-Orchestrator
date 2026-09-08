# AI Workflow Orchestrator

V3 of an AI system that converts natural-language automation requests into structured, dependency-aware workflow plans and selects an automation provider.

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

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

V3 still uses dry-run deployment by default. No external provider API is called.
