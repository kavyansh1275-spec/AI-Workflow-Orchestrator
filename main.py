from core.orchestrator import Orchestrator
from core.v10 import V10Engine


def main() -> None:
    print("AI Workflow Orchestrator - V10")
    print("Unified end-to-end AI workflow pipeline with quality gates, runtime, releases, and autonomous supervision.")
    print("Safe dry-run mode is enabled. Type an automation request. Type 'exit' to quit.\n")

    engine = V10Engine(Orchestrator())

    while True:
        request = input("> ").strip()
        if request.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not request:
            continue

        try:
            run = engine.run(request, environment="staging", dry_run=True)
            print("\nV10 Run:")
            print(run.model_dump_json(indent=2))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
