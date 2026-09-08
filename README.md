# AI Workflow Orchestrator

V1 Foundation for an AI system that converts natural-language automation requests into structured workflow plans.

## V1 scope

- Parse a user request into a workflow plan.
- Represent triggers, actions, and workflow metadata.
- Validate workflow structure.
- Execute a small provider-independent workflow simulation.
- Keep integrations isolated so n8n, Make, and Zapier adapters can be added safely later.

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

V1 is intentionally provider-independent. Real API calls and credentials are not part of this foundation.
