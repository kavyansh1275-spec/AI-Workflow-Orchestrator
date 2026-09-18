# JARVIS Skill Engine

JARVIS is being built as a modular assistant with a core brain, memory, planner, skill router, specialized skills and tool integrations.

## V1 foundation
- 31+ registered skills
- keyword-based skill routing
- bounded planning
- in-memory conversation skill history
- SQLite memory foundation
- dry-run execution
- unit tests

## Run
From the repository root:

python -m jarvis.main

## Test
python -m unittest discover -s jarvis/tests -v

The current release is intentionally dry-run. Real browser, terminal, GitHub, Blender and model tools will be connected incrementally with verification gates.
