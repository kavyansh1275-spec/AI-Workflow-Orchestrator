# AI Workflow Orchestrator

V10 is the unified end-to-end orchestration layer for an AI system that converts natural-language automation requests into structured workflow plans, selects a provider, validates integrations, generates provider artifacts, simulates execution, prepares production-style releases, and supervises workflow health.

## V10 full orchestration layer

V10 composes the capabilities built across V1-V9 into one deterministic pipeline:

1. **Understand** — interpret the natural-language request with the V5 decision engine.
2. **Decide** — select the provider and workflow strategy.
3. **Plan** — build a dependency-aware workflow.
4. **Validate** — enforce workflow and integration quality gates.
5. **Generate** — create the provider-specific artifact.
6. **Execute** — run the local credential-free runtime simulation.
7. **Release** — prepare a staging release plan without external deployment.
8. **Supervise** — evaluate health and produce autonomous monitor/retry/rollback decisions.

Every V10 run receives a unique run ID, confidence score, timestamped pipeline events, quality-gate results, and a structured result containing the outputs of the previous layers.

## Post-V10 Part 1 — Credential foundation

The first production-hardening layer now provides a secure credential abstraction for future provider adapters:

- Credentials are loaded from environment variables only.
- Secrets are never written to the repository or persisted by the manager.
- Provider readiness can be inspected without exposing secret values.
- Secret values are masked when status is displayed.
- Missing credentials produce actionable provider-specific errors.
- Supported provider configuration keys are `N8N_API_KEY`, `MAKE_API_TOKEN`, and `ZAPIER_API_TOKEN`.
- Optional provider base URLs are supported through `N8N_BASE_URL`, `MAKE_BASE_URL`, and `ZAPIER_BASE_URL`.

Example local environment configuration:

```text
N8N_API_KEY=<set locally>
N8N_BASE_URL=<your n8n API base URL>
MAKE_API_TOKEN=<set locally>
MAKE_BASE_URL=<your Make API base URL>
ZAPIER_API_TOKEN=<set locally>
ZAPIER_BASE_URL=<your Zapier API base URL>
```

Do **not** commit real credentials. GitHub's documentation explicitly warns against committing passwords or API keys to a repository. citeturn0search1

The credential layer is intentionally separate from the provider adapters: it gives future n8n/Make/Zapier integrations a common credential contract without pretending that live API deployment is already implemented.

## Safety and deployment policy

- V10 is dry-run by default.
- No external provider API calls are required by the orchestration foundation.
- Live execution remains explicitly blocked until credential-aware provider adapters are implemented and tested against the providers' current APIs.
- Autonomous actions remain recommendations/state transitions rather than uncontrolled external actions.

## Previous versions

- **V1:** Workflow foundation and planning.
- **V2:** Provider selection and dry-run deployment.
- **V3:** Natural-language workflow intelligence.
- **V4:** Provider-specific workflow generation.
- **V5:** AI decision engine and provider optimization.
- **V6:** Deterministic local execution runtime.
- **V7:** Integration capability expansion and validation.
- **V8:** Production-style releases, deployment history, health, and rollback.
- **V9:** Autonomous workflow health supervision and recovery decisions.
- **V10:** Unified end-to-end orchestration pipeline.

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

The project remains safe-by-default. V10 is the complete orchestration foundation, and Part 1 establishes the credential boundary needed before real provider deployment work begins.
