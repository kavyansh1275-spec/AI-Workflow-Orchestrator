from core.orchestrator import Orchestrator


def main() -> None:
    print("AI Workflow Orchestrator - V4")
    print("Natural-language understanding + provider-specific workflow generation enabled.")
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
            generated = orchestrator.generate(request)

            print("\nIntent:")
            print(intent)
            print("\nWorkflow:")
            print(workflow.to_pretty_json())
            print("\nGenerated provider artifact (dry-run):")
            print(generated)
            print("\nDry-run deployment:")
            print(orchestrator.deploy(request, dry_run=True))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
