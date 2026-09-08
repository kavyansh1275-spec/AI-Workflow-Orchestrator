# AI Workflow Orchestrator

V9 of an AI system that converts natural-language automation requests into structured, dependency-aware workflow plans, selects an automation provider, validates integrations, generates provider artifacts, safely executes workflows, prepares production-style releases, and autonomously supervises workflow health and recovery decisions.

## V9 autonomous management layer

- Monitor workflow health from execution results.
- Maintain workflow supervision state and consecutive failure counts.
- Automatically decide between monitor, retry, and rollback actions.
- Trigger rollback decisions after three consecutive reported failures.
- Generate unique decision IDs, confidence scores, reasons, timestamps, and metadata.
- Expose autonomous supervision through the orchestrator and CLI.
- Keep all autonomous decisions deterministic and dry-run by default.
- Do not perform live external provider actions automatically.

## Previous versions

- **V1:** Workflow foundation and planning.
- **V2:** Provider selection and dry-run deployment.
- **V3:** Natural-language workflow intelligence.
- **V4:** Provider-specific workflow generation.
- **V5:** AI decision engine and provider optimization.
- **V6:** Deterministic local execution runtime.
- **V7:** Integration capability expansion and validation.
- **V8:** Production-style releases, deployment history, health, and rollback.

## Run

```bash
python main.py
```

## Test

```bash
python -m unittest discover -s tests -v
```

V9 remains credential-free and safe-by-default. Autonomous decisions are recommendations/state transitions only; live provider execution is intentionally deferred to the final production versions.