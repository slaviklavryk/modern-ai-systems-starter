"""Week 6 — clean the Week 5 graph before retrieving from it.

    import cleaning
    cleaning.apply()          # before resolve_results(), so the entries take effect

Week 5's `kg_model.py` holds the alias and type tables the reference extraction was
loaded with. Week 6 adds to them here rather than editing that file, so that Week 5's
code and its figures stay as they were.

Each entry was written on 2026-10-06 by reading what resolution reported for the
reference extraction (`resolved["merged"]`, `resolved["type_conflicts"]`) and checking
the corpus. As in Week 5, an entry is added only when it is certain: a wrong merge puts
a false fact into the graph, a missed one only leaves two nodes. Measured effect: 388
entities become 372, and 10 type conflicts become 2; 8 more relationships are dropped,
each one wrong (such as functions of the mathematics document typed as tools).
"""

import kg_model

# Different names for one entity: key -> key.
MORE_ALIASES = {
    "gemini embedding 001": "gemini-embedding-001",  # the same model, spelled with spaces
    "tools": "tool",
    "the prompt lab": "prompt lab",
    "openrouter-model baai-bge-m3": "baai/bge-m3",   # the same model, named through OpenRouter
    "docker desktop": "docker",                      # Docker is installed as Docker Desktop
    "ingest": "ingestion",                           # the stage and the process
    "thinking budget": "thinking dial",              # the course's name for the same setting
}

# The type of an entity returned under more than one: key -> label.
MORE_TYPES = {
    "gold set": "Deliverable",           # Week 3's graded ten-query gold set
    "evaluation seed": "Deliverable",
    "hello.py": "Tool",                  # a script students run
    "encoder network": "Topic",
    "llm-only application": "Topic",
    "baai/bge-m3": "Tool",
    "basic ramp": "Topic",               # the mathematics document; harmless either way
    "ramp function": "Topic",
    "shifted ramp": "Topic",
}


def apply() -> None:
    """Add the Week 6 entries to Week 5's tables. Running it twice changes nothing."""
    kg_model.ALIASES.update(MORE_ALIASES)
    kg_model.TYPES.update(MORE_TYPES)
