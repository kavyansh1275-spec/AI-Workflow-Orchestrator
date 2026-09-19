from __future__ import annotations

import json
import sys

from brain import JarvisBrain


def main() -> None:
    print("JARVIS — AI Engineering & Operations")
    print("Flow: interface → main.py → brain.py → skill/tool → execution → result")
    print("Type 'exit' to quit. Safe external actions remain gated.\n")

    brain = JarvisBrain()

    while True:
        request = input("JARVIS > ").strip()
        if request.lower() in {"exit", "quit"}:
            print("JARVIS: Goodbye!")
            break
        if not request:
            continue
        try:
            result = brain.execute(
                request,
                emit=lambda event: print(
                    f"[{event.stage.upper():10}] {event.status:10} {event.message}"
                ),
            )
            print("\nRESULT:")
            print(json.dumps(result, indent=2, default=str))
            print()
        except Exception as exc:
            print(f"JARVIS ERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    # CLI remains available for debugging; the normal entry point is the GUI.
    if "--cli" in sys.argv:
        main()
    else:
        from gui import launch
        launch()
