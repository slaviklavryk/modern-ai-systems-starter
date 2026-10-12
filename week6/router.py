"""Week 6 — one model call chooses the retriever; then retrieve and answer.

    from router import ask
    result = ask(driver, emb, llm, "Which parts of the course use Chroma?")
    print(result["retriever"], result["answer"])

The router is Week 5's structured output applied to a new decision: its schema allows
only the names of the four retrievers, so it cannot choose one that does not exist. It
chooses once and does not look at the result. Week 7 lets the model choose again after
seeing what a tool returned; that loop is what makes it an agent.

Measured 2026-10-06/09, two runs, re-scored 2026-10-11 on the five questions of the
course test set: the router chose a retriever that answered correctly in 6 of 10 choices.
It sent most questions to vector retrieval.
"""

from typing import Literal

from pydantic import BaseModel

from retrievers import answer, by_name, chat, hybrid, text_to_cypher, vector

# The instruction is built from two parts. DATA says what the course material is; RETRIEVERS
# says, for each retriever, what it returns and which kind of question it suits. The model
# sees only the question, so each description is about questions, not about how the
# retriever works inside. No test-set question is quoted: the router is scored on them.
DATA = ("You choose how to retrieve the information needed to answer a question about a "
        "university course. The course material is held two ways: as passages of text, and "
        "as a graph of topics, tools and deliverables extracted from it. Choose one retriever:")

RETRIEVERS = {
    "vector": "the passages nearest in meaning to the question. For a question answered by "
              "one passage: a definition, an explanation, a figure, an instruction.",
    "name":   "the graph's facts about an entity the question names exactly. For what a "
              "named topic, tool or deliverable builds on, uses or assesses.",
    "hybrid": "the nearest passages, then the graph's facts about everything they mention. "
              "For a question about how things are connected when the entities are not "
              "named exactly.",
    "cypher": "a database query written for the question. For counting, listing or "
              "comparing across the whole course.",
}


def instruction(retrievers: dict = RETRIEVERS) -> str:
    """The router's system instruction: DATA, then one line per retriever."""
    return DATA + "\n" + "\n".join(f"- {name}: {does}" for name, does in retrievers.items())


ROUTE = instruction()


class Route(BaseModel):
    # Built from the same dictionary as the descriptions, as Week 5 built extraction's
    # entity types from kg_model.py: the choices and the descriptions cannot disagree.
    retriever: Literal[tuple(RETRIEVERS)]


def route(llm, question: str, system: str = ROUTE) -> str:
    """The retriever the model chooses for this question. Pass `system` to try another
    instruction, built with `instruction()`."""
    return chat(llm, question, system=system, schema=Route).parsed.retriever


def retrieve(driver, emb, llm, question: str, retriever: str) -> dict:
    """Run one named retriever. Returns {"sources", and for cypher "query", "problem"}."""
    if retriever == "vector":
        return {"sources": vector(driver, emb, question)}
    if retriever == "name":
        return {"sources": by_name(driver, question)}
    if retriever == "hybrid":
        return {"sources": hybrid(driver, emb, question)}
    sources, query, problem = text_to_cypher(driver, llm, question)
    return {"sources": sources, "query": query, "problem": problem}


def ask(driver, emb, llm, question: str, retriever: str = None) -> dict:
    """Question in, answer out. The router chooses unless a retriever is named."""
    chosen = retriever or route(llm, question)
    result = retrieve(driver, emb, llm, question, chosen)
    result.update(retriever=chosen, answer=answer(llm, question, result["sources"]))
    return result
