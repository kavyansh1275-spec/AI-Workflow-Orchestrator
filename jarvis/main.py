from .brain import JarvisBrain
from .config import load_config

def run() -> None:
    config = load_config()
    brain = JarvisBrain(config)
    print("JARVIS Skill Engine V1")
    print("Type a task, or 'exit' to quit.\n")
    while True:
        try:
            request = input("JARVIS > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if request.lower() in {"exit", "quit"}:
            return
        if request:
            print(brain.handle(request))

if __name__ == "__main__":
    run()
