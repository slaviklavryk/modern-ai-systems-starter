"""Week 7 — memory: facts about the user, written by the application, kept across
conversations.

    from memory import MemoryStore, extract
    facts = extract(llm, turn_text)                       # one model call, structured output
    store = MemoryStore()                                 # week7/chroma/, a collection of its own
    ids = store.add(facts, source=turn_text, when="2026-10-17")
    store.mark_profile(ids)                               # these facts go in every context
    store.profile()                                       # explicit: the facts for every call
    store.recall("Which embedding model should I use?")   # retrieved: the facts nearest the question
    store.replace(ids[0], "a newer fact", source=..., when=...)
    store.delete(ids[1])

The application decides what is stored: the model only proposes facts, through a schema,
and the code writes them with the turn they came from and the date. Tools, with which a
model could decide to store something itself, are Week 8.

The store is Week 3's VectorStore holding facts instead of chunks, in its own folder,
apart from the graph, which the Week 6 setup step rebuilds. Two additions: each fact gets
an id that is never reused, so that a fact can be replaced or deleted; and a fact can be
marked as part of the profile.
"""

import pathlib
import sys
import uuid
from typing import Optional

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week3"):
    sys.path.insert(0, str(_HERE.parent / _d))

from pydantic import BaseModel  # noqa: E402

from vector_store import VectorStore  # noqa: E402


class Memory(BaseModel):
    facts: list[str]


# The lecture's instruction, unchanged.
EXTRACT = ("From the user's message, list the facts about the user that will still be "
           "useful in a later conversation. Leave out the question itself and anything "
           "that matters only now. Write each fact as one short sentence about the user.")


def extract(llm, turn: str) -> list[str]:
    """The facts worth remembering from one user turn. One model call."""
    return llm.chat(turn, system=EXTRACT, schema=Memory).parsed.facts


class MemoryStore(VectorStore):
    """Facts about one user, each with its source, the date it was stored, and whether it
    belongs to the profile."""

    def __init__(self, embedder=None, name: str = "memory", *, reset: bool = False):
        super().__init__(embedder, name, path=str(_HERE / "chroma"), reset=reset)

    def add(self, facts: list[str], *, source: str, when: str, profile: bool = False) -> list[str]:
        """Embed and store facts; returns one id per fact. A fact already stored word for
        word keeps its id and is not stored again, so re-running a cell adds nothing.
        (VectorStore numbers ids by count, which would reuse an id after a delete.)"""
        ids = {f["fact"]: f["id"] for f in self.all()}
        new = [fact for fact in dict.fromkeys(facts) if fact not in ids]
        if new:
            new_ids = [uuid.uuid4().hex[:8] for _ in new]
            vectors = self.embedder.embed_batch(new, task_type="RETRIEVAL_DOCUMENT")
            metadatas = [{"source": source, "when": when, "profile": profile} for _ in new]
            self._collection.add(ids=new_ids, embeddings=vectors, documents=new, metadatas=metadatas)
            ids.update(zip(new, new_ids))
        return [ids[fact] for fact in facts]

    def all(self) -> list[dict]:
        got = self._collection.get(include=["documents", "metadatas"])
        return [{"id": i, "fact": doc, **meta}
                for i, doc, meta in zip(got["ids"], got["documents"], got["metadatas"])]

    def mark_profile(self, fact_ids: list[str], profile: bool = True) -> None:
        """Put stored facts in the profile, or take them out. Their text is unchanged."""
        got = self._collection.get(ids=fact_ids, include=["metadatas"])
        self._collection.update(ids=got["ids"],
                                metadatas=[{**meta, "profile": profile} for meta in got["metadatas"]])

    def profile(self) -> list[str]:
        """Explicit memory: the facts placed in every context, whatever the question."""
        return [f["fact"] for f in self.all() if f["profile"]]

    def recall(self, question: str, k: int = 3) -> list[str]:
        """Retrieved memory: the k facts nearest in meaning to the question."""
        k = min(k, self.count())
        return [h["chunk"] for h in self.search(question, n_results=k)] if k else []

    def replace(self, fact_id: str, fact: str, *, source: str, when: str,
                profile: Optional[bool] = None) -> None:
        """A newer fact in place of an old one: same id, new text, source and date."""
        old = self._collection.get(ids=[fact_id], include=["metadatas"])
        if not old["ids"]:
            raise KeyError(f"no fact with id {fact_id}")
        keep = old["metadatas"][0]["profile"] if profile is None else profile
        self._collection.update(
            ids=[fact_id], documents=[fact],
            embeddings=[self.embedder.embed(fact, task_type="RETRIEVAL_DOCUMENT")],
            metadatas=[{"source": source, "when": when, "profile": keep}])

    def delete(self, fact_id: str) -> None:
        self._collection.delete(ids=[fact_id])


# ------------------------------------------------- the lecture's stale-memory prompts
ASSIST = ("You are the course assistant. Use what you know about the user when it helps. "
          "Two sentences maximum.")


def about_user(facts: list[dict], question: str, *, today: Optional[str] = None) -> str:
    """What the model is told about the user, then the question. With `today`, every fact
    carries the date it was stored, and the prompt states today's."""
    if today is None:
        lines = [f"- {f['fact']}" for f in facts]
        head = ""
    else:
        lines = [f"- (stored in {f['when']}) {f['fact']}" for f in facts]
        head = f"TODAY: {today}\n"
    return f"{head}WHAT YOU KNOW ABOUT THE USER\n" + "\n".join(lines) + f"\n\nQUESTION\n{question}"
