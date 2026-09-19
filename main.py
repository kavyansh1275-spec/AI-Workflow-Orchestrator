from core.orchestrator import Orchestrator
from core.v10 import V10Engine


def _clarification_prompt(missing: str) -> str:
    prompts = {
        "email recipient": "What email address should receive the notification?",
        "destination channel": "Which channel should receive the message?",
        "Notion destination": "Which Notion destination should receive the page?",
    }
    return prompts.get(missing, f"Please provide: {missing}.")


def main() -> None:
    print("AI Workflow Orchestrator - V10")
    print("Unified end-to-end AI workflow pipeline with quality gates, runtime, releases, and autonomous supervision.")
    print("Safe dry-run mode is enabled. Type 'exit' to quit.\n")

    engine = V10Engine(Orchestrator())

    while True:
        request = input("> ").strip()
        if request.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not request:
            continue

        try:
            decision = engine.orchestrator.decide(request)
            missing = decision.get("requirements", {}).get("missing", [])
            answers = {}
            for item in missing:
                answer = input(f"AI Workflow Orchestrator: {_clarification_prompt(item)} ").strip()
                if not answer:
                    raise ValueError(f"missing required clarification: {item}")
                answers[item] = answer

            run = engine.run(
                request,
                environment="staging",
                dry_run=True,
                clarification_answers=answers,
            )
            print("\nV10 Run:")
            print(run.model_dump_json(indent=2))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
