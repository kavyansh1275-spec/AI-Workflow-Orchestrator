from core.orchestrator import Orchestrator


def main() -> None:
    print("AI Workflow Orchestrator - V1")
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
            workflow = orchestrator.build(request)
            print(workflow.to_pretty_json())
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
