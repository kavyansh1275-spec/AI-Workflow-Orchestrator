from core.orchestrator import Orchestrator


def main() -> None:
    print("AI Workflow Orchestrator - V3")
    print("Natural-language intent analysis + dependency-aware planning enabled.")
    print("Type an automation request. Type 'exit' to quit.\n")

    orchestrator = Orchestrator()

    while True:
        request = input("> ").strip()
        if request.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not request:
            continue

        try:
            intent = orchestrator.analyze(request)
            workflow = orchestrator.build(request)
            print("\nIntent:")
            print(intent)
            print("\nWorkflow:")
            print(workflow.to_pretty_json())
            print("\nDry-run deployment:")
            print(orchestrator.deploy(request, dry_run=True))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
