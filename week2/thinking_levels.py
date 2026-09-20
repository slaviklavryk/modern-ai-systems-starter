"""Week 2 — how much thinking does a task actually need?

Runs the same two tasks at every thinking level and reports what each one
cost. One task is trivial; the other requires several steps.

    python thinking_levels.py

The point is not that more thinking is better. It is that the amount a task
requires varies, and that both too little and too much are expensive in
different ways.

Note on `thinking_level` vs `thinking_budget`
---------------------------------------------
From Gemini 3.5 onwards, `thinking_budget` is rejected with an error. Use
`thinking_level`, whose values are MINIMAL, LOW, MEDIUM and HIGH.

This makes 8 API calls. At roughly 6 requests per minute on the free tier you
will see rate limiting partway through; the script waits and continues, so
expect it to take two to three minutes.
"""

import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

MODEL = "gemini-3.5-flash"
LEVELS = ["MINIMAL", "LOW", "MEDIUM", "HIGH"]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EASY = (
    "Classify this support ticket as exactly one word - billing, account, "
    'or technical: "invoice shows wrong VAT"'
)

HARD = (
    "A shop sells pens in packs of 7 and pencils in packs of 12. Anna bought "
    "3 packs of pens and 2 packs of pencils, then gave away 9 pens and 5 "
    "pencils. She then bought one more pack of each. How many pens and "
    "pencils does she have? Answer with just two numbers."
)

HARD_ANSWER = ("19", "31")


def ask(prompt: str, level: str):
    """One call at a given thinking level. Returns (thinking, answer, seconds, text)."""
    for attempt in range(1, 6):
        try:
            started = time.time()
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level=level)
                ),
            )
            usage = response.usage_metadata
            return (
                usage.thoughts_token_count or 0,
                usage.candidates_token_count or 0,
                time.time() - started,
                (response.text or "").strip(),
            )
        except errors.ClientError as exc:
            if exc.code != 429:
                raise
            print(f"    [rate limited, waiting 25s]")
            time.sleep(25)
        except errors.ServerError:
            print(f"    [503, model busy, retrying]")
            time.sleep(6)
    raise RuntimeError("gave up after 5 attempts")


def run(title: str, prompt: str, check=None) -> None:
    print(f"\n{title}")
    print(f"  {'level':<9}{'thinking':>9}{'answer':>8}{'seconds':>9}   result")
    print("  " + "-" * 68)
    for level in LEVELS:
        thinking, answer, seconds, text = ask(prompt, level)
        mark = ""
        if check is not None:
            mark = "  correct" if all(part in text for part in check) else "  WRONG"
        shown = text.replace("\n", " ")[:28]
        print(f"  {level:<9}{thinking:>9}{answer:>8}{seconds:>8.1f}s   {shown!r}{mark}")


if __name__ == "__main__":
    print(f"\nmodel: {MODEL}")

    run("EASY — classify a support ticket", EASY)
    run("HARD — several steps, one right answer", HARD, check=HARD_ANSWER)

    print(
        "\n  Two questions to answer from your own numbers:\n"
        "    1. On the easy task, what did the extra thinking buy you?\n"
        "    2. On the hard task, where is the lowest level that still gets it right?\n"
        "       What do the levels above it cost, and what do they add?\n"
        "\n  Note: the counts are not exact and not always ordered. The level sets\n"
        "  roughly how much reasoning is allowed, not a precise budget, so MEDIUM\n"
        "  can occasionally exceed HIGH. Re-run it and compare.\n"
    )
