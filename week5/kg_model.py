"""Week 5 — the declared model of the course knowledge graph, written down once.

    from kg_model import ENTITY_TYPES, EXTRACTED_TYPES, STRUCTURAL_TYPES, key

Everything else this week reads its types from here: the extraction schema
(`extraction.py`) builds its `Literal` types from these dictionaries, and the
loader (`kg_loader.py`) refuses any relationship type that is not listed. A model
written in three places drifts; a model written in one place cannot.

The graph is built from the documents alone
-------------------------------------------
Nothing is written by hand. The text layer comes from chunking the Week 3 sample
corpus, exactly as Week 3 chunked it:

    (:Document)-[:HAS_CHUNK]->(:Chunk)-[:NEXT]->(:Chunk)
    (:Document)-[:FOR_WEEK]->(:Week)        the week, read from the file name

Everything else comes from extraction. A chunk mentions entities, and states
relationships between them:

    (:Chunk)-[:MENTIONS]->(:Topic | :Tool | :Deliverable)
    (:Topic)-[:BUILDS_ON]->(:Topic)         a topic requires another
    (:Topic)-[:USES]->(:Tool)               a topic is taught or done with a tool
    (:Deliverable)-[:ASSESSES]->(:Topic)    a lab or project assesses a topic

Every extracted relationship records the chunks that state it, each id once:

    r.chunks = [ids]

That list is what lets an answer built on the relationship cite its source.
"""

import re

# Entity types extraction may return: label -> the property each is merged on.
ENTITY_TYPES = {"Topic": "name", "Tool": "name", "Deliverable": "name"}

# Relationship types extraction may return: type -> (from label, to label).
EXTRACTED_TYPES = {
    "BUILDS_ON": ("Topic", "Topic"),
    "USES": ("Topic", "Tool"),
    "ASSESSES": ("Deliverable", "Topic"),
}

# Relationships the loader writes itself, never extraction. Listed so that the
# loader's check covers every type it writes.
STRUCTURAL_TYPES = {
    "HAS_CHUNK": ("Document", "Chunk"),
    "NEXT": ("Chunk", "Chunk"),
    "FOR_WEEK": ("Document", "Week"),
    "MENTIONS": ("Chunk", "Topic, Tool or Deliverable"),
}

DECLARED_TYPES = {**EXTRACTED_TYPES, **STRUCTURAL_TYPES}

# Resolution decides two things: which names are one entity, and what type it is.
# Both tables were written on 2026-10-04 by reading what the reference extraction
# (extractions/course_corpus.json) returned. A wrong merge puts a false fact into
# the graph; a missed one only leaves two nodes where there should be one. So an
# entry is added only when it is certain, and most of the 428 entities are left
# as extraction returned them.

# Different names for one entity, which key() alone cannot merge: key -> key.
ALIASES = {
    # deliverables, named with their titles or by an older name
    "lab 1 - vector rag": "lab 1",
    "lab 2 - knowledge graph and graph rag": "lab 2",
    "lab 2 - knowledge graph / graph rag": "lab 2",
    "lab 3 - agent, tools, memory": "lab 3",
    "final integrated project": "final project",
    "milestone 0 - project proposal": "project proposal",
    "milestone 0 proposal": "project proposal",
    # tools
    "chromadb": "chroma",
    "gemini-3.5-flash": "gemini 3.5 flash",
    "starter-repo": "starter repository",
    "openrouter's baai-bge-m3": "baai/bge-m3",
    # topics: singular and plural, abbreviation and full name, title and name
    "rag": "retrieval-augmented generation",
    "retrieval augmented generation": "retrieval-augmented generation",
    "embedding": "embeddings",
    "token": "tokens",
    "transformer": "transformers",
    "large language model": "llm",
    "chunking a corpus": "chunking",
    "system instructions": "system instruction",
    "thoughts_token_count": "thoughts token count",
    "the modern ai application stack": "ai application stack",
}

# The type of an entity that extraction returned under more than one: key -> label.
# A relationship whose end then has the wrong type for the relationship (a Tool at
# the end of a BUILDS_ON, say) is dropped, and reported.
TYPES = {
    "chroma": "Tool", "neo4j": "Tool", "docker": "Tool", "faiss": "Tool",
    "mariadb": "Tool", "postgresql": "Tool", "gemini-embedding-001": "Tool",
    "claude": "Tool", "gpt": "Tool", "vectorstore": "Tool",
    "lab 1": "Deliverable", "lab 2": "Deliverable", "project proposal": "Deliverable",
    "retrieval-augmented generation": "Topic",
}


def key(name: str) -> str:
    """The form two names must share to be the same entity.

    Lower case, one kind of dash, single spaces, no punctuation at either end.
    "Retrieval-Augmented Generation" and "retrieval-augmented generation." share
    a key; "Embedding" and "Embeddings" do not, and need an alias.
    """
    k = re.sub(r"[‐-―]", "-", name.lower())
    k = " ".join(k.split()).strip(" .,;:!?\"'()[]")
    return ALIASES.get(k, k)
