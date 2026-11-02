"""The parts of the course system, as parts of one LangChain agent.

    from agent_stack import course_tools, memory_tools, search_tool, context, extract_after, ask
    tools = course_tools(driver, emb)          # the tools, by name
    agent = create_agent(model, tools=[...], middleware=[context(INSTRUCTION, retrieve=...)])
    history = ask(agent, "What distance does Chroma use by default?")
    show_context("How do we change it?", INSTRUCTION, retrieve=...)   # no model call

Two pieces of middleware decide where retrieval and memory are placed:

  context        builds the system prompt before every model call, from the instruction,
                 the examples, and, when the application rather than the model decides,
                 the recalled facts about the user and the retrieved sources.
  extract_after  after each run, one model call proposes facts about the user from the
                 user's message, and the code stores them.
"""

import functools
import operator
import pathlib
import sys
import time
from datetime import date
from typing import Callable, Literal, Optional

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week2", "week3", "week4", "week5", "week6", "week7", "week8"):
    sys.path.insert(0, str(_HERE.parent / _d))

import requests  # noqa: E402
from langchain.agents.middleware import after_agent, dynamic_prompt  # noqa: E402
from langchain.tools import tool  # noqa: E402
from langchain_core.messages.utils import count_tokens_approximately  # noqa: E402

from agent_kit import COUNTER, answer, show  # noqa: E402
from memory import EXTRACT, Memory, MemoryStore  # noqa: E402
from retrievers import by_name, read  # noqa: E402

Retriever = Callable[[str], list[str]]      # a question in, a list of sources out


# ---------------------------------------------------------------- tools
NBU = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"
OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}
DOCUMENTS_MENTIONING = """
MATCH (d:Document)-[:HAS_CHUNK]->(:Chunk)-[:MENTIONS]->(e:Entity {name: $name})
RETURN DISTINCT d.name AS document ORDER BY document"""


def course_tools(driver, emb) -> dict:
    """The tools that need no memory store, by name."""

    @tool
    def exchange_rate(currency: str) -> str:
        """The official hryvnia exchange rate set by the National Bank of Ukraine for one
        currency, given its ISO 4217 code such as EUR or USD. Use it for any question about
        a current rate."""
        rows = requests.get(f"{NBU}?valcode={currency}&json", timeout=10).json()
        if not rows:                                # an unknown code returns an empty list
            return f"No NBU rate for {currency!r}."
        r = rows[0]
        return f"1 {r['cc']} = {r['rate']} UAH, set by the NBU for {r['exchangedate']}"

    @tool
    def calculate(a: float, op: Literal["+", "-", "*", "/"], b: float) -> float:
        """Apply one arithmetic operation to two numbers. Use it for every calculation
        instead of working it out yourself."""
        return OPS[op](a, b)

    @tool
    def facts_by_name(query: str) -> str:
        """Facts from the course graph about tools, topics and labs named in the query.
        Returns nothing if the query names none."""
        facts = by_name(driver, query)
        return "\n".join(facts) if facts else "No facts: the query names nothing in the graph."

    @tool
    def documents_mentioning(name: str) -> str:
        """List the course documents that mention a tool, topic or lab, given its name as
        the course graph spells it, for example 'Chroma'."""
        rows = read(driver, DOCUMENTS_MENTIONING, name=name)
        return "\n".join(r["document"] for r in rows) or f"No documents mention {name!r}."

    return {t.name: t for t in (exchange_rate, calculate, facts_by_name, documents_mentioning)}


def search_tool(retrieve: Retriever):
    """Any retriever, offered to the model as the tool `search_course`."""

    @tool
    def search_course(query: str) -> str:
        """Search the course materials (lectures, practicals and plans) for passages and
        facts relevant to the query. Use it for any question about the course."""
        return "\n".join(retrieve(query)) or "Nothing found."

    return search_course


def memory_tools(store: MemoryStore) -> list:
    """Tools over the memory store: the model reads it, and decides what to write."""

    @tool
    def recall_memory(query: str) -> str:
        """The stored facts about the user nearest in meaning to the query. Use it when an
        answer depends on the user: their project, their setup, what they did before."""
        facts = store.recall(query, k=3)
        return "\n".join(facts) if facts else "Nothing is stored about the user."

    @tool
    def remember(fact: str) -> str:
        """Store one fact about the user that will still matter in a later conversation,
        written as one short sentence about the user. Do not store the question itself or
        anything that matters only now."""
        [fact_id] = store.add([fact], source="agent", when=str(date.today()))
        return f"Stored as {fact_id}."

    return [recall_memory, remember]


def as_result(error, request):
    """For ToolErrorMiddleware: the error, returned to the model as the tool's result."""
    return f"Error: {type(error).__name__}: {error}"


# ---------------------------------------------------------------- the context
@functools.lru_cache(maxsize=64)
def _retrieved(retrieve: Retriever, question: str) -> tuple:
    """One retrieval per question: a run may call the model several times, and each call
    builds the system prompt again."""
    return tuple(retrieve(question))


def system_prompt(question: str, instruction: str, examples=(), *,
                  retrieve: Optional[Retriever] = None,
                  store: Optional[MemoryStore] = None) -> str:
    """The system prompt for one question: the instruction and the examples, then what the
    application looked up itself. Memory and sources appear only when the application, not
    the model, retrieves them."""
    parts = [instruction]
    if examples:
        parts.append("EXAMPLES\n" + "\n\n".join(f"Question: {q}\nAnswer: {a}" for q, a in examples))
    if store is not None:
        facts = store.recall(question, k=3)
        parts.append("WHAT YOU KNOW ABOUT THE USER\n"
                     + ("\n".join(f"- {f}" for f in facts) or "(nothing stored)"))
    if retrieve is not None:
        sources = _retrieved(retrieve, question)
        parts.append("SOURCES\n" + ("\n".join(f"[{i}] {s}" for i, s in enumerate(sources, 1))
                                    or "(none found)"))
    return "\n\n".join(parts)


def context(instruction: str, examples=(), *, retrieve: Optional[Retriever] = None,
            store: Optional[MemoryStore] = None):
    """Middleware that builds the system prompt before every model call, for the latest
    question in the conversation."""

    @dynamic_prompt
    def assemble(request) -> str:
        question = next((m.text for m in reversed(request.messages) if m.type == "human"), "")
        return system_prompt(question, instruction, examples, retrieve=retrieve, store=store)

    return assemble


# ---------------------------------------------------------------- memory, written by the application
def extract_after(model, store: MemoryStore):
    """Middleware that runs once after each run: one model call proposes facts about the
    user from the user's message, as structured output, and the code stores them."""
    extractor = model.with_structured_output(Memory, method="function_calling")

    @after_agent
    def store_facts(state, runtime) -> None:
        turn = next(m.text for m in reversed(state["messages"]) if m.type == "human")
        facts = extractor.invoke([("system", EXTRACT), ("user", turn)]).facts
        ids = store.add(facts, source=turn, when=str(date.today())) if facts else []
        print(f"memory: {len(ids)} fact{'' if len(ids) == 1 else 's'} extracted and stored"
              + "".join(f"\n  {i}  {f}" for i, f in zip(ids, facts)))
        return None

    return store_facts


# ---------------------------------------------------------------- one turn
def ask(agent, question: str, history: Optional[list] = None, *, quiet: bool = False) -> list:
    """One turn: prints its steps, its answer and its model calls, and returns the whole
    conversation, to pass back as `history`.

    If LangChain summarised the earlier turns during this turn, the summary is printed first.
    The last line gives the length of the history that will be sent with the next question.
    """
    sent = list(history or []) + [{"role": "user", "content": question}]
    before, started = COUNTER.calls, time.perf_counter()
    messages = agent.invoke({"messages": sent})["messages"]
    seconds = time.perf_counter() - started
    if not quiet:
        start = max(i for i, m in enumerate(messages) if m.type == "human" and m.text == question)
        earlier = {m["content"] if isinstance(m, dict) else m.text for m in sent}
        summary = [m for m in messages[:start] if m.text not in earlier
                   and m.additional_kwargs.get("lc_source") == "summarization"]
        for m in summary:                       # made in this turn, not carried from before
            print(f"summary   {' '.join(m.text.split())[:600]}")
        *steps, last = messages[start:]
        show(steps)
        answer(last)
        calls = COUNTER.calls - before
        print(f"{calls} model call{'' if calls == 1 else 's'} in this turn ({seconds:.0f} s), "
              f"{COUNTER.calls} since the kernel started")
        if last.type == "ai" and last.response_metadata.get("model_name"):
            print(f"answered by: {last.response_metadata['model_name']}")
        print(f"history: {len(messages)} messages, about "
              f"{count_tokens_approximately(messages):,} tokens")
    return messages


def show_context(question: str, instruction: str, examples=(), *,
                 retrieve: Optional[Retriever] = None, store: Optional[MemoryStore] = None,
                 width: int = 150) -> None:
    """The system prompt `context` would build for this question, each line cut to `width`
    characters. No model call; retrieval and recall run as they would in the agent."""
    for line in system_prompt(question, instruction, examples,
                              retrieve=retrieve, store=store).splitlines():
        print(line if len(line) <= width else f"{line[:width]} … ({len(line):,} characters)")
