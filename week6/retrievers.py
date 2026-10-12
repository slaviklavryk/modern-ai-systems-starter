"""Week 6 — four ways to retrieve from the course graph, and one way to answer.

    from retrievers import vector, by_name, hybrid, text_to_cypher, answer
    sources = hybrid(driver, emb, question)       # numbered sources, each with its chunks
    print(answer(llm, question, sources))         # Week 3's grounded instruction, unchanged

Each retriever turns a question into a list of sources: passages, or facts that carry the
ids of the chunks stating them, so that every claim in an answer can be traced to text.

    vector          the passages nearest in meaning (Week 3's retriever)
    by_name         the facts about entities the question names exactly
    hybrid          the nearest passages, plus the facts about everything they mention
    text_to_cypher  rows of a query the model writes, run in a read-only transaction

Every retriever reads through a read-only transaction (`read`), so none can write to the
graph, whatever its query says. For the three whose queries we wrote this is a precaution;
for text_to_cypher, whose query the model writes, it is the safeguard that matters.

Measured 2026-10-07/09 on the course test set (five questions, two runs, 10 answers
each, correct / partly / wrong / silent when an answer exists; re-scored 2026-10-11 when
the set was cut from ten questions; Q3 measured 2026-10-11): hybrid 6/2/1/1, vector
4/4/2/0, by_name 4/2/2/2, text_to_cypher 4/2/1/3 (queries then written by gpt-5-nano).
See `evaluate.py`.
"""

import json
import pathlib
import re
import sys
import time

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week2", "week3", "week4", "week5"):
    sys.path.insert(0, str(_HERE.parent / _d))
sys.path.insert(0, str(_HERE))

from neo4j import unit_of_work  # noqa: E402
from pydantic import BaseModel  # noqa: E402

import kg_model  # noqa: E402
from context_lab import render  # noqa: E402
from llm_client import LLMClient  # noqa: E402
from vector_check import INDEX, require_same_model  # noqa: E402

# Week 3's grounded instruction, unchanged.
SYSTEM = ("You answer questions using only the sources you are given. If the sources do "
          "not answer the question, reply exactly: not stated. Never fill a gap from your "
          "own knowledge.")
TASK = "Answer the question using only the SOURCES above."
FORMAT = "Two sentences maximum. Put the source number in square brackets after each claim."

VERB = {"BUILDS_ON": "builds on", "USES": "uses", "ASSESSES": "assesses"}
MAX_FACTS = 25     # facts handed to the model at most; more cost tokens and bury the answer


# ---------------------------------------------------------------- reading the graph
def read(driver, query: str, **params) -> list[dict]:
    """Week 4's `run`, in a read-only transaction: the database refuses any write.

    Measured 2026-10-11 on Neo4j 5.26 Community: CREATE, SET and apoc.create.node were
    each refused with "Writing in read access mode not allowed"; nothing was written.
    Vector search (`db.index.vector.queryNodes`) works as before.
    """
    records, _summary, _keys = driver.execute_query(query, parameters_=params, routing_="r")
    return [record.data() for record in records]


def cypher_text(query: str, **params) -> str:
    """The query with its parameters written in, to read or to paste into Neo4j Browser."""
    for name, value in params.items():
        query = query.replace(f"${name}", json.dumps(value, ensure_ascii=False))
    return query


# ---------------------------------------------------------------- the model call
def chat(llm, prompt, **kwargs):
    """llm.chat, waiting and retrying when Lightning rate-limits.

    Measured 2026-10-07: about 28 calls in quick succession return HTTP 429; a wait of
    20 seconds was enough each time.
    """
    for delay in (20, 40, 80, 160):
        try:
            return llm.chat(prompt, **kwargs)
        except Exception as exc:
            if "429" not in str(exc):
                raise
            print(f"  rate-limited; waiting {delay}s")
            time.sleep(delay)
    return llm.chat(prompt, **kwargs)


def answer(llm, question: str, sources: list[str]) -> str:
    """Answer from the sources alone, citing them by number. No sources, no call."""
    if not sources:
        return "not stated (no sources)"
    return chat(llm, render(question, task=TASK, fmt=FORMAT, sources=sources), system=SYSTEM).text


# ---------------------------------------------------------------- shared steps
def nearest_chunks(driver, emb, question: str, k: int = 3) -> list[dict]:
    """The k chunks nearest in meaning. Fetches 50 and keeps k, since the index is
    approximate at small k (Week 4: 85% of the exact top 5 at k=5, 97.5% at k=50)."""
    require_same_model(driver, emb)
    vector_ = emb.embed(question, task_type="RETRIEVAL_QUERY")
    return read(driver, f"""
        CALL db.index.vector.queryNodes('{INDEX}', 50, $v) YIELD node, score
        RETURN node.id AS id, node.text AS text ORDER BY score DESC LIMIT $k""", v=vector_, k=k)


# Graph by name runs two queries: every entity name (the matching is done in Python, by
# kg_model.key), then the facts touching the names found.
ENTITY_NAMES = "MATCH (e:Entity) RETURN e.name AS name"

FACTS = """UNWIND $names AS n
MATCH (e:Entity {name: n})-[r:BUILDS_ON|USES|ASSESSES]-()
RETURN DISTINCT startNode(r).name AS a, type(r) AS rel, endNode(r).name AS b,
       r.chunks AS chunks
ORDER BY a, b"""


def facts_about(driver, names: list[str]) -> list[str]:
    """Every extracted fact touching these entities, as a sentence naming its chunks."""
    rows = read(driver, FACTS, names=names)
    return [f"{r['a']} {VERB[r['rel']]} {r['b']}. (stated in {', '.join(r['chunks'])})"
            for r in rows][:MAX_FACTS]


def named_entities(driver, question: str) -> list[str]:
    """The graph's entities whose key occurs in the question as whole words.

    The same key as resolution (`kg_model.key`), so "embeddings" finds "Embedding" through
    the alias table. Where one match lies inside a longer one, the longer wins.
    """
    q = " " + " ".join(re.sub(r"[^\w\s./-]", " ", question.lower()).split()) + " "
    names = [r["name"] for r in read(driver, ENTITY_NAMES)]
    hits = [n for n in names if f" {kg_model.key(n)} " in q]
    return [n for n in hits
            if not any(kg_model.key(n) != kg_model.key(o) and kg_model.key(n) in kg_model.key(o)
                       for o in hits)]


# ---------------------------------------------------------------- the retrievers
def vector(driver, emb, question: str) -> list[str]:
    """Week 3's retriever: the three nearest passages."""
    return [f"{c['text']} (chunk {c['id']})" for c in nearest_chunks(driver, emb, question)]


def by_name(driver, question: str) -> list[str]:
    """The facts about the entities the question names. Silent when it names none."""
    return facts_about(driver, named_entities(driver, question))


def hybrid(driver, emb, question: str) -> list[str]:
    """The three nearest passages, then the facts about every entity they mention."""
    chunks = nearest_chunks(driver, emb, question)
    mentioned = read(driver, """
        UNWIND $ids AS id MATCH (:Chunk {id: id})-[:MENTIONS]->(e:Entity)
        RETURN collect(DISTINCT e.name) AS names""", ids=[c["id"] for c in chunks])[0]["names"]
    return [f"{c['text']} (chunk {c['id']})" for c in chunks] + facts_about(driver, mentioned)


# ---------------------------------------------------------------- text-to-Cypher
PROPERTIES = {"Document": ["name", "kind"], "Chunk": ["id", "text", "source"],
              "Week": ["number"], **{label: ["name"] for label in kg_model.ENTITY_TYPES}}


def schema_text() -> str:
    """The graph's schema for the prompt, generated from kg_model.py so it cannot drift."""
    nodes = "\n".join(f"  (:{label} {{{', '.join(props)}}})" for label, props in PROPERTIES.items())
    entities = "|".join(kg_model.ENTITY_TYPES)
    declared = {**kg_model.STRUCTURAL_TYPES, **kg_model.EXTRACTED_TYPES,
                "MENTIONS": ("Chunk", entities)}      # kg_model writes this end in words
    rels = "\n".join(f"  (:{frm})-[:{t}]->(:{to})" for t, (frm, to) in declared.items())
    return (f"Nodes and their properties:\n{nodes}\nRelationships:\n{rels}\n"
            f"Every {', '.join(kg_model.EXTRACTED_TYPES)} relationship has r.chunks: the ids "
            "of the chunks that state it. Chunk ids look like 'week-03-lecture.md#7'.")


WRITE = f"""You write one Cypher query for Neo4j 5 that retrieves what is needed to answer
a question about a university course, from this graph:

{schema_text()}

Rules:
- Read only: MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY, LIMIT, count, collect.
- Use only the labels, relationship types and properties listed above.
- Entity names were extracted from text and their exact spelling is unknown: match them
  with toLower(n.name) CONTAINS a lower-case word from the question, never with equality.
- Return the evidence, not only a count: include names, and r.chunks or chunk ids where
  they exist, so that the answer can cite them.
- Start the pattern from the entity the question names, and follow relationships out
  from it. Use MATCH, not OPTIONAL MATCH: rows without the entity are not evidence.
- Prefer one MATCH and one RETURN; add WITH only when the question needs it.

Example. Question: Where is Docker discussed?
MATCH (e:Tool)<-[:MENTIONS]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
WHERE toLower(e.name) CONTAINS 'docker'
RETURN e.name AS tool, d.name AS document, collect(c.id) AS chunks"""


class CypherQuery(BaseModel):
    query: str


# The model that writes the query. Measured 2026-10-11 on the test set (two runs each):
# under the earlier instruction gpt-5-nano began with OPTIONAL MATCH from every document in
# 5 of 10 queries; under this one it guessed labels (Chroma as a Topic) and found the right
# four documents for the counting question in 0 of 2 runs. gpt-5-mini found them in 2 of 2,
# at about 13 s per question against nano's 6.
# Answers are still written by the llm passed in, as for the other retrievers.
WRITER_MODEL = "openai/gpt-5-mini"
_writers = {}


def writer_for(llm):
    """A client for WRITER_MODEL on the same provider (Lightning only); else llm itself."""
    if llm.provider != "lightning":
        return llm
    if WRITER_MODEL not in _writers:
        _writers[WRITER_MODEL] = LLMClient(provider="lightning", model=WRITER_MODEL)
    return _writers[WRITER_MODEL]


@unit_of_work(timeout=5)
def _read(tx, cypher, limit):
    return [r.data() for r in tx.run(cypher)][:limit]


def text_to_cypher(driver, llm, question: str, *, limit: int = 50,
                   attempts: int = 2, writer=None) -> tuple[list[str], str, str]:
    """The model writes a query; it runs read-only, within 5 seconds and 50 rows.

    The query is written by `writer`, by default WRITER_MODEL (see above).

    The query is not inspected before it runs. The read-only transaction is the
    safeguard: the database refuses any write, whatever the query says (measured
    2026-10-06 and 2026-10-11 on Neo4j 5.26 Community, APOC's writing procedures
    included). The timeout and the row cap bound what a valid query can cost.

    A query the database rejects (a syntax error, an undefined variable) is sent back
    to the model with the database's message, once: the error names the fault exactly.

    Returns (sources, query, problem): problem is None when the last query ran, else the
    database's reason. Generated queries sometimes contain literal backslash-n sequences
    (4 of 20 measured); they are turned into line breaks before running.
    """
    writer = writer or writer_for(llm)
    prompt = question
    for attempt in range(attempts):
        query = chat(writer, prompt, system=WRITE, schema=CypherQuery).parsed.query
        query = query.replace("\\n", "\n").strip().rstrip(";")
        problem, rows = None, []
        try:
            with driver.session() as s:
                rows = s.execute_read(_read, query, limit)
            break
        except Exception as exc:
            problem = str(exc).splitlines()[0][:200]
            print(f"  query rejected: {problem}")
            prompt = (f"{question}\n\nYour previous query:\n{query}\n\nNeo4j rejected it:\n"
                      f"{problem}\n\nWrite a corrected query.")
    sources = [str(r)[:400] for r in rows]
    return sources, query, problem
