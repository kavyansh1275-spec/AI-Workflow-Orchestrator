# JARVIS Skill Engine

JARVIS is a modular assistant with a core brain, memory, planner, skill router, AI provider layer, specialized skills and tool integrations.

## V1 foundation
- 31+ registered skills
- keyword-based skill routing
- bounded planning
- in-memory conversation skill history
- SQLite memory foundation
- dry-run execution
- unit tests

## V2 AI brain
- provider abstraction
- Gemini support when `GEMINI_API_KEY` and the optional `google-genai` package are available
- automatic local fallback when Gemini is unavailable
- configurable provider/model
- AI response attached to the routed plan
- no API keys are stored in the repository

## Run

From the repository root:

```bash
python -m jarvis.main
```

For a dependency-free local run:

```text
set JARVIS_PROVIDER=local
python -m jarvis.main
```

To use Gemini, install `google-genai` and set `GEMINI_API_KEY` in your environment. Never commit the key.

## Test

```bash
python -m unittest discover -s jarvis/tests -v
```

JARVIS remains in dry-run mode until execution tools are added and verified. The next versions will add persistent memory, research, programming tools, computer control, creative tools, business workflows and autonomous verification incrementally.
