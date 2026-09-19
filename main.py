from core.orchestrator import Orchestrator
from core.v10 import V10Engine


def _clarification_prompt(missing: str) -> str:
    prompts = {
        "email recipient": "What email address should receive the notification?",
        "business owner email": "What email address should receive the business-owner alert?",
        "destination channel": "Which channel should receive the message?",
        "team notification channel": "Which Slack channel should receive the team alert?",
        "Notion destination": "Which Notion destination should receive the page?",
        "follow-up task destination": "Where should follow-up tasks be created?",
        "Google Sheets destination": "Which Google Sheet should store the orders?",
        "order database": "Which Airtable base or database should store the orders?",
        "order source": "What webhook or order source should trigger the workflow?",
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
    import sys

    if "--cli" in sys.argv:
        main()
    else:
        from gui import launch
        launch()
