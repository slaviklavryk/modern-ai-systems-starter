"""Week 1 — prompt lab helpers.

The experiments live in `prompt_lab.ipynb`. This file holds the two helpers it
uses, so there is one copy of them rather than two:

    from prompt_lab import ask, repeat

Everything here is deliberately short enough to read. Open it.

Runs on Gemini by default. Set `LLM_PROVIDER=lightning` in `.env` to run this
same notebook against Lightning AI instead -- see `llm_client.py` for what
that does and does not carry over between the two.
"""

import pathlib
import sys

# `llm_client` lives in ../common (shared by Week 1 and Week 2). Put that folder
# on the path so `from llm_client import ...` works from this week's folder.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "common"))

from llm_client import LLMClient

_llm = LLMClient()
MODEL = _llm.model


def ask(prompt: str, *, label: str = "", show_tokens: bool = True) -> str:
    """Send one prompt. Print the answer, return it.

    Rate limits and transient server errors are handled inside LLMClient.
    """
    if label:
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
    print(f"> {prompt.strip()[:200]}")

    result = _llm.chat(prompt)

    print(f"\n{result.text}\n")

    if show_tokens:
        u = result.usage
        print(
            f"  [tokens] prompt={u.prompt_tokens} "
            f"thinking={u.thinking_tokens} "
            f"answer={u.answer_tokens}"
        )
    return result.text


def repeat(prompt: str, n: int = 3, *, label: str = "") -> list[str]:
    """Send the same prompt n times. Are the answers identical?"""
    if label:
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
    answers = []
    for i in range(n):
        print(f"\n--- run {i + 1} of {n} ---")
        answers.append(ask(prompt, show_tokens=True))
    identical = len(set(answers)) == 1
    print(f"\n  [all {n} runs identical? {identical}]")
    return answers


if __name__ == "__main__":
    # Smoke test: confirms the key, the SDK, and the network all work.
    # The actual experiments are in prompt_lab.ipynb.
    ask("Reply with exactly: prompt lab ready", label="smoke test")
