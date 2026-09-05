"""Week 1 — prompt lab helpers.

The experiments live in `prompt_lab.ipynb`. This file holds the two helpers it
uses, so there is one copy of them rather than two:

    from prompt_lab import ask, repeat

Everything here is deliberately short enough to read. Open it.
"""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

MODEL = "gemini-flash-latest"
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def ask(prompt: str, *, label: str = "", show_tokens: bool = True) -> str:
    """Send one prompt. Print the answer, return it.

    Handles the two failures you will actually hit:
      429  the free tier allows ~6 requests per minute, in a fixed window
      503  transient server load, unrelated to you
    """
    if label:
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
    print(f"> {prompt.strip()[:200]}")

    attempts = 6
    for attempt in range(1, attempts + 1):
        try:
            response = _client.models.generate_content(model=MODEL, contents=prompt)
            break
        except errors.ClientError as exc:
            if exc.code != 429:
                raise
            # A fixed per-minute window, not a backoff -- waiting 2s does nothing.
            print(f"  [rate limited: ~6 requests/minute. waiting 25s, attempt {attempt}]")
            time.sleep(25)
        except errors.ServerError:
            # Server-side load. Back off exponentially: the model is busy for
            # everyone, and retrying hard makes it worse.
            wait = min(4 * 2 ** (attempt - 1), 60)
            print(f"  [503, model busy. waiting {wait}s, attempt {attempt}/{attempts}]")
            time.sleep(wait)
    else:
        raise RuntimeError(
            f"{MODEL} stayed unavailable across {attempts} attempts. "
            "This is server-side load, not your key or your quota -- try again shortly."
        )

    text = (response.text or "").strip()
    print(f"\n{text}\n")

    if show_tokens:
        usage = response.usage_metadata
        print(
            f"  [tokens] prompt={usage.prompt_token_count} "
            f"thinking={usage.thoughts_token_count} "
            f"answer={usage.candidates_token_count}"
        )
    return text


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
