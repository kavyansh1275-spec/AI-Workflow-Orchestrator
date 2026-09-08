# AI Workflow Orchestrator

V2 foundation for an AI system that converts natural-language automation requests into structured workflow plans and selects an automation provider.

## V1 foundation

- Parse a user request into a workflow plan.
- Represent triggers, actions, and workflow metadata.
- Validate workflow structure.
- Execute a provider-independent workflow simulation.
- Keep n8n, Make, and Zapier integrations isolated.

## V2 scope

- Detect an explicit n8n, Make, or Zapier provider from the request.
- Fall back to a generic provider when no provider is requested.
- Route provider deployments through a central registry.
- Support safe dry-run deployment without external API calls or credentials.
- Keep real provider API deployment deferred to a later version.

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

V2 is intentionally safe-by-default: dry-run deployment is enabled and no external provider API is called.
