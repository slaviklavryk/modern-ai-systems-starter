"""Week 7 — a conversation over the Week 6 retrievers.

    from conversation import Conversation
    llm = LLMClient()
    talk = Conversation(llm, retrieve=lambda q: hybrid(driver, emb, q))
    talk.ask("What distance does Chroma use by default?")
    talk.ask("How do we change it?")        # a follow-up: rewritten before retrieval

The model keeps no session. A conversation is the list of earlier turns, sent again with
every call. One turn here is three steps:

    rewrite    a follow-up becomes a standalone question (one model call; skipped on turn 1)
    retrieve   the Week 6 retriever searches for the rewritten question
    answer     Week 3's grounded instruction, with the earlier turns sent before it

The history keeps the earlier questions and answers, not their sources: the lecture
measured that keeping the sources makes every later call several times longer.

Model calls go through Week 6's `chat`, which waits and retries when the backend answers
429. OpenRouter's free models do so when the provider behind them is busy.
"""

import pathlib
import sys
from dataclasses import dataclass, field
from typing import Callable, Optional

_HERE = pathlib.Path(__file__).resolve().parent
for _d in ("common", "week2", "week3", "week4", "week5", "week6"):
    sys.path.insert(0, str(_HERE.parent / _d))

from context_lab import render  # noqa: E402
from retrievers import FORMAT, SYSTEM, TASK, chat  # noqa: E402

# The lecture's instruction, unchanged.
REWRITE = ("Rewrite the user's last question so that it can be understood without the "
           "conversation. Keep its meaning. Reply with the question only.")


@dataclass(repr=False)
class Turn:
    n: int
    question: str           # as the user asked it
    searched: str           # what the retriever received: the rewrite, or the question
    memory: list[str]       # facts about the user placed before the sources
    sources: list[str]      # what the retriever returned
    prompt: str             # the user message of this call: sources, task, format, question
    answer: str
    sent: list[tuple[str, str]] = field(default_factory=list)   # the history sent with it

    def __repr__(self):
        return f"Turn {self.n}: {self.question!r} -> {self.answer[:70]!r}"


def history_of(turns: list[Turn]) -> list[tuple[str, str]]:
    """The earlier turns as messages: each question as "user", each answer as "assistant"."""
    return [m for t in turns for m in (("user", t.question), ("assistant", t.answer))]


def transcript(turns: list[Turn]) -> str:
    return "\n".join(f"User: {t.question}\nAssistant: {t.answer}" for t in turns)


def rewrite_prompt(turns: list[Turn], question: str) -> str:
    """What the rewriting call reads: the conversation so far, then the follow-up."""
    return f"{transcript(turns)}\nUser: {question}"


def rewrite(llm, turns: list[Turn], question: str) -> str:
    """The follow-up as a standalone question, written by the model from the conversation."""
    return chat(llm, rewrite_prompt(turns, question), system=REWRITE).text.strip()


def stack_of(system: str, history: list[tuple[str, str]], prompt: str) -> list[tuple[str, str, str]]:
    """Every message one call sends, in order, as (role, part of the context, text).

    The role is what the API receives: "system", "user", or "assistant", which marks the
    model's own earlier reply. The part says what the message is for.
    """
    stack = [("system", "instruction", system)]
    for i, (role, text) in enumerate(history):
        whose = "the user's message" if role == "user" else "the model's answer"
        stack.append((role, f"history · turn {i // 2 + 1}, {whose}", text))
    stack.append(("user", "this turn · sources, task, format, question", prompt))
    return stack


def show_call(system: str, history: list[tuple[str, str]], prompt: str, *, full: bool = True) -> None:
    """Print the messages one call sends, in order: in full, or one line each."""
    stack = stack_of(system, history, prompt)
    if not full:
        for role, part, text in stack:
            print(f"  {role:10} {part:46} {len(text):>6,} characters")
        return
    for role, part, text in stack:
        print(f"──── {role} │ {part} ({len(text):,} characters)")
        print(text)
    print("────")


class Conversation:
    """One conversation: its turns, and how each new turn is retrieved and answered.

    retrieve:  question -> sources, e.g. a Week 6 retriever
    rewrite:   rewrite follow-ups before retrieval (Part 2)
    memory:    question -> facts about the user, placed before the sources (Part 4)
    """

    def __init__(self, llm, retrieve: Callable[[str], list[str]], *, rewrite: bool = True,
                 memory: Optional[Callable[[str], list[str]]] = None):
        self.llm, self.retrieve = llm, retrieve
        self.rewrites, self.memory = rewrite, memory
        self.turns: list[Turn] = []

    def ask(self, question: str, *, show: Optional[str] = None) -> Turn:
        """One turn, logged in order: the question; its rewrite, if any; the facts about
        the user, if any; the messages sent, with show="stack" (one line each) or "full"
        (their whole text); and the answer."""
        if show not in (None, "stack", "full"):
            raise ValueError("show is 'stack', 'full', or None")
        n = len(self.turns) + 1
        print(f"════ turn {n} " + "═" * 60)
        _log("question", question)

        # 1. Rewrite a follow-up as a standalone question (the first turn has no history).
        searched = question
        if self.rewrites and self.turns:
            searched = rewrite(self.llm, self.turns, question)
            _log("rewritten", f"{searched}\n(what the retriever searched for; the model is "
                              "still asked the question above)")

        # 2. Memory: the facts about the user this turn receives, if there is memory.
        facts = self.memory(searched) if self.memory else []
        if self.memory:
            _log("memory", "\n".join(facts) or "(no facts)")

        # 3. Retrieve sources for the rewritten question; the user's facts go first.
        sources = [f"About the user: {f}" for f in facts] + self.retrieve(searched)

        # 4. Context: the history, then this turn's prompt with the question as asked.
        prompt = render(question, task=TASK, fmt=FORMAT, sources=sources)
        history = history_of(self.turns)
        if show:
            held = f"{len(history)} history messages" if history else "no history"
            _log("context", f"one request to the model: the instruction, {held}, this turn's prompt")
            show_call(SYSTEM, history, prompt, full=show == "full")

        # 5. Answer: one call with the instruction, the history, and this turn's prompt.
        answer = chat(self.llm, prompt, system=SYSTEM, history=history).text
        _log("answer", answer)
        print()

        # 6. Keep the turn: the next call sends its question and answer as history.
        turn = Turn(n, question, searched, facts, sources, prompt, answer, history)
        self.turns.append(turn)
        return turn


def _log(label: str, text: str) -> None:
    """One labelled entry of a turn's log; later lines of the text are indented under it."""
    first, *rest = text.splitlines() or [""]
    print(f"{label:10} {first}")
    for line in rest:
        print(f"{'':10} {line}")
