"""Week 8 — helpers for the agent notebook: the model, and a view of what the agent did.

    from agent_kit import openrouter_model, definition, ask
    model = openrouter_model()                          # LangChain's chat model, on OpenRouter
    agent = create_agent(model, tools=[exchange_rate], system_prompt=SYSTEM)
    print(definition(exchange_rate))                    # what the model is told about a tool
    history = ask(agent, "What is the hryvnia rate for the euro?")
    history = ask(agent, "And for the dollar?", history)    # the same conversation

The agent is LangChain's `create_agent`, which runs the loop of the lecture. The tools are
written in the notebook, where the agent is built one step at a time; this module only
connects the model and prints what happened.

`ask` prints one turn's steps in the order they were exchanged, one line each, then the
answer in full under a rule of its own, and the number of model calls the turn made. Every
model call is one request to OpenRouter, and free models allow 50 a day.
"""

import json
import os
import pathlib
import sys
import textwrap
from typing import Optional

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "common"))

from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402
from langchain_core.utils.function_calling import convert_to_openai_tool  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402

from llm_client import LLMClient  # noqa: E402

OPENROUTER = "https://openrouter.ai/api/v1"
WIDTH = 220          # characters of a step printed; the model receives all of it
WRAP = 90            # characters per line of a printed answer
LIMIT_REACHED = "Model call limits exceeded"     # how ModelCallLimitMiddleware ends a run


class _CallCounter(BaseCallbackHandler):
    """Counts model calls: LangChain reports each one before it is sent."""

    def __init__(self):
        self.calls = 0

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.calls += 1


COUNTER = _CallCounter()


def openrouter_model(model: Optional[str] = None) -> ChatOpenAI:
    """LangChain's chat model on OpenRouter, with the course's pinned free model.

    OpenRouter speaks the OpenAI-compatible format, so LangChain's `ChatOpenAI` is pointed
    at OpenRouter's address. The model id is read from common/llm_client.py, so that it is
    pinned in one place. A 429 (a busy free model) is retried; a request that has not
    answered in 120 s is abandoned, so that a stalled call cannot freeze the kernel.
    """
    pinned = LLMClient(provider="openrouter").model       # also checks OPENROUTER_API_KEY
    return ChatOpenAI(model=model or pinned, base_url=OPENROUTER,
                      api_key=os.environ["OPENROUTER_API_KEY"],
                      timeout=120, max_retries=6, callbacks=[COUNTER])


def definition(tool) -> str:
    """The tool's definition exactly as it is sent to the model, as JSON."""
    return json.dumps(convert_to_openai_tool(tool), indent=2, ensure_ascii=False)


def ask(agent, question: str, history: Optional[list] = None, *, quiet: bool = False) -> list:
    """One turn: the conversation so far, then the question.

    Prints this turn's steps, then its answer in full, and the model calls it made, and
    returns the whole conversation. Pass it back as `history` to continue the same
    conversation; leave `history` out to start a new one, with an empty history.
    """
    sent = list(history or []) + [{"role": "user", "content": question}]
    before = COUNTER.calls
    messages = agent.invoke({"messages": sent})["messages"]
    if not quiet:
        *steps, last = messages[len(sent) - 1:]
        show(steps)
        answer(last)
        calls = COUNTER.calls - before
        print(f"{calls} model call{'' if calls == 1 else 's'} in this turn, "
              f"{COUNTER.calls} since the kernel started")
    return messages


def answer(message) -> None:
    """A turn's last message in full: the model's answer, or the reason there is none."""
    if message.type == "ai" and message.text.startswith(LIMIT_REACHED):
        print(f"\n──── no answer {'─' * 56}")
        print("The run was stopped at the limit on model calls before the model answered.")
        print(message.text)
    else:
        print(f"\n──── answer {'─' * 59}")
        for line in (message.text.strip() or "(empty)").splitlines():
            indent = " " * (len(line) - len(line.lstrip()))
            print(textwrap.fill(line, WRAP, subsequent_indent=indent) if line.strip() else "")
    print("─" * 71)


def show(messages) -> None:
    """One line per message: the role, then what the message carries."""
    for m in messages:
        if m.type == "human":
            _line("user", m.text)
        elif m.type == "ai":
            for call in m.tool_calls:
                _line("assistant", f"calls {call['name']} "
                                   f"{json.dumps(call['args'], ensure_ascii=False)}")
            if m.text or not m.tool_calls:
                _line("assistant", m.text or "(empty)")
        elif m.type == "tool":
            _line("tool", f"{m.name} → {m.text}")
        else:
            _line(m.type, m.text)


def _line(role: str, text: str) -> None:
    text = " ".join(str(text).split())
    if len(text) > WIDTH:
        text = f"{text[:WIDTH]} … ({len(text):,} characters)"
    print(f"{role:10}  {text}")
