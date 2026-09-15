"""Week 2 — assembling a context, one part at a time.

The exercises live in `context_lab.ipynb`. This file holds the helpers it uses,
so there is one copy of them rather than two:

    from context_lab import ask, show, counttokens, calls

Everything here is deliberately short enough to read. Open it.

Runs on Gemini by default. Set `LLM_PROVIDER=lightning` in `.env` to run this
same notebook against Lightning AI instead. See `llm_client.py` for exactly
what carries over and what does not between the two -- in particular,
`counttokens()` has no free equivalent on Lightning and falls back to a labelled
rough estimate rather than a measured figure; see its docstring below.

The shape of `ask()` is the lesson
----------------------------------
Each keyword argument is one row of the context table from the lecture:

    system=      standing rules, set once by you        (never changes)
    examples=    demonstrations of the task             (never changes)
    task=        what to do with the sources            (never changes)
    fmt=         the shape of the answer                (never changes)
    sources=     passages for THIS question             (changes every call)
    question     what the user asked                    (changes every call)

Only the last two change between calls. Everything above them is placed in the
context by software you wrote, which is why the course says context engineering
rather than prompting.

Note that `system` is not part of the prompt string. It is passed to the model
as a system instruction, which is why the Week 1 lab could not have discovered
it.

Rate limit
----------
Gemini's free tier allows roughly 6 generation requests per minute, in a fixed
window; LLMClient waits and retries rather than raising. `counttokens()` on Gemini
uses `count_tokens`, which does NOT consume that budget (measured: 10 calls in
2.1s), so inspect contexts as often as you like there -- it is the calls that
are scarce. This does not hold on Lightning; see `counttokens()` below.
"""

from llm_client import LLMClient

_llm = LLMClient()


def calls() -> int:
    """How many generation requests this notebook has made so far."""
    return _llm.calls


def counttokens(text: str) -> int:
    """Tokens in a string. Free and exact on Gemini (does not touch the 6/min
    budget). Lightning has no free tokenizer endpoint (verified 2026-09-13:
    none found), so on that backend this returns a rough ~4-characters-per-token
    estimate instead -- unmeasured, not to be treated as accurate, and present
    only so this function and show() keep working when LLM_PROVIDER=lightning.
    """
    try:
        return _llm.count_tokens(text)
    except NotImplementedError:
        return max(1, len(text) // 4)


def render(
    question: str,
    *,
    task: str | None = None,
    sources: list[str] | None = None,
    examples: list[tuple[str, str]] | None = None,
    fmt: str | None = None,
) -> str:
    """Assemble the prompt string from its parts.

    This is the whole of "context engineering" at Week 2 scale: a function that
    puts strings together in a fixed order. Read it, then read it again and
    notice that nothing here is done by the model.
    """
    blocks = []

    if sources:
        numbered = "\n".join(f"[{i}] {s.strip()}" for i, s in enumerate(sources, 1))
        blocks.append(f"SOURCES\n{numbered}")

    if examples:
        shown = "\n".join(f"  {inp}  ->  {out}" for inp, out in examples)
        blocks.append(f"EXAMPLES\n{shown}")

    if task:
        blocks.append(f"TASK\n{task.strip()}")

    if fmt:
        blocks.append(f"FORMAT\n{fmt.strip()}")

    blocks.append(f"QUESTION\n{question.strip()}")
    return "\n\n".join(blocks)


def show(question: str, *, system: str | None = None, **parts) -> str:
    """Print the context that WOULD be sent, and its token count. No API call
    on Gemini. On Lightning the count is an estimate -- see counttokens() -- so this
    still makes no call either way.
    """
    prompt = render(question, **parts)
    total = counttokens(prompt) + (counttokens(system) if system else 0)
    label = "tokens" if _llm.provider == "gemini" else "tokens (rough estimate -- see counttokens() docstring)"

    print("=" * 72)
    if system:
        print(f"SYSTEM (sent as a system instruction, not as prompt text)\n{system.strip()}\n")
    print(prompt)
    print("-" * 72)
    print(f"  [{total} {label}, every one of them paid for on every call]")
    return prompt


def ask(
    question: str,
    *,
    system: str | None = None,
    temperature: float | None = None,
    schema=None,
    level: str | None = None,
    show_prompt: bool = True,
    label: str = "",
    **parts,
):
    """Send one assembled context. Print the answer, return the result.

    Returns an llm_client.ChatResult, not a raw provider response, so notebook
    cells read `.text`, `.usage.thinking_tokens` / `.usage.prompt_tokens` /
    `.usage.answer_tokens`, and `.parsed` the same way regardless of which
    backend LLM_PROVIDER selects.
    """
    if label:
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))

    prompt = show(question, system=system, **parts) if show_prompt else render(question, **parts)

    result = _llm.chat(prompt, system=system, temperature=temperature, schema=schema, thinking=level)

    print(f"\n{result.text}\n")

    u = result.usage
    print(
        f"  [tokens] prompt={u.prompt_tokens} "
        f"thinking={u.thinking_tokens} "
        f"answer={u.answer_tokens}"
        f"   [calls this session: {_llm.calls}]"
    )
    return result


if __name__ == "__main__":
    # Smoke test: confirms the key, the SDK, and the network all work.
    # The actual exercises are in context_lab.ipynb.
    ask("Reply with exactly: context lab ready", show_prompt=False, label="smoke test")
